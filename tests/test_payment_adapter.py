"""결제 PG 어댑터 단위 테스트 — 캐시카우 자동화 1순위."""

from __future__ import annotations

from kormarc_auto.server.payment_adapter import (
    LocalManualAdapter,
    PaymentResult,
    PortOneAdapter,
    StripeAdapter,
    SubscriptionResult,
    estimate_total_for_period,
    get_adapter,
)


def test_local_manual_charge_succeeds():
    a = LocalManualAdapter()
    r = a.charge("kma_xxxx", 30000, description="작은도서관 4월")
    assert r.ok
    assert r.provider == "local-manual"
    assert r.amount_krw == 30000
    assert r.transaction_id and r.transaction_id.startswith("manual_")


def test_local_manual_subscribe():
    a = LocalManualAdapter()
    s = a.subscribe("kma_xxxx", "월정액(작은도서관)", 30000)
    assert s.ok
    assert s.subscription_id
    assert s.monthly_amount_krw == 30000


def test_local_manual_cancel():
    a = LocalManualAdapter()
    assert a.cancel_subscription("kma_xxxx", "manual_sub_1") is True


def test_local_manual_tax_invoice_returns_none():
    """수동 발행은 URL 없음 (PO 직접 작성)."""
    a = LocalManualAdapter()
    url = a.issue_tax_invoice("kma_xxxx", 30000, business_no="000-00-00000", period="2026-04")
    assert url is None


def test_local_manual_always_available():
    assert LocalManualAdapter().is_available() is True


def test_portone_unavailable_without_keys(monkeypatch):
    monkeypatch.delenv("KORMARC_PORTONE_API_KEY", raising=False)
    monkeypatch.delenv("KORMARC_PORTONE_API_SECRET", raising=False)
    a = PortOneAdapter()
    assert a.is_available() is False
    r = a.charge("kma_xxxx", 30000)
    assert r.ok is False
    assert "ADR 0007" in (r.error or "")


def test_portone_charge_raises_when_keys_set_but_not_implemented(monkeypatch):
    """키만 설정하고 실제 SDK 미통합 — NotImplementedError."""
    monkeypatch.setenv("KORMARC_PORTONE_API_KEY", "test_key")
    monkeypatch.setenv("KORMARC_PORTONE_API_SECRET", "test_secret")
    a = PortOneAdapter()
    assert a.is_available() is True
    import pytest

    with pytest.raises(NotImplementedError, match="ADR 0007"):
        a.charge("kma_xxxx", 30000)


def test_stripe_inactive_by_default(monkeypatch):
    """ADR 0009 §33 inactive 보호 — KORMARC_EAST_ASIAN_ACTIVATED 없으면 unavailable."""
    monkeypatch.delenv("KORMARC_EAST_ASIAN_ACTIVATED", raising=False)
    monkeypatch.setenv("KORMARC_STRIPE_API_KEY", "sk_test_xxx")
    a = StripeAdapter()
    assert a.is_available() is False


def test_stripe_charge_returns_inactive_error(monkeypatch):
    monkeypatch.delenv("KORMARC_EAST_ASIAN_ACTIVATED", raising=False)
    a = StripeAdapter()
    r = a.charge("kma_xxxx", 30000)
    assert r.ok is False
    assert "inactive" in (r.error or "").lower() or "ADR 0009" in (r.error or "")


def test_get_adapter_default_to_local(monkeypatch):
    monkeypatch.delenv("KORMARC_PG_PROVIDER", raising=False)
    a = get_adapter()
    assert isinstance(a, LocalManualAdapter)


def test_get_adapter_portone_falls_back_to_local_when_no_keys(monkeypatch):
    """portone 선택 + 키 없음 → local 폴백 (graceful)."""
    monkeypatch.setenv("KORMARC_PG_PROVIDER", "portone")
    monkeypatch.delenv("KORMARC_PORTONE_API_KEY", raising=False)
    monkeypatch.delenv("KORMARC_PORTONE_API_SECRET", raising=False)
    a = get_adapter()
    assert isinstance(a, LocalManualAdapter)


def test_get_adapter_explicit_local_arg():
    a = get_adapter("local")
    assert isinstance(a, LocalManualAdapter)


def test_estimate_total_for_period():
    assert estimate_total_for_period(0) == 0
    assert estimate_total_for_period(50) == 5000  # 50 x 100 KRW
    assert estimate_total_for_period(1000) == 100000


def test_payment_result_dataclass():
    r = PaymentResult(ok=True, provider="local-manual", amount_krw=100)
    assert r.ok and r.amount_krw == 100


def test_subscription_result_dataclass():
    s = SubscriptionResult(
        ok=True,
        provider="local-manual",
        plan_name="작은",
        monthly_amount_krw=30000,
    )
    assert s.ok and s.plan_name == "작은"
