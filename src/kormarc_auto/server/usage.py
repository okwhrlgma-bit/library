"""사용량 카운터 + 결제 안내 (MVP).

파일 기반 카운터 (DB는 MVP-2). 키별로 누적 카운트 저장.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Any

from kormarc_auto.constants import (
    FREE_QUOTA_DEFAULT,
    PRICE_PER_RECORD_KRW,
    USAGE_DB_PATH,
    USAGE_LOG_PATH,
    get_payment_info_url,
)

logger = logging.getLogger(__name__)

_lock = Lock()


def _db_path() -> Path:
    path = Path(os.getenv("KORMARC_USAGE_DB", USAGE_DB_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _log_path() -> Path:
    path = Path(os.getenv("KORMARC_USAGE_LOG", USAGE_LOG_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]


def _load_db() -> dict[str, Any]:
    path = _db_path()
    if not path.exists():
        return {}
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("usage DB 로드 실패: %s — 빈 DB로 시작", e)
        return {}


def _save_db(db: dict[str, Any]) -> None:
    _db_path().write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def get_usage(api_key: str) -> dict[str, Any]:
    """키의 사용량 조회 (없으면 신규 발급 — quota=FREE_QUOTA_DEFAULT)."""
    key_hash = _hash_key(api_key)
    with _lock:
        db = _load_db()
        record = db.get(key_hash)
        if record is None:
            record = {
                "key_hash": key_hash,
                "free_quota": FREE_QUOTA_DEFAULT,
                "used": 0,
                "created_at": int(time.time()),
            }
            db[key_hash] = record
            _save_db(db)
    return dict(record)


def can_consume(api_key: str) -> tuple[bool, dict[str, Any]]:
    """사용 가능 여부 + 현재 상태 반환."""
    record = get_usage(api_key)
    remaining = record["free_quota"] - record["used"]
    return remaining > 0, {
        **record,
        "remaining": remaining,
        "price_per_record_krw": PRICE_PER_RECORD_KRW,
        "payment_url": get_payment_info_url() if remaining <= 5 else None,
    }


def consume(api_key: str, *, kind: str, ok: bool, ref: str | None = None) -> dict[str, Any]:
    """1회 사용 차감 + 로그 기록.

    Args:
        api_key: 사용자 API 키
        kind: 'isbn' / 'photo' / 'search' 등
        ok: 성공 여부 (실패는 차감하지 않음)
        ref: 식별자 (ISBN, query 등 — 마스킹 권장)

    Returns:
        업데이트된 사용량 dict
    """
    key_hash = _hash_key(api_key)
    if ok:
        with _lock:
            db = _load_db()
            record = db.setdefault(
                key_hash,
                {
                    "key_hash": key_hash,
                    "free_quota": FREE_QUOTA_DEFAULT,
                    "used": 0,
                    "created_at": int(time.time()),
                },
            )
            record["used"] += 1
            db[key_hash] = record
            _save_db(db)
    _append_log(key_hash=key_hash, kind=kind, ok=ok, ref=ref)
    _, status = can_consume(api_key)
    return status


def _append_log(*, key_hash: str, kind: str, ok: bool, ref: str | None) -> None:
    """logs/usage.jsonl에 한 줄 추가."""
    entry = {
        "ts": int(time.time()),
        "key_hash": key_hash,
        "kind": kind,
        "ok": ok,
        "ref": ref,
        "cost_estimate_krw": PRICE_PER_RECORD_KRW if ok else 0,
    }
    try:
        with _log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("usage 로그 기록 실패: %s", e)


def reset_usage(api_key: str) -> dict[str, Any]:
    """[관리자용] 키의 사용량 초기화."""
    key_hash = _hash_key(api_key)
    with _lock:
        db = _load_db()
        if key_hash in db:
            db[key_hash]["used"] = 0
            _save_db(db)
    return get_usage(api_key)


def export_account_data(api_key: str) -> dict[str, Any]:
    """개인정보 자기결정권 — 키 소유자 본인 데이터 일괄 다운로드.

    개인정보보호법 §35-3 (개인정보 전송요구권). 키별 모든 보유 데이터
    (사용량 + 사용 로그 + 가입 정보 + 피드백)를 한 dict로 반환.

    Returns:
        {
            "ok": True,
            "exported_at": iso8601,
            "key_hash": "...",
            "usage_record": {used, free_quota, created_at},
            "usage_log": [{ts, kind, ok, ref}, ...],
            "signup_record": {ts, email, library_name} | None,
            "feedback": [{ts, rating, category, comment}, ...],
        }
    """
    from datetime import datetime

    key_hash = _hash_key(api_key)
    with _lock:
        db = _load_db()
        usage_record = db.get(key_hash)

    # usage 로그 필터링
    usage_log: list[dict[str, Any]] = []
    log_path = _log_path()
    if log_path.exists():
        with log_path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("key_hash") == key_hash:
                    usage_log.append(e)

    # signup·feedback도 동일 key_hash로 필터링
    signup_record = _read_match("logs/signups.jsonl", key_hash)
    feedback_records = _read_match("logs/feedback.jsonl", key_hash, all_matches=True)

    return {
        "ok": True,
        "exported_at": datetime.now().isoformat(),
        "key_hash": key_hash,
        "usage_record": usage_record,
        "usage_log_count": len(usage_log),
        "usage_log": usage_log,
        "signup_record": signup_record,
        "feedback": feedback_records or [],
    }


def delete_account_data(api_key: str) -> dict[str, Any]:
    """개인정보 자기결정권 — 키 소유자 본인 데이터 영구 삭제.

    개인정보보호법 §36 (정정·삭제 요구권). 사용량 카운터·사용 로그·
    가입 기록·피드백을 모두 제거. 백업 zip은 별도(scripts/backup_logs.py).

    Returns:
        {"ok": True, "deleted": {usage: True/False, log_lines: int, signups: int, feedback: int}}
    """
    key_hash = _hash_key(api_key)
    deleted = {"usage": False, "log_lines": 0, "signups": 0, "feedback": 0}

    with _lock:
        db = _load_db()
        if key_hash in db:
            del db[key_hash]
            _save_db(db)
            deleted["usage"] = True

    log_path = _log_path()
    if log_path.exists():
        kept: list[str] = []
        removed = 0
        with log_path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    kept.append(line)
                    continue
                if e.get("key_hash") == key_hash:
                    removed += 1
                else:
                    kept.append(line)
        if removed:
            with log_path.open("w", encoding="utf-8") as f:
                f.writelines(kept)
        deleted["log_lines"] = removed

    deleted["signups"] = _strip_match("logs/signups.jsonl", key_hash)
    deleted["feedback"] = _strip_match("logs/feedback.jsonl", key_hash)

    return {"ok": True, "deleted": deleted}


def _read_match(
    relpath: str, key_hash: str, *, all_matches: bool = False
) -> Any:
    """logs/{relpath}에서 key_hash 일치 항목을 읽어옴."""
    path = Path(relpath)
    if not path.is_absolute():
        path = Path(os.getcwd()) / path
    if not path.exists():
        return [] if all_matches else None
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("key_hash") == key_hash or e.get("api_key_hash") == key_hash:
                out.append(e)
                if not all_matches:
                    return e
    return out if all_matches else (out[0] if out else None)


def _strip_match(relpath: str, key_hash: str) -> int:
    """logs/{relpath}에서 key_hash 일치 줄 제거. 제거 건수 반환."""
    path = Path(relpath)
    if not path.is_absolute():
        path = Path(os.getcwd()) / path
    if not path.exists():
        return 0
    kept: list[str] = []
    removed = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                kept.append(line)
                continue
            if e.get("key_hash") == key_hash or e.get("api_key_hash") == key_hash:
                removed += 1
            else:
                kept.append(line)
    if removed:
        with path.open("w", encoding="utf-8") as f:
            f.writelines(kept)
    return removed
