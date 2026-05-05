"""갈래 B Cycle 19B (P32) — Activation 정의 + 이탈 위험 감지.

원칙 (외부 매출 보고서 P32·MadKudu·Lenny Rachitsky 2.5x 정합):
- activation = ISBN 100건 + 보고서 1회 (의미 있는 가치 실현)
- D+7 = 활성화 체크 + 인사이드 컨택 (이탈 위험 감지)
- 14일 trial 종료 D-7/D-3/D-0 = 결제 전환 트리거
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

ACTIVATION_THRESHOLD_RECORDS: int = 100  # ISBN 자동 생성 건수
ACTIVATION_THRESHOLD_REPORTS: int = 1  # 보고서 출력 횟수

ChurnRiskLevel = Literal["safe", "watch", "at_risk", "lost"]


@dataclass(frozen=True)
class ActivationStatus:
    """사용자 activation 상태."""

    user_id: str
    is_activated: bool
    records_processed: int
    reports_generated: int
    days_since_signup: int
    churn_risk: ChurnRiskLevel
    next_action: str

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "is_activated": self.is_activated,
            "records_processed": self.records_processed,
            "reports_generated": self.reports_generated,
            "days_since_signup": self.days_since_signup,
            "churn_risk": self.churn_risk,
            "next_action": self.next_action,
        }


def _churn_level(
    *,
    is_activated: bool,
    days_since_signup: int,
    records_processed: int,
) -> ChurnRiskLevel:
    """D+7 활성화 + 사용 패턴 → 이탈 위험."""
    if is_activated:
        return "safe"
    if days_since_signup <= 3:
        return "safe"  # 아직 시간
    if days_since_signup <= 7 and records_processed > 10:
        return "watch"
    if days_since_signup <= 14 and records_processed > 0:
        return "at_risk"
    return "lost"  # 14일 경과 + 사용 0


def _next_action_for(level: ChurnRiskLevel, days: int) -> str:
    """이탈 위험별 다음 권고 액션."""
    actions = {
        "safe": "✓ 활성·다음 = 가치 실현 ISBN 100건 + 보고서 출력 권유 알림",
        "watch": ("🟡 D+7 watch·인사이드 컨택 큐 = '5분 위저드 미완? 도움 필요?' 이메일"),
        "at_risk": (
            "🔴 D+14 at_risk·전화 또는 1:1 데모 권유 = 'KOLAS III D-day·"
            "마이그레이션 무료 진단' 트리거"
        ),
        "lost": ("⛔ D+14+ lost·자동 재마케팅 = 14일 후 KOLAS III 카운트다운 알림 1회만"),
    }
    return actions.get(level, "검토 필요")


def check_activation(
    *,
    user_id: str,
    signed_up_at: datetime,
    records_processed: int,
    reports_generated: int,
    now: datetime | None = None,
) -> ActivationStatus:
    """사용자 activation 상태 산정."""
    if now is None:
        now = datetime.now(UTC)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    if signed_up_at.tzinfo is None:
        signed_up_at = signed_up_at.replace(tzinfo=UTC)

    days = (now - signed_up_at).days
    is_activated = (
        records_processed >= ACTIVATION_THRESHOLD_RECORDS
        and reports_generated >= ACTIVATION_THRESHOLD_REPORTS
    )
    risk = _churn_level(
        is_activated=is_activated,
        days_since_signup=days,
        records_processed=records_processed,
    )
    return ActivationStatus(
        user_id=user_id,
        is_activated=is_activated,
        records_processed=records_processed,
        reports_generated=reports_generated,
        days_since_signup=days,
        churn_risk=risk,
        next_action=_next_action_for(risk, days),
    )


def is_at_risk_of_churn(status: ActivationStatus) -> bool:
    return status.churn_risk in ("at_risk", "lost")


def trial_end_trigger(
    *, signed_up_at: datetime, trial_days: int = 14, now: datetime | None = None
) -> str | None:
    """14일 trial 종료 D-7/D-3/D-0 트리거."""
    if now is None:
        now = datetime.now(UTC)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    if signed_up_at.tzinfo is None:
        signed_up_at = signed_up_at.replace(tzinfo=UTC)

    end = signed_up_at + timedelta(days=trial_days)
    days_remaining = (end - now).days

    if days_remaining == 7:
        return "D-7 = 결제 전환 첫 알림 (월 ₩30,000~ 플랜 안내)"
    if days_remaining == 3:
        return "D-3 = 마지막 알림 + Founding Member 50% 할인 강조 (~2026-06-30)"
    if days_remaining == 0:
        return "D-0 = 자동 freemium 50건/월 전환 + 업그레이드 옵션 상시 표시"
    return None
