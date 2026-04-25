"""도서관 정보나루 API 클라이언트 (보조 — 키워드/대출통계).

엔드포인트: http://data4library.kr
인증: authKey (무료 발급)
용도: ISBN별 핵심 키워드 추출 (650/653 주제어 추천 보조)
"""

from __future__ import annotations

import logging
import os

import requests

from kormarc_auto.api._http import cached_get
from kormarc_auto.constants import DATA4LIBRARY_KEYWORDS_URL, HTTP_TIMEOUT

logger = logging.getLogger(__name__)

KEYWORD_API_URL = DATA4LIBRARY_KEYWORDS_URL
DEFAULT_TIMEOUT = HTTP_TIMEOUT
SOURCE_NAME = "data4library"


class Data4LibraryError(Exception):
    """도서관 정보나루 API 오류."""


def fetch_keywords(isbn13: str, *, auth_key: str | None = None) -> list[str]:
    """ISBN13의 대출 데이터 기반 핵심 키워드 추출.

    Args:
        isbn13: 13자리 ISBN
        auth_key: 인증키. 미지정 시 DATA4LIBRARY_AUTH_KEY 환경변수.

    Returns:
        키워드 리스트 (가중치 높은 순). 응답 없으면 빈 리스트.
    """
    key = auth_key or os.getenv("DATA4LIBRARY_AUTH_KEY")
    if not key:
        logger.debug("DATA4LIBRARY_AUTH_KEY 미설정 — 키워드 조회 건너뜀")
        return []

    params = {"authKey": key, "isbn13": isbn13, "format": "json"}

    try:
        response = cached_get(KEYWORD_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout:
        logger.warning("도정나 API 타임아웃: isbn=%s", isbn13)
        return []
    except requests.RequestException as e:
        logger.warning("도정나 API 요청 실패: isbn=%s, err=%s", isbn13, e)
        return []

    try:
        data = response.json()
    except ValueError:
        return []

    items = data.get("response", {}).get("items", [])
    keywords: list[str] = []
    for item in items:
        word = item.get("item", {}).get("word")
        if word:
            keywords.append(word.strip())

    return keywords
