"""사서교사 전용 대시보드 — Part 81 페인 #25 정합 (P2 강화).

사서교사 페인:
- 13.9% 정규직만·88% 비정규직·자원봉사
- 자료 관리 + 교과 협력 + 프로젝트 학습 + 행정 = 모든 업무
- 일반 교사 행정 7.23h/주 + 도서관 = 더 부담

해결: 사서교사 일과 통합 대시보드 (P2 + P15 순회 정합).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchoolLibrarianTask:
    """사서교사 업무 1건."""

    name: str
    category: str  # "cataloging·collaboration·program·admin·etc"
    estimated_minutes: int
    is_automatable: bool = False  # kormarc-auto 자동화 가능?
    priority: int = 3  # 1~5


# 사서교사 표준 일과 (KCI 학술 + 교육부 4차 계획 정합)
STANDARD_TASKS = [
    SchoolLibrarianTask(
        name="신간 등록·KORMARC",
        category="cataloging",
        estimated_minutes=120,
        is_automatable=True,
        priority=4,
    ),
    SchoolLibrarianTask(
        name="학생 자료 검색·추천",
        category="collaboration",
        estimated_minutes=60,
        is_automatable=False,
        priority=4,
    ),
    SchoolLibrarianTask(
        name="교과 협력 수업 지원",
        category="collaboration",
        estimated_minutes=180,
        is_automatable=False,
        priority=5,
    ),
    SchoolLibrarianTask(
        name="독서 프로그램 운영",
        category="program",
        estimated_minutes=120,
        is_automatable=False,
        priority=4,
    ),
    SchoolLibrarianTask(
        name="자원봉사 학부모 관리",
        category="admin",
        estimated_minutes=60,
        is_automatable=False,
        priority=3,
    ),
    SchoolLibrarianTask(
        name="DLS 입력·관리",
        category="cataloging",
        estimated_minutes=90,
        is_automatable=True,
        priority=4,
    ),
    SchoolLibrarianTask(
        name="장서점검·배가",
        category="admin",
        estimated_minutes=120,
        is_automatable=True,
        priority=3,
    ),
    SchoolLibrarianTask(
        name="학교 행정·결재",
        category="admin",
        estimated_minutes=180,
        is_automatable=False,
        priority=3,
    ),
    SchoolLibrarianTask(
        name="학교운영위 보고",
        category="admin",
        estimated_minutes=60,
        is_automatable=True,
        priority=3,
    ),
    SchoolLibrarianTask(
        name="시도교육청 통계 보고",
        category="admin",
        estimated_minutes=120,
        is_automatable=True,
        priority=3,
    ),
]


def calculate_weekly_savings(tasks: list[SchoolLibrarianTask] | None = None) -> dict:
    """사서교사 주간 시간 절감 계산.

    Returns:
        dict(total·automatable·saved·non_automatable)
    """
    if tasks is None:
        tasks = STANDARD_TASKS

    total_min = sum(t.estimated_minutes for t in tasks)
    automatable_min = sum(t.estimated_minutes for t in tasks if t.is_automatable)
    # 자동화율 80% (일부 사서 검토 필요)
    saved_min = int(automatable_min * 0.8)

    return {
        "total_minutes_per_week": total_min,
        "total_hours_per_week": round(total_min / 60, 1),
        "automatable_minutes": automatable_min,
        "saved_minutes": saved_min,
        "saved_hours": round(saved_min / 60, 1),
        "remaining_focus_hours": round((total_min - saved_min) / 60, 1),
        "automation_ratio": round(saved_min / max(total_min, 1), 2),
    }


def render_school_librarian_dashboard(librarian_name: str = "사서교사 선생님") -> None:
    """Streamlit 사서교사 대시보드."""
    try:
        import streamlit as st
    except ImportError:
        return

    savings = calculate_weekly_savings()

    st.markdown(f"### 👨‍🏫 {librarian_name} 대시보드")
    st.caption("사서교사 일과 통합 (Part 81·페인 #25 정합)")

    col1, col2, col3 = st.columns(3)
    col1.metric("주간 업무 시간", f"{savings['total_hours_per_week']}h")
    col2.metric("자동화 절감", f"{savings['saved_hours']}h", f"+{savings['saved_minutes']}분")
    col3.metric("전문 일에 집중", f"{savings['remaining_focus_hours']}h")

    st.progress(
        savings["automation_ratio"], text=f"자동화 {int(savings['automation_ratio'] * 100)}%"
    )

    st.info(
        "**사서교사 = 자료 관리 + 교과 협력 + 프로젝트 + 행정 = 다 함**\n\n"
        "kormarc-auto = KORMARC·DLS·통계·행정 자동 = 교과 협력·수업 지원에 집중 가능."
    )


def categorize_tasks() -> dict:
    """업무 카테고리별 그룹화."""
    by_cat: dict[str, list[SchoolLibrarianTask]] = {}
    for t in STANDARD_TASKS:
        by_cat.setdefault(t.category, []).append(t)
    return by_cat


__all__ = [
    "STANDARD_TASKS",
    "SchoolLibrarianTask",
    "calculate_weekly_savings",
    "categorize_tasks",
    "render_school_librarian_dashboard",
]
