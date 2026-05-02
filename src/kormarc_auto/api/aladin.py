"""알라딘 OPEN API 클라이언트.

엔드포인트: http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx
인증: TTBKey (회원가입 + 블로그 등록 후 1~2일)
신뢰도: 0.80 (상용 데이터, 출처 표시 의무)
출처 표시: "도서 DB 제공 : 알라딘 인터넷서점(www.aladin.co.kr)"
일일 호출 한도: 5,000회
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

from kormarc_auto.api._http import cached_get
from kormarc_auto.constants import (
    ALADIN_ATTRIBUTION,
    ALADIN_LOOKUP_URL,
    ALADIN_SEARCH_URL,
    CONFIDENCE_ALADIN,
    HTTP_TIMEOUT,
)

logger = logging.getLogger(__name__)

ALADIN_API_URL = ALADIN_LOOKUP_URL
DEFAULT_TIMEOUT = HTTP_TIMEOUT
SOURCE_NAME = "aladin"
SOURCE_CONFIDENCE = CONFIDENCE_ALADIN
SOURCE_ATTRIBUTION = ALADIN_ATTRIBUTION


class AladinAPIError(Exception):
    """알라딘 API 호출 실패."""


def fetch_by_isbn(isbn: str, *, ttb_key: str | None = None) -> dict[str, Any] | None:
    """ISBN으로 알라딘 도서 정보를 조회한다.

    Args:
        isbn: 13자리 ISBN
        ttb_key: TTBKey. 미지정 시 환경변수 ALADIN_TTB_KEY 사용.

    Returns:
        조회 성공 시 정규화된 dict.
        미등록 시 None.

    Raises:
        AladinAPIError: 네트워크/인증/파싱 오류.

    Note:
        반환 데이터 사용 시 반드시 출처 표시 (`SOURCE_ATTRIBUTION`).
    """
    key = ttb_key or os.getenv("ALADIN_TTB_KEY")
    if not key:
        raise AladinAPIError("ALADIN_TTB_KEY 환경변수가 설정되지 않았습니다.")

    params = {
        "ttbkey": key,
        "itemIdType": "ISBN13",
        "ItemId": isbn,
        "output": "js",
        "Version": "20131101",
        "OptResult": "ebookList,usedList,Toc,Story",
    }

    try:
        response = cached_get(ALADIN_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as e:
        logger.warning("알라딘 API 타임아웃: isbn=%s", isbn)
        raise AladinAPIError(f"타임아웃 (isbn={isbn})") from e
    except requests.RequestException as e:
        logger.warning("알라딘 API 요청 실패: isbn=%s, err=%s", isbn, e)
        raise AladinAPIError(f"요청 실패: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise AladinAPIError(f"JSON 파싱 실패: {e}") from e

    items = data.get("item", [])
    if not items:
        logger.info("알라딘: ISBN %s 미등록", isbn)
        return None

    return _normalize(items[0])


def search_by_query(
    query: str,
    *,
    ttb_key: str | None = None,
    limit: int = 10,
    query_type: str = "Keyword",
) -> list[dict[str, Any]]:
    """알라딘 ItemSearch — 키워드/표제/저자 검색.

    Args:
        query: 검색어
        ttb_key: 인증키 (없으면 환경변수)
        limit: 최대 결과 수 (1~50)
        query_type: "Keyword" / "Title" / "Author" / "Publisher"

    Returns:
        후보 리스트 (각 항목은 _normalize 결과). 출처 표시 의무.
    """
    key = ttb_key or os.getenv("ALADIN_TTB_KEY")
    if not key:
        raise AladinAPIError("ALADIN_TTB_KEY 환경변수가 설정되지 않았습니다.")

    params = {
        "ttbkey": key,
        "Query": query,
        "QueryType": query_type,
        "MaxResults": max(1, min(limit, 50)),
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101",
        "OptResult": "ebookList",
    }

    try:
        response = cached_get(ALADIN_SEARCH_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as e:
        raise AladinAPIError(f"타임아웃 (query={query})") from e
    except requests.RequestException as e:
        raise AladinAPIError(f"요청 실패: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise AladinAPIError(f"JSON 파싱 실패: {e}") from e

    items = data.get("item", []) or []
    return [_normalize(it) for it in items[:limit]]


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """알라딘 응답을 공통 BookData 형식으로 정규화."""

    def _clean(value: Any) -> str | None:
        if value is None:
            return None
        s = str(value).strip()
        return s or None

    pubdate = _clean(raw.get("pubDate"))  # "YYYY-MM-DD"
    pubyear = pubdate[:4] if pubdate else None

    price_raw = raw.get("priceStandard") or raw.get("priceSales")
    price = (
        int(price_raw) if isinstance(price_raw, (int, str)) and str(price_raw).isdigit() else None
    )

    sub_info = raw.get("subInfo", {}) if isinstance(raw.get("subInfo"), dict) else {}

    return {
        "source": SOURCE_NAME,
        "confidence": SOURCE_CONFIDENCE,
        "attribution": SOURCE_ATTRIBUTION,
        "isbn": _clean(raw.get("isbn13")) or _clean(raw.get("isbn")),
        "title": _clean(raw.get("title")),
        "author": _clean(raw.get("author")),
        "publisher": _clean(raw.get("publisher")),
        "publication_year": pubyear,
        "publication_date": pubdate,
        "price": price,
        "summary": _clean(raw.get("description")),
        "category": _clean(raw.get("categoryName")),
        "cover_url": _clean(raw.get("cover")),
        "toc": _clean(sub_info.get("toc")),
        "story": _clean(sub_info.get("story")),
        "raw": raw,
    }
