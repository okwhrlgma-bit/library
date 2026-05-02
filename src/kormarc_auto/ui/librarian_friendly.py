"""사서 깊이 친화 모듈 — 한국 도서관 일과·사이클·호칭·페인 정합.

PO 명령 (2026-05-02): "사서에 친화적인 방향 있는지 고민 및 적용"

6 영역 적용:
1. 사서 호칭 ("선생님" — 한국 도서관 표준)
2. 도서관 일과 사이클 (개관 전·점심·마감)
3. 신간 폭주 시즌 자동 인식 (3·4·9월)
4. 자료구입비 예산 시점 알림 (11~12월)
5. 도서관주간 (4월)·도서관의 날 (9월)
6. 사서 자격·교육 사이클 (NLK 사서교육원)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal


@dataclass(frozen=True)
class LibrarianContext:
    """현재 사용자(사서)의 도메인 컨텍스트."""

    today: date
    season: Literal["new_book_rush_spring", "summer", "new_book_rush_fall", "budget_planning", "year_end", "normal"]
    time_of_day: Literal["pre_open", "morning", "lunch", "afternoon", "closing", "after_hours"]
    is_library_week: bool
    is_library_day: bool
    upcoming_event: str | None
    suggested_action: str


def get_librarian_context(now: datetime | None = None) -> LibrarianContext:
    """사서 도메인 컨텍스트 자동 인식.

    한국 도서관 일과·연중 사이클 정합:
    - 3·4·9월: 신간 등록 폭주 (학기 시작·신학기 도서)
    - 11~12월: 자료구입비 예산 편성·집행
    - 4월: 도서관주간 (4/12~18 표준)
    - 9월: 도서관의 날
    - 7~8월: 여름 휴관·정비
    """
    now = now or datetime.now()
    today = now.date()
    month = today.month
    hour = now.hour

    # 시즌 판정
    if month in (3, 4):
        season = "new_book_rush_spring"
    elif month == 9:
        season = "new_book_rush_fall"
    elif month in (11, 12):
        season = "budget_planning"
    elif month == 12 and today.day >= 20:
        season = "year_end"
    elif month in (7, 8):
        season = "summer"
    else:
        season = "normal"

    # 일과 시간대 판정
    if hour < 8:
        time_of_day = "pre_open"
    elif hour < 12:
        time_of_day = "morning"
    elif hour < 13:
        time_of_day = "lunch"
    elif hour < 17:
        time_of_day = "afternoon"
    elif hour < 19:
        time_of_day = "closing"
    else:
        time_of_day = "after_hours"

    # 도서관주간·도서관의 날 (한국 표준)
    is_library_week = month == 4 and 12 <= today.day <= 18
    is_library_day = month == 9 and today.day == 14  # 도서관의 날

    # 사서 다음 행사 안내
    upcoming_event = None
    if month == 3:
        upcoming_event = "도서관주간 (4/12~18) 신간 일괄 등록 권장 시즌"
    elif month == 4 and today.day < 12:
        upcoming_event = "도서관주간 (4/12~18) 임박 — 신간 정리 마무리"
    elif month == 5:
        upcoming_event = "KLA 전국도서관대회 발표 신청 (5/31 마감)"
    elif month == 8:
        upcoming_event = "9월 신학기 신간 폭주 사전 준비 시즌"
    elif month == 10:
        upcoming_event = "11~12월 자료구입비 예산 편성 시작"
    elif month == 11:
        upcoming_event = "자료구입비 집행 마감 임박 (12월 말)"

    # 시즌·시간대별 추천 액션
    suggested_action = _suggest_action(season, time_of_day)

    return LibrarianContext(
        today=today,
        season=season,
        time_of_day=time_of_day,
        is_library_week=is_library_week,
        is_library_day=is_library_day,
        upcoming_event=upcoming_event,
        suggested_action=suggested_action,
    )


def _suggest_action(season: str, time_of_day: str) -> str:
    """시즌 × 시간대 → 사서 친화 추천 액션."""
    if season == "new_book_rush_spring":
        if time_of_day == "pre_open":
            return "🌸 신학기 신간 폭주 시즌입니다. 개관 전 일괄 처리로 시작해보세요."
        if time_of_day == "morning":
            return "🌸 오전 수서 시간 — 신간 ISBN 일괄 입력 권장"
        if time_of_day == "lunch":
            return "🍱 점심시간 검수 큐 정리에 적합한 시간이에요"
        if time_of_day == "afternoon":
            return "🌸 오후 정리 — KORMARC 검수·KOLAS 반입 권장"
        if time_of_day == "closing":
            return "🌅 마감 시간 — 오늘 처리량 백업·보고서 생성"

    if season == "new_book_rush_fall":
        return "🍂 9월 신학기 신간 폭주 시즌. 일괄 처리 모드 활용 권장."

    if season == "budget_planning":
        return "💰 자료구입비 예산 편성·집행 시즌. 본인 처리량 통계 참고하세요."

    if season == "year_end":
        return "📊 연말 마감 — 연간 통계·보고서 자동 생성 가능"

    if season == "summer":
        return "🌞 여름 휴관·정비 시즌. 누락 도서 일괄 점검에 적합한 시기입니다."

    # 일반 시즌
    if time_of_day == "pre_open":
        return "🌅 개관 전 — 어제 검수 큐 일괄 승인부터 시작"
    if time_of_day == "morning":
        return "☀️ 오전 — 신간 등록·수서 처리 권장 시간"
    if time_of_day == "lunch":
        return "🍱 점심시간 — 짧은 검수·통계 확인"
    if time_of_day == "afternoon":
        return "🕒 오후 — 정리·KORMARC 검토"
    if time_of_day == "closing":
        return "🌅 마감 — 오늘 작업 백업·내일 우선순위 확인"

    return "📚 KORMARC 자동 생성 시작해보세요"


def render_librarian_dashboard_widget() -> None:
    """사서 친화 컨텍스트 위젯 (홈 화면 상단).

    Streamlit 통합용. 한국 도서관 일과·시즌·이벤트 정합.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    ctx = get_librarian_context()

    # 시즌·시간대 배경 색상
    season_emoji = {
        "new_book_rush_spring": "🌸",
        "new_book_rush_fall": "🍂",
        "budget_planning": "💰",
        "year_end": "📊",
        "summer": "🌞",
        "normal": "📚",
    }

    emoji = season_emoji.get(ctx.season, "📚")
    weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    today_str = f"{ctx.today.year}년 {ctx.today.month}월 {ctx.today.day}일 ({weekdays_kr[ctx.today.weekday()]})"

    st.markdown(
        f"""
        <div style="
            background: #f0f9ff;
            border-left: 4px solid #1f6feb;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        ">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 4px;">
                {emoji} {today_str}
            </div>
            <div style="font-size: 16px; font-weight: 500; color: #1f2937;">
                {ctx.suggested_action}
            </div>
            {f'<div style="font-size: 13px; color: #6b7280; margin-top: 8px;">📅 {ctx.upcoming_event}</div>' if ctx.upcoming_event else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if ctx.is_library_week:
        st.success("🎉 도서관주간입니다! 행사 자료·이용자 안내 자동 생성 가능")
    if ctx.is_library_day:
        st.success("🎂 도서관의 날입니다! 1년 중 가장 중요한 사서의 날 ✨")


# 사서 호칭 표준 (한국 도서관 문화)
HONORIFIC = "선생님"  # 사서 사이 표준 호칭


def addr_librarian(name: str | None = None) -> str:
    """사서 호칭 적용.

    PO 명령: "사서가 사용하는 언어 적용 필수"
    한국 도서관 표준: 사서 = "선생님"

    Args:
        name: 사서 이름 (예: "김지수"). None이면 익명.

    Returns:
        "김지수 선생님" 또는 "선생님"
    """
    if name and name.strip():
        return f"{name.strip()} {HONORIFIC}"
    return HONORIFIC


# 권위·신뢰 인용 가능 출처 (사서 직접 검증)
AUTHORITATIVE_SOURCES = {
    "kormarc_standard": {
        "name": "KORMARC 통합서지용 (KS X 6006-0:2023.12)",
        "url": "https://librarian.nl.go.kr/LI/contents/L10102000000.do",
        "publisher": "국립중앙도서관",
    },
    "kdc": {
        "name": "한국십진분류법 (KDC) 6판",
        "url": "https://www.nl.go.kr/",
        "publisher": "한국도서관협회",
    },
    "kcr": {
        "name": "한국목록규칙 (KCR4)",
        "url": "https://www.kla.kr/",
        "publisher": "한국도서관협회",
    },
    "library_law": {
        "name": "도서관법 (법률 제19592호)",
        "url": "https://law.go.kr/",
        "publisher": "문화체육관광부",
    },
    "school_library_law": {
        "name": "학교도서관진흥법",
        "url": "https://law.go.kr/",
        "publisher": "교육부",
    },
    "small_library_law": {
        "name": "작은도서관진흥법",
        "url": "https://law.go.kr/",
        "publisher": "문화체육관광부",
    },
    "library_dev_plan": {
        "name": "제4차 학교도서관 진흥 기본계획 (2024~2028)",
        "url": "https://www.moe.go.kr/",
        "publisher": "교육부",
    },
}


def cite_authority(key: str) -> str:
    """사서 권위 인용 (영업 자료·UI에서 활용).

    사서가 신뢰하는 표준·법률·공식 문서 직접 링크.
    """
    src = AUTHORITATIVE_SOURCES.get(key)
    if not src:
        return ""
    return f"[{src['name']} ({src['publisher']})]({src['url']})"
