"""연속간행물 KORMARC 처리 — NL Korea 「연속간행물용기술규칙」 기반.

연속간행물 = 잡지·학술지·신문·연간보고서.

핵심 필드:
- 022 ISSN
- 245 ▾n 권차/권호 + ▾p 분권표제
- 260/264 발행
- 310 발행빈도 (월간·계간·연간)
- 321 이전 발행빈도
- 362 권차표시
- 780/785 변천 (이전·이후 표제)

발행상태 (008 06):
- c 현행 연속간행물
- d 종간 연속간행물
"""

from __future__ import annotations

from pymarc import Field, Indicators, Record, Subfield

FREQUENCY_KEYWORDS = {
    "일간": "Daily",
    "주간": "Weekly",
    "격주간": "Biweekly",
    "월간": "Monthly",
    "격월간": "Bimonthly",
    "계간": "Quarterly",
    "반년간": "Semiannual",
    "연간": "Annual",
    "비정기간": "Irregular",
}


def add_issn(record: Record, issn: str) -> None:
    """022 ▾a ISSN 추가."""
    if not issn:
        return
    digits = "".join(c for c in issn if c.isdigit() or c.upper() == "X")
    if len(digits) != 8:
        return
    formatted = f"{digits[:4]}-{digits[4:]}"
    record.add_field(
        Field(
            tag="022",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=formatted)],
        )
    )


def add_frequency(record: Record, frequency: str) -> None:
    """310 ▾a 발행빈도 (반복 가능)."""
    if not frequency:
        return
    record.add_field(
        Field(
            tag="310",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=frequency)],
        )
    )


def add_volume_designation(
    record: Record,
    *,
    start: str | None = None,
    end: str | None = None,
) -> None:
    """362 ▾a 권차표시 (예: '제1권 제1호 (2024년 1월)-')."""
    if not start and not end:
        return
    parts = []
    if start:
        parts.append(start)
    parts.append("-")
    if end:
        parts.append(end)
    value = "".join(parts)
    record.add_field(
        Field(
            tag="362",
            indicators=Indicators("0", " "),
            subfields=[Subfield(code="a", value=value)],
        )
    )


def add_title_history(
    record: Record,
    *,
    preceding_title: str | None = None,
    succeeding_title: str | None = None,
) -> None:
    """780/785 — 이전·이후 표제 (변천)."""
    if preceding_title:
        record.add_field(
            Field(
                tag="780",
                indicators=Indicators("0", "0"),
                subfields=[Subfield(code="t", value=preceding_title)],
            )
        )
    if succeeding_title:
        record.add_field(
            Field(
                tag="785",
                indicators=Indicators("0", "0"),
                subfields=[Subfield(code="t", value=succeeding_title)],
            )
        )


def detect_frequency_from_title(title: str) -> str | None:
    """표제에서 발행빈도 키워드 추출."""
    if not title:
        return None
    for kw in FREQUENCY_KEYWORDS:
        if kw in title:
            return kw
    return None
