"""결제 PG 어댑터 — 캐시카우 자동화의 마지막 1축.

ADR 0007 (포트원 채택, proposed) + ADR 0011 (매니지드 스택) 결정 이행.
billing.py가 약속한 "이 모듈만 교체"의 인터페이스를 미리 박아둠 →
PO 사업자 등록·통신판매 신고·포트원 가맹 완료 시 환경변수만 설정하면
**1줄 교체로 캐시카우 가동**.

3개 어댑터:
1. **LocalManualAdapter** — 현재 (카카오뱅크/통장 수동 입금, PO 직접 확인)
2. **PortOneAdapter** — 포트원 PG (정기결제·세금계산서 자동, ADR 0007 트리거 후)
3. **StripeAdapter** — 미국 §33 활성화 시 (ADR 0009 트리거 후, 현재 inactive)

선택 로직:
- `KORMARC_PG_PROVIDER` 환경변수 = `local` | `portone` | `stripe`
- 미설정 시 `local` 폴백 (현재 운영 모드)
- portone 선택 + `KORMARC_PORTONE_API_KEY` 미설정 → graceful fallback to local + 경고

평가축:
- §12 매출 의향: PG 도입 직후 학교/공공 결제팀 거부 0% — 캐시카우 직결
- §0 마크 시간: 영향 X (사서가 결제 직접 처리 시간 0)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from kormarc_auto.constants import PRICE_PER_RECORD_KRW

logger = logging.getLogger(__name__)


@dataclass
class PaymentResult:
    """결제 시도 결과."""

    ok: bool
    provider: str
    transaction_id: str | None = None
    amount_krw: int = 0
    receipt_url: str | None = None
    tax_invoice_url: str | None = None
    error: str | None = None


@dataclass
class SubscriptionResult:
    """월정액 구독 결과 (정기결제)."""

    ok: bool
    provider: str
    subscription_id: str | None = None
    plan_name: str | None = None
    monthly_amount_krw: int = 0
    next_billing_at: str | None = None  # ISO datetime
    error: str | None = None


class PaymentAdapter(Protocol):
    """결제 어댑터 인터페이스. 모든 PG 구현체는 이를 구현."""

    provider_name: str

    def charge(
        self,
        api_key: str,
        amount_krw: int,
        *,
        description: str = "",
        idempotency_key: str | None = None,
    ) -> PaymentResult:
        """1회성 결제 (권당 과금 또는 일시불 청구)."""
        ...

    def subscribe(
        self,
        api_key: str,
        plan_name: str,
        monthly_amount_krw: int,
        *,
        billing_day: int = 1,
    ) -> SubscriptionResult:
        """월정액 정기결제 등록 (PO 시간 0의 핵심)."""
        ...

    def cancel_subscription(
        self,
        api_key: str,
        subscription_id: str,
    ) -> bool:
        """구독 해지."""
        ...

    def issue_tax_invoice(
        self,
        api_key: str,
        amount_krw: int,
        *,
        business_no: str,
        period: str,
    ) -> str | None:
        """세금계산서 발행 → URL 반환. 학교/공공 결제팀 필수."""
        ...

    def is_available(self) -> bool:
        """이 어댑터가 현재 환경에서 사용 가능한지."""
        ...


# ── 1. LocalManualAdapter — 현재 운영 모드 (카카오뱅크/통장 수동) ────────


class LocalManualAdapter:
    """카카오뱅크 직접 입금 + PO 수동 확인. ADR 0007 트리거 충족 전 기본값."""

    provider_name = "local-manual"

    def charge(
        self,
        api_key: str,
        amount_krw: int,
        *,
        description: str = "",
        idempotency_key: str | None = None,
    ) -> PaymentResult:
        # 실제 결제는 PO가 수동 확인 — 여기서는 청구서만 생성
        logger.info(
            "수동 청구 발생: key=%s amount=%d description=%s",
            api_key[:8] + "...",
            amount_krw,
            description[:50],
        )
        return PaymentResult(
            ok=True,
            provider=self.provider_name,
            transaction_id=f"manual_{int(datetime.now().timestamp())}",
            amount_krw=amount_krw,
            receipt_url=None,
            error=None,
        )

    def subscribe(
        self,
        api_key: str,
        plan_name: str,
        monthly_amount_krw: int,
        *,
        billing_day: int = 1,
    ) -> SubscriptionResult:
        logger.info(
            "수동 구독 등록: key=%s plan=%s monthly=%d",
            api_key[:8] + "...",
            plan_name,
            monthly_amount_krw,
        )
        return SubscriptionResult(
            ok=True,
            provider=self.provider_name,
            subscription_id=f"manual_sub_{int(datetime.now().timestamp())}",
            plan_name=plan_name,
            monthly_amount_krw=monthly_amount_krw,
            next_billing_at=None,  # PO가 매월 카카오뱅크 입금 확인
            error=None,
        )

    def cancel_subscription(self, api_key: str, subscription_id: str) -> bool:
        logger.info("수동 구독 해지: key=%s sub=%s", api_key[:8] + "...", subscription_id)
        return True

    def issue_tax_invoice(
        self,
        api_key: str,
        amount_krw: int,
        *,
        business_no: str,
        period: str,
    ) -> str | None:
        # PO 수동 발행 — billing.render_invoice_pdf로 영수증만 생성
        logger.warning(
            "세금계산서 수동 발행 필요: PO 직접 작성 (사업자 등록 후 자동화). "
            "amount=%d biz=%s period=%s",
            amount_krw,
            business_no,
            period,
        )
        return None  # 수동 발행이라 URL 없음

    def is_available(self) -> bool:
        return True  # 항상 가능 (PO 직접 처리)


# ── 2. PortOneAdapter — ADR 0007 트리거 후 활성화 ──────────────────────


class PortOneAdapter:
    """포트원 PG 어댑터. ADR 0007 트리거 (사업자 등록 + 통신판매 신고 + 포트원 가맹) 충족 시 활성화.

    환경변수:
    - KORMARC_PORTONE_API_KEY (필수)
    - KORMARC_PORTONE_API_SECRET (필수)
    - KORMARC_PORTONE_CHANNEL_KEY (선택, 멀티 PG 시)
    - KORMARC_BIZ_NO (세금계산서 발행자 사업자번호)

    실 SDK 통합은 트리거 후 도입 (현재는 인터페이스 보존).
    """

    provider_name = "portone"

    def __init__(self) -> None:
        self.api_key = os.getenv("KORMARC_PORTONE_API_KEY")
        self.api_secret = os.getenv("KORMARC_PORTONE_API_SECRET")
        self.channel_key = os.getenv("KORMARC_PORTONE_CHANNEL_KEY")
        self.biz_no = os.getenv("KORMARC_BIZ_NO")

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def _not_implemented(self, op: str) -> Any:
        raise NotImplementedError(
            f"PortOneAdapter.{op}는 ADR 0007 트리거 충족 후 구현. "
            "현재 사용하려면 KORMARC_PG_PROVIDER=local로 폴백."
        )

    def charge(
        self,
        api_key: str,
        amount_krw: int,
        *,
        description: str = "",
        idempotency_key: str | None = None,
    ) -> PaymentResult:
        if not self.is_available():
            return PaymentResult(
                ok=False,
                provider=self.provider_name,
                amount_krw=amount_krw,
                error="PortOne API key not configured (ADR 0007 트리거 미충족)",
            )
        # TODO ADR 0007 활성화 후: portone-server-sdk Python 통합
        # from portone_server_sdk import PortOneClient
        # client = PortOneClient(self.api_secret)
        # response = client.payment.pay_with_billing_key(...)
        return self._not_implemented("charge")

    def subscribe(
        self,
        api_key: str,
        plan_name: str,
        monthly_amount_krw: int,
        *,
        billing_day: int = 1,
    ) -> SubscriptionResult:
        if not self.is_available():
            return SubscriptionResult(
                ok=False,
                provider=self.provider_name,
                plan_name=plan_name,
                monthly_amount_krw=monthly_amount_krw,
                error="PortOne not configured",
            )
        return self._not_implemented("subscribe")

    def cancel_subscription(self, api_key: str, subscription_id: str) -> bool:
        if not self.is_available():
            return False
        return self._not_implemented("cancel_subscription")

    def issue_tax_invoice(
        self,
        api_key: str,
        amount_krw: int,
        *,
        business_no: str,
        period: str,
    ) -> str | None:
        if not self.is_available():
            return None
        return self._not_implemented("issue_tax_invoice")


# ── 3. StripeAdapter — ADR 0009 §33 미국 활성화 시 ───────────────────


class StripeAdapter:
    """Stripe 어댑터 — 미국 동아시아 컬렉션 활성화 시. ADR 0009 트리거 후."""

    provider_name = "stripe"

    def __init__(self) -> None:
        self.api_key = os.getenv("KORMARC_STRIPE_API_KEY")

    def is_available(self) -> bool:
        # ADR 0009 §33 inactive 보호
        if os.getenv("KORMARC_EAST_ASIAN_ACTIVATED") != "1":
            return False
        return bool(self.api_key)

    def charge(
        self,
        api_key: str,
        amount_krw: int,
        *,
        description: str = "",
        idempotency_key: str | None = None,
    ) -> PaymentResult:
        return PaymentResult(
            ok=False,
            provider=self.provider_name,
            error="Stripe inactive (ADR 0009 트리거 미충족)",
        )

    def subscribe(
        self,
        api_key: str,
        plan_name: str,
        monthly_amount_krw: int,
        *,
        billing_day: int = 1,
    ) -> SubscriptionResult:
        return SubscriptionResult(
            ok=False,
            provider=self.provider_name,
            plan_name=plan_name,
            error="Stripe inactive",
        )

    def cancel_subscription(self, api_key: str, subscription_id: str) -> bool:
        return False

    def issue_tax_invoice(
        self,
        api_key: str,
        amount_krw: int,
        *,
        business_no: str,
        period: str,
    ) -> str | None:
        return None  # 미국은 W-9·1099로 별도


# ── 어댑터 선택 (단일 진입점) ────────────────────────────────────────


_REGISTRY: dict[str, type[PaymentAdapter]] = {
    "local": LocalManualAdapter,
    "portone": PortOneAdapter,
    "stripe": StripeAdapter,
}


def get_adapter(provider: str | None = None) -> PaymentAdapter:
    """현재 활성 결제 어댑터 반환.

    선택 로직:
    1. provider 인자 직접 지정 시 그것 (테스트용)
    2. 환경변수 KORMARC_PG_PROVIDER
    3. 폴백: local (수동 입금)
    """
    name = (provider or os.getenv("KORMARC_PG_PROVIDER") or "local").lower()
    cls = _REGISTRY.get(name, LocalManualAdapter)
    adapter = cls()
    if not adapter.is_available():
        if name != "local":
            logger.warning("결제 어댑터 %s 사용 불가 (트리거 미충족) — local로 폴백", name)
        return LocalManualAdapter()
    return adapter


def estimate_total_for_period(records_count: int) -> int:
    """기간 사용량 → 권당 과금 합계."""
    return records_count * PRICE_PER_RECORD_KRW


__all__ = [
    "LocalManualAdapter",
    "PaymentAdapter",
    "PaymentResult",
    "PortOneAdapter",
    "StripeAdapter",
    "SubscriptionResult",
    "estimate_total_for_period",
    "get_adapter",
]
