"""KORMARC 2023.12 M/A/O 적용 수준 검증 테스트."""

from __future__ import annotations

from kormarc_auto.kormarc.application_level import (
    M_FIELDS,
    determine_application_level,
    validate_application_level,
)


def test_m_fields_count_and_membership():
    assert "245" in M_FIELDS
    assert "008" in M_FIELDS
    assert "049" in M_FIELDS  # 자관 청구기호
    assert "880" not in M_FIELDS  # 한자 있을 때만 A


def test_determine_m_field_returns_M():
    assert determine_application_level("245", {}, "book_single") == "M"
    assert determine_application_level("008", {}, "thesis") == "M"


def test_022_is_A_for_serial_only():
    assert determine_application_level("022", {}, "serial_current") == "A"
    assert determine_application_level("022", {}, "book_single") == "O"


def test_502_is_A_for_thesis_only():
    assert determine_application_level("502", {}, "thesis") == "A"
    assert determine_application_level("502", {}, "book_single") == "O"


def test_880_triggered_by_hanja_in_title():
    book = {"title": "韓國史"}
    assert determine_application_level("880", book, "book_single") == "A"
    book_no_hanja = {"title": "한국사"}
    assert determine_application_level("880", book_no_hanja, "book_single") == "O"


def test_440_490_triggered_by_series():
    book = {"series_title": "민음 세계문학전집"}
    assert determine_application_level("440", book, "book_single") == "A"
    assert determine_application_level("490", book, "book_single") == "A"


def test_336_337_338_always_A():
    """RDA 매체·내용·전달 유형은 KORMARC 2023.12에서 항상 적용."""
    for tag in ("336", "337", "338"):
        assert determine_application_level(tag, {}, "book_single") == "A"


def test_validate_missing_M_fields():
    present = {"245", "260"}
    issues = validate_application_level(present, {}, "book_single")
    missing_tags = {tag for tag, level, _ in issues if level == "M"}
    assert "008" in missing_tags
    assert "020" in missing_tags
    assert "049" in missing_tags


def test_validate_thesis_missing_502_is_A_violation():
    present = M_FIELDS  # 모든 M 통과
    issues = validate_application_level(present, {}, "thesis")
    a_violations = [tag for tag, level, _ in issues if level == "A"]
    assert "502" in a_violations


def test_validate_serial_missing_022_is_A_violation():
    present = M_FIELDS
    issues = validate_application_level(present, {}, "serial_current")
    a_violations = [tag for tag, level, _ in issues if level == "A"]
    assert "022" in a_violations


def test_validate_complete_book_passes():
    present = M_FIELDS | {"336", "337", "338"}  # 모든 M + RDA 3종
    issues = validate_application_level(present, {}, "book_single")
    assert issues == []
