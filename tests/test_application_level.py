"""KORMARC 2023.12 M/A/O 적용 수준 검증 테스트."""

from __future__ import annotations

from kormarc_auto.kormarc.application_level import (
    M_FIELD_GROUPS,
    M_FIELDS,
    determine_application_level,
    validate_application_level,
)


def test_m_fields_count_and_membership():
    assert "245" in M_FIELDS
    assert "008" in M_FIELDS
    assert "300" in M_FIELDS
    # 049/056/090는 OR 그룹 (자관 prefix 정책 차이)
    assert "049" not in M_FIELDS
    assert any("049" in g for g in M_FIELD_GROUPS)
    # 260/264는 OR 그룹 (옛 260 또는 RDA 264)
    assert "260" not in M_FIELDS
    assert any("264" in g for g in M_FIELD_GROUPS)
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


def test_440_490_triggered_by_series_or_group():
    """440 또는 490 둘 다 가능 (validate에서 OR 처리)."""
    book = {"series_title": "민음 세계문학전집"}
    assert determine_application_level("490", book, "book_single") == "A"
    assert determine_application_level("440", book, "book_single") == "A"


def test_validate_series_or_group_satisfied_by_440():
    """440만 있어도 490 누락은 OK (실 KOLAS .mrc 정합)."""
    present = M_FIELDS | {"260", "049", "007", "440"}
    issues = validate_application_level(
        present,
        {"series_title": "민음 세계문학전집"},
        "book_single",
    )
    a_violations = [tag for tag, level, _ in issues if level == "A"]
    assert "440/490" not in a_violations
    assert "440" not in a_violations


def test_validate_series_or_group_violated_when_both_missing():
    present = M_FIELDS | {"260", "049", "007"}
    issues = validate_application_level(
        present,
        {"series_title": "있는 시리즈"},
        "book_single",
    )
    a_or_violations = [tag for tag, level, _ in issues if level == "A" and "/" in tag]
    assert "440/490" in a_or_violations


def test_336_337_338_optional_korean_practice():
    """RDA 매체·내용·전달은 KORMARC 2023.12 권장이나 한국 KOLAS 실무
    미적용 다수 (자관 .mrc 174 = 0% 적용). default O."""
    for tag in ("336", "337", "338"):
        assert determine_application_level(tag, {}, "book_single") == "O"


def test_validate_missing_M_fields():
    present = {"245"}
    issues = validate_application_level(present, {}, "book_single")
    missing_tags = {tag for tag, level, _ in issues if level == "M"}
    assert "008" in missing_tags
    assert "020" in missing_tags
    # 049는 OR 그룹으로 보고 (049/056/090 중 1개 필요)
    assert any("049" in t for t in missing_tags)
    assert any("260" in t for t in missing_tags)


def test_validate_or_group_satisfied_by_either():
    """260만 있어도 264 누락은 OK. 049만 있어도 056·090 누락 OK."""
    present = M_FIELDS | {"260", "049", "007"}
    issues = validate_application_level(present, {}, "book_single")
    or_violations = [tag for tag, level, _ in issues if "/" in tag]
    assert or_violations == []


def test_validate_thesis_missing_502_is_A_violation():
    present = M_FIELDS | {"260", "049", "007"}
    issues = validate_application_level(present, {}, "thesis")
    a_violations = [tag for tag, level, _ in issues if level == "A"]
    assert "502" in a_violations


def test_validate_serial_missing_022_is_A_violation():
    present = M_FIELDS | {"260", "049", "007"}
    issues = validate_application_level(present, {}, "serial_current")
    a_violations = [tag for tag, level, _ in issues if level == "A"]
    assert "022" in a_violations


def test_validate_complete_book_passes():
    """KOLAS 실무 정합 — 008·245·300·020·005·260·049·007 = 모든 M+OR
    정합."""
    present = M_FIELDS | {"260", "049", "007"}
    issues = validate_application_level(present, {}, "book_single")
    assert issues == []
