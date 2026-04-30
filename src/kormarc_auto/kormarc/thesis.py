"""KORMARC 학위논문 (thesis) 빌더 — Phase 1.5.

KORMARC 2023.12 9번째 자료유형 (학위논문):
- LDR 06=a (어문)
- LDR 07=m (단행본 단위)
- 008 06=s (단일발행)
- 008 24-27 내용형식 (m=학위논문 포함)
- 502 ▾a 학위논문 명시
       ▾b 학위 종류 (석사·박사)
       ▾c 수여 기관 (서울대학교)
       ▾d 학과·전공
       ▾g 수여연도
- 504 ▾a 참고문헌 주기
- 700 ▾a 지도교수 ▾e 지도
- 856 ▾u dCollection·RISS·KCI URL

대학·연구도서관 PILOT 핵심 (RISS 18,000개 학위논문 양식 정합).
"""

from __future__ import annotations

from typing import Any

from pymarc import Field, Indicators, Subfield


def build_thesis_fields(thesis_data: dict[str, Any]) -> list[Field]:
    """학위논문 특화 필드 (502·504·700·856) → Field 리스트.

    Args:
        thesis_data: 통합 dict
            (`degree`·`institution`·`department`·`year`·`advisor`·`url`·`bibliography`)

    Returns:
        502·504·700·856 필드 리스트.
    """
    fields: list[Field] = []

    # 502 — 학위논문 주기
    sub502 = [Subfield(code="a", value="학위논문")]
    if degree := thesis_data.get("degree"):
        sub502.append(Subfield(code="b", value=degree))
    if institution := thesis_data.get("institution"):
        sub502.append(Subfield(code="c", value=institution))
    if department := thesis_data.get("department"):
        sub502.append(Subfield(code="d", value=department))
    if year := thesis_data.get("year"):
        sub502.append(Subfield(code="g", value=str(year)))
    fields.append(
        Field(
            tag="502",
            indicators=Indicators(" ", " "),
            subfields=sub502,
        )
    )

    # 504 — 참고문헌·서지 주기
    if biblio := thesis_data.get("bibliography"):
        fields.append(
            Field(
                tag="504",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=biblio)],
            )
        )

    # 700 — 지도교수 (보조저록 — 인명)
    if advisor := thesis_data.get("advisor"):
        fields.append(
            Field(
                tag="700",
                indicators=Indicators("1", " "),  # 1=성-이름 도치
                subfields=[
                    Subfield(code="a", value=advisor),
                    Subfield(code="e", value="지도"),
                ],
            )
        )

    # 856 — dCollection·RISS·KCI URL
    if url := thesis_data.get("url"):
        fields.append(
            Field(
                tag="856",
                indicators=Indicators("4", "0"),
                subfields=[Subfield(code="u", value=url)],
            )
        )

    return fields


def format_502_text(thesis_data: dict[str, Any]) -> str:
    """502 ▾a 단일 텍스트 포맷 (한국 대학 관례).

    예: "학위논문(석사)--서울대학교 교육학과, 2026"
    """
    degree = thesis_data.get("degree", "")
    institution = thesis_data.get("institution", "")
    department = thesis_data.get("department", "")
    year = thesis_data.get("year", "")

    parts = []
    if degree:
        parts.append(f"학위논문({degree})")
    else:
        parts.append("학위논문")
    tail_parts = []
    if institution:
        head = institution
        if department:
            head = f"{head} {department}"
        tail_parts.append(head)
    if year:
        tail_parts.append(str(year))
    tail = ", ".join(tail_parts)
    return f"{parts[0]}--{tail}" if tail else parts[0]


__all__ = [
    "build_thesis_fields",
    "format_502_text",
]
