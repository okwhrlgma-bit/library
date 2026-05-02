"""POST /webhook/portone FastAPI route 테스트 (HMAC 검증 + 분기)."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

_TMPDIR = Path(tempfile.mkdtemp(prefix="kormarc_webhook_test_"))
os.environ["KORMARC_USAGE_DB"] = str(_TMPDIR / "usage.json")
os.environ["KORMARC_USAGE_LOG"] = str(_TMPDIR / "usage.jsonl")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from kormarc_auto.server.app import create_app

    return TestClient(create_app())


def test_webhook_portone_invalid_signature_returns_401(client, monkeypatch):
    monkeypatch.setenv("KORMARC_PORTONE_WEBHOOK_SECRET", "test-secret")
    payload = b'{"type":"Transaction.Paid","data":{}}'
    r = client.post(
        "/webhook/portone",
        content=payload,
        headers={"webhook-signature": "wrong_sig"},
    )
    assert r.status_code == 401
    assert "signature" in r.json()["detail"].lower()


def test_webhook_portone_no_secret_returns_401(client, monkeypatch):
    """KORMARC_PORTONE_WEBHOOK_SECRET 미설정 시 401 (ADR 0007 트리거 미충족)."""
    monkeypatch.delenv("KORMARC_PORTONE_WEBHOOK_SECRET", raising=False)
    payload = b'{"type":"Transaction.Paid"}'
    r = client.post("/webhook/portone", content=payload, headers={"webhook-signature": "abc"})
    assert r.status_code == 401


def test_webhook_portone_valid_signature_processes(client, monkeypatch):
    secret = "test-secret-key"
    monkeypatch.setenv("KORMARC_PORTONE_WEBHOOK_SECRET", secret)
    payload = json.dumps(
        {
            "type": "Transaction.Paid",
            "data": {
                "transactionId": "tx_test_001",
                "amount": {"total": 50000},
                "customerKey": "user_test",
            },
        }
    ).encode("utf-8")
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    r = client.post(
        "/webhook/portone",
        content=payload,
        headers={"webhook-signature": sig},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["received"] == "Transaction.Paid"
    assert data["transaction_id"] == "tx_test_001"
