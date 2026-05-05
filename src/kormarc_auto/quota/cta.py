"""갈래 B Cycle 13B (P33) — 한도 초과 CTA + 개인화 메시지.

Mixpanel 가치 실현 +32%·Pendo 행동 트리거 3.4x·외부 매출 보고서 P33.

CTA 원칙:
- 100% 도달 = 즉시 업그레이드 옵션 + 다음달 자동 초기화 안내 둘 다 (둘 중 하나 누락 = STOP)
- 개인화 메시지 = 사용자 본인 데이터로만 (다른 도서관 데이터 노출 X)
- 한국 학교·공공 = 결재선 문화·강제 없는 옵션 우선
"""

from __future__ import annotations

from dataclasses import dataclass

from kormarc_auto.quota.tracker import QuotaTracker


@dataclass(frozen=True)
class UpgradeCTA:
    """업그레이드 권유 메시지 + 추천 플랜."""

    headline: str
    body: str
    recommended_plan: str  # "small" / "school" / "public" / "enterprise"
    safety_margin_x: float  # 추천 플랜 한도 / 현재 사용량
    cta_label: str = "플랜 업그레이드"
    secondary_cta: str = "다음달 1일 자동 초기화"


def _recommend_plan_for_usage(monthly_avg: int) -> tuple[str, int]:
    """사용량 기반 플랜 추천 (1.5배 안전마진)."""
    target = int(monthly_avg * 1.5)
    if target <= 500:
        return ("small", 500)
    if target <= 2000:
        return ("school", 2000)
    if target <= 10000:
        return ("public", 10000)
    return ("enterprise", 999_999_999)


def personalized_upgrade_cta(
    tracker: QuotaTracker, *, library_name_hint: str = "이 도서관"
) -> UpgradeCTA:
    """사용자 데이터 기반 개인화 CTA (다른 도서관 데이터 X)."""
    avg = tracker.current_count
    plan_code, plan_limit = _recommend_plan_for_usage(avg)
    margin = plan_limit / max(1, avg)
    plan_label = {
        "small": "작은도서관 (월 ₩30,000·VAT 별도)",
        "school": "학교도서관 (월 ₩50,000·VAT 별도)",
        "public": "공공도서관 (월 ₩150,000·VAT 별도·★ 추천)",
        "enterprise": "기관 (문의·맞춤 견적)",
    }.get(plan_code, plan_code)

    if plan_code == "enterprise":
        body = (
            f"{library_name_hint}의 이번달 사용량 = {avg}건. "
            f"전담 매니저·SLA·SSO·CSAP 환경이 필요한 규모입니다. "
            f"맞춤 견적 문의."
        )
    else:
        body = (
            f"{library_name_hint}의 이번달 사용량 = {avg}건. "
            f"{plan_label}이면 월 {plan_limit}건 = {margin:.1f}배 안전마진. "
            f"연간결제 시 17% 할인 (2개월 무료)."
        )

    return UpgradeCTA(
        headline="한도 도달·업그레이드 또는 다음달 대기",
        body=body,
        recommended_plan=plan_code,
        safety_margin_x=round(margin, 2),
    )


def quota_warning_message(tracker: QuotaTracker, *, library_name_hint: str = "이 도서관") -> str:
    """80% pre-warning 인앱 배너 본문."""
    used = tracker.current_count
    total = tracker.monthly_limit
    remaining = tracker.remaining_records()
    return (
        f"⚠ {library_name_hint} 이번달 KORMARC 생성 = {used}/{total}건 사용. "
        f"남은 {remaining}건 이내 = 다음달 1일 자동 초기화. "
        f"여유 있게 쓰려면 플랜 업그레이드 (연간 17% 할인)."
    )


def quota_block_message(tracker: QuotaTracker, *, library_name_hint: str = "이 도서관") -> str:
    """100% block 결제 모달 본문 (24h grace 안내 포함)."""
    return (
        f"📚 {library_name_hint} 이번달 한도 {tracker.monthly_limit}건 모두 사용. "
        f"24시간 추가 처리 가능 (학교 결재 시간 고려). "
        f"즉시 업그레이드하면 한도 즉시 확장·다음달 1일 무료 한도 자동 초기화."
    )
