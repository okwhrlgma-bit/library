"""포트원 webhook 처리 stub — ADR 0007 트리거 후 활성화.

포트원 PG → 우리 서버: 결제 완료·취소·환불·정기결제 갱신 알림.
HMAC-SHA256 서명 검증 필수 (KORMARC_PORTONE_WEBHOOK_SECRET).

이벤트 타입 (포트원 v2):
- Transaction.Paid — 1회성 결제 완료
- Transaction.Cancelled — 결제 취소·환불
- BillingKey.Issued — 정기결제 등록 완료
- BillingKey.Deleted — 정기결제 해지

사업자 등록 후 Phase 3 (`/webhook/portone` 엔드포인트) 활성화.
현재는 인터페이스 + 검증 로직만 보존.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WebhookEvent:
    """포트원 webhook 이벤트 (정규화)."""

    event_type: str  # Transaction.Paid·Transaction.Cancelled·BillingKey.* 등
    transaction_id: str | None
    subscription_id: str | None
    amount_krw: int
    customer_key: str | None  # 사용자 식별 (api_key 또는 이메일)
    raw: dict[str, Any]

    @property
    def is_payment(self) -> bool:
        return self.event_type.startswith("Transaction.")

    @property
    def is_subscription(self) -> bool:
        return self.event_type.startswith("BillingKey.")


def verify_signature(
    payload: bytes,
    signature_header: str,
    *,
    secret: str | None = None,
) -> bool:
    """포트원 webhook HMAC-SHA256 서명 검증.

    Args:
        payload: HTTP body (raw bytes)
        signature_header: HTTP 헤더 `webhook-signature` 값
        secret: webhook secret (미지정 시 KORMARC_PORTONE_WEBHOOK_SECRET 환경변수)

    Returns:
        검증 통과 여부.
    """
    secret = secret or os.getenv("KORMARC_PORTONE_WEBHOOK_SECRET")
    if not secret:
        logger.warning("KORMARC_PORTONE_WEBHOOK_SECRET 미설정 — 검증 불가 (ADR 0007 미충족)")
        return False
    if not signature_header:
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header.lower())


def parse_event(payload: dict[str, Any]) -> WebhookEvent:
    """포트원 webhook payload → WebhookEvent.

    포트원 v2 스펙 정합 (Transaction·BillingKey 이벤트).
    """
    event_type = payload.get("type") or payload.get("eventType") or ""
    data = payload.get("data") or payload

    return WebhookEvent(
        event_type=event_type,
        transaction_id=data.get("transactionId") or data.get("paymentId"),
        subscription_id=data.get("billingKey") or data.get("subscriptionId"),
        amount_krw=int(data.get("amount", {}).get("total", 0))
        if isinstance(
            data.get("amount"),
            dict,
        )
        else int(data.get("amount", 0) or 0),
        customer_key=data.get("customerKey") or data.get("customerId"),
        raw=payload,
    )


def handle_event(event: WebhookEvent) -> dict[str, Any]:
    """이벤트 분기 처리 stub — ADR 0007 트리거 후 실 로직.

    현재: logger 기록 + idempotency 키 응답.
    후속: usage.py·billing.py 통합 (구독 상태 갱신·DB 업데이트).
    """
    logger.info(
        "포트원 webhook 수신: type=%s tx=%s sub=%s amount=%d customer=%s",
        event.event_type,
        event.transaction_id,
        event.subscription_id,
        event.amount_krw,
        event.customer_key,
    )

    # ADR 0007 트리거 후 실 로직:
    # if event.event_type == "Transaction.Paid":
    #     usage.mark_paid(event.customer_key, event.amount_krw, event.transaction_id)
    # elif event.event_type == "Transaction.Cancelled":
    #     usage.mark_refunded(event.transaction_id)
    # elif event.event_type == "BillingKey.Issued":
    #     billing.register_subscription(event.customer_key, event.subscription_id)

    return {
        "ok": True,
        "received": event.event_type,
        "transaction_id": event.transaction_id,
    }


__all__ = [
    "WebhookEvent",
    "handle_event",
    "parse_event",
    "verify_signature",
]
