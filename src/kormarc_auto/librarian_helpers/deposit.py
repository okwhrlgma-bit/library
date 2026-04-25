"""납본 추적 — 도서관법 제20조(자료 납본) 관련 사서 보조.

도서관법 제20조: 도서관 자료를 발행·제작하는 자는 30일 내에 국립중앙도서관에
2부 이상 납본해야 함. 사서가 자관의 발간 자료 (학술지·연감·소식지·시민문집 등)
납본 이력을 추적·점검할 때 사용.

저장: logs/deposit_log.jsonl (가벼운 NDJSON)
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_lock = Lock()

# 도서관법 제20조: 발행 후 30일 이내 납본
DEPOSIT_DEADLINE_DAYS = 30


def _log_path() -> Path:
    p = Path(os.getenv("KORMARC_DEPOSIT_LOG", "logs/deposit_log.jsonl"))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def record_deposit(
    *,
    title: str,
    isbn: str | None = None,
    publication_date: str | date,
    deposit_date: str | date | None = None,
    recipient: str = "국립중앙도서관",
    copies: int = 2,
    note: str = "",
) -> dict[str, Any]:
    """납본 이력 1건 기록.

    Args:
        title: 자료 표제
        isbn: ISBN-13 (없으면 ISSN·자체번호)
        publication_date: 발행일 (YYYY-MM-DD)
        deposit_date: 납본일 (None이면 오늘)
        recipient: 납본 기관 (기본: 국립중앙도서관)
        copies: 납본 부수 (법정 2부)
        note: 자유 메모
    """
    pub_str = _to_str(publication_date)
    dep_str = _to_str(deposit_date) if deposit_date else date.today().isoformat()
    entry = {
        "id": f"dep_{int(time.time())}_{hash(title) & 0xFFFF:04x}",
        "ts": int(time.time()),
        "title": title,
        "isbn": isbn,
        "publication_date": pub_str,
        "deposit_date": dep_str,
        "recipient": recipient,
        "copies": int(copies),
        "note": note,
    }
    with _lock, _log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info("납본 이력 기록: %s (%s)", title, dep_str)
    return entry


def list_deposits(*, limit: int = 100) -> list[dict[str, Any]]:
    """전체 납본 이력 (최근순)."""
    p = _log_path()
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    out.sort(key=lambda e: e.get("ts", 0), reverse=True)
    return out[:limit]


def find_overdue_deposits(
    *,
    today: date | None = None,
    expected_publications: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """발행 후 30일 초과인데 납본 기록 없는 자료 찾기.

    Args:
        today: 기준일 (기본: 오늘)
        expected_publications: 자관이 발행한 자료 목록 [{title, isbn, publication_date}, ...].
            None이면 빈 리스트 (사서가 명시적으로 입력해야 함).

    Returns:
        납본 의무 위반 후보 리스트 + 경과 일수.
    """
    today = today or date.today()
    deposits = list_deposits(limit=10000)
    deposited_keys = {(d.get("isbn") or d["title"]) for d in deposits}

    overdue: list[dict[str, Any]] = []
    for pub in expected_publications or []:
        key = pub.get("isbn") or pub.get("title")
        if not key or key in deposited_keys:
            continue
        try:
            pub_date = datetime.strptime(pub["publication_date"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        days_since = (today - pub_date).days
        if days_since > DEPOSIT_DEADLINE_DAYS:
            overdue.append(
                {
                    "title": pub.get("title"),
                    "isbn": pub.get("isbn"),
                    "publication_date": pub["publication_date"],
                    "days_since_publication": days_since,
                    "deadline_passed_by": days_since - DEPOSIT_DEADLINE_DAYS,
                }
            )
    overdue.sort(key=lambda x: x["deadline_passed_by"], reverse=True)
    return overdue


def _to_str(d: str | date | datetime) -> str:
    if isinstance(d, str):
        return d
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


def deposit_deadline(publication_date: str | date) -> date:
    """발행일 → 납본 마감일 (발행 후 30일)."""
    if isinstance(publication_date, str):
        pub = datetime.strptime(publication_date, "%Y-%m-%d").date()
    elif isinstance(publication_date, datetime):
        pub = publication_date.date()
    else:
        pub = publication_date
    return pub + timedelta(days=DEPOSIT_DEADLINE_DAYS)


__all__ = [
    "DEPOSIT_DEADLINE_DAYS",
    "deposit_deadline",
    "find_overdue_deposits",
    "list_deposits",
    "record_deposit",
]
