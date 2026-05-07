"""Cycle 70 — Supabase B2C Auth 통합 (ADR 0050 정합).

원칙:
- B2C 사서 개인 한정·B2B X (AWS Cognito Seoul Phase 2)
- 자관 .mrc·자관 양식 = 사서 컴퓨터 (헌법 §14·invariant 12)
- 사서 PII만 = Supabase (이메일·해시 PW·결제 history)
- 환경변수만·코드에 키 박지 X (헌법 §3·invariant)
- PIPA §28의8 = 6수신자 = privacy-policy v2 발행 의무

사용:
    from kormarc_auto.auth import get_supabase_client, is_b2c_auth_available

    if is_b2c_auth_available():
        client = get_supabase_client()
        # client.sign_up(email, password)
        # client.sign_in(email, password)
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Supabase 무료 한도 (50K MAU·500MB DB·1GB Storage)
SUPABASE_FREE_MAU_LIMIT = 50_000

# 사서 PII 스키마 (DB 저장 = 최소만)
USER_PROFILE_SCHEMA = {
    "id": "UUID·Supabase Auth 자동",
    "email": "string·로그인 ID",
    "library_type": "small/school/public/university/private",
    "library_code": "도서관 식별 부호 (옵션·자관 자동)",
    "subscription_tier": "free/personal/pro/founding",
    "created_at": "timestamp·자동",
    "updated_at": "timestamp·자동",
}


@dataclass(frozen=True)
class AuthState:
    """B2C Auth 상태 (Streamlit session·읽기 전용)."""

    is_authenticated: bool
    user_id: str | None
    email: str | None
    library_type: str | None
    subscription_tier: str  # free/personal/pro/founding


class SupabaseClient:
    """Supabase Auth wrapper·B2C 한정·환경변수 read.

    실 LLM·Supabase API 호출 = supabase-py (Phase 2·PO 토큰 발급 후 활성).
    현재 = scaffold·환경변수 read만·통합 검증 후 sign_up/in 활성.
    """

    def __init__(self, url: str | None = None, anon_key: str | None = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.anon_key = anon_key or os.getenv("SUPABASE_ANON_KEY", "")
        self._configured = bool(self.url and self.anon_key)

    @property
    def configured(self) -> bool:
        """환경변수 SUPABASE_URL + SUPABASE_ANON_KEY 모두 = True."""
        return self._configured

    def status(self) -> dict[str, str]:
        """현재 통합 상태 (디버깅·Streamlit 표시용)."""
        return {
            "configured": str(self._configured),
            "url_set": str(bool(self.url)),
            "anon_key_set": str(bool(self.anon_key)),
            "scope": "B2C 사서 개인 (Cycle 70·ADR 0050)",
            "data_locality": "사서 PII만·자관 .mrc = 사서 컴퓨터 (헌법 §14)",
        }

    def sign_up_url(self, email: str) -> str:
        """Sign-up 진입 URL (Streamlit 외부 redirect·실 통합은 supabase-py)."""
        if not self._configured:
            return "/auth/setup-required"
        return f"{self.url}/auth/v1/signup?email={email}"

    def sign_in_url(self) -> str:
        """Sign-in URL (B2C·체크카드·세금계산서 X)."""
        if not self._configured:
            return "/auth/setup-required"
        return f"{self.url}/auth/v1/login"


def get_supabase_client() -> SupabaseClient:
    """Supabase 클라이언트 (env 자동 read)."""
    return SupabaseClient()


def is_b2c_auth_available() -> bool:
    """B2C Auth 활성 여부 (env 설정 시).

    True = Streamlit B2C 진입점에서 sign-up/in 표시
    False = "곧 출시 예정" placeholder + .exe 사용 권장
    """
    return get_supabase_client().configured


def require_b2c_subscription(state: AuthState) -> bool:
    """결제 게이트 (Cycle 11 P31 정합).

    free = 50건/월 한도·personal·pro·founding = 무제한
    """
    return state.subscription_tier in ("personal", "pro", "founding")


def get_subscription_features(tier: str) -> dict[str, bool | int]:
    """플랜별 기능 (B2C 정합·Cycle 68 ADR 0050)."""
    features = {
        "free": {
            "monthly_records": 50,
            "ai_classification": False,
            "ocr_cover": False,
            "vernacular_880": False,
            "priority_support": False,
            "monthly_krw": 0,
        },
        "personal": {  # ₩9,900/월
            "monthly_records": -1,  # 무제한
            "ai_classification": False,
            "ocr_cover": False,
            "vernacular_880": False,
            "priority_support": False,
            "monthly_krw": 9_900,
        },
        "pro": {  # ₩19,900/월
            "monthly_records": -1,
            "ai_classification": True,
            "ocr_cover": True,
            "vernacular_880": True,
            "priority_support": True,
            "monthly_krw": 19_900,
        },
        "founding": {  # ₩4,950/월·1,000명·~2026-06-30
            "monthly_records": -1,
            "ai_classification": False,
            "ocr_cover": False,
            "vernacular_880": False,
            "priority_support": False,
            "monthly_krw": 4_950,
            "perpetual_50pct": True,
        },
    }
    return features.get(tier, features["free"])


__all__ = [
    "SUPABASE_FREE_MAU_LIMIT",
    "USER_PROFILE_SCHEMA",
    "AuthState",
    "SupabaseClient",
    "get_subscription_features",
    "get_supabase_client",
    "is_b2c_auth_available",
    "require_b2c_subscription",
]
