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
import re
import secrets
import time
from collections import deque
from pathlib import Path
from threading import Lock
from typing import Any

from kormarc_auto.constants import FREE_QUOTA_DEFAULT, get_payment_info_url

logger = logging.getLogger(__name__)

_lock = Lock()

# 분당 가입 시도 윈도우 (이메일/IP별)
_SIGNUP_WINDOW_SECONDS = 60
_SIGNUP_MAX_PER_WINDOW = 5
_signup_attempts: dict[str, deque[float]] = {}
_attempts_lock = Lock()

# 이메일 정규식 (RFC 5322 단순화 — 99% 케이스 충분)
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class SignupError(Exception):
    """가입 실패 (검증·레이트 리밋)."""


def validate_email(email: str) -> str:
    """이메일 형식 검증 + 정규화 (소문자 trim)."""
    email = (email or "").strip().lower()
    if not _EMAIL_RE.match(email):
        raise SignupError(f"이메일 형식이 올바르지 않습니다: {email}")
    if len(email) > 200:
        raise SignupError("이메일이 너무 깁니다 (최대 200자)")
    return email


def check_rate_limit(key: str) -> None:
    """동일 키(이메일/IP)의 분당 가입 시도 제한.

    Raises:
        SignupError: 분당 한도 초과
    """
    now = time.time()
    with _attempts_lock:
        bucket = _signup_attempts.setdefault(key, deque())
        while bucket and now - bucket[0] > _SIGNUP_WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= _SIGNUP_MAX_PER_WINDOW:
            raise SignupError(
                f"가입 시도가 너무 잦습니다. {_SIGNUP_WINDOW_SECONDS}초 후 다시 시도하세요."
            )
        bucket.append(now)


def _signup_log_path() -> Path:
    """신규 가입자 누적 로그 (PO가 매월 점검·정식 결제 전환)."""
    path = Path(os.getenv("KORMARC_SIGNUP_LOG", "logs/signups.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def issue_free_trial_key(
    email: str,
    library_name: str | None = None,
    *,
    client_ip: str | None = None,
) -> dict[str, Any]:
    """이메일·도서관명 받아 신규 무료 체험 키 발급.

    Args:
        email: 사서 이메일 (식별·연락용)
        library_name: 도서관명 (옵션, 통계용)
        client_ip: 호출자 IP (레이트 리밋용)

    Returns:
        Dict with api_key, free_quota, library_name, ui_url, api_url,
        payment_url, expires_at, next_steps.

    Raises:
        SignupError: 이메일 형식 오류 또는 레이트 리밋
    """
    email = validate_email(email)
    if library_name:
        library_name = library_name.strip()[:200] or None

    check_rate_limit(f"email:{email}")
    if client_ip:
        check_rate_limit(f"ip:{client_ip}")

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

    docs_base = os.getenv("KORMARC_PUBLIC_DOCS_URL", "https://github.com/okwhr/kormarc-auto/blob/main/docs")
    kakao_channel = os.getenv("KORMARC_KAKAO_CHANNEL_URL", "https://pf.kakao.com/_kormarc")
    welcome = (
        f"환영합니다, {library_name or '사서 선생님'}!\n"
        f"무료 {FREE_QUOTA_DEFAULT}건 발급 완료. ISBN 13자리만 입력하시면 5초 안에 KORMARC 생성됩니다.\n"
        f"[검증] 자관 「내를건너서 숲으로 도서관」 .mrc 174 파일·3,383 레코드 → 99.82% 정합 "
        f"(KORMARC 2023.12 한국 KOLAS 실무 정합).\n"
        f"막히는 부분은 카카오 채널({kakao_channel})로 24시간 SLA 응대."
    )
    return {
        "api_key": api_key,
        "free_quota": FREE_QUOTA_DEFAULT,
        "library_name": library_name,
        "ui_url": os.getenv("KORMARC_PUBLIC_UI_URL", "http://localhost:8501"),
        "api_url": os.getenv("KORMARC_PUBLIC_API_URL", "http://localhost:8000"),
        "payment_url": get_payment_info_url(),
        "terms_url": f"{docs_base}/terms-of-service.md",
        "privacy_url": f"{docs_base}/privacy-policy.md",
        "kakao_channel_url": kakao_channel,
        "welcome_message": welcome,
        "expires_at": None,
        "next_steps": [
            "위 api_key를 안전한 곳에 보관하세요. 분실 시 재발급 필요합니다.",
            f"무료 체험은 {FREE_QUOTA_DEFAULT}건. 초과 시 결제 안내가 응답에 포함됩니다.",
            "Streamlit UI 또는 REST API 모두 X-API-Key 헤더로 사용.",
            "이용약관·개인정보 처리방침을 확인하세요 (terms_url / privacy_url 필드).",
            f"질문은 카카오 채널 1:1 문의: {kakao_channel} (24시간 SLA, 영업일).",
        ],
    }


def _append_signup_log(entry: dict[str, Any]) -> None:
    with _lock:
        try:
            with _signup_log_path().open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning("signup 로그 기록 실패: %s", e)
