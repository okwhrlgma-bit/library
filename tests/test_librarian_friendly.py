"""librarian_friendly 사서 깊이 친화 테스트 (Part 49)."""

from __future__ import annotations

from datetime import datetime

from kormarc_auto.ui.librarian_friendly import (
    AUTHORITATIVE_SOURCES,
    HONORIFIC,
    addr_librarian,
    cite_authority,
    get_librarian_context,
)


def test_honorific_is_seonsaengnim() -> None:
    """한국 도서관 표준 호칭 = '선생님' (PO 필수 명령)."""
    assert HONORIFIC == "선생님"


def test_addr_librarian_with_name() -> None:
    """이름 + 선생님."""
    assert addr_librarian("김지수") == "김지수 선생님"


def test_addr_librarian_anonymous() -> None:
    """이름 없으면 '선생님'만."""
    assert addr_librarian(None) == "선생님"
    assert addr_librarian("") == "선생님"
    assert addr_librarian("   ") == "선생님"


def test_authoritative_sources_include_kormarc() -> None:
    """KORMARC·KCR4·KDC·도서관법 권위 인용."""
    keys = AUTHORITATIVE_SOURCES.keys()
    assert "kormarc_standard" in keys
    assert "kdc" in keys
    assert "kcr" in keys
    assert "library_law" in keys
    assert "school_library_law" in keys


def test_cite_authority_returns_markdown_link() -> None:
    """인용 = Markdown 링크 형식."""
    cite = cite_authority("kormarc_standard")
    assert cite.startswith("[")
    assert "](" in cite
    assert "국립중앙도서관" in cite


def test_cite_authority_for_unknown_returns_empty() -> None:
    """알 수 없는 키 = 빈 문자열."""
    assert cite_authority("nonexistent") == ""


def test_get_librarian_context_spring_rush() -> None:
    """3·4월 = 신학기 신간 폭주 시즌."""
    march = datetime(2026, 3, 15, 9, 0)
    ctx = get_librarian_context(now=march)
    assert ctx.season == "new_book_rush_spring"


def test_get_librarian_context_fall_rush() -> None:
    """9월 = 가을 신학기 시즌."""
    sept = datetime(2026, 9, 5, 10, 0)
    ctx = get_librarian_context(now=sept)
    assert ctx.season == "new_book_rush_fall"


def test_get_librarian_context_budget_planning() -> None:
    """11~12월 = 자료구입비 예산 시즌."""
    nov = datetime(2026, 11, 10, 14, 0)
    ctx = get_librarian_context(now=nov)
    assert ctx.season == "budget_planning"


def test_get_librarian_context_summer() -> None:
    """7~8월 = 여름 휴관·정비."""
    jul = datetime(2026, 7, 20, 14, 0)
    ctx = get_librarian_context(now=jul)
    assert ctx.season == "summer"


def test_library_week_detection() -> None:
    """도서관주간 (4/12~18) 자동 인식."""
    library_week_day = datetime(2026, 4, 14, 10, 0)
    ctx = get_librarian_context(now=library_week_day)
    assert ctx.is_library_week is True


def test_library_day_detection() -> None:
    """도서관의 날 (9/14) 자동 인식."""
    library_day = datetime(2026, 9, 14, 10, 0)
    ctx = get_librarian_context(now=library_day)
    assert ctx.is_library_day is True


def test_time_of_day_pre_open() -> None:
    """개관 전 시간대 (08:00 미만)."""
    pre_open = datetime(2026, 5, 2, 7, 30)
    ctx = get_librarian_context(now=pre_open)
    assert ctx.time_of_day == "pre_open"


def test_time_of_day_lunch() -> None:
    """점심시간 (12~13)."""
    lunch = datetime(2026, 5, 2, 12, 30)
    ctx = get_librarian_context(now=lunch)
    assert ctx.time_of_day == "lunch"


def test_suggested_action_not_empty() -> None:
    """모든 컨텍스트 = 추천 액션 제공."""
    ctx = get_librarian_context()
    assert ctx.suggested_action
    assert len(ctx.suggested_action) > 5
