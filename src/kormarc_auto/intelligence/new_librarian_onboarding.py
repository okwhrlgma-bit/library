"""신입 사서 적응 가이드 시스템 — Part 82 페인 #27 정합.

사서 페인 (Part 82):
- 신입 = 수습 = 숙련 사서 50% 생산성 (한국생산성본부)
- 매뉴얼 부재 = 부서마다 다른 교육 = 품질 편차
- P14 야간·P15 순회·P4 1년 계약직 = 인수인계 X = 시행착오

해결: 7단 적응 가이드 자동 + Mem0 자관 KB 통합.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OnboardingStep:
    """적응 단계 1건."""

    day_offset: int  # Day 1~30
    title: str
    description: str
    estimated_minutes: int
    is_critical: bool = False  # 필수 단계 (skip X)


# 사서 신입 표준 7단 적응 (Day 1~30)
DEFAULT_STEPS = [
    OnboardingStep(1, "자관 정보 학습 (KB 자동)", "자관 prefix·청구기호·정책 = Mem0 자동 검색", 30, True),
    OnboardingStep(1, "kormarc-auto 5분 가이드", "ISBN 입력·KORMARC 자동·KOLAS export", 5, True),
    OnboardingStep(2, "선임 사서 인수인계 매뉴얼", "handover_manual.py 자동 생성·읽기", 60, True),
    OnboardingStep(3, "이용자 응대 매뉴얼", "NLK 표준 + AI Agent 1차 응대 학습", 60, True),
    OnboardingStep(7, "첫 50건 처리", "kormarc-auto = 권당 1분·시간 측정", 50, False),
    OnboardingStep(14, "감정노동 보호 학습", "서울시 7대 지침 + incident_logger", 30, True),
    OnboardingStep(30, "1개월 평가·피드백", "personal_stats_dashboard·승진 자료", 60, False),
]


@dataclass
class OnboardingPlan:
    """신입 사서 적응 계획."""

    librarian_name: str
    sasagwan: str
    start_date: date
    steps: list[OnboardingStep]

    def get_today_steps(self, current_date: date) -> list[OnboardingStep]:
        """오늘 해야 할 단계 (Day = day_offset과 일치)."""
        days_since_start = (current_date - self.start_date).days + 1  # Day 1부터 시작
        return [s for s in self.steps if s.day_offset == days_since_start]

    def get_remaining_steps(self, current_date: date) -> list[OnboardingStep]:
        """남은 단계."""
        days_since_start = (current_date - self.start_date).days
        return [s for s in self.steps if s.day_offset > days_since_start]

    def progress_percentage(self, current_date: date) -> int:
        """진행률 (0~100)."""
        days_since_start = (current_date - self.start_date).days
        completed = sum(1 for s in self.steps if s.day_offset <= days_since_start)
        return int(completed / max(len(self.steps), 1) * 100)


def create_default_plan(librarian_name: str, sasagwan: str, start_date: date | None = None) -> OnboardingPlan:
    """표준 적응 계획 생성 (7단 30일)."""
    return OnboardingPlan(
        librarian_name=librarian_name,
        sasagwan=sasagwan,
        start_date=start_date or date.today(),
        steps=list(DEFAULT_STEPS),
    )


def estimate_productivity(days_since_start: int) -> float:
    """신입 생산성 곡선 (수습 0.5 → 1주 0.7 → 1개월 0.9 → 3개월 1.0).

    한국생산성본부 데이터 기반·우리 도구 가속 가정.
    기본 신입 = 50% / 우리 도구 사용 신입 = 70% (즉시·KB 활용).
    """
    if days_since_start < 7:
        return 0.7  # 우리 도구 = 즉시 70% (기본 50%·KB·매뉴얼)
    elif days_since_start < 30:
        return 0.85
    elif days_since_start < 90:
        return 0.95
    else:
        return 1.0


__all__ = [
    "DEFAULT_STEPS",
    "OnboardingPlan",
    "OnboardingStep",
    "create_default_plan",
    "estimate_productivity",
]
