"""Claude Vision으로 책 표지/판권지/목차에서 메타데이터 추출.

2단계 비용 최적화:
1. Stage 1 (Haiku 4.5): 표지/판권지에서 ISBN-13만 추출 (저렴)
2. Stage 2 (Sonnet 4.6): ISBN 없으면 전체 메타데이터 추출 (정확)

ISBN이 추출되면 호출부(`photo_pipeline`)가 외부 API로 메타데이터를 보강하므로
Stage 2는 호출되지 않음 → 비용 90% 절감.
"""

from __future__ import annotations

import base64
import io
import logging
import os
from pathlib import Path
from typing import Any

from kormarc_auto._anthropic_client import (
    AnthropicClientError,
    cached_messages,
    make_image_cache_key,
)
from kormarc_auto.constants import (
    CONFIDENCE_VISION_ONLY,
    DEFAULT_LIGHT_MODEL,
    DEFAULT_VISION_MODEL,
    VISION_IMAGE_MAX_LONGEST_SIDE,
    VISION_PROMPT_VERSION,
)

logger = logging.getLogger(__name__)


_ISBN_TOOL = {
    "name": "report_isbn",
    "description": "이미지에서 발견한 ISBN-13을 보고한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "isbn13": {
                "type": ["string", "null"],
                "description": "13자리 숫자 ISBN. 발견 못 하면 null.",
            },
            "found_in": {
                "type": "string",
                "enum": ["barcode", "copyright_page", "back_cover", "front_cover", "none"],
                "description": "어디서 발견했는지",
            },
        },
        "required": ["isbn13", "found_in"],
    },
}


_METADATA_TOOL = {
    "name": "report_book_metadata",
    "description": "책 표지·판권지·목차 이미지에서 추출한 한국 도서 메타데이터를 보고한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "isbn": {"type": ["string", "null"], "description": "13자리 ISBN"},
            "title": {"type": ["string", "null"], "description": "본표제"},
            "subtitle": {"type": ["string", "null"], "description": "부표제"},
            "author": {
                "type": ["string", "null"],
                "description": "저자/역자 (여러 명은 ' ; '로 구분)",
            },
            "publisher": {"type": ["string", "null"]},
            "publication_year": {"type": ["string", "null"], "description": "YYYY"},
            "publication_place": {"type": ["string", "null"], "description": "발행지 (도시명)"},
            "price": {"type": ["integer", "null"], "description": "정가 정수, 단위 없이"},
            "additional_code": {"type": ["string", "null"], "description": "ISBN 부가기호 5자리"},
            "kdc": {"type": ["string", "null"], "description": "표지/판권지에 인쇄된 KDC"},
            "pages": {"type": ["string", "null"], "description": "총 페이지수"},
            "summary": {
                "type": ["string", "null"],
                "description": "표지/뒷표지 카피에서 추출한 요약",
            },
            "warnings": {
                "type": "array",
                "items": {"type": "string"},
                "description": "추출이 모호한 항목·이유",
            },
        },
        "required": ["isbn", "title", "warnings"],
    },
}


_ISBN_SYSTEM_PROMPT = """\
당신은 한국 도서의 표지·판권지·뒷표지 이미지에서 ISBN-13을 정확히 추출하는 전문가다.

규칙:
- ISBN-13은 978 또는 979로 시작하는 13자리 숫자
- 바코드 아래 인쇄된 숫자, 또는 판권지("ISBN" 표기 옆) 우선
- 하이픈은 제거하고 13자리 숫자만 보고
- 발견하지 못하면 isbn13=null

반드시 report_isbn 도구를 호출해 결과를 보고한다.
"""


_METADATA_SYSTEM_PROMPT = """\
당신은 한국 도서의 표지·판권지·뒷표지·목차 이미지에서 KORMARC 목록 작성에 필요한 메타데이터를 추출하는 전문가 사서다.

추출 우선순위:
1. 판권지 (출판사·발행연도·ISBN·정가·KDC가 가장 정확)
2. 표지 (표제·부표제·저자·출판사)
3. 뒷표지 (요약·바코드)

규칙:
- 본표제(title)와 부표제(subtitle) 명확히 구분
- 저자 여러 명: ' ; '로 구분 (예: "김영하 ; 한강")
- 역자가 있으면 author에 "원저자 / 역자명 옮김" 형태
- 발행연도는 YYYY 4자리만
- 가격은 단위 없이 정수만 (예: "₩13,000" → 13000)
- ISBN 부가기호 5자리는 별도 (additional_code)
- KDC가 인쇄돼 있으면 그대로, 없으면 null (추정 금지 — 별도 분류기가 처리)
- 모호하거나 자신 없는 항목은 null로 두고 warnings에 사유 명시

반드시 report_book_metadata 도구를 호출해 결과를 보고한다.
"""


