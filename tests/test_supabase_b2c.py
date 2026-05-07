"""Cycle 70 — Supabase B2C Auth 회귀.

ADR 0050 정합·B2C 한정·헌법 §3 (env only)·invariant 12 (자관 데이터 = 사서 컴퓨터).
"""

from __future__ import annotations

import pytest

from kormarc_auto.auth import (
    SUPABASE_FREE_MAU_LIMIT,
    AuthState,
    SupabaseClient,
    is_b2c_auth_available,
)
from kormarc_auto.auth.supabase_client import (
    USER_PROFILE_SCHEMA,
    get_subscription_features,
    require_b2c_subscription,
)


class TestSupabaseClient:
    def test_no_env_returns_unconfigured(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
        client = SupabaseClient()
        assert client.configured is False

    def test_with_env_configured(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_ANON_KEY", "test_anon_key")
        client = SupabaseClient()
        assert client.configured is True

    def test_status_returns_dict(self):
        client = SupabaseClient(url="https://x.co", anon_key="key")
        status = client.status()
        assert "configured" in status
        assert "data_locality" in status
        assert "사서 컴퓨터" in status["data_locality"]

    def test_no_hardcoded_keys_in_module(self):
        """헌법 §3 = API 키 하드코딩 X·env only."""
        import inspect

        from kormarc_auto.auth import supabase_client as mod

        src = inspect.getsource(mod)
        # sk_·sb_·실제 키 패턴 = 0건 보장
        assert "sk-ant-api03-" not in src
        assert "sbp_" not in src
        assert "sb-" not in src.lower() or "sbp_" not in src.lower()

    def test_is_b2c_auth_available_no_env(self, monkeypatch):
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
        assert is_b2c_auth_available() is False

    def test_is_b2c_auth_available_with_env(self, monkeypatch):
        monkeypatch.setenv("SUPABASE_URL", "https://x.co")
        monkeypatch.setenv("SUPABASE_ANON_KEY", "k")
        assert is_b2c_auth_available() is True


class TestAuthState:
    def test_state_immutable(self):
        from dataclasses import FrozenInstanceError

        state = AuthState(
            is_authenticated=True,
            user_id="u1",
            email="x@example.com",
            library_type="small",
            subscription_tier="personal",
        )
        with pytest.raises(FrozenInstanceError):
            state.is_authenticated = False  # type: ignore[misc]


class TestSubscriptionGate:
    def test_free_tier_gate(self):
        state = AuthState(True, "u1", "x@y.com", "small", "free")
        assert require_b2c_subscription(state) is False

    def test_personal_tier_passes(self):
        state = AuthState(True, "u1", "x@y.com", "small", "personal")
        assert require_b2c_subscription(state) is True

    def test_pro_tier_passes(self):
        state = AuthState(True, "u1", "x@y.com", "small", "pro")
        assert require_b2c_subscription(state) is True

    def test_founding_tier_passes(self):
        state = AuthState(True, "u1", "x@y.com", "small", "founding")
        assert require_b2c_subscription(state) is True

    def test_unauthenticated_blocked(self):
        state = AuthState(False, None, None, None, "free")
        assert require_b2c_subscription(state) is False


class TestSubscriptionFeatures:
    def test_free_features(self):
        f = get_subscription_features("free")
        assert f["monthly_records"] == 50
        assert f["monthly_krw"] == 0
        assert f["ai_classification"] is False

    def test_personal_features(self):
        f = get_subscription_features("personal")
        assert f["monthly_records"] == -1  # 무제한
        assert f["monthly_krw"] == 9_900
        assert f["ai_classification"] is False

    def test_pro_features(self):
        f = get_subscription_features("pro")
        assert f["monthly_records"] == -1
        assert f["monthly_krw"] == 19_900
        assert f["ai_classification"] is True
        assert f["ocr_cover"] is True
        assert f["vernacular_880"] is True

    def test_founding_perpetual_50pct(self):
        f = get_subscription_features("founding")
        assert f["monthly_krw"] == 4_950
        assert f.get("perpetual_50pct") is True

    def test_unknown_tier_defaults_to_free(self):
        f = get_subscription_features("unknown")
        assert f["monthly_records"] == 50
        assert f["monthly_krw"] == 0


class TestConstitutionInvariants:
    """헌법 §3 (env only)·§14 (자관 데이터 = 사서 컴퓨터·invariant 12) 정합."""

    def test_no_self_storage_of_jagwan_mrc(self):
        """자관 .mrc 저장 = 절대 X (헌법 §14·invariant 12)."""
        # USER_PROFILE_SCHEMA = 자관 .mrc 필드 X
        for field in USER_PROFILE_SCHEMA:
            assert ".mrc" not in field.lower()
            assert "marc_record" not in field.lower()
            assert "kormarc" not in field.lower()

    def test_b2c_only_pii_minimal(self):
        """B2C·사서 PII 최소만·전화·주민번호 X."""
        for field in USER_PROFILE_SCHEMA:
            assert "phone" not in field.lower()
            assert "rrn" not in field.lower()  # 주민번호
            assert "address" not in field.lower()

    def test_supabase_free_mau_50k(self):
        """무료 한도 = 50K MAU (사서 5만명 가능·B2C 충분)."""
        assert SUPABASE_FREE_MAU_LIMIT == 50_000


class TestEnvironmentSeparation:
    """B2B (AWS Cognito Seoul) vs B2C (Supabase) 분리·ADR 0047 부분 supersede."""

    def test_b2c_only_scope(self):
        client = SupabaseClient(url="x", anon_key="y")
        status = client.status()
        # B2C·B2B 분리 명시
        assert "B2C" in status["scope"]
