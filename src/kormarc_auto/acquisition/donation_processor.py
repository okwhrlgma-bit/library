"""기증 도서 자동 처리 — Part 82 페인 #30 정합.

사서 페인:
- NLK 책다모아·자치구 기증 = 사서 별도 절차
- 기증 = 검수·등록·기증증서 자동 X = 사서 시간

해결: 기증 처리 흐름 자동·기증증서 자동 생성.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DonationItem:
    """기증 도서 1건."""

    isbn: str
    title: str
    donor_name: str
    donor_contact: str = ""
    donation_date: date = date.today()
    condition: str = "양호"  # "양호·보통·낮음·폐기 검토"
    accept_decision: str = "pending"  # "accepted·rejected·pending"
    rejection_reason: str = ""


def evaluate_donation(item: DonationItem, *, library_has_copy: bool = False) -> dict:
    """기증 검수 자동.

    공공도서관 장서관리 매뉴얼 정합.
    """
    accept = True
    reason = ""

    # 1. 조건 검수
    if item.condition in ("폐기 검토", "낮음"):
        accept = False
        reason = "도서 상태 불량"

    # 2. 복본 검사 (자관 이미 보유)
    if library_has_copy and item.condition != "양호":
        accept = False
        reason = "복본 보유 + 상태 불량"

    return {
        "decision": "accepted" if accept else "rejected",
        "reason": reason,
        "needs_librarian_review": item.condition == "보통",
    }


def generate_donation_certificate(item: DonationItem, library_name: str) -> str:
    """기증증서 자동 생성 (markdown)."""
    return f"""# 기증증서

## {library_name}

전 사서 [PO]

---

## 기증자 정보

| 항목 | 내용 |
|---|---|
| 기증자 | {item.donor_name} |
| 연락처 | {item.donor_contact or "(미기재)"} |
| 기증 일자 | {item.donation_date.year}년 {item.donation_date.month}월 {item.donation_date.day}일 |

## 기증 도서

| 항목 | 내용 |
|---|---|
| ISBN | {item.isbn} |
| 도서명 | {item.title} |
| 상태 | {item.condition} |

---

위 도서를 {library_name}에 기증해주신 점에 감사드리며, 본 증서를 발급합니다.

본 도서는 도서관 자료로 등록되어 모든 이용자에게 도움이 될 것입니다.

> kormarc-auto 자동 생성
"""


__all__ = ["DonationItem", "evaluate_donation", "generate_donation_certificate"]
