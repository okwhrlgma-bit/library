"""주제명 표목 (Subject Heading) — Part 74 정합.

KORMARC 6XX 필드 (650 일반·651 지명·600 인명·610 단체) 자동.
NLK 주제명 thesaurus + AI 추천 → 6XX.

사서 페인 (Part 74·E1):
- 6XX 주제명 = 검색·OPAC 핵심
- 사서 = 수동 입력 = 권당 3분
- KDC만으로는 부족 (이용자 검색 = 키워드)

해결: AI 추천 + NLK thesaurus = 자동.
"""
from __future__ import annotations

from typing import Any

from pymarc import Field, Record, Subfield


def add_subject_headings(
    book_data: dict[str, Any],
    record: Record,
    *,
    max_subjects: int = 5,
) -> Record:
    """주제명 표목 자동 추가 (650·651·600 분기).

    Args:
        book_data: subject_keywords (list[str]) + KDC + AI 추천
        record: pymarc.Record
        max_subjects: 권당 최대 주제명 (기본 5건)

    Returns:
        record (in-place 수정)
    """
    keywords = book_data.get("subject_keywords") or []
    if not keywords:
        # AI 추천에서 fallback
        keywords = book_data.get("ai_subjects") or []

    for kw in keywords[:max_subjects]:
        term = kw if isinstance(kw, str) else kw.get("term", "")
        if not term:
            continue

        # 인명·지명·일반 분기
        tag = _classify_subject(term)
        record.add_field(
            Field(
                tag=tag,
                indicators=[" ", "0"],  # 0 = LCSH·NLK 정합
                subfields=[Subfield(code="a", value=term)],
            )
        )

    return record


def _classify_subject(term: str) -> str:
    """주제명 분류 → 6XX 태그 결정.

    - 인명 = 600
    - 지명 = 651
    - 단체 = 610
    - 일반 = 650
    """
    # 단순 휴리스틱 (Phase 1)
    if any(suffix in term for suffix in ["전기", "회고록", "평전"]):
        return "600"
    if any(region in term for region in ["국", "도", "시", "군", "구", "해", "산"]):
        if len(term) <= 4:  # 짧은 지명
            return "651"
    if "협회" in term or "회사" in term or "재단" in term:
        return "610"
    return "650"  # default 일반


__all__ = ["add_subject_headings"]
