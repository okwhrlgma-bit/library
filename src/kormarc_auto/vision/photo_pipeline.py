"""사진 → KORMARC 통합 흐름 (Phase 2).

전략 (비용 최적화):
1. 바코드 (pyzbar, 무료, 가장 빠름) → 성공 시 외부 API 보강
2. Vision Stage 1 (Haiku, 저렴) → 표지에서 ISBN-13 텍스트 추출
3. Vision Stage 2 (Sonnet) → ISBN조차 없을 때만 종합 메타데이터 추출
4. Vision 결과에 ISBN 있으면 외부 API로 보강 → confidence 0.85
   ISBN 없으면 Vision 결과만 → confidence 0.65 (사람 검토 필수)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from kormarc_auto.api.aggregator import aggregate_by_isbn
from kormarc_auto.constants import (
    CONFIDENCE_BARCODE,
    CONFIDENCE_VISION_ONLY,
    CONFIDENCE_VISION_WITH_API,
)
from kormarc_auto.vision.barcode import extract_isbn_from_image
from kormarc_auto.vision.claude_vision import (
    extract_isbn_via_vision,
    extract_metadata_from_photos,
)

logger = logging.getLogger(__name__)


def photo_to_book_data(image_paths: list[str | Path]) -> dict[str, Any]:
    """책 사진들 → 통합 BookData.

    Args:
        image_paths: 표지·판권지·목차 (순서 무관, 1~3장)

    Returns:
        BookData dict. 추가 키:
        - `vision_isbn`: 바코드/비전에서 추출한 ISBN
        - `vision_only`: True면 외부 API 보강 실패 (사람 검토 필수)
        - `extraction_method`: "barcode" / "vision_isbn" / "vision_full" / "none"
    """
    if not image_paths:
        return {
            "confidence": 0.0,
            "vision_only": True,
            "error": "이미지 입력 없음",
            "extraction_method": "none",
        }

    # 1. 바코드 우선 (무료·즉시)
    isbn: str | None = None
    for path in image_paths:
        isbn = extract_isbn_from_image(path)
        if isbn:
            logger.info("바코드 ISBN 추출 성공: %s", isbn)
            return _enrich_with_isbn(isbn, source="barcode")

    # 2. Vision Stage 1: ISBN 텍스트 추출 (Haiku, 저렴)
    isbn = extract_isbn_via_vision(image_paths)
    if isbn:
        logger.info("Vision Stage 1 ISBN 추출 성공: %s", isbn)
        return _enrich_with_isbn(isbn, source="vision_isbn")

    # 3. Vision Stage 2: 종합 메타데이터 (Sonnet, 비싸지만 마지막 수단)
    logger.info("ISBN 미발견 — Vision Stage 2 종합 추출 시도")
    vision_data = extract_metadata_from_photos(image_paths)

    # Stage 2가 ISBN을 추출했으면 외부 API 보강 시도
    vision_isbn = vision_data.get("isbn")
    if vision_isbn and len(str(vision_isbn)) == 13:
        logger.info("Vision Stage 2가 ISBN 회수: %s — 외부 API 보강", vision_isbn)
        enriched = _enrich_with_isbn(str(vision_isbn), source="vision_full")
        # Vision의 warnings는 보존
        if vision_data.get("warnings"):
            enriched.setdefault("warnings", []).extend(vision_data["warnings"])
        return enriched

    # 외부 API 보강 불가 — Vision 결과만 반환
    return {
        **vision_data,
        "vision_only": True,
        "extraction_method": "vision_full",
        "confidence": vision_data.get("confidence") or CONFIDENCE_VISION_ONLY,
    }


def _enrich_with_isbn(isbn: str, *, source: str) -> dict[str, Any]:
    """ISBN으로 외부 API 호출해 BookData 채움. 실패 시 ISBN만 반환.

    Args:
        isbn: 13자리 ISBN
        source: "barcode" / "vision_isbn" / "vision_full"

    Returns:
        BookData dict (sources·source_map·confidence·attributions 포함)
    """
    try:
        data = aggregate_by_isbn(isbn)
    except Exception as e:
        logger.warning("ISBN %s 외부 API 보강 실패: %s — Vision 결과만 사용", isbn, e)
        return {
            "isbn": isbn,
            "sources": [source],
            "source_map": {"isbn": source},
            "confidence": CONFIDENCE_VISION_ONLY if source != "barcode" else CONFIDENCE_BARCODE,
            "attributions": [],
            "vision_isbn": isbn,
            "vision_only": True,
            "extraction_method": source,
            "warnings": [f"외부 API 보강 실패: {e}"],
        }

    if not data.get("sources"):
        # 외부 API 모두 실패
        return {
            "isbn": isbn,
            "sources": [source],
            "source_map": {"isbn": source},
            "confidence": CONFIDENCE_VISION_ONLY,
            "attributions": [],
            "vision_isbn": isbn,
            "vision_only": True,
            "extraction_method": source,
        }

    data["vision_isbn"] = isbn
    data["vision_only"] = False
    data["extraction_method"] = source
    if source == "barcode":
        data["confidence"] = max(data.get("confidence", 0.0), CONFIDENCE_BARCODE)
    else:
        data["confidence"] = max(data.get("confidence", 0.0), CONFIDENCE_VISION_WITH_API)
    return data
