"""FastAPI 서버 단위 테스트 (TestClient)."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# 테스트용 사용량 DB·로그를 임시 폴더로
_TMPDIR = Path(tempfile.mkdtemp(prefix="kormarc_test_"))
os.environ["KORMARC_USAGE_DB"] = str(_TMPDIR / "usage.json")
os.environ["KORMARC_USAGE_LOG"] = str(_TMPDIR / "usage.jsonl")
os.environ["KORMARC_CORS_ORIGINS"] = "*"


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from kormarc_auto.server.app import create_app

    app = create_app()
    return TestClient(app)


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_pricing(client):
    r = client.get("/pricing")
    assert r.status_code == 200
    body = r.json()
    assert body["price_per_record_krw"] > 0
    assert "free_quota_default" in body


def test_isbn_requires_api_key(client):
    r = client.post("/isbn", json={"isbn": "9788936434120"})
    assert r.status_code == 401


def test_isbn_short_key_rejected(client):
    r = client.post("/isbn", json={"isbn": "9788936434120"}, headers={"X-API-Key": "x"})
    assert r.status_code == 401


@patch("kormarc_auto.server.app.aggregate_by_isbn")
def test_isbn_success_flow(mock_agg, client):
    mock_agg.return_value = {
        "isbn": "9788936434120",
        "title": "작별하지 않는다",
        "author": "한강",
        "publisher": "창비",
        "publication_year": "2021",
        "kdc": "813.7",
        "sources": ["nl_korea"],
        "source_map": {"title": "nl_korea"},
        "confidence": 0.95,
        "attributions": [],
    }
    r = client.post(
        "/isbn",
        json={"isbn": "9788936434120"},
        headers={"X-API-Key": "test_key_at_least_8"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["title"] == "작별하지 않는다"
    assert body["mrc_base64"] is not None
    assert body["usage"]["used"] >= 1


@patch("kormarc_auto.server.app.search_by_query")
def test_search_returns_candidates(mock_search, client):
    mock_search.return_value = [
        {"isbn": "9788936434120", "title": "T", "author": "A", "source": "nl_korea", "confidence": 0.9}
    ]
    r = client.post(
        "/search",
        json={"query": "한강", "limit": 5},
        headers={"X-API-Key": "test_key_at_least_8"},
    )
    assert r.status_code == 200
    assert len(r.json()["candidates"]) == 1


def test_usage_endpoint(client):
    r = client.get("/usage", headers={"X-API-Key": "newkey_xxx_yyy"})
    assert r.status_code == 200
    body = r.json()
    assert body["free_quota"] >= 1
    assert body["used"] >= 0
    assert body["remaining"] >= 0


def test_signup_endpoint_issues_key(client):
    """무료 체험 자동 발급 — 인증 없이 누구나."""
    r = client.post("/signup", json={"email": "librarian@example.com", "library_name": "테스트도서관"})
    assert r.status_code == 200
    body = r.json()
    assert body["api_key"].startswith("kma_")
    assert len(body["api_key"]) > 20
    assert body["free_quota"] >= 1
    assert "ui_url" in body
    assert "api_url" in body


def test_signup_email_validation(client):
    """이메일 너무 짧으면 422."""
    r = client.post("/signup", json={"email": "x"})
    assert r.status_code == 422
