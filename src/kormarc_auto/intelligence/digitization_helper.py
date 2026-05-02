"""디지털화·OCR 보조 — Part 82+ 페인 #36 정합.

사서 페인:
- 종이 자료 디지털화 = AI-OCR 부담
- 메타데이터 추출 = 수동 시간

해결: 책 표지·판권지 OCR → 자동 메타데이터 추출.
T2 AI/ML + Anthropic Vision 통합 기반.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class OcrExtraction:
    """OCR 추출 결과."""

    raw_text: str
    isbn: str = ""
    title: str = ""
    author: str = ""
    publisher: str = ""
    year: str = ""
    confidence: float = 0.0  # 0.0~1.0


def extract_metadata_from_text(raw_text: str) -> OcrExtraction:
    """OCR 텍스트 → 메타데이터 자동 추출 (Phase 1·정규식 기반).

    Phase 2 = Anthropic Vision API 통합 (T2).

    Args:
        raw_text: OCR 결과 (Anthropic Vision·Tesseract·외부 OCR)

    Returns:
        OcrExtraction (필드별 추출)
    """
    # ISBN-13 추출
    isbn_match = re.search(r"\b(978|979)[- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d\b", raw_text)
    isbn = re.sub(r"[-\s]", "", isbn_match.group()) if isbn_match else ""

    # 출판년도 (1900~2099) — '년' 한글 경계 허용
    year_match = re.search(r"(19\d{2}|20\d{2})(?=\D|$)", raw_text)
    year = year_match.group(1) if year_match else ""

    # 출판사 (한글 단어 직전·"출판" 키워드)
    pub_match = re.search(
        r"([가-힣A-Za-z]{2,20})\s*(?:출판|출판사|발행|펴낸곳)",
        raw_text
    )
    publisher = pub_match.group(1).strip() if pub_match else ""

    # 저자 (한글 이름 + 지음·저·옮김 패턴)
    author_match = re.search(r"([가-힣]{2,15}(?:\s*[가-힣]{2,10})?)\s*(?:지음|저|옮김|역|글)", raw_text)
    author = author_match.group(1).strip() if author_match else ""

    # 신뢰도 (필드 추출 갯수 기반)
    extracted = sum(1 for v in [isbn, year, publisher, author] if v)
    confidence = extracted / 4 if extracted else 0

    return OcrExtraction(
        raw_text=raw_text,
        isbn=isbn,
        title="",  # 제목 추출 = AI Vision Phase 2
        author=author,
        publisher=publisher,
        year=year,
        confidence=confidence,
    )


def merge_with_isbn_lookup(
    ocr_result: OcrExtraction,
    isbn_metadata: dict,
) -> dict:
    """OCR + ISBN API 통합 (정확도 최대화).

    OCR ISBN 추출 후 = aggregate_by_isbn 호출 = 정확 메타데이터 보강.

    Args:
        ocr_result: OcrExtraction
        isbn_metadata: aggregate_by_isbn 결과

    Returns:
        통합 dict (ISBN API 우선·OCR 보조)
    """
    return {
        "isbn": ocr_result.isbn or isbn_metadata.get("isbn", ""),
        "title": isbn_metadata.get("title", ""),
        "author": isbn_metadata.get("author") or ocr_result.author,
        "publisher": isbn_metadata.get("publisher") or ocr_result.publisher,
        "year": isbn_metadata.get("year") or ocr_result.year,
        "ocr_confidence": ocr_result.confidence,
        "isbn_api_sources": isbn_metadata.get("sources", []),
    }


__all__ = ["OcrExtraction", "extract_metadata_from_text", "merge_with_isbn_lookup"]
