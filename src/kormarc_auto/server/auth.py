"""FastAPI X-API-Key 인증 + 사용량 검증."""

from __future__ import annotations

import os
from typing import Any

from fastapi import Header, HTTPException, status

from kormarc_auto.server.usage import can_consume, get_usage


def _admin_keys() -> set[str]:
    """관리자 키 (모든 사용량 무제한). 환경변수 KORMARC_ADMIN_KEYS (쉼표 구분)."""
    raw = os.getenv("KORMARC_ADMIN_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def _allowed_user_keys() -> set[str] | None:
    """발급된 사용자 키 (환경변수 KORMARC_USER_KEYS 쉼표 구분).

    None이면 키 형식만 맞으면 자동 등록 (개발 모드).
    """
    raw = os.getenv("KORMARC_USER_KEYS", "")
    keys = {k.strip() for k in raw.split(",") if k.strip()}
    return keys or None


def require_api_key(x_api_key: str = Header(default="", alias="X-API-Key")) -> str:
    """헤더에서 API 키 추출·검증. 통과하면 키 반환."""
    if not x_api_key or len(x_api_key) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key 헤더가 없거나 너무 짧습니다 (최소 8자).",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    allowed = _allowed_user_keys()
    if allowed is not None and x_api_key not in allowed and x_api_key not in _admin_keys():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="등록되지 않은 API 키입니다.",
        )
    return x_api_key


def check_quota(api_key: str) -> dict[str, Any]:
    """무료 한도 체크 — 초과 시 402 + 결제 안내."""
    if api_key in _admin_keys():
        return {"admin": True, "remaining": 9999}

    ok, status_dict = can_consume(api_key)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "무료 사용량 초과 — 결제 안내를 따라주세요.",
                "usage": status_dict,
            },
        )
    return status_dict


def get_usage_status(api_key: str) -> dict[str, Any]:
    """현재 키의 사용량 상태 조회 (인증·할당량 검사 안 함)."""
    return get_usage(api_key)
