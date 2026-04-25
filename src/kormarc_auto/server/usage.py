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
    PAYMENT_INFO_URL,
    PRICE_PER_RECORD_KRW,
    USAGE_DB_PATH,
    USAGE_LOG_PATH,
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
        "payment_url": PAYMENT_INFO_URL if remaining <= 5 else None,
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
