"""작은도서관 자원봉사 onboarding — 페르소나 02 100점 (작은도서관 관장).

배경:
- 학교도서관 86% 자원봉사 (사서교사 13.9% 배치)
- 작은도서관 6,830관 = 1인 사서·자원봉사 의존
- 자원봉사 = KORMARC 지식 0~약함 → 사서 검수 부담 ↑

해결:
1. 자원봉사 등급 5단계 (E0 신규 → E4 숙련)
2. 등급별 권한 제한 (E0 = 입력만·E4 = 검수까지)
3. 5분 튜토리얼 + 첫 5권 멘토링
4. 자동 검수 hook (사서 검토 필요 항목 자동 표시)

사서 결정권 보존: 자원봉사 입력 = 항상 사서 최종 승인 필요.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

VolunteerLevel = Literal["E0", "E1", "E2", "E3", "E4"]


# 자원봉사 등급별 정의
VOLUNTEER_LEVELS: dict[VolunteerLevel, dict] = {
    "E0": {
        "name": "신규 (Day 1)",
        "permissions": ["read_only", "scan_isbn"],
        "completion_required": "5분 튜토리얼 + 첫 5권 사서 동석",
        "can_save_record": False,
    },
    "E1": {
        "name": "초급 (5권 완료)",
        "permissions": ["read_only", "scan_isbn", "input_basic"],
        "completion_required": "기본 입력 (제목·저자·ISBN) 5권 정확",
        "can_save_record": True,  # 사서 승인 필수
    },
    "E2": {
        "name": "중급 (50권 완료)",
        "permissions": ["read_only", "scan_isbn", "input_basic", "input_full"],
        "completion_required": "전체 필드 입력 50권·사서 검수 통과 90%+",
        "can_save_record": True,  # 사서 승인 필수
    },
    "E3": {
        "name": "고급 (200권 완료)",
        "permissions": ["read_only", "scan_isbn", "input_full", "review_others"],
        "completion_required": "다른 자원봉사 입력 검수 가능",
        "can_save_record": True,
    },
    "E4": {
        "name": "숙련 (500권 + 사서 추천)",
        "permissions": ["read_only", "scan_isbn", "input_full", "review_others", "approve_self"],
        "completion_required": "사서 추천 + 시험 통과",
        "can_save_record": True,  # 자체 승인 가능 (사서 사후 검토)
    },
}


@dataclass(frozen=True)
class Volunteer:
    """자원봉사 1명 프로필."""

    volunteer_id: str
    name_anonymized: str  # "자원봉사 A·B·C" (실명 X)
    library_id: str
    level: VolunteerLevel
    records_completed: int  # 입력한 KORMARC 권수
    quality_score: float  # 사서 검수 통과율 (0.0~1.0)
    onboarded_at: str  # ISO 8601
    last_active_at: str | None = None
    completed_tutorials: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OnboardingStep:
    """온보딩 단계 1개."""

    step_id: str
    title: str
    duration_minutes: int
    type_: Literal["tutorial", "shadowing", "practice", "test"]
    completion_criterion: str


# 5분 onboarding 튜토리얼 (E0 진입)
ONBOARDING_TUTORIAL: list[OnboardingStep] = [
    OnboardingStep(
        step_id="welcome",
        title="환영합니다 (작은도서관 자원봉사)",
        duration_minutes=1,
        type_="tutorial",
        completion_criterion="시작 버튼 클릭",
    ),
    OnboardingStep(
        step_id="scan_demo",
        title="ISBN 바코드 스캔 시연 (1권)",
        duration_minutes=1,
        type_="shadowing",
        completion_criterion="시범 ISBN 1권 스캔 확인",
    ),
    OnboardingStep(
        step_id="auto_fill",
        title="자동 입력 결과 확인 (제목·저자·KDC)",
        duration_minutes=1,
        type_="tutorial",
        completion_criterion="자동 채움 결과 30초 검토",
    ),
    OnboardingStep(
        step_id="librarian_review",
        title="사서 검수 단계 안내 (왜 필요한가)",
        duration_minutes=1,
        type_="tutorial",
        completion_criterion="검수 단계 이해 확인",
    ),
    OnboardingStep(
        step_id="first_practice",
        title="첫 5권 = 사서와 함께",
        duration_minutes=1,
        type_="practice",
        completion_criterion="첫 5권 사서 동석 입력 완료",
    ),
]


def can_volunteer_save(volunteer: Volunteer, action: str = "input_basic") -> bool:
    """자원봉사가 해당 작업 권한 있는지."""
    perms = VOLUNTEER_LEVELS.get(volunteer.level, {}).get("permissions", [])
    return action in perms


def calculate_next_level(volunteer: Volunteer) -> VolunteerLevel | None:
    """다음 등급 진입 가능 여부."""
    if volunteer.level == "E0" and volunteer.records_completed >= 5:
        return "E1"
    if (
        volunteer.level == "E1"
        and volunteer.records_completed >= 50
        and volunteer.quality_score >= 0.9
    ):
        return "E2"
    if volunteer.level == "E2" and volunteer.records_completed >= 200:
        return "E3"
    if volunteer.level == "E3" and volunteer.records_completed >= 500:
        return "E4"  # 단 사서 추천·시험은 별도
    return None


def create_volunteer_profile(
    volunteer_id: str,
    name_anonymized: str,
    library_id: str,
) -> Volunteer:
    """신규 자원봉사 등록 (E0 시작)."""
    return Volunteer(
        volunteer_id=volunteer_id,
        name_anonymized=name_anonymized,
        library_id=library_id,
        level="E0",
        records_completed=0,
        quality_score=0.0,
        onboarded_at=datetime.now(UTC).isoformat(),
    )


def progress_summary(volunteer: Volunteer) -> dict:
    """자원봉사 진척 요약 (대시보드 표시)."""
    next_level = calculate_next_level(volunteer)
    level_meta = VOLUNTEER_LEVELS[volunteer.level]
    return {
        "volunteer_id": volunteer.volunteer_id,
        "current_level": volunteer.level,
        "current_level_name": level_meta["name"],
        "records_completed": volunteer.records_completed,
        "quality_score": volunteer.quality_score,
        "next_level": next_level,
        "can_save": level_meta["can_save_record"],
        "permissions": level_meta["permissions"],
    }


__all__ = [
    "ONBOARDING_TUTORIAL",
    "VOLUNTEER_LEVELS",
    "OnboardingStep",
    "Volunteer",
    "VolunteerLevel",
    "calculate_next_level",
    "can_volunteer_save",
    "create_volunteer_profile",
    "progress_summary",
]
