"""한자 ↔ 한글 변환 (hanja 라이브러리 래퍼)."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

HANJA_PATTERN = re.compile(r"[一-鿿]")


def has_hanja(text: str | None) -> bool:
    """문자열에 한자(CJK Unified Ideographs)가 포함되어 있는가."""
    if not text:
        return False
    return bool(HANJA_PATTERN.search(text))


def hanja_to_hangul(text: str) -> str:
    """한자를 한글 발음으로 변환.

    예: "韓國의 歷史" → "한국의 역사"
    예외/모호한 경우는 원본 유지.
    """
    if not text:
        return text
    try:
        import hanja
    except ImportError:
        logger.warning("hanja 라이브러리 미설치. `pip install hanja` 후 재시도.")
        return text

    return hanja.translate(text, "substitution")
