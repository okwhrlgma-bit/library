"""국립중앙도서관 ISBN 서지정보 API 클라이언트.

엔드포인트: https://www.nl.go.kr/seoji/SearchApi.do
인증: 회원가입 → 인증키 신청 → 담당자 승인 (1~3 영업일)
신뢰도: 0.95 (한국 자료 1순위 데이터 소스)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

from kormarc_auto.api._http import cached_get
from kormarc_auto.constants import (
    CONFIDENCE_NL_KOREA,
    HTTP_TIMEOUT,
    NL_KOREA_ATTRIBUTION,
    NL_KOREA_ISBN_URL,
)

logger = logging.getLogger(__name__)

NL_API_URL = NL_KOREA_ISBN_URL
DEFAULT_TIMEOUT = HTTP_TIMEOUT
SOURCE_NAME = "nl_korea"
SOURCE_CONFIDENCE = CONFIDENCE_NL_KOREA
SOURCE_ATTRIBUTION = NL_KOREA_ATTRIBUTION


class NLKoreaAPIError(Exception):
    """국립중앙도서관 API 호출 실패."""


def fetch_by_isbn(isbn: str, *, cert_key: str | None = None) -> dict[str, Any] | None:
    """ISBN으로 국립중앙도서관 서지 정보를 조회한다.

    Args:
        isbn: 13자리 ISBN (하이픈 제거됨)
        cert_key: 인증키. 미지정 시 환경변수 NL_CERT_KEY 사용.

    Returns:
        조회 성공 시 정규화된 dict (source, confidence, raw 포함).
        ISBN 미등록 또는 응답 비어있을 시 None.

    Raises:
        NLKoreaAPIError: 네트워크 오류, 인증 실패, 응답 파싱 실패.
    """
    key = cert_key or os.getenv("NL_CERT_KEY")
    if not key:
        raise NLKoreaAPIError("NL_CERT_KEY 환경변수가 설정되지 않았습니다.")

    params = {
        "cert_key": key,
        "result_style": "json",
        "page_no": 1,
        "page_size": 10,
        "isbn": isbn,
    }

    try:
        response = cached_get(NL_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as e:
        logger.warning("NL Korea API 타임아웃: isbn=%s", isbn)
        raise NLKoreaAPIError(f"타임아웃 (isbn={isbn})") from e
    except requests.RequestException as e:
        logger.warning("NL Korea API 요청 실패: isbn=%s, err=%s", isbn, e)
        raise NLKoreaAPIError(f"요청 실패: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise NLKoreaAPIError(f"JSON 파싱 실패: {e}") from e

    docs = data.get("docs", [])
    if not docs:
        logger.info("NL Korea: ISBN %s 미등록", isbn)
        return None

    raw = docs[0]
    return _normalize(raw)


def search_by_query(
    query: str,
    *,
    cert_key: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """키워드(표제·저자 등)로 국립중앙도서관 ISBN 서지 검색.

    Args:
        query: 검색어 (표제·저자·키워드)
        cert_key: 인증키 (없으면 환경변수)
        limit: 최대 결과 수

    Returns:
        후보 리스트 (각 항목은 _normalize 결과와 동일 구조).
    """
    key = cert_key or os.getenv("NL_CERT_KEY")
    if not key:
        raise NLKoreaAPIError("NL_CERT_KEY 환경변수가 설정되지 않았습니다.")

    params = {
        "cert_key": key,
        "result_style": "json",
        "page_no": 1,
        "page_size": max(1, min(limit, 30)),
        "title": query,
    }

    try:
        response = cached_get(NL_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as e:
        raise NLKoreaAPIError(f"타임아웃 (query={query})") from e
    except requests.RequestException as e:
        raise NLKoreaAPIError(f"요청 실패: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise NLKoreaAPIError(f"JSON 파싱 실패: {e}") from e

    docs = data.get("docs", []) or []
    return [_normalize(d) for d in docs[:limit]]


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """국립중앙도서관 응답을 공통 BookData 형식으로 정규화."""

    def _clean(value: Any) -> str | None:
        """공백 제거 + 빈 값 None 변환."""
        if value is None:
            return None
        s = str(value).strip()
        return s or None

    isbn = _clean(raw.get("EA_ISBN")) or _clean(raw.get("ISBN"))
    title = _clean(raw.get("TITLE"))
    author = _clean(raw.get("AUTHOR"))
    publisher = _clean(raw.get("PUBLISHER"))

    pubdate = _clean(raw.get("PUBLISH_PREDATE"))  # YYYYMMDD or YYYY-MM-DD
    pubyear = pubdate[:4] if pubdate else None

    # 가격 (PRE_PRICE는 문자열, 숫자만 추출)
    price_raw = _clean(raw.get("PRE_PRICE"))
    price = None
    if price_raw and price_raw.isdigit():
        price = int(price_raw)

    # 페이지수 ("345 p." 같은 형태)
    page_raw = _clean(raw.get("PAGE"))

    return {
        "source": SOURCE_NAME,
        "confidence": SOURCE_CONFIDENCE,
        "attribution": SOURCE_ATTRIBUTION,
        "isbn": isbn,
        "title": title,
        "subtitle": _clean(raw.get("SUBTITLE")),
        "author": author,
        "publisher": publisher,
        "publication_year": pubyear,
        "publication_date": pubdate,
        "publication_place": _clean(raw.get("PUBLISHER_URL")),  # 정확하진 않음, 대체값
        "price": price,
        "additional_code": _clean(raw.get("ADDITIONAL_CODE")),
        "kdc": _clean(raw.get("KDC")),
        "ddc": _clean(raw.get("DDC")),
        "pages": page_raw,
        "book_size": _clean(raw.get("BOOK_SIZE")),
        "series_title": _clean(raw.get("SERIES_TITLE")),
        "series_no": _clean(raw.get("SERIES_NO")),
        "summary": _clean(raw.get("BOOK_SUMMARY")) or _clean(raw.get("BOOK_INTRODUCTION")),
        "toc": _clean(raw.get("TABLE_OF_CONTENTS")),
        "keywords": _clean(raw.get("KEYWORD")),
        "raw": raw,
    }
