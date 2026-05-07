"""Cycle 78 — B2C 메트릭 (MRR·activation·churn·시간 절감 환산).

원칙 (ADR 0046 invariant 11 정합):
- 인터뷰 0건 = 가설·임계값 시뮬·향후 v2 재조정
- LLM 호출 0·통계 결정적
- 사서 PII = 우리 서버 X (Auth만·헌법 §14)

타겟 (Cycle 68 ADR 0050):
- B2C ₩9,900/월·Pro ₩19,900·Founding ₩4,950
- TAM 31,500 사서·SOM 1,500~3,000명
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

# 임계값 (외부 858 보고서·ChartMogul 2026 정합·인터뷰 후 v2)
MRR_TARGET_MONTHLY_KRW = 5_000_000  # 시드 매출·SOM 500명 × ₩9,900 + 일부 Pro
ACTIVATION_THRESHOLD_RECORDS = 100  # 100권 처리 + 보고서 1회 = activation
CHURN_RISK_INACTIVE_DAYS = 14  # D+14 미사용 = 이탈 위험
HOURLY_RATE_LIBRARIAN_KRW = 20_000  # 사서 시급 추정
TIME_SAVED_PER_RECORD_MINUTES = 6  # 8분 → 2분 (헌법 §0)


class SubscriptionTier(StrEnum):
    """B2C 4 플랜 (Cycle 68 ADR 0050 정합)."""

    FREE = "free"  # ₩0·50건/월
    PERSONAL = "personal"  # ₩9,900/월·무제한
    PRO = "pro"  # ₩19,900/월·AI·OCR·880
    FOUNDING = "founding"  # ₩4,950/월·100관 한정·~2026-06-30·영구 50%


@dataclass(frozen=True)
class SaaSMetrics:
    """B2C 메트릭 매트릭스 (현재 시점·시뮬)."""

    total_users: int
    paid_users: int
    free_users: int
    mrr_krw: int
    activated_users: int  # 100권+ 처리·보고서 1회
    activation_rate_pct: float
    churn_at_risk: int  # D+14 미사용
    target_progress_pct: float  # MRR_TARGET 대비


def calculate_mrr(
    personal_count: int = 0,
    pro_count: int = 0,
    founding_count: int = 0,
) -> int:
    """월 매출 (MRR·KRW)."""
    return personal_count * 9_900 + pro_count * 19_900 + founding_count * 4_950


def is_user_activated(records_processed: int, has_report: bool = False) -> bool:
    """사용자 activation 여부 (Cycle 19B + 78 정합).

    activation = 100권 처리 + 보고서 1회 (의미 있는 가치 실현).
    Lenny Rachitsky 2025·activation 정의 시 2.5x 전환.
    """
    return records_processed >= ACTIVATION_THRESHOLD_RECORDS and has_report


def calculate_time_saved_value(records_per_month: int) -> dict[str, str]:
    """사서 시간 절감 환산 (헌법 §0 = 8분 → 2분 = 6분/권).

    Returns:
        시간·시급 환산·SaaS ROI
    """
    minutes_saved = records_per_month * TIME_SAVED_PER_RECORD_MINUTES
    hours_saved = minutes_saved / 60
    krw_saved = int(hours_saved * HOURLY_RATE_LIBRARIAN_KRW)
    saas_monthly = 9_900  # Personal 기준

    return {
        "records_per_month": f"{records_per_month}권",
        "minutes_saved": f"{minutes_saved:,}분",
        "hours_saved": f"{hours_saved:.1f}시간",
        "krw_saved": f"₩{krw_saved:,}",
        "saas_monthly": f"₩{saas_monthly:,}",
        "roi": f"{krw_saved // saas_monthly}:1" if saas_monthly else "∞:1",
        "context": (
            f"권당 {TIME_SAVED_PER_RECORD_MINUTES}분 절감 × {records_per_month}권 = "
            f"매월 {hours_saved:.1f}시간·₩{krw_saved:,} 가치"
        ),
    }


def estimate_churn_risk(days_since_last_use: int, records_processed: int) -> str:
    """이탈 위험 4 단계 (D+7·D+14·D+30·D+60).

    외부 858 보고서·ChartMogul churn 표준.
    """
    if days_since_last_use >= 60:
        return "critical"  # 거의 이탈
    if days_since_last_use >= 30:
        return "high"  # D+30 미사용 = 위험
    if days_since_last_use >= CHURN_RISK_INACTIVE_DAYS:
        return "medium"  # D+14 미사용 = 트리거
    if records_processed < 10:
        return "onboarding"  # 첫 사용·도입 미완성
    return "active"  # 정상


def render_summary(m: SaaSMetrics) -> str:
    """B2C 매트릭스 요약 (CLI·dashboard 인용용)."""
    progress_emoji = (
        "🔴" if m.target_progress_pct < 30 else "🟡" if m.target_progress_pct < 80 else "🟢"
    )
    return (
        f"=== B2C 메트릭 (Cycle 78·시뮬·인터뷰 0건) ===\n"
        f"총 사용자: {m.total_users}명\n"
        f"  └─ 결제: {m.paid_users}명 / 무료: {m.free_users}명\n"
        f"MRR: ₩{m.mrr_krw:,} / 목표 ₩{MRR_TARGET_MONTHLY_KRW:,} "
        f"({m.target_progress_pct:.1f}%) {progress_emoji}\n"
        f"Activation: {m.activated_users}명 ({m.activation_rate_pct:.1f}%)\n"
        f"Churn 위험 (D+14 미사용): {m.churn_at_risk}명\n"
        f"⚠ 정직 헤더: 인터뷰 0건·SOM 시뮬·invariant 11 (PMF 결정 X)\n"
    )


def make_demo_snapshot() -> SaaSMetrics:
    """베타 시드 시뮬 (50명 trial·5명 결제·1년차 가설)."""
    paid = 5
    free = 45
    return SaaSMetrics(
        total_users=paid + free,
        paid_users=paid,
        free_users=free,
        mrr_krw=calculate_mrr(personal_count=5),
        activated_users=12,
        activation_rate_pct=12 / 50 * 100,
        churn_at_risk=8,
        target_progress_pct=calculate_mrr(personal_count=5) / MRR_TARGET_MONTHLY_KRW * 100,
    )


__all__ = [
    "ACTIVATION_THRESHOLD_RECORDS",
    "CHURN_RISK_INACTIVE_DAYS",
    "HOURLY_RATE_LIBRARIAN_KRW",
    "MRR_TARGET_MONTHLY_KRW",
    "TIME_SAVED_PER_RECORD_MINUTES",
    "SaaSMetrics",
    "SubscriptionTier",
    "calculate_mrr",
    "calculate_time_saved_value",
    "estimate_churn_risk",
    "is_user_activated",
    "make_demo_snapshot",
    "render_summary",
]
