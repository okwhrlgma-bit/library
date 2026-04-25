"""자관 장서 DB — 생성한 .mrc 파일 인덱스·내부 검색.

사서가 우리 도구로 생성한 .mrc를 자기 도서관 정보로 누적·검색·일괄편집.
KOLAS·DLS와 별개로 우리 시스템 안에서도 검색 가능하게 함.

저장: logs/library_index.jsonl (가벼운 NDJSON, SQLite 없이)
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

logger = logging.getLogger(__name__)

_lock = Lock()


def _index_path() -> Path:
    path = Path(os.getenv("KORMARC_LIBRARY_INDEX", "logs/library_index.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def add_record(book_data: dict[str, Any], *, mrc_path: str | None = None) -> str:
    """1건 인덱스 추가. record_id 반환."""
    record_id = hashlib.sha1(
        f"{book_data.get('isbn', '')}_{book_data.get('title', '')}_{time.time()}".encode()
    ).hexdigest()[:12]
    entry = {
        "id": record_id,
        "ts": int(time.time()),
        "isbn": book_data.get("isbn"),
        "title": book_data.get("title"),
        "subtitle": book_data.get("subtitle"),
        "author": book_data.get("author"),
        "publisher": book_data.get("publisher"),
        "publication_year": book_data.get("publication_year"),
        "kdc": book_data.get("kdc"),
        "ddc": book_data.get("ddc"),
        "registration_no": book_data.get("registration_no"),
        "call_number": book_data.get("call_number"),
        "mrc_path": mrc_path,
    }
    with _lock:
        with _index_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return record_id


def search_local(
    query: str = "",
    *,
    kdc_prefix: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """자관 장서 검색 (필드 통합 + KDC 범위 + 연도 범위)."""
    path = _index_path()
    if not path.exists():
        return []

    q = query.strip().lower() if query else ""
    out: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if q:
                    haystack = " ".join(
                        str(e.get(k, "") or "")
                        for k in ("isbn", "title", "subtitle", "author", "publisher", "registration_no", "call_number")
                    ).lower()
                    if q not in haystack:
                        continue

                if kdc_prefix:
                    kdc = str(e.get("kdc") or "")
                    if not kdc.startswith(kdc_prefix):
                        continue

                yr_str = str(e.get("publication_year") or "")
                if yr_str.isdigit():
                    yr = int(yr_str)
                    if year_from and yr < year_from:
                        continue
                    if year_to and yr > year_to:
                        continue

                out.append(e)
    except OSError:
        return []

    out.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return out[:limit]


def stats() -> dict[str, Any]:
    """자관 장서 통계 (PO 통계·보고서용)."""
    path = _index_path()
    if not path.exists():
        return {"total": 0, "by_kdc_main": {}, "by_year": {}}

    total = 0
    by_kdc_main: dict[str, int] = {}
    by_year: dict[str, int] = {}
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                kdc = str(e.get("kdc") or "")
                main = kdc[:1] + "00" if kdc else "미분류"
                by_kdc_main[main] = by_kdc_main.get(main, 0) + 1
                yr = str(e.get("publication_year") or "미상")[:4]
                by_year[yr] = by_year.get(yr, 0) + 1
    except OSError:
        return {"total": 0, "by_kdc_main": {}, "by_year": {}}

    return {
        "total": total,
        "by_kdc_main": dict(sorted(by_kdc_main.items())),
        "by_year": dict(sorted(by_year.items(), reverse=True)),
    }


def delete_record(record_id: str) -> bool:
    """레코드 1건 삭제 (휴지통 → 30일 보관은 추후 별도 모듈)."""
    path = _index_path()
    if not path.exists():
        return False
    found = False
    with _lock:
        lines: list[str] = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get("id") == record_id:
                        found = True
                        continue
                except json.JSONDecodeError:
                    pass
                lines.append(line)
        if found:
            path.write_text("".join(lines), encoding="utf-8")
    return found
