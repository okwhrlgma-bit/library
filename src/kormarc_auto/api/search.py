"""키워드/표제/저자 다건 검색 — 사서가 ISBN 모를 때 사용.

폴백: NL Korea → 알라딘 → 카카오. 결과는 ISBN으로 dedup 후 신뢰도 정렬.
"""

from __future__ import annotations

import logging
from typing import Any

from kormarc_auto.api import aladin, kakao, nl_korea

logger = logging.getLogger(__name__)


def search_by_query(query: str, *, limit: int = 10) -> list[dict[str, Any]]:
    """다중 소스 키워드 검색 → 후보 도서 리스트.

    Args:
        query: 검색어 (표제/저자/키워드)
        limit: 최대 결과 수

    Returns:
        후보 dict 리스트. 각 항목 키:
        - isbn, title, author, publisher, publication_year, cover_url
        - confidence (0.0~1.0), source (소스명), attribution (있을 때)
    """
    if not query or not query.strip():
        return []

    candidates: list[dict[str, Any]] = []

    # 1. 국립중앙도서관 (한국 자료 1순위)
    try:
        nl_results = nl_korea.search_by_query(query, limit=limit)
        candidates.extend(_pick_search_fields(nl_results))
    except nl_korea.NLKoreaAPIError as e:
        logger.warning("NL Korea 검색 실패: %s", e)

    # 2. 알라딘 (상용)
    if len(_dedup_by_isbn(candidates)) < limit:
        try:
            al_results = aladin.search_by_query(query, limit=limit)
            candidates.extend(_pick_search_fields(al_results))
        except aladin.AladinAPIError as e:
            logger.warning("알라딘 검색 실패: %s", e)

    # 3. 카카오 (보조)
    if len(_dedup_by_isbn(candidates)) < limit:
        try:
            kk_results = kakao.search_by_query(query, limit=limit)
            candidates.extend(_pick_search_fields(kk_results))
        except kakao.KakaoAPIError as e:
            logger.warning("카카오 검색 실패: %s", e)

    # 4. ISBN dedup + 신뢰도 정렬
    deduped = _dedup_by_isbn(candidates)
    deduped.sort(key=lambda c: c.get("confidence", 0.0), reverse=True)
    return deduped[:limit]


def _pick_search_fields(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """소스별 정규화 결과 → 검색 후보 형식 (가벼운 dict)."""
    out: list[dict[str, Any]] = []
    for r in results:
        if not r:
            continue
        out.append(
            {
                "isbn": r.get("isbn"),
                "title": r.get("title"),
                "author": r.get("author"),
                "publisher": r.get("publisher"),
                "publication_year": r.get("publication_year"),
                "cover_url": r.get("cover_url"),
                "confidence": r.get("confidence", 0.0),
                "source": r.get("source", "unknown"),
                "attribution": r.get("attribution"),
            }
        )
    return out


def _dedup_by_isbn(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """ISBN 기준 중복 제거 — 같은 ISBN이면 confidence 높은 쪽 유지."""
    seen: dict[str, dict[str, Any]] = {}
    for c in candidates:
        isbn = c.get("isbn")
        key = str(isbn) if isbn else f"_no_isbn_{c.get('title', '')}_{c.get('author', '')}"
        existing = seen.get(key)
        if existing is None or c.get("confidence", 0.0) > existing.get("confidence", 0.0):
            seen[key] = c
    return list(seen.values())
