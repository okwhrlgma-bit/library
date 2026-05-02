"""부가기호 디코더 테스트 (Part 87 / ADR 0021)."""

from __future__ import annotations

import pytest

from kormarc_auto.classification.budgaeho_decoder import (
    KDC_MAIN,
    PUBLICATION_FORM,
    TARGET_AUDIENCE,
    decode_budgaeho,
    extract_kdc_from_budgaeho,
)


def test_decode_budgaeho_typical_literature():
    """`03810` = 교양·단행본·문학·한국문학."""
    result = decode_budgaeho("03810")
    assert result is not None
    assert result.target_audience == "교양"
    assert result.publication_form == "단행본"
    assert result.kdc_2digit == "81"
    assert result.kdc_main.startswith("8 (문학")
    assert result.confidence == 1.0


def test_decode_budgaeho_children():
    """`73810` = 아동·단행본·문학·한국문학."""
    result = decode_budgaeho("73810")
    assert result is not None
    assert result.target_audience == "아동 (만 14세 미만)"
    assert result.kdc_2digit == "81"


def test_decode_budgaeho_textbook():
    """`53400` = 학습참고서·단행본·자연과학."""
    result = decode_budgaeho("53400")
    assert result is not None
    assert result.target_audience == "학습참고서 (중·고)"
    assert result.kdc_main.startswith("4 (자연과학")


def test_decode_budgaeho_invalid_length():
    assert decode_budgaeho("0381") is None  # 4자리
    assert decode_budgaeho("038100") is None  # 6자리
    assert decode_budgaeho("") is None


def test_decode_budgaeho_invalid_chars():
    assert decode_budgaeho("0381A") is None
    assert decode_budgaeho("ABCDE") is None


def test_decode_budgaeho_none_input():
    assert decode_budgaeho(None) is None  # type: ignore[arg-type]
    assert decode_budgaeho(12345) is None  # type: ignore[arg-type]


def test_extract_kdc_from_budgaeho_helper():
    assert extract_kdc_from_budgaeho("03810") == "81"
    assert extract_kdc_from_budgaeho("90090") == "09"
    assert extract_kdc_from_budgaeho("invalid") is None


def test_kdc_main_completeness():
    """KDC 0~9 모두 정의."""
    for digit in "0123456789":
        assert digit in KDC_MAIN


def test_target_audience_completeness():
    """독자대상 0~9 모두 정의."""
    for digit in "0123456789":
        assert digit in TARGET_AUDIENCE


def test_publication_form_completeness():
    """발행형태 0~9 모두 정의."""
    for digit in "0123456789":
        assert digit in PUBLICATION_FORM


def test_decoded_result_is_immutable():
    """frozen dataclass 검증."""
    result = decode_budgaeho("03810")
    assert result is not None
    with pytest.raises((AttributeError, TypeError)):
        result.target_audience = "변경"  # type: ignore[misc]


def test_part87_reference_example():
    """Part 87 §4.2 보고서 예제 정확성 검증."""
    result = decode_budgaeho("03810")
    assert result is not None
    # 보고서: "교양·단행본·문학·한국문학"
    assert "교양" in result.target_audience
    assert "단행본" in result.publication_form
    assert "문학" in result.kdc_main
