"""Cycle 61 (ADR 0045 §C) — 사용자/추천자/결제자 3-단계 funnel.

기존 단일 funnel (Cycle 14B) = 틀림.
실제 도서관 SaaS 결제 = 3 분리:

    사서 = 사용자 (시간 절감 매력)
       ↓ 사서가 추천
    사서 = 추천자 (학교운영위·자치구에 들고 감)
       ↓ 의사결정자 승인
    학교/자치구 = 결제자 (예산·세금계산서)

각 단계 conversion = 다른 마케팅·메시지·KPI 필요.
외부 매출 보고서 §결제자 ≠ 사용자 정합.
"""

from __future__ import annotations

from dataclasses import dataclass

# 3-단계 funnel 표준 이벤트
USER_EVENTS = (
    "demo_start",
    "signup",
    "first_record_built",
    "activation_100_records",
    "weekly_return",
)

ADVOCATE_EVENTS = (
    "share_with_colleague",
    "internal_demo_to_committee",
    "loi_drafted",
    "champion_identified",
)

BUYER_EVENTS = (
    "quote_requested",
    "tax_invoice_issued",
    "payment_authorized",
    "contract_signed",
    "first_payment_received",
)


@dataclass(frozen=True)
class ThreeStageMetrics:
    """3 단계 conversion 매트릭스."""

    user_count: int
    advocate_count: int
    buyer_count: int
    user_to_advocate_pct: float  # 사용자 → 추천자
    advocate_to_buyer_pct: float  # 추천자 → 결제자
    user_to_buyer_pct: float  # 사용자 → 결제자 (전체)


def calculate_three_stage(events: list[dict]) -> ThreeStageMetrics:
    """3-단계 funnel 계산.

    Args:
        events: 이벤트 리스트 (event_name, user_id, timestamp)

    Returns:
        각 단계 카운트 + conversion %
    """
    by_user: dict[str, set[str]] = {}
    for ev in events:
        uid = ev.get("user_id", "")
        if not uid:
            continue
        by_user.setdefault(uid, set()).add(ev.get("event_name", ""))

    user_count = sum(1 for evs in by_user.values() if any(e in USER_EVENTS for e in evs))
    advocate_count = sum(1 for evs in by_user.values() if any(e in ADVOCATE_EVENTS for e in evs))
    buyer_count = sum(1 for evs in by_user.values() if any(e in BUYER_EVENTS for e in evs))

    return ThreeStageMetrics(
        user_count=user_count,
        advocate_count=advocate_count,
        buyer_count=buyer_count,
        user_to_advocate_pct=(advocate_count / user_count * 100) if user_count else 0,
        advocate_to_buyer_pct=(buyer_count / advocate_count * 100) if advocate_count else 0,
        user_to_buyer_pct=(buyer_count / user_count * 100) if user_count else 0,
    )


def stage_health_signals(m: ThreeStageMetrics) -> dict[str, str]:
    """단계별 건강 신호 (외부 매출 보고서 P32·옵트인 trial 8-15% 정합).

    임계:
    - 사용자 → 추천자 ≥ 30% = 정합 (사서 만족)
    - 추천자 → 결제자 ≥ 20% = 정합 (의사결정자 승인)
    - 사용자 → 결제자 (전체) ≥ 6% = 외부 858 보고서 옵트인 trial 표준
    """
    signals = {}

    if m.user_count == 0:
        return {"status": "데이터 부족·1주 누적 후 재측정"}

    if m.user_to_advocate_pct < 30:
        signals["user_to_advocate"] = (
            f"⚠ {m.user_to_advocate_pct:.1f}% < 30% — 사서 만족도 검토·NPS 수집 활성"
        )
    else:
        signals["user_to_advocate"] = f"✅ {m.user_to_advocate_pct:.1f}% (≥30%·정합)"

    if m.advocate_count == 0:
        signals["advocate_to_buyer"] = "추천자 0건·M9-A 자관 PILOT 외 X"
    elif m.advocate_to_buyer_pct < 20:
        signals["advocate_to_buyer"] = (
            f"⚠ {m.advocate_to_buyer_pct:.1f}% < 20% — 의사결정자 승인 차단·"
            "학교운영위·자치구 메시지 검토"
        )
    else:
        signals["advocate_to_buyer"] = f"✅ {m.advocate_to_buyer_pct:.1f}% (≥20%·정합)"

    if m.user_to_buyer_pct < 6:
        signals["overall"] = (
            f"⚠ 전체 {m.user_to_buyer_pct:.1f}% < 6% — 결제 채널 (B2C·학교·자치구) 분리 강화"
        )
    else:
        signals["overall"] = f"✅ 전체 {m.user_to_buyer_pct:.1f}% (≥6%·외부 858 표준)"

    return signals


def render_three_stage_summary(m: ThreeStageMetrics) -> str:
    """텍스트 요약 (CLI·report.md 인용용)."""
    return (
        f"=== 3-단계 funnel (사용자→추천자→결제자) ===\n"
        f"사서 (사용자)         : {m.user_count}명\n"
        f"  ↓ {m.user_to_advocate_pct:.1f}% 추천 전환\n"
        f"사서 (추천자)         : {m.advocate_count}명\n"
        f"  ↓ {m.advocate_to_buyer_pct:.1f}% 결제 전환\n"
        f"학교/자치구 (결제자)  : {m.buyer_count}건\n"
        f"전체 (사용자→결제자) : {m.user_to_buyer_pct:.1f}%\n"
    )


__all__ = [
    "ADVOCATE_EVENTS",
    "BUYER_EVENTS",
    "USER_EVENTS",
    "ThreeStageMetrics",
    "calculate_three_stage",
    "render_three_stage_summary",
    "stage_health_signals",
]
