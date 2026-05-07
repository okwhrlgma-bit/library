"""Cycle 70 (B2C 활성) — Supabase Auth 통합·B2C 사서 한정.

ADR 0050 부분 supersede·B2C 한정·자관 데이터 = 사서 컴퓨터 (헌법 §14·invariant 12).
환경변수: SUPABASE_URL·SUPABASE_ANON_KEY·SUPABASE_ACCESS_TOKEN (BYOK or 우리 키).
"""

from kormarc_auto.auth.supabase_client import (
    SUPABASE_FREE_MAU_LIMIT,
    AuthState,
    SupabaseClient,
    get_supabase_client,
    is_b2c_auth_available,
)

__all__ = [
    "SUPABASE_FREE_MAU_LIMIT",
    "AuthState",
    "SupabaseClient",
    "get_supabase_client",
    "is_b2c_auth_available",
]
