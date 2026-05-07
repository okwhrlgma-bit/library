"""Cycle 78 — B2C 메트릭 모듈 (MRR·activation·churn·시간 절감 환산).

ADR 0050 + 0051 정합·founder fit B2C "몰래 쓰기".
LLM 호출 0·통계 결정적 (V3 §4.10).
"""

from kormarc_auto.b2c.metrics import (
    ACTIVATION_THRESHOLD_RECORDS,
    MRR_TARGET_MONTHLY_KRW,
    SaaSMetrics,
    SubscriptionTier,
    calculate_mrr,
    calculate_time_saved_value,
    estimate_churn_risk,
    is_user_activated,
)

__all__ = [
    "ACTIVATION_THRESHOLD_RECORDS",
    "MRR_TARGET_MONTHLY_KRW",
    "SaaSMetrics",
    "SubscriptionTier",
    "calculate_mrr",
    "calculate_time_saved_value",
    "estimate_churn_risk",
    "is_user_activated",
]
