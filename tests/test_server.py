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
        {
            "isbn": "9788936434120",
            "title": "T",
            "author": "A",
            "source": "nl_korea",
            "confidence": 0.9,
        }
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
    r = client.post(
        "/signup", json={"email": "librarian@example.com", "library_name": "테스트도서관"}
    )
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


def test_signup_invalid_email_format(client):
    """이메일 형식 오류는 429 (signup error)."""
    r = client.post("/signup", json={"email": "notanemail"})
    assert r.status_code == 429


def test_feedback_endpoint(client):
    """피드백 저장 엔드포인트."""
    r = client.post(
        "/feedback",
        json={"rating": 4, "comment": "사용 편함", "category": "ux"},
        headers={"X-API-Key": "fb_test_key_xxx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "key_hash" in body


def test_feedback_requires_content(client):
    """rating·comment 둘 다 비면 400."""
    r = client.post(
        "/feedback",
        json={"rating": 0, "comment": ""},
        headers={"X-API-Key": "fb_test_key_xxx"},
    )
    assert r.status_code == 400


def test_admin_stats_requires_admin_key(client):
    """일반 키는 403."""
    r = client.get("/admin/stats", headers={"X-API-Key": "regular_user_key_xxx"})
    assert r.status_code == 403


def test_admin_stats_with_admin_key(client, monkeypatch):
    """관리자 키면 통계 반환."""
    monkeypatch.setenv("KORMARC_ADMIN_KEYS", "admin_key_for_test_xxx")
    r = client.get("/admin/stats", headers={"X-API-Key": "admin_key_for_test_xxx"})
    assert r.status_code == 200
    body = r.json()
    assert "users" in body
    assert "usage_24h" in body
    assert "revenue_estimate_30d_krw" in body


def test_migrate_from_kolas_public(client):
    """KOLAS 종료 마이그레이션 안내 — 인증 없이 공개."""
    r = client.get("/migrate-from-kolas")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["kolas_eos"] == "2026-12-31"
    assert "key_points" in body
    assert len(body["compatible_systems"]) >= 3
    assert "po_contact" in body


def test_batch_vendor_requires_key(client):
    """B2B 일괄 — 키 없으면 401."""
    r = client.post("/batch-vendor", json={"isbns": ["9788936434120"]})
    assert r.status_code == 401


def test_batch_vendor_rejects_empty(client):
    r = client.post(
        "/batch-vendor",
        json={"isbns": []},
        headers={"X-API-Key": "vendor_test_key_xxxxxxx"},
    )
    assert r.status_code == 400


def test_batch_vendor_rejects_too_many(client):
    r = client.post(
        "/batch-vendor",
        json={"isbns": ["9788936434120"] * 1001},
        headers={"X-API-Key": "vendor_test_key_xxxxxxx"},
    )
    assert r.status_code == 400


@patch("kormarc_auto.server.app.aggregate_by_isbn")
def test_batch_vendor_success(mock_agg, client):
    """B2B 일괄 — 정상 케이스 (1건)."""
    mock_agg.return_value = {
        "isbn": "9788936434120",
        "title": "테스트",
        "author": "저자",
        "publisher": "출판사",
        "pub_year": "2024",
        "pages": "200",
        "language": "kor",
        "kdc": "813.7",
        "confidence": 0.9,
        "sources": ["nl_korea"],
    }
    r = client.post(
        "/batch-vendor",
        json={"isbns": ["9788936434120"], "agency": "VENDOR1"},
        headers={"X-API-Key": "vendor_test_key_xxxxxxx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["total"] == 1
    assert body["success"] == 1
    assert body["results"][0]["mrc_base64"]


def test_billing_monthly_requires_admin(client, monkeypatch):
    """월간 청구는 관리자 키만."""
    monkeypatch.setenv("KORMARC_ADMIN_KEYS", "admin_only_zzz_xxx")
    r = client.get(
        "/billing/monthly/2026/4",
        headers={"X-API-Key": "regular_user_key_xxx"},
    )
    assert r.status_code == 403


def test_billing_monthly_with_admin(client, monkeypatch):
    """관리자 키로 월간 집계 — 빈 로그라도 200."""
    monkeypatch.setenv("KORMARC_ADMIN_KEYS", "admin_only_zzz_xxx")
    r = client.get(
        "/billing/monthly/2026/4",
        headers={"X-API-Key": "admin_only_zzz_xxx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["year"] == 2026
    assert body["month"] == 4
    assert "total_records" in body


def test_account_export_requires_key(client):
    """본인 데이터 다운로드 — 키 필수 (인증)."""
    r = client.get("/account/export")
    assert r.status_code == 401


def test_account_export_returns_data(client):
    """본인 데이터 다운로드 — 키 있으면 자기 데이터만."""
    r = client.get(
        "/account/export",
        headers={"X-API-Key": "exporter_test_key_xxxxxxx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "exported_at" in body
    assert "key_hash" in body
    assert "usage_log" in body
    assert "feedback" in body


def test_account_delete_requires_key(client):
    r = client.delete("/account/delete")
    assert r.status_code == 401


def test_account_delete_returns_count(client):
    """본인 데이터 영구 삭제."""
    # 먼저 사용량 1건 발생
    r = client.get(
        "/usage",
        headers={"X-API-Key": "deleter_test_key_xxxxxxx"},
    )
    assert r.status_code == 200

    r = client.delete(
        "/account/delete",
        headers={"X-API-Key": "deleter_test_key_xxxxxxx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "deleted" in body
    assert isinstance(body["deleted"]["log_lines"], int)


def test_deposit_form_requires_key(client):
    r = client.post(
        "/legal/deposit-form",
        json={"book_data": {"title": "테스트"}},
    )
    assert r.status_code == 401


def test_deposit_form_success(client):
    pytest.importorskip("reportlab")
    r = client.post(
        "/legal/deposit-form",
        json={
            "book_data": {
                "title": "사서 자료집",
                "author": "○○사서",
                "publisher": "테스트출판",
                "publication_year": "2026",
                "isbn": "9788912345678",
            },
            "submitter_name": "○○사서",
            "publisher_address": "서울 강남구",
            "consents_preservation": True,
        },
        headers={"X-API-Key": "depositor_test_key_xxxxxxx"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["copies"] == 1  # 보존 동의 → 1부
    assert body["deadline"]
    assert body["pdf_base64"]


def test_deposit_form_rejects_no_title(client):
    r = client.post(
        "/legal/deposit-form",
        json={"book_data": {"author": "x"}},
        headers={"X-API-Key": "depositor_test_key_yyyyyyy"},
    )
    assert r.status_code == 400
