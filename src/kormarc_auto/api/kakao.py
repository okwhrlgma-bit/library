"""카카오 책 검색 API 클라이언트 (보조).

엔드포인트: https://dapi.kakao.com/v3/search/book
인증: REST API 키 (Authorization 헤더)
신뢰도: 0.75 (보조 소스)
일일 호출 한도: 30,000회 (넉넉)
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

from kormarc_auto.api._http import cached_get
from kormarc_auto.constants import CONFIDENCE_KAKAO, HTTP_TIMEOUT, KAKAO_BOOK_URL

logger = logging.getLogger(__name__)

KAKAO_API_URL = KAKAO_BOOK_URL
DEFAULT_TIMEOUT = HTTP_TIMEOUT
SOURCE_NAME = "kakao"
SOURCE_CONFIDENCE = CONFIDENCE_KAKAO


class KakaoAPIError(Exception):
    """카카오 API 호출 실패."""


def fetch_by_isbn(isbn: str, *, api_key: str | None = None) -> dict[str, Any] | None:
    """ISBN으로 카카오 책 검색.

    Args:
        isbn: 10자리 또는 13자리 ISBN
        api_key: REST API 키. 미지정 시 KAKAO_API_KEY 환경변수 사용.

    Returns:
        조회 성공 시 정규화된 dict, 없으면 None.
    """
    key = api_key or os.getenv("KAKAO_API_KEY")
    if not key:
        raise KakaoAPIError("KAKAO_API_KEY 환경변수가 설정되지 않았습니다.")

    headers = {"Authorization": f"KakaoAK {key}"}
    params = {"target": "isbn", "query": isbn}

    try:
        response = cached_get(
            KAKAO_API_URL, params=params, headers=headers, timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
    except requests.Timeout as e:
        logger.warning("카카오 API 타임아웃: isbn=%s", isbn)
        raise KakaoAPIError(f"타임아웃 (isbn={isbn})") from e
    except requests.RequestException as e:
        logger.warning("카카오 API 요청 실패: isbn=%s, err=%s", isbn, e)
        raise KakaoAPIError(f"요청 실패: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise KakaoAPIError(f"JSON 파싱 실패: {e}") from e

    docs = data.get("documents", [])
    if not docs:
        return None

    return _normalize(docs[0])


def search_by_query(
    query: str,
    *,
    api_key: str | None = None,
    limit: int = 10,
    target: str = "title",
) -> list[dict[str, Any]]:
    """카카오 책 검색 — 키워드/표제/저자.

    Args:
        query: 검색어
        api_key: REST API 키 (없으면 환경변수)
        limit: 최대 결과 수 (1~50)
        target: "title" / "isbn" / "publisher" / "person"

    Returns:
        후보 리스트 (각 항목은 _normalize 결과).
    """
    key = api_key or os.getenv("KAKAO_API_KEY")
    if not key:
        raise KakaoAPIError("KAKAO_API_KEY 환경변수가 설정되지 않았습니다.")

    headers = {"Authorization": f"KakaoAK {key}"}
    params = {"query": query, "size": max(1, min(limit, 50)), "target": target}

    try:
        response = cached_get(
            KAKAO_API_URL, params=params, headers=headers, timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
    except requests.Timeout as e:
        raise KakaoAPIError(f"타임아웃 (query={query})") from e
    except requests.RequestException as e:
        raise KakaoAPIError(f"요청 실패: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise KakaoAPIError(f"JSON 파싱 실패: {e}") from e

    docs = data.get("documents", []) or []
    return [_normalize(d) for d in docs[:limit]]


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """카카오 응답을 공통 BookData 형식으로 정규화."""
    isbn_field = raw.get("isbn", "")
    isbn13 = next((tok for tok in isbn_field.split() if len(tok) == 13), None)

    authors = raw.get("authors", [])
    translators = raw.get("translators", [])

    pubdate = raw.get("datetime", "")
    pubyear = pubdate[:4] if pubdate else None

    return {
        "source": SOURCE_NAME,
        "confidence": SOURCE_CONFIDENCE,
        "isbn": isbn13 or isbn_field,
        "title": raw.get("title"),
        "author": " ; ".join(authors) if authors else None,
        "translators": translators,
        "publisher": raw.get("publisher"),
        "publication_year": pubyear,
        "publication_date": pubdate,
        "price": raw.get("price"),
        "summary": raw.get("contents"),
        "cover_url": raw.get("thumbnail"),
        "category": raw.get("status"),
        "raw": raw,
    }
