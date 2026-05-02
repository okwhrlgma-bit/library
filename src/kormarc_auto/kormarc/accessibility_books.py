"""장애인 도서 5 자료유형 — Part 71 정합.

사서 페인 (Part 71):
- 점자·큰글자·촉감·DAISY·수화 영상 = KORMARC 명시 X
- 장애인 도서관 (KNLB·30관·800+ 자료실) 진입 X
- 장애인차별금지법·도서관법 정합 의무

해결: 5 builder 통합 = 장애인 도서 KORMARC 자동.
KOLAS·KLMS·책나래 호환.
"""

from __future__ import annotations

from typing import Any, Literal

from pymarc import Field, Subfield

AccessibilityType = Literal[
    "braille",  # 점자
    "large_print",  # 큰 글자
    "tactile",  # 촉감 자료
    "daisy",  # DAISY 녹음 도서
    "sign_language",  # 수화 영상
]


def build_accessibility_fields(
    book_data: dict[str, Any],
    *,
    accessibility_type: AccessibilityType,
) -> list[Field]:
    """장애인 도서 KORMARC 필드 자동.

    Args:
        book_data: ISBN·제목·저자 등 기본 + 자료유형별 추가
        accessibility_type: 5 종 중 1

    Returns:
        list[Field] (245 ▾h·300·538·546 등)
    """
    fields: list[Field] = []

    if accessibility_type == "braille":
        # 점자 도서
        fields.append(_field_300(book_data, "점자 ○권"))
        fields.append(_field_538("점자 자료"))
        fields.append(_field_546("점자 (한글 점자)"))
        fields.append(_field_521("이용 대상자: 시각장애인"))

    elif accessibility_type == "large_print":
        # 큰 글자 도서 (대활자)
        fields.append(_field_250("대활자판"))
        fields.append(_field_538("Large print"))
        fields.append(_field_521("이용 대상자: 노인·시각장애인"))

    elif accessibility_type == "tactile":
        # 촉감 도서 (입체)
        format_str = book_data.get("tactile_format", "촉감·입체 자료")
        fields.append(_field_300(book_data, format_str))
        fields.append(_field_538("촉감·입체 자료"))
        fields.append(_field_521("이용 대상자: 시각장애 어린이·일반"))

    elif accessibility_type == "daisy":
        # DAISY 녹음 도서
        duration = book_data.get("duration", "")
        narrator = book_data.get("narrator", "")
        fields.append(_field_300(book_data, "CD ○매" + (f" · {duration}" if duration else "")))
        fields.append(_field_538("DAISY 형식 (DAISY 2.02·3.0)"))
        if narrator:
            fields.append(_field_511(narrator))
        if duration:
            fields.append(_field_306(duration))
        fields.append(_field_521("이용 대상자: 시각장애인·청각장애·노인"))

    elif accessibility_type == "sign_language":
        # 수화 영상
        runtime = book_data.get("runtime", "")
        fields.append(_field_300(book_data, "DVD ○매" + (f" · {runtime}" if runtime else "")))
        fields.append(_field_538("수화 통역 영상"))
        fields.append(_field_546("한국 수어 (KSL)·자막 포함"))
        fields.append(_field_521("이용 대상자: 청각장애인·일반"))

    return fields


def _field_245_h(media_str: str) -> Field:
    """245 ▾h 자료유형 표시 (별도 함수로 호출)."""
    return Field(
        tag="245",
        indicators=["1", "0"],
        subfields=[Subfield(code="h", value=f"[{media_str}]")],
    )


def _field_250(edition: str) -> Field:
    return Field(
        tag="250",
        indicators=[" ", " "],
        subfields=[Subfield(code="a", value=edition)],
    )


def _field_300(book_data: dict[str, Any], extent: str) -> Field:
    return Field(
        tag="300",
        indicators=[" ", " "],
        subfields=[Subfield(code="a", value=extent)],
    )


def _field_306(duration: str) -> Field:
    return Field(
        tag="306",
        indicators=[" ", " "],
        subfields=[Subfield(code="a", value=duration)],
    )


def _field_511(narrator: str) -> Field:
    return Field(
        tag="511",
        indicators=["0", " "],
        subfields=[Subfield(code="a", value=f"낭독: {narrator}")],
    )


def _field_521(audience: str) -> Field:
    return Field(
        tag="521",
        indicators=[" ", " "],
        subfields=[Subfield(code="a", value=audience)],
    )


def _field_538(spec: str) -> Field:
    return Field(
        tag="538",
        indicators=[" ", " "],
        subfields=[Subfield(code="a", value=spec)],
    )


def _field_546(language: str) -> Field:
    return Field(
        tag="546",
        indicators=[" ", " "],
        subfields=[Subfield(code="a", value=language)],
    )


__all__ = ["AccessibilityType", "build_accessibility_fields"]
