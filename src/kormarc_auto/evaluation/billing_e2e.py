"""결제 흐름 e2e 검증 — 6-1 (4 plan + 권당 + grace + 환불).

PO 명령 (12-섹션 §6.1): "월 3·5·15·30만원 4 plan + 권당 100원·200원 + grace + 환불"
PIPA 정합 + 영업 신뢰 = 결제 흐름 깨지면 매출 0.

시나리오:
1. 신규 가입 → 무료 50건 → 한도 도달 → 결제 안내
2. 권당 200원 종량제 (Part 88·기본 가격)
3. 월 정액 업그레이드 (proration)
4. 결제 실패 → 7일 grace → 차단 → 1주 100% 환불
5. 본인 데이터 export (§35-3) + 영구 삭제 (§36)
6. admin 권한 = PIPA 마스킹 (사서 식별 정보)

본 모듈 = 흐름 시뮬·실 결제 X. 실 결제 = server/billing.py + payment_adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal

PlanType = Literal["free", "metered", "personal", "small", "school", "large", "enterprise"]
PaymentStatus = Literal["paid", "pending", "failed", "grace", "blocked", "refunded"]


# 가격 매트릭스 (Part 88 v2 결정 = 권당 200원 1차)
PLAN_PRICING: dict[PlanType, dict] = {
    "free": {"monthly_won": 0, "metered_won_per_book": 0, "free_book_quota": 50},
    "metered": {"monthly_won": 0, "metered_won_per_book": 200, "free_book_quota": 50},  # 1차 추천
    "personal": {"monthly_won": 9_900, "metered_won_per_book": 0, "free_book_quota": 9999},
    "small": {"monthly_won": 30_000, "metered_won_per_book": 0, "free_book_quota": 9999},
    "school": {"monthly_won": 50_000, "metered_won_per_book": 0, "free_book_quota": 9999},
    "large": {"monthly_won": 150_000, "metered_won_per_book": 0, "free_book_quota": 9999},
    "enterprise": {"monthly_won": 300_000, "metered_won_per_book": 0, "free_book_quota": 9999},
}


@dataclass
class BillingState:
    """도서관별 결제 상태 (per-tenant)."""

    tenant_id: str
    plan: PlanType
    status: PaymentStatus
    books_processed_this_month: int = 0
    last_payment_at: str | None = None
    last_failure_at: str | None = None
    grace_until: str | None = None
    blocked_at: str | None = None


@dataclass
class BillingEvent:
    """결제 이벤트 (audit_log)."""

    tenant_id: str
    event_type: str  # "signup" / "process_book" / "monthly_charge" / "fail" / "refund" / "block"
    amount_won: int
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict | None = None


def is_within_free_quota(state: BillingState) -> bool:
    """무료 50건 한도 내 여부."""
    quota = PLAN_PRICING[state.plan]["free_book_quota"]
    return state.books_processed_this_month < quota


def calculate_book_charge(state: BillingState) -> int:
    """권당 처리 비용 계산 (한도 초과 시).

    Returns:
        처리 비용 (원). 0 = 무료 한도 내 또는 정액제.
    """
    if is_within_free_quota(state):
        return 0
    plan_meta = PLAN_PRICING[state.plan]
    metered = plan_meta.get("metered_won_per_book", 0)
    return metered


def calculate_monthly_invoice(state: BillingState) -> int:
    """월 청구액 계산 (정액 + 종량 + 한도 초과)."""
    plan_meta = PLAN_PRICING[state.plan]
    monthly = plan_meta["monthly_won"]
    metered_per_book = plan_meta.get("metered_won_per_book", 0)
    free_quota = plan_meta["free_book_quota"]

    over_quota = max(0, state.books_processed_this_month - free_quota)
    metered_total = over_quota * metered_per_book
    return monthly + metered_total


def transition_on_payment_failure(state: BillingState, *, grace_days: int = 7) -> BillingState:
    """결제 실패 → grace 진입."""
    now = datetime.now(UTC)
    grace_end = (now + timedelta(days=grace_days)).isoformat()
    return BillingState(
        tenant_id=state.tenant_id,
        plan=state.plan,
        status="grace",
        books_processed_this_month=state.books_processed_this_month,
        last_payment_at=state.last_payment_at,
        last_failure_at=now.isoformat(),
        grace_until=grace_end,
        blocked_at=state.blocked_at,
    )


def transition_on_grace_expired(state: BillingState) -> BillingState:
    """grace 만료 → 차단."""
    return BillingState(
        tenant_id=state.tenant_id,
        plan=state.plan,
        status="blocked",
        books_processed_this_month=state.books_processed_this_month,
        last_payment_at=state.last_payment_at,
        last_failure_at=state.last_failure_at,
        grace_until=state.grace_until,
        blocked_at=datetime.now(UTC).isoformat(),
    )


def is_eligible_for_refund(state: BillingState, *, refund_window_days: int = 7) -> bool:
    """1주 100% 환불 자격 (PIPA + 영업 신뢰)."""
    if not state.last_payment_at:
        return False
    paid_at = datetime.fromisoformat(state.last_payment_at.replace("Z", "+00:00"))
    elapsed = datetime.now(UTC) - paid_at
    return elapsed.days < refund_window_days


def process_refund(state: BillingState) -> tuple[BillingState, BillingEvent]:
    """환불 처리 (1주 100%)."""
    if not is_eligible_for_refund(state):
        raise ValueError("환불 기간 초과 (7일)")

    plan_meta = PLAN_PRICING[state.plan]
    refund_won = plan_meta["monthly_won"] + (
        max(0, state.books_processed_this_month - plan_meta["free_book_quota"])
        * plan_meta.get("metered_won_per_book", 0)
    )

    new_state = BillingState(
        tenant_id=state.tenant_id,
        plan="free",  # 환불 = free로 강등
        status="refunded",
        books_processed_this_month=state.books_processed_this_month,
    )
    event = BillingEvent(
        tenant_id=state.tenant_id,
        event_type="refund",
        amount_won=-refund_won,
        metadata={"refund_reason": "1주 100% 환불"},
    )
    return new_state, event


def mask_admin_view(state: BillingState) -> dict:
    """admin /billing/monthly = PIPA 식별정보 마스킹."""
    return {
        "tenant_id_hash": f"***{state.tenant_id[-4:]}",  # 끝 4자리만
        "plan": state.plan,
        "status": state.status,
        "books_processed": state.books_processed_this_month,
        "monthly_invoice_won": calculate_monthly_invoice(state),
    }


__all__ = [
    "PLAN_PRICING",
    "BillingEvent",
    "BillingState",
    "PaymentStatus",
    "PlanType",
    "calculate_book_charge",
    "calculate_monthly_invoice",
    "is_eligible_for_refund",
    "is_within_free_quota",
    "mask_admin_view",
    "process_refund",
    "transition_on_grace_expired",
    "transition_on_payment_failure",
]
