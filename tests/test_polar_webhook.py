"""Polar webhook 처리 모듈 테스트 (Cycle 1260·AP-TAUTOLOGICAL-TEST-001 회복).

대상: landing/api/webhook.py (Vercel serverless)
- _verify_polar: HMAC SHA256 timing-safe 검증 (Polar 표준 t=,v1=)
- _classify_polar_event: 이벤트 분류 (paid·refund·license·other)
- handler: BaseHTTPRequestHandler (do_GET·do_POST·401·400·200)

본 테스트 = helper 함수 단위 검증·BaseHTTPRequestHandler 직접 호출은 mock 부담 ↑·다음 cycle.
"""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
import sys
from pathlib import Path

import pytest


# webhook.py module load (Vercel serverless·sys.path 외)
_WEBHOOK_PATH = (
    Path(__file__).resolve().parents[1] / "landing" / "api" / "webhook.py"
)
_spec = importlib.util.spec_from_file_location("polar_webhook", _WEBHOOK_PATH)
_module = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["polar_webhook"] = _module
_spec.loader.exec_module(_module)  # type: ignore[union-attr]

_verify_polar = _module._verify_polar
_classify_polar_event = _module._classify_polar_event


# ═══════════════════════════════════════════════════════════════
# 1. _verify_polar HMAC SHA256 timing-safe (Polar 표준 t=,v1=)
# ═══════════════════════════════════════════════════════════════


def _make_polar_signature(secret: str, payload: bytes, timestamp: str = "1700000000") -> str:
    """Polar 표준 헤더 = t=timestamp,v1=hex_sig."""
    signed = f"{timestamp}.".encode("utf-8") + payload
    sig = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


def test_verify_polar_match():
    """정확한 HMAC SHA256 = True."""
    secret = "polar_test_secret"
    payload = b'{"type":"order.created"}'
    header = _make_polar_signature(secret, payload)
    assert _verify_polar(payload, header, secret) is True


def test_verify_polar_mismatch():
    """잘못된 sig = False (fail-secure)."""
    secret = "polar_test_secret"
    payload = b'{"type":"order.created"}'
    bad_header = "t=1700000000,v1=" + "0" * 64
    assert _verify_polar(payload, bad_header, secret) is False


def test_verify_polar_empty_inputs():
    """빈 입력 가드 3중 = 모두 False."""
    assert _verify_polar(b"", "t=1,v1=abc", "secret") is False
    assert _verify_polar(b"payload", "", "secret") is False
    assert _verify_polar(b"payload", "t=1,v1=abc", "") is False


def test_verify_polar_missing_timestamp():
    """t= 누락 = False."""
    payload = b'{"type":"test"}'
    header = "v1=" + "a" * 64  # t= 없음
    assert _verify_polar(payload, header, "secret") is False


def test_verify_polar_missing_signature():
    """v1= 누락 = False."""
    payload = b'{"type":"test"}'
    header = "t=1700000000"  # v1= 없음
    assert _verify_polar(payload, header, "secret") is False


def test_verify_polar_malformed_header():
    """key=value 형식 X = False."""
    payload = b'{"type":"test"}'
    assert _verify_polar(payload, "garbage_no_equals", "secret") is False


# ═══════════════════════════════════════════════════════════════
# 2. _classify_polar_event 이벤트 분류
# ═══════════════════════════════════════════════════════════════


def test_classify_polar_event_paid():
    """결제 완료 3 이벤트."""
    assert _classify_polar_event("order.created") == "paid"
    assert _classify_polar_event("subscription.created") == "paid"
    assert _classify_polar_event("subscription.uncanceled") == "paid"


def test_classify_polar_event_refund():
    """환불 4 이벤트."""
    assert _classify_polar_event("order.refunded") == "refund"
    assert _classify_polar_event("subscription.canceled") == "refund"
    assert _classify_polar_event("subscription.revoked") == "refund"
    assert _classify_polar_event("refund.created") == "refund"


def test_classify_polar_event_license():
    """benefit_grant.* = license."""
    assert _classify_polar_event("benefit_grant.created") == "license"
    assert _classify_polar_event("benefit_grant.updated") == "license"
    assert _classify_polar_event("benefit_grant.revoked") == "license"


def test_classify_polar_event_other():
    """미지정 이벤트 = other."""
    assert _classify_polar_event("subscription.updated") == "other"
    assert _classify_polar_event("checkout.created") == "other"
    assert _classify_polar_event("unknown.event") == "other"
    assert _classify_polar_event("") == "other"


# ═══════════════════════════════════════════════════════════════
# 3. handler 클래스 import 검증 (BaseHTTPRequestHandler)
# ═══════════════════════════════════════════════════════════════


def test_handler_class_exists():
    """handler 클래스 = Vercel Python serverless 표준."""
    from http.server import BaseHTTPRequestHandler

    assert hasattr(_module, "handler")
    assert issubclass(_module.handler, BaseHTTPRequestHandler)
    assert hasattr(_module.handler, "do_GET")
    assert hasattr(_module.handler, "do_POST")
