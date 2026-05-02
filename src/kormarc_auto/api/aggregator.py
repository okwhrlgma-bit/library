"""다중 소스 통합 — 폴백 순서대로 호출하고 결과를 신뢰도 가중 통합.

Part 87 (2026-05-03) waterfall 정식화:
- KDC 폴백 = nl_korea(SEOJI) → data4library → 부가기호 디코더 → AI
- 부가기호 = 0 API 호출·100% 정확 = SEOJI KDC 공백 (2020-12-31 이후) 즉시 해소
"""

from __future__ import annotations

import logging
from typing import Any

from kormarc_auto.api import aladin, data4library, kakao, nl_korea
from kormarc_auto.classification.budgaeho_decoder import decode_budgaeho

logger = logging.getLogger(__name__)

# 필드별로 어느 소스를 우선할지. 신뢰도 순서.
FIELD_PRIORITY: dict[str, list[str]] = {
    "title": ["nl_korea", "aladin", "kakao"],
    "author": ["nl_korea", "aladin", "kakao"],
    "publisher": ["nl_korea", "aladin", "kakao"],
    "publication_year": ["nl_korea", "aladin", "kakao"],
    "publication_date": ["nl_korea", "aladin", "kakao"],
    "kdc": ["nl_korea"],  # KDC는 NL Korea가 가장 정확
    "ddc": ["nl_korea"],
    "summary": ["aladin", "nl_korea", "kakao"],  # 알라딘이 풍부
    "toc": ["aladin", "nl_korea"],
    "cover_url": ["aladin", "kakao"],
    "price": ["nl_korea", "aladin"],
    "pages": ["nl_korea"],
    "book_size": ["nl_korea"],
    "series_title": ["nl_korea", "aladin"],
    "series_no": ["nl_korea"],
    "additional_code": ["nl_korea"],
    "category": ["aladin", "kakao"],
    "story": ["aladin"],
}


def aggregate_by_isbn(isbn: str) -> dict[str, Any]:
    """폴백 순서로 외부 API 호출 → 통합 BookData 반환.

    Args:
        isbn: 13자리 ISBN

    Returns:
        통합된 dict. 추가 필드:
        - `sources`: 호출 성공한 소스 리스트
        - `source_map`: 각 필드가 어느 소스에서 왔는지
        - `confidence`: 종합 신뢰도 (가장 높은 소스 기준)
        - `attributions`: 출처 표시 의무 문구 리스트
        - `keywords`: 도정나 키워드 (있으면)
    """
    results: dict[str, dict[str, Any]] = {}

    # 1순위: 국립중앙도서관
    try:
        nl = nl_korea.fetch_by_isbn(isbn)
        if nl:
            results["nl_korea"] = nl
    except nl_korea.NLKoreaAPIError as e:
        logger.warning("NL Korea 실패, 다음 소스로 폴백: %s", e)

    # 2순위: 알라딘
    try:
        al = aladin.fetch_by_isbn(isbn)
        if al:
            results["aladin"] = al
    except aladin.AladinAPIError as e:
        logger.warning("알라딘 실패, 다음 소스로 폴백: %s", e)

    # 3순위: 카카오 (NL과 알라딘 모두 실패 시에만 호출 — 한도 절약)
    if not results:
        try:
            kk = kakao.fetch_by_isbn(isbn)
            if kk:
                results["kakao"] = kk
        except kakao.KakaoAPIError as e:
            logger.warning("카카오 실패: %s", e)

    if not results:
        logger.error("모든 소스 실패: ISBN=%s", isbn)
        return {
            "isbn": isbn,
            "sources": [],
            "source_map": {},
            "confidence": 0.0,
            "attributions": [],
            "keywords": [],
        }

    merged = _merge_by_priority(results)
    merged["isbn"] = isbn
    merged["sources"] = list(results.keys())
    merged["confidence"] = max(r["confidence"] for r in results.values())

    attributions = [r["attribution"] for r in results.values() if r.get("attribution")]
    merged["attributions"] = attributions

    # 보조: 도정나 키워드
    try:
        merged["keywords"] = data4library.fetch_keywords(isbn)
    except Exception as e:
        logger.debug("도정나 키워드 조회 실패: %s", e)
        merged["keywords"] = []

    # KDC 폴백: SEOJI/data4library 모두 미스 시 부가기호에서 추출 (Part 87)
    if not merged.get("kdc") and merged.get("additional_code"):
        decoded = decode_budgaeho(str(merged["additional_code"]))
        if decoded:
            merged["kdc"] = decoded.kdc_2digit
            merged["kdc_source"] = "budgaeho_decoder"
            merged.setdefault("source_map", {})["kdc"] = "budgaeho"
            merged["kdc_audience"] = decoded.target_audience
            merged["kdc_form"] = decoded.publication_form
            logger.info(
                "KDC 폴백 = 부가기호 디코더 (ISBN=%s, KDC=%s, 출처=%s)",
                isbn,
                decoded.kdc_2digit,
                decoded.raw,
            )

    return merged


def _merge_by_priority(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """필드별 우선순위에 따라 가장 신뢰도 높은 값 선택."""
    merged: dict[str, Any] = {}
    source_map: dict[str, str] = {}

    all_fields = set()
    for r in results.values():
        all_fields.update(r.keys())
    all_fields -= {"source", "confidence", "attribution", "raw"}

    for field in all_fields:
        priority = FIELD_PRIORITY.get(field, list(results.keys()))
        for source_name in priority:
            if source_name in results:
                value = results[source_name].get(field)
                if value not in (None, "", [], {}):
                    merged[field] = value
                    source_map[field] = source_name
                    break

    merged["source_map"] = source_map
    return merged
