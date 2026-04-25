"""AI 없이 사진에서 ISBN·텍스트 추출 — EasyOCR 기반.

하이브리드 흐름:
1. 바코드 인식 (pyzbar) — 무료, 가장 빠름
2. OCR 텍스트 추출 (EasyOCR) — 무료, 한국어·숫자 인식
3. ISBN 패턴 검출 (정규식) — 13자리 978/979 시작
4. ISBN 발견 시 외부 API(NL/알라딘/카카오)로 메타 보강
5. 모든 게 실패해야만 AI Vision (KORMARC_DISABLE_AI=0일 때)

EasyOCR는 첫 호출 시 한국어·영어 모델 ~100MB 자동 다운로드.
이후엔 오프라인·무료로 동작.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ISBN-13 패턴: 978/979 + 10자리 숫자, 사이에 하이픈/공백 허용
_ISBN_PATTERNS = [
    re.compile(r"97[89][\s\-]?\d{1,5}[\s\-]?\d{1,7}[\s\-]?\d{1,7}[\s\-]?\d"),
    re.compile(r"97[89]\d{10}"),
]


@lru_cache(maxsize=1)
def get_reader() -> Any:
    """EasyOCR 리더 lazy-load (한국어 + 영어).

    첫 호출 시 모델 다운로드 (~100MB, 1회만).

    Returns:
        easyocr.Reader 또는 None (미설치 시)
    """
    try:
        import easyocr
    except ImportError:
        logger.warning("easyocr 미설치 — `pip install easyocr` 또는 `pip install -e .[ocr]`")
        return None

    logger.info("EasyOCR 모델 로드 중 (첫 호출 시 ~100MB 다운로드)")
    return easyocr.Reader(["ko", "en"], gpu=False, verbose=False)


def extract_text_from_image(image_path: str | Path) -> list[str]:
    """이미지에서 텍스트 라인 추출 (AI 없이).

    Args:
        image_path: 이미지 파일 경로

    Returns:
        인식된 텍스트 라인 리스트 (신뢰도 0.5 이상만, 신뢰도 내림차순)
    """
    reader = get_reader()
    if reader is None:
        return []

    try:
        results = reader.readtext(str(image_path), detail=1)
    except Exception as e:
        logger.warning("OCR 실패: %s — %s", image_path, e)
        return []

    # results: list of (bbox, text, confidence)
    lines = [
        (text, conf)
        for _bbox, text, conf in results
        if conf >= 0.5 and text.strip()
    ]
    lines.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in lines]


def extract_isbn_from_image_ocr(image_path: str | Path) -> str | None:
    """이미지에서 OCR로 ISBN-13 추출 (AI 없이).

    바코드 인식이 실패한 경우 사용. 판권지·뒷표지의 인쇄된 ISBN 텍스트 인식.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        13자리 ISBN 또는 None
    """
    lines = extract_text_from_image(image_path)
    if not lines:
        return None

    # 모든 텍스트를 합쳐 정규식 검색 (줄 단위 + 전체 단위)
    full_text = " ".join(lines)
    for line in [*lines, full_text]:
        for pattern in _ISBN_PATTERNS:
            for match in pattern.findall(line):
                digits = "".join(c for c in match if c.isdigit())
                if (
                    len(digits) == 13
                    and (digits.startswith("978") or digits.startswith("979"))
                    and _is_valid_isbn13_checksum(digits)
                ):
                    logger.info("OCR ISBN 추출 성공: %s (소스: %s)", digits, image_path)
                    return digits
    return None


def _is_valid_isbn13_checksum(isbn: str) -> bool:
    """ISBN-13 체크섬 검증 — 잘못 인식된 OCR 결과 거름."""
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(isbn[:12]))
    check = (10 - (total % 10)) % 10
    return check == int(isbn[12])


def extract_metadata_hints_from_ocr(image_paths: list[str | Path]) -> dict[str, Any]:
    """OCR 텍스트에서 표제·저자·출판사 등 힌트 추출 (휴리스틱).

    AI 없이 키워드 매칭 기반. 정확도 낮음 — 사서 검토 필수.

    Returns:
        {
            "isbn": str | None,
            "title_candidates": list[str],
            "publisher_candidates": list[str],
            "raw_lines": list[str],
            "confidence": float,
        }
    """
    all_lines: list[str] = []
    isbn: str | None = None

    for path in image_paths:
        lines = extract_text_from_image(path)
        all_lines.extend(lines)
        if isbn is None:
            isbn = extract_isbn_from_image_ocr(path)

    # 출판사 후보: 끝에 "출판사·사·문고·BOOKS" 등 포함 라인
    publisher_keywords = ("출판사", "출판", "books", "press", "문고", "사", "주식회사")
    publisher_candidates = [
        line for line in all_lines if any(kw in line.lower() for kw in publisher_keywords)
    ][:5]

    # 표제 후보: 가장 긴 한글 라인 + 신뢰도 상위 3개
    title_candidates = sorted(
        [line for line in all_lines if any(0xAC00 <= ord(c) <= 0xD7A3 for c in line)],
        key=len,
        reverse=True,
    )[:3]

    confidence = 0.5 if isbn else 0.3

    return {
        "isbn": isbn,
        "title_candidates": title_candidates,
        "publisher_candidates": publisher_candidates,
        "raw_lines": all_lines[:30],
        "confidence": confidence,
    }
