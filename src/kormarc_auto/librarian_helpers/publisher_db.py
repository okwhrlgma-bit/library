"""출판사 정보 캐시 + ISBN 출판사 식별자 매핑.

ISBN 분해:
  978 89 937462 78 8
  접두 국가 출판사ID 책번호 체크섬

같은 출판사 책은 같은 출판사ID(978-89-{XXXXXX}) → 한 번 등록하면 다음부터 자동.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_lock = Lock()


def _db_path() -> Path:
    path = Path(os.getenv("KORMARC_PUBLISHER_DB", "logs/publisher_cache.json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load() -> dict[str, dict[str, Any]]:
    path = _db_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save(db: dict[str, dict[str, Any]]) -> None:
    _db_path().write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_publisher_id(isbn: str) -> str | None:
    """ISBN-13에서 한국 출판사 식별자 추출.

    978-89-{2~5자리 출판사ID}-{책번호}-{체크섬}

    한국 출판사ID 길이는 가변이라 정확한 분해는 ISBN 한국위원회 매핑표 필요.
    여기선 단순 키로 사용 (ISBN[3:9] = 6자리)
    """
    digits = "".join(c for c in isbn if c.isdigit())
    if len(digits) != 13:
        return None
    if not (digits.startswith("97889") or digits.startswith("97879")):
        return None
    # 978/979 + 89 = 5자리 + 출판사ID + 책번호 + 체크섬
    # 한국 출판사ID는 1~7자리. 평균 6자리로 가정 (대형 출판사는 짧음)
    return digits[5:9]  # 4자리 prefix를 출판사 그룹 키로


def lookup_publisher(isbn: str) -> dict[str, Any] | None:
    """ISBN으로 캐시된 출판사 정보 조회."""
    pub_id = extract_publisher_id(isbn)
    if not pub_id:
        return None
    with _lock:
        db = _load()
        return db.get(pub_id)


def remember_publisher(
    isbn: str,
    *,
    publisher: str,
    publication_place: str | None = None,
    series_titles: list[str] | None = None,
) -> None:
    """ISBN의 출판사 정보 캐시에 저장.

    같은 출판사ID의 다음 책은 자동 채움.
    """
    pub_id = extract_publisher_id(isbn)
    if not pub_id or not publisher:
        return

    with _lock:
        db = _load()
        existing = db.get(pub_id, {})
        existing["publisher"] = publisher
        if publication_place:
            existing["publication_place"] = publication_place
        if series_titles:
            existing.setdefault("series_titles", [])
            for s in series_titles:
                if s and s not in existing["series_titles"]:
                    existing["series_titles"].append(s)
                    existing["series_titles"] = existing["series_titles"][:20]
        existing["use_count"] = int(existing.get("use_count", 0)) + 1
        db[pub_id] = existing
        _save(db)


def autocomplete_publishers(prefix: str, *, limit: int = 10) -> list[str]:
    """입력 prefix로 시작하는 출판사 자동완성 (사용 빈도 내림차순)."""
    if not prefix:
        return []
    prefix = prefix.strip().lower()
    with _lock:
        db = _load()

    matches = [
        (entry["publisher"], int(entry.get("use_count", 0)))
        for entry in db.values()
        if entry.get("publisher") and entry["publisher"].lower().startswith(prefix)
    ]
    matches.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in matches[:limit]]


def all_publishers() -> list[dict[str, Any]]:
    """저장된 모든 출판사 (PO 점검용)."""
    with _lock:
        return list(_load().values())
