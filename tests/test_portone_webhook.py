"""포트원 webhook 처리 모듈 테스트."""

from __future__ import annotations

import hashlib
import hmac

from kormarc_auto.server.portone_webhook import (
    WebhookEvent,
    handle_event,
    parse_event,
    verify_signature,
)


def test_verify_signature_passes_with_correct_hmac():
    secret = "test-secret-key"
    payload = b'{"type":"Transaction.Paid","data":{}}'
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, expected, secret=secret) is True


def test_verify_signature_fails_with_wrong_hmac():
    payload = b'{"type":"Transaction.Paid"}'
    assert verify_signature(payload, "wrong_sig_xyz", secret="test-secret") is False


def test_verify_signature_fails_when_secret_missing(monkeypatch):
    monkeypatch.delenv("KORMARC_PORTONE_WEBHOOK_SECRET", raising=False)
    assert verify_signature(b"{}", "anysig") is False


def test_parse_transaction_paid_event():
    payload = {
        "type": "Transaction.Paid",
        "data": {
            "transactionId": "tx_123abc",
            "amount": {"total": 50000},
            "customerKey": "user_42",
        },
    }
    event = parse_event(payload)
    assert event.event_type == "Transaction.Paid"
    assert event.transaction_id == "tx_123abc"
    assert event.amount_krw == 50000
    assert event.customer_key == "user_42"
    assert event.is_payment is True
    assert event.is_subscription is False


def test_parse_billing_key_issued_event():
    payload = {
        "type": "BillingKey.Issued",
        "data": {
            "billingKey": "bk_xyz789",
            "customerKey": "user_99",
        },
    }
    event = parse_event(payload)
    assert event.event_type == "BillingKey.Issued"
    assert event.subscription_id == "bk_xyz789"
    assert event.is_subscription is True
    assert event.is_payment is False


def test_handle_event_returns_ok():
    event = WebhookEvent(
        event_type="Transaction.Paid",
        transaction_id="tx_001",
        subscription_id=None,
        amount_krw=30000,
        customer_key="user_1",
        raw={},
    )
    result = handle_event(event)
    assert result["ok"] is True
    assert result["transaction_id"] == "tx_001"
    assert result["received"] == "Transaction.Paid"
