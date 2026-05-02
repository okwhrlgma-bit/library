"""Part 82+ 최종 모듈 테스트."""

from __future__ import annotations


def test_digitization_helper_basic():
    from kormarc_auto.intelligence.digitization_helper import (
        extract_metadata_from_text,
        merge_with_isbn_lookup,
    )

    # OCR 텍스트 (책 판권지 시뮬)
    text = """어린왕자
앙투안 드 생텍쥐페리 지음
김화영 옮김

열린책들 출판
2007년 1월 5일
ISBN 978-89-374-3707-6"""

    result = extract_metadata_from_text(text)
    assert result.isbn == "9788937437076"
    assert result.year == "2007"
    assert "열린책들" in result.publisher
    assert result.confidence > 0

    # ISBN API 통합
    api_data = {
        "isbn": "9788937437076",
        "title": "어린왕자",
        "author": "앙투안 드 생텍쥐페리",
        "publisher": "열린책들",
        "year": "2007",
        "sources": ["nlk"],
    }
    merged = merge_with_isbn_lookup(result, api_data)
    assert merged["title"] == "어린왕자"  # API 우선
    assert merged["isbn"] == "9788937437076"
    assert "ocr_confidence" in merged
