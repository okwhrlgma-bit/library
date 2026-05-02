"""validate_record_full — KORMARC + M/A/O 통합 검증 테스트."""

from __future__ import annotations

from pymarc import Field, Indicators, Record, Subfield

from kormarc_auto.kormarc.validator import validate_record_full


def _minimal_record(extras: list[Field] | None = None) -> Record:
    """008 + 245만 갖는 최소 record."""
    record = Record()
    record.add_field(Field(tag="008", data="250129s2024    ulk           kor".ljust(40)))
    record.add_field(
        Field(
            tag="245",
            indicators=Indicators("1", "0"),
            subfields=[Subfield(code="a", value="테스트 표제")],
        )
    )
    for f in extras or []:
        record.add_field(f)
    return record


def test_minimal_record_flags_m_field_violations():
    issues = validate_record_full(_minimal_record(), {}, "book_single")
    flat = " ".join(issues)
    assert "[M] 005" in flat
    assert "[M] 020" in flat
    assert "[M] 300" in flat
    assert "260/264" in flat  # OR 그룹
    assert "049/056/090" in flat


def test_complete_book_record_passes():
    extras = [
        Field(tag="005", data="20260129000000.0"),
        Field(tag="007", data="ta"),
        Field(
            tag="020",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="9788912345678")],
        ),
        Field(
            tag="260",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="b", value="민음사")],
        ),
        Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="320 p.")],
        ),
        Field(
            tag="049",
            indicators=Indicators("0", " "),
            subfields=[Subfield(code="l", value="EQ12345")],
        ),
    ]
    issues = validate_record_full(_minimal_record(extras), {}, "book_single")
    m_issues = [i for i in issues if "[M]" in i]
    assert m_issues == []


def test_thesis_missing_502_flagged():
    extras = [
        Field(tag="005", data="20260129000000.0"),
        Field(tag="007", data="ta"),
        Field(
            tag="020",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="9788912345678")],
        ),
        Field(
            tag="260",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="b", value="서울대")],
        ),
        Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="100 p.")],
        ),
        Field(
            tag="049",
            indicators=Indicators("0", " "),
            subfields=[Subfield(code="l", value="EQ99999")],
        ),
    ]
    issues = validate_record_full(_minimal_record(extras), {}, "thesis")
    assert any("[A] 502" in i for i in issues)


def test_book_with_hanja_missing_880_flagged():
    extras = [
        Field(tag="005", data="20260129000000.0"),
        Field(tag="007", data="ta"),
        Field(
            tag="020",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="9788912345678")],
        ),
        Field(
            tag="260",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="b", value="민음사")],
        ),
        Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="320 p.")],
        ),
        Field(
            tag="049",
            indicators=Indicators("0", " "),
            subfields=[Subfield(code="l", value="EQ12345")],
        ),
    ]
    book = {"title": "韓國史 통론"}
    issues = validate_record_full(_minimal_record(extras), book, "book_single")
    assert any("[A] 880" in i for i in issues)
