"""신규 사용자 키 자동 발급 — 사서가 1분 만에 50건 무료 체험 시작.

흐름:
1. POST /signup {email, library_name?}
2. 서버가 임의 32자 키 생성 + usage DB에 quota=50 등록
3. 응답으로 키 + Streamlit URL + 사용 안내
4. (선택) 이메일/카카오 알림은 외부 연동 (별도 모듈)

PO가 KORMARC_USER_KEYS 화이트리스트 모드를 쓰는 경우, 자동 발급된 키는
"신규" 마커로 별도 파일에 누적 → PO가 정기적으로 화이트리스트로 승격.
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import time
from pathlib import Path
from threading import Lock
from typing import Any

from kormarc_auto.constants import FREE_QUOTA_DEFAULT, PAYMENT_INFO_URL

logger = logging.getLogger(__name__)

_lock = Lock()


def _signup_log_path() -> Path:
    """신규 가입자 누적 로그 (PO가 매월 점검·정식 결제 전환)."""
    path = Path(os.getenv("KORMARC_SIGNUP_LOG", "logs/signups.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def issue_free_trial_key(email: str, library_name: str | None = None) -> dict[str, Any]:
    """이메일·도서관명 받아 신규 무료 체험 키 발급.

    Args:
        email: 사서 이메일 (식별·연락용)
        library_name: 도서관명 (옵션, 통계용)

    Returns:
        {
            "api_key": str,             # 32자 안전 토큰
            "free_quota": int,
            "library_name": str | None,
            "ui_url": str,              # Streamlit 안내
            "api_url": str,
            "payment_url": str,
            "expires_at": int | None,   # 현재는 None (무제한)
        }
    """
    api_key = "kma_" + secrets.token_urlsafe(24)

    # usage DB 초기화 (get_usage가 첫 호출 시 자동 등록)
    from kormarc_auto.server.usage import get_usage

    get_usage(api_key)

    entry = {
        "ts": int(time.time()),
        "email": email,
        "library_name": library_name,
        "api_key_preview": api_key[:12] + "...",
        "quota": FREE_QUOTA_DEFAULT,
    }
    _append_signup_log(entry)

    return {
        "api_key": api_key,
        "free_quota": FREE_QUOTA_DEFAULT,
        "library_name": library_name,
        "ui_url": os.getenv("KORMARC_PUBLIC_UI_URL", "http://localhost:8501"),
        "api_url": os.getenv("KORMARC_PUBLIC_API_URL", "http://localhost:8000"),
        "payment_url": PAYMENT_INFO_URL,
        "expires_at": None,
        "next_steps": [
            "위 api_key를 안전한 곳에 보관하세요. 분실 시 재발급 필요합니다.",
            f"무료 체험은 {FREE_QUOTA_DEFAULT}건. 초과 시 결제 안내가 응답에 포함됩니다.",
            "Streamlit UI 또는 REST API 모두 X-API-Key 헤더로 사용.",
        ],
    }


def _append_signup_log(entry: dict[str, Any]) -> None:
    with _lock:
        try:
            with _signup_log_path().open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning("signup 로그 기록 실패: %s", e)
