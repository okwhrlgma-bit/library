"""이용자 알림 메시지 템플릿 — 연체·반납·예약·도서관 휴관.

KOLAS의 알림 기능을 사서 PC가 아닌 곳에서도 쓸 수 있게 텍스트 생성.
실제 발송(SMS/email)은 사서가 자기 시스템(KOLAS·문자 게이트웨이)으로 보냄.

PO 자료 「내숲 도서관 운영 매뉴얼」의 이용자 안내 흐름 매칭.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

# 메시지 길이 제약 — SMS는 80바이트(한글 40자) / LMS는 2,000바이트
SMS_MAX_KOREAN = 40
LMS_MAX_KOREAN = 1000


def _korean_date(d: date | datetime | str) -> str:
    """'2026-04-25' → '2026년 4월 25일'."""
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    return f"{d.year}년 {d.month}월 {d.day}일"


def overdue_notice(
    *,
    user_name: str,
    book_title: str,
    due_date: date | datetime | str,
    overdue_days: int,
    library_name: str = "○○도서관",
    fine_per_day: int = 0,
    contact: str = "",
) -> dict[str, Any]:
    """연체 알림 — SMS·LMS·email 본문 동시 생성.

    Returns:
        {"sms": str, "lms": str, "email_subject": str, "email_body": str}
    """
    due_str = _korean_date(due_date)
    fine = overdue_days * fine_per_day if fine_per_day else 0

    sms = (
        f"[{library_name}] {user_name}님, 「{book_title[:20]}」 "
        f"{overdue_days}일 연체. 반납 부탁드립니다."
    )

    lms_lines = [
        f"[{library_name}] 도서 연체 안내",
        "",
        f"{user_name}님, 안녕하세요.",
        "",
        f"대출 도서 「{book_title}」가 {overdue_days}일 연체되었습니다.",
        f"  · 반납 예정일: {due_str}",
        f"  · 연체 일수: {overdue_days}일",
    ]
    if fine:
        lms_lines.append(f"  · 연체료: {fine:,}원")
    lms_lines += [
        "",
        "빠른 시일 내 반납해 주시기 바랍니다.",
    ]
    if contact:
        lms_lines.append(f"문의: {contact}")
    lms = "\n".join(lms_lines)

    email_subject = f"[{library_name}] 도서 연체 안내 — {book_title}"
    email_body = lms + "\n\n감사합니다."

    return {
        "sms": sms[:SMS_MAX_KOREAN * 2],  # 안전 마진
        "lms": lms[:LMS_MAX_KOREAN * 2],
        "email_subject": email_subject,
        "email_body": email_body,
        "overdue_days": overdue_days,
        "fine_krw": fine,
    }


def return_reminder(
    *,
    user_name: str,
    book_title: str,
    due_date: date | datetime | str,
    library_name: str = "○○도서관",
    days_before: int = 3,
) -> dict[str, str]:
    """반납 예정 사전 알림 (보통 만기 3일 전)."""
    due_str = _korean_date(due_date)
    sms = (
        f"[{library_name}] {user_name}님, 「{book_title[:20]}」 "
        f"반납일 {due_str} ({days_before}일 후) — 안내드립니다."
    )
    lms = (
        f"[{library_name}] 도서 반납 안내\n\n"
        f"{user_name}님,\n\n"
        f"대출하신 「{book_title}」의 반납일이 다가오고 있습니다.\n"
        f"  · 반납 예정일: {due_str}\n"
        f"  · 남은 기간: {days_before}일\n\n"
        "기한 내 반납 또는 연장(가능 시) 부탁드립니다.\n\n감사합니다."
    )
    return {
        "sms": sms[:SMS_MAX_KOREAN * 2],
        "lms": lms,
        "email_subject": f"[{library_name}] 도서 반납 안내 — {book_title}",
        "email_body": lms,
    }


def reservation_ready(
    *,
    user_name: str,
    book_title: str,
    pickup_deadline: date | datetime | str,
    library_name: str = "○○도서관",
    pickup_location: str = "1층 안내데스크",
) -> dict[str, str]:
    """예약 도서 도착 알림."""
    deadline_str = _korean_date(pickup_deadline)
    sms = (
        f"[{library_name}] {user_name}님, 예약하신 「{book_title[:18]}」 "
        f"도착. {deadline_str}까지 수령."
    )
    lms = (
        f"[{library_name}] 예약 도서 도착 안내\n\n"
        f"{user_name}님이 예약하신 도서가 도착했습니다.\n\n"
        f"  · 도서명: {book_title}\n"
        f"  · 수령 장소: {pickup_location}\n"
        f"  · 수령 기한: {deadline_str}\n\n"
        "기한 내 수령하지 않으시면 다음 예약자에게 양도됩니다.\n\n감사합니다."
    )
    return {
        "sms": sms[:SMS_MAX_KOREAN * 2],
        "lms": lms,
        "email_subject": f"[{library_name}] 예약 도서 도착 — {book_title}",
        "email_body": lms,
    }


def closure_notice(
    *,
    library_name: str,
    closure_dates: list[date | str],
    reason: str = "정기 휴관일",
    contact: str = "",
) -> dict[str, str]:
    """휴관 안내 (정기 휴관·시설 점검·국경일)."""
    dates_str = ", ".join(_korean_date(d) for d in closure_dates)
    sms = f"[{library_name}] 휴관 안내: {dates_str} ({reason})"
    lms = (
        f"[{library_name}] 휴관 안내\n\n"
        f"이용자 여러분께 안내드립니다.\n\n"
        f"  · 휴관일: {dates_str}\n"
        f"  · 사유: {reason}\n\n"
        "이용에 참고 부탁드립니다."
    )
    if contact:
        lms += f"\n\n문의: {contact}"
    return {
        "sms": sms[:SMS_MAX_KOREAN * 2],
        "lms": lms,
        "email_subject": f"[{library_name}] 휴관 안내",
        "email_body": lms,
    }


def calculate_overdue_days(due_date: date | datetime | str, today: date | None = None) -> int:
    """연체 일수 계산 (대출일이 아닌 반납 예정일 기준). 0 이상."""
    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    if isinstance(due_date, datetime):
        due_date = due_date.date()
    today = today or date.today()
    delta = today - due_date
    return max(0, delta.days)


def calculate_fine(overdue_days: int, fine_per_day: int = 100, cap_krw: int | None = None) -> int:
    """연체료 계산 — 일일 100원 기본, 상한 적용 가능."""
    if overdue_days <= 0:
        return 0
    fine = overdue_days * fine_per_day
    if cap_krw is not None:
        fine = min(fine, cap_krw)
    return fine


__all__ = [
    "calculate_fine",
    "calculate_overdue_days",
    "closure_notice",
    "overdue_notice",
    "reservation_ready",
    "return_reminder",
]