def _load_image_bytes(path: str | Path) -> tuple[bytes, str]:
    """이미지 파일 → (bytes, media_type). longest_side ≤ 1568px로 리사이즈."""
    try:
        from PIL import Image
    except ImportError as e:
        raise AnthropicClientError("Pillow 미설치 — `pip install Pillow`로 설치하세요.") from e

    img = Image.open(str(path))
    img = img.convert("RGB") if img.mode not in ("RGB", "L") else img

    longest = max(img.size)
    if longest > VISION_IMAGE_MAX_LONGEST_SIDE:
        ratio = VISION_IMAGE_MAX_LONGEST_SIDE / longest
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue(), "image/jpeg"


def _build_image_blocks(image_paths: list[str | Path]) -> tuple[list[dict[str, Any]], list[bytes]]:
    """이미지 경로 → anthropic 메시지 content 블록 + 캐시 키용 raw bytes."""
    blocks: list[dict[str, Any]] = []
    raw_list: list[bytes] = []
    for path in image_paths:
        data, media_type = _load_image_bytes(path)
        raw_list.append(data)
        blocks.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64.standard_b64encode(data).decode("ascii"),
                },
            }
        )
    return blocks, raw_list


def extract_isbn_via_vision(
    image_paths: list[str | Path],
    *,
    model: str | None = None,
) -> str | None:
    """Stage 1: 표지·판권지에서 ISBN-13만 추출 (저렴, Haiku).

    Args:
        image_paths: 이미지 1~3장
        model: 기본 DEFAULT_LIGHT_MODEL

    Returns:
        13자리 ISBN 또는 None
    """
    if not image_paths:
        return None

    use_model = model or os.getenv("CLAUDE_LIGHT_MODEL") or DEFAULT_LIGHT_MODEL
    image_blocks, raw_list = _build_image_blocks(image_paths[:3])
    cache_key = make_image_cache_key(raw_list, f"isbn-{VISION_PROMPT_VERSION}", use_model)

    try:
        result = cached_messages(
            cache_key=cache_key,
            model=use_model,
            system=_ISBN_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        *image_blocks,
                        {"type": "text", "text": "이 이미지들에서 ISBN-13을 찾아 보고하세요."},
                    ],
                }
            ],
            tools=[_ISBN_TOOL],
            tool_name="report_isbn",
            max_tokens=256,
        )
    except AnthropicClientError as e:
        logger.warning("Vision ISBN 추출 실패: %s", e)
        return None

    tool_input = result.get("tool_input") or {}
    isbn = tool_input.get("isbn13")
    if isinstance(isbn, str):
        digits = "".join(c for c in isbn if c.isdigit())
        if len(digits) == 13 and (digits.startswith("978") or digits.startswith("979")):
            logger.info("Vision ISBN 추출 성공: %s (소스: %s)", digits, tool_input.get("found_in"))
            return digits
    return None


def extract_metadata_from_photos(
    image_paths: list[str | Path],
    *,
    model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Stage 2: 책 사진들로부터 종합 서지 메타데이터 추출 (Sonnet).

    호출자(`photo_pipeline`)가 ISBN 1차 추출에 실패한 경우에만 호출되어야 한다.

    Args:
        image_paths: 표지·판권지·목차 이미지 1~3장
        model: 기본 DEFAULT_VISION_MODEL (sonnet-4-6)
        api_key: 미사용 (환경변수 ANTHROPIC_API_KEY 우선) — 인터페이스 호환용

    Returns:
        BookData 호환 dict + sources/source_map/confidence/warnings
    """
    _ = api_key  # 인터페이스 호환 (실제는 환경변수 사용)
    if not image_paths:
        return {
            "sources": [],
            "source_map": {},
            "confidence": 0.0,
            "warnings": ["이미지 입력 없음"],
        }

    use_model = model or os.getenv("CLAUDE_VISION_MODEL") or DEFAULT_VISION_MODEL
    image_blocks, raw_list = _build_image_blocks(image_paths[:3])
    cache_key = make_image_cache_key(raw_list, f"meta-{VISION_PROMPT_VERSION}", use_model)

    try:
        result = cached_messages(
            cache_key=cache_key,
            model=use_model,
            system=_METADATA_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        *image_blocks,
                        {
                            "type": "text",
                            "text": "이 이미지들에서 한국 도서 메타데이터를 추출해 보고하세요.",
                        },
                    ],
                }
            ],
            tools=[_METADATA_TOOL],
            tool_name="report_book_metadata",
            max_tokens=1500,
        )
    except AnthropicClientError as e:
        logger.error("Vision 메타데이터 추출 실패: %s", e)
        return {
            "sources": [],
            "source_map": {},
            "confidence": 0.0,
            "warnings": [f"Vision 호출 실패: {e}"],
        }

    tool_input = result.get("tool_input") or {}
    extracted_keys = [
        k for k in tool_input if k != "warnings" and tool_input.get(k) not in (None, "", [])
    ]
    return {
        **{k: v for k, v in tool_input.items() if k != "warnings"},
        "sources": ["claude_vision"],
        "source_map": {k: "claude_vision" for k in extracted_keys},
        "confidence": CONFIDENCE_VISION_ONLY,
        "warnings": tool_input.get("warnings", []) or [],
    }
