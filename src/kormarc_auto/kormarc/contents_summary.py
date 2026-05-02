"""목차·요약 (Contents·Summary) — Part 74 정합.

KORMARC 505 (목차·서지적 권차) + 520 (요약) 자동.
알라딘·예스24·NLK 데이터 → 자동·없으면 = 비워둠 (사서 입력 가능).

사서 페인 (Part 74·E1):
- 505 목차 = 권당 3분 = 사서 수동
- 520 요약 = 권당 5분 = 사서 수동
- 검색·OPAC 추천에 직접 영향

해결: 외부 API 데이터 자동 + 사서 수정 가능.
"""
from __future__ import annotations

from typing import Any

from pymarc import Field, Record, Subfield


def add_contents_summary(book_data: dict[str, Any], record: Record) -> Record:
    """목차·요약 자동 추가.

    Args:
        book_data:
            - contents·toc (목차 string)
            - description·summary·intro (요약 string)
        record: pymarc.Record

    Returns:
        record (in-place)
    """
    # 505 목차
    if contents := (book_data.get("contents") or book_data.get("toc")):
        # 목차 = 줄바꿈 → ' -- ' 변환 (KORMARC 표준)
        formatted = " -- ".join(line.strip() for line in contents.split("\n") if line.strip())
        if formatted:
            record.add_field(
                Field(
                    tag="505",
                    indicators=["0", " "],
                    subfields=[Subfield(code="a", value=formatted)],
                )
            )

    # 520 요약·해제
    if summary := (book_data.get("description") or book_data.get("summary") or book_data.get("intro")):
        summary_clean = summary.strip()
        if len(summary_clean) > 1000:
            summary_clean = summary_clean[:997] + "..."
        record.add_field(
            Field(
                tag="520",
                indicators=[" ", " "],
                subfields=[Subfield(code="a", value=summary_clean)],
            )
        )

    return record


__all__ = ["add_contents_summary"]
