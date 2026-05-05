"""갈래 B Cycle 19B (P32·외부 매출 보고서) — 5분 온보딩 위저드 + activation.

원칙:
- 5단계 = 자관코드 → 분류체계 → 880 한자 → DLS/KOLAS → 첫 ISBN
- activation = ISBN 100건 + 보고서 1회 (Lenny Rachitsky 2.5x 전환)
- 14일 trial → freemium 자동 전환 (옵트인 8-15% 목표)
- D+7 활성화 체크 + 인사이드 컨택 큐
"""

from kormarc_auto.onboarding.activation import (
    ACTIVATION_THRESHOLD_RECORDS,
    ActivationStatus,
    check_activation,
    is_at_risk_of_churn,
)
from kormarc_auto.onboarding.wizard import (
    WIZARD_STEPS,
    OnboardingState,
    WizardStep,
    advance_step,
    initial_state,
    is_complete,
)

__all__ = [
    "ACTIVATION_THRESHOLD_RECORDS",
    "WIZARD_STEPS",
    "ActivationStatus",
    "OnboardingState",
    "WizardStep",
    "advance_step",
    "check_activation",
    "initial_state",
    "is_at_risk_of_churn",
    "is_complete",
]
