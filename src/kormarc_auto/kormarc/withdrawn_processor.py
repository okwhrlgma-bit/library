"""제적·withdrawn 처리 — Part 70 갭 9 정합.

사서 페인 (Part 70):
- 분실·파손·제적 처리 = 사서 수동
- 008 변경·853 제적 일자·자관 history 보존 X

해결: 008·583 자동·history 누적.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from pymarc import Field, Subfield

WithdrawalReason = Literal[
    "lost",          # 분실
    "damaged",       # 파손
    "duplicate",     # 중복
    "outdated",      # 노후
    "donated_out",   # 외부 기증
    "policy",        # 정책 폐기
]


@dataclass(frozen=True)
class WithdrawalRecord:
    """제적 1건 (자관 history)."""

    isbn: str
    registration_no: str
    reason: WithdrawalReason
    withdrawn_date: date
    librarian_name: str = ""
    notes: str = ""


def add_withdrawal_fields(
    record_data: dict,
    *,
    reason: WithdrawalReason,
    withdrawn_date: date,
) -> list[Field]:
    """제적 KORMARC 필드 자동 추가 (583·005 갱신).

    Args:
        record_data: 기존 KORMARC 데이터
        reason: 제적 사유
        withdrawn_date: 제적 일자

    Returns:
        list[Field] (583·005 갱신)
    """
    reason_kr = {
        "lost": "분실",
        "damaged": "파손",
        "duplicate": "중복 폐기",
        "outdated": "노후 폐기",
        "donated_out": "외부 기증",
        "policy": "정책 폐기",
    }

    # 583 처리 정보 (액션 노트)
    note = (
        f"제적 ({reason_kr[reason]}) — {withdrawn_date.year}년 "
        f"{withdrawn_date.month}월 {withdrawn_date.day}일"
    )
    f583 = Field(
        tag="583",
        indicators=[" ", " "],
        subfields=[
            Subfield(code="a", value="withdrawn"),
            Subfield(code="c", value=withdrawn_date.isoformat()),
            Subfield(code="z", value=note),
        ],
    )

    return [f583]


def is_withdrawn(record_data: dict) -> bool:
    """제적 여부 확인 (583 필드 검색)."""
    for field in record_data.get("data_fields", []):
        if field.get("tag") == "583":
            for sub in field.get("subfields", []):
                if sub.get("code") == "a" and "withdrawn" in (sub.get("value") or ""):
                    return True
    return False


__all__ = ["WithdrawalReason", "WithdrawalRecord", "add_withdrawal_fields", "is_withdrawn"]
