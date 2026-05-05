"""갈래 B Cycle 11 (P31) — 4 플랜 단일 진실 소스.

외부 858 출처 보고서 + 외부 매출 성장 보고서 (2026-05-05) 정합:
- 한국도서관법 정합 명명 (작은도서관·학교·공공·기관)
- VAT 별도·연 결제 17% 할인 (2개월 무료·ChartMogul Recurly 표준)
- 신규 50% 첫 1년·5/10/100관 묶음 10/15/20/25/30%
- Founding Member 영구 50%·100관 한정·2026-06-30 데드라인·연간결제 의무 (LTD 금지)
- 영구 freemium 50건/월 + 30일 무료 체험 (신용카드 미등록·옵트인 8-15% 목표)
- 도서관부호 또는 사업자등록번호 1:1 매칭 (남용 차단)

ENV override 가능 (운영 중 hotfix·default 변경 = ADR 필수).

ADR 0026 한국 SaaS 결정 §D + 외부 매출 보고서 P31 정합.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

BillingCycle = Literal["monthly", "quarterly", "annual"]


@dataclass(frozen=True)
class Plan:
    """단일 플랜 정의."""

    code: str  # "free", "small", "school", "public", "enterprise"
    label: str
    label_en: str
    monthly_krw: int  # VAT 별도
    monthly_records: int  # KORMARC 자동생성 한도 (건/월)
    user_count: int  # 사서 사용자 수
    branch_count: int  # 분관 수
    api_call_limit_monthly: int  # API 호출 한도
    sso_audit_log: bool = False
    csap_environment: bool = False
    support_channel: str = "email"  # "email", "email+phone", "dedicated_manager"
    description: str = ""

    @property
    def annual_krw_after_discount(self) -> int:
        """연 결제 17% 할인 = 2개월 무료."""
        return int(self.monthly_krw * 12 * (1 - 0.17))


# 4 플랜 (외부 858 출처 §4.1·외부 매출 보고서 P31 정합)
PLANS: dict[str, Plan] = {
    "free": Plan(
        code="free",
        label="무료 체험 (영구 freemium)",
        label_en="Free (forever)",
        monthly_krw=0,
        monthly_records=50,
        user_count=1,
        branch_count=1,
        api_call_limit_monthly=0,
        support_channel="email",
        description="50건/월·1 사서·30일 무료 trial 후 자동 freemium 전환·신용카드 미등록",
    ),
    "small": Plan(
        code="small",
        label="작은도서관",
        label_en="Small Library (Lite)",
        monthly_krw=int(os.getenv("KORMARC_PRICE_SMALL_KRW", "30000")),
        monthly_records=500,
        user_count=1,
        branch_count=1,
        api_call_limit_monthly=0,
        support_channel="email",
        description="사립 작은도서관·25㎡ 미만·자원봉사 사서·1관 운영",
    ),
    "school": Plan(
        code="school",
        label="학교도서관",
        label_en="School Library (Standard)",
        monthly_krw=int(os.getenv("KORMARC_PRICE_SCHOOL_KRW", "50000")),
        monthly_records=2000,
        user_count=3,
        branch_count=1,
        api_call_limit_monthly=10000,
        support_channel="email",
        description="초·중·고 학교도서관·DLS 반입·학교회계 3.1~2.28",
    ),
    "public": Plan(
        code="public",
        label="공공도서관 (추천)",
        label_en="Public Library (Pro·★ Recommended)",
        monthly_krw=int(os.getenv("KORMARC_PRICE_PUBLIC_KRW", "150000")),
        monthly_records=10000,
        user_count=10,
        branch_count=5,
        api_call_limit_monthly=100000,
        support_channel="email+phone",
        description="시·군·구립 일반 공공도서관·KOLAS III 마이그레이션·5 분관",
    ),
    "enterprise": Plan(
        code="enterprise",
        label="B2B / 기관",
        label_en="Enterprise",
        monthly_krw=int(os.getenv("KORMARC_PRICE_ENTERPRISE_KRW", "300000")),
        monthly_records=999_999_999,  # 무제한
        user_count=999_999,
        branch_count=999,
        api_call_limit_monthly=999_999_999,
        sso_audit_log=True,
        csap_environment=True,
        support_channel="dedicated_manager",
        description="대학·도서관 컨소시엄·도서납품사·SSO·Audit Log·CSAP 환경·전담 매니저·SLA·맞춤 컨설팅",
    ),
}


# 묶음 할인 (자치구·교육청 일괄 도입)
BUNDLE_DISCOUNTS: dict[int, float] = {
    1: 0.0,
    5: 0.10,  # 5개관 이상 10%
    10: 0.15,  # 10개관 이상 15%
    25: 0.20,  # 자치구 단위 (외부 매출 보고서 P38)
    100: 0.25,  # 교육청 100+관
}


@dataclass(frozen=True)
class FoundingMember:
    """Founding Member 영구 할인 (외부 매출 보고서 핵심 의사결정 #3)."""

    discount_pct: float = 0.50
    seat_limit: int = 100
    deadline: date = field(default_factory=lambda: date(2026, 6, 30))
    annual_only: bool = True  # 연간결제 의무 (LTD 금지)
    permanent_lock_in: bool = True  # 가격 영구 동결


FOUNDING_MEMBER = FoundingMember()


def get_plan(code: str) -> Plan:
    if code not in PLANS:
        raise ValueError(f"Unknown plan code: {code}. Available: {list(PLANS.keys())}")
    return PLANS[code]


def list_plans() -> list[Plan]:
    """전체 플랜 (Free 포함·UI 가격표 렌더링용)."""
    return list(PLANS.values())


def apply_bundle_discount(monthly_total_krw: int, branch_count: int) -> tuple[int, float]:
    """묶음 할인 적용. (할인된 금액, 적용된 할인율) 반환."""
    discount = 0.0
    for threshold, pct in sorted(BUNDLE_DISCOUNTS.items()):
        if branch_count >= threshold:
            discount = pct
    discounted = int(monthly_total_krw * (1 - discount))
    return discounted, discount


def apply_cycle_discount(monthly_krw: int, cycle: BillingCycle) -> int:
    """결제 주기별 할인 적용. 1주기 총액 반환."""
    if cycle == "monthly":
        return monthly_krw
    if cycle == "quarterly":
        # 5% (시장 표준)
        return int(monthly_krw * 3 * (1 - 0.05))
    if cycle == "annual":
        # 17% (2개월 무료·ChartMogul·Recurly)
        return int(monthly_krw * 12 * (1 - 0.17))
    raise ValueError(f"Unknown billing cycle: {cycle}")


def apply_founding_discount(amount_krw: int, *, founding_member: bool) -> int:
    """Founding Member 50% 영구 할인 적용."""
    if not founding_member:
        return amount_krw
    return int(amount_krw * (1 - FOUNDING_MEMBER.discount_pct))


def calculate_quote(
    *,
    plan_code: str,
    branch_count: int = 1,
    cycle: BillingCycle = "monthly",
    founding_member: bool = False,
    vat_rate: float = 0.10,
) -> dict:
    """B2B 견적 계산. 모든 할인·VAT·중첩 상한 적용.

    외부 매출 보고서 P31·P38 게이트:
    - 70% 초과 할인 방지 (시장 학습 위험)
    - VAT 별도 표기
    - 묶음 + 연간 + Founding 중첩 가능
    """
    plan = get_plan(plan_code)

    # 1. 단가 (월) × 분관 수
    monthly_per_branch = plan.monthly_krw
    monthly_total = monthly_per_branch * branch_count

    # 2. 묶음 할인
    after_bundle, bundle_pct = apply_bundle_discount(monthly_total, branch_count)

    # 3. 결제 주기 할인 (월 단위로 환산)
    if cycle == "monthly":
        cycle_total = after_bundle
        cycle_pct = 0.0
    elif cycle == "quarterly":
        cycle_total = int(after_bundle * 3 * (1 - 0.05))
        cycle_pct = 0.05
    else:  # annual
        cycle_total = int(after_bundle * 12 * (1 - 0.17))
        cycle_pct = 0.17

    # 4. Founding Member
    after_founding = apply_founding_discount(cycle_total, founding_member=founding_member)
    founding_pct = FOUNDING_MEMBER.discount_pct if founding_member else 0.0

    # 5. 70% 상한 게이트 (Founding 50% + 묶음 30% = 65% = OK·그 이상 = 시장 학습 위험)
    base_period_total = monthly_total * (
        1 if cycle == "monthly" else 3 if cycle == "quarterly" else 12
    )
    total_discount_pct = 1 - (after_founding / base_period_total) if base_period_total else 0
    if total_discount_pct > 0.70:
        # 70% 상한 강제·warning
        after_founding = int(base_period_total * 0.30)

    # 6. VAT 별도
    vat = int(after_founding * vat_rate)
    grand_total = after_founding + vat

    return {
        "plan_code": plan_code,
        "plan_label": plan.label,
        "branch_count": branch_count,
        "cycle": cycle,
        "founding_member": founding_member,
        "monthly_per_branch_krw": monthly_per_branch,
        "monthly_total_krw_before_discount": monthly_total,
        "bundle_discount_pct": bundle_pct,
        "cycle_discount_pct": cycle_pct,
        "founding_discount_pct": founding_pct,
        "total_discount_pct": round(total_discount_pct, 4),
        "subtotal_krw": after_founding,
        "vat_krw": vat,
        "grand_total_krw": grand_total,
        "vat_rate": vat_rate,
        "currency": "KRW",
        "valid_until_days": 30,
    }
