"""이용자 알림 템플릿 단위 테스트."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.librarian_helpers import notifications  # noqa: E402


def test_overdue_notice_basic():
    msg = notifications.overdue_notice(
        user_name="홍길동",
        book_title="작별하지 않는다",
        due_date="2026-04-01",
        overdue_days=24,
        library_name="테스트도서관",
    )
    assert "홍길동" in msg["sms"]
    assert "작별하지 않는다" in msg["sms"]
    assert "24일" in msg["sms"]
    assert "테스트도서관" in msg["sms"]
    assert msg["overdue_days"] == 24
    assert msg["fine_krw"] == 0


def test_overdue_notice_with_fine():
    msg = notifications.overdue_notice(
        user_name="홍길동",
        book_title="작별하지 않는다",
        due_date="2026-04-01",
        overdue_days=10,
        fine_per_day=100,
    )
    assert msg["fine_krw"] == 1000
    assert "1,000원" in msg["lms"]


def test_return_reminder():
    msg = notifications.return_reminder(
        user_name="이순신",
        book_title="조선왕조실록",
        due_date="2026-05-01",
        days_before=3,
    )
    assert "이순신" in msg["sms"]
    assert "조선왕조실록" in msg["sms"]


def test_reservation_ready():
    msg = notifications.reservation_ready(
        user_name="김유신",
        book_title="삼국유사",
        pickup_deadline="2026-04-30",
    )
    assert "김유신" in msg["sms"]
    assert "예약" in msg["lms"]


def test_closure_notice():
    msg = notifications.closure_notice(
        library_name="테스트도서관",
        closure_dates=["2026-05-05", "2026-05-06"],
        reason="어린이날 + 대체공휴일",
    )
    assert "휴관" in msg["sms"]
    assert "어린이날" in msg["lms"]


def test_calculate_overdue_days():
    assert notifications.calculate_overdue_days(date(2026, 4, 1), today=date(2026, 4, 25)) == 24
    # 만기 전: 0
    assert notifications.calculate_overdue_days(date(2026, 5, 1), today=date(2026, 4, 25)) == 0
    # 문자열 입력
    assert notifications.calculate_overdue_days("2026-04-01", today=date(2026, 4, 10)) == 9


def test_calculate_fine():
    assert notifications.calculate_fine(0) == 0
    assert notifications.calculate_fine(10, fine_per_day=100) == 1000
    # 상한
    assert notifications.calculate_fine(100, fine_per_day=100, cap_krw=5000) == 5000


def test_korean_date_format():
    """SMS·LMS의 날짜는 'N년 N월 N일' 형식."""
    msg = notifications.return_reminder(
        user_name="홍길동",
        book_title="테스트",
        due_date="2026-05-15",
    )
    assert "2026년 5월 15일" in msg["lms"]
