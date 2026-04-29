"""KORMARC 전자저널 (ejournal) 빌더 — Phase 1.5.

KORMARC 2023.12 6번째 자료유형 (전자저널):
- LDR 06=a (어문)
- LDR 07=s (연속간행물)
- 008 06=c (현행) 또는 d (폐간)
- 008 18-21 발행빈도 (m=월간·w=주간·q=계간·a=연간)
- 008 23=o (온라인)
- 022 ▾a ISSN (필수)
- 310 ▾a 발행빈도 명시
- 362 ▾a 권차 (예: "Vol.1 No.1 (2026.01)~")
- 856 ▾u URL
"""

from __future__ import annotations

from typing import Any

from pymarc import Field, Indicators, Subfield

FREQUENCY_CODES: dict[str, str] = {
    "monthly": "m",
    "weekly": "w",
    "quarterly": "q",
    "annual": "a",
    "biweekly": "b",
    "daily": "d",
}


def build_ejournal_fields(journal_data: dict[str, Any]) -> list[Field]:
    """전자저널 특화 필드 (022·310·362·856) → Field 리스트.

    Args:
        journal_data: 통합 dict (`issn`·`title`·`url`·`frequency`·`first_issue`)

    Returns:
        022·310·362·856 필드 리스트.
    """
    fields: list[Field] = []

    # 022 — ISSN (필수)
    if issn := journal_data.get("issn"):
        fields.append(
            Field(
                tag="022",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=issn)],
            )
        )

    # 310 — 발행빈도
    if freq := journal_data.get("frequency"):
        fields.append(
            Field(
                tag="310",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=freq)],
            )
        )

    # 362 — 권차 (간행 정보)
    if first := journal_data.get("first_issue"):
        fields.append(
            Field(
                tag="362",
                indicators=Indicators("0", " "),  # 정식 표기
                subfields=[Subfield(code="a", value=f"{first}~")],
            )
        )

    # 856 — URL
    if url := journal_data.get("url"):
        fields.append(
            Field(
                tag="856",
                indicators=Indicators("4", "0"),
                subfields=[Subfield(code="u", value=url)],
            )
        )

    return fields


def derive_008_18_21(frequency: str) -> str:
    """008 18-21 발행빈도 부호 (4자리·앞 1글자만 사용)."""
    code = FREQUENCY_CODES.get(frequency, " ")
    return code + "   "  # 4자리 채움


__all__ = ["FREQUENCY_CODES", "build_ejournal_fields", "derive_008_18_21"]
