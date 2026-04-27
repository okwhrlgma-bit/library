"""Streamlit UI 인증 가드 — Part G Step 2·8 (DECISIONS 6dim+7).

streamlit-authenticator 0.4.2 기반. `.streamlit/auth_config.yaml` (.gitignore)
미존재 시 PO에게 셋업 명령 안내 후 차단.

Streamlit 1.46+ 네이티브 OIDC + Cloudflare Access로의 마이그레이션은 도메인
구매·OAuth 셋업 후 별도 ADR. 그때까지 본 모듈이 1차 인증 책임.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)


def _config_path() -> Path:
    """프로젝트 루트의 .streamlit/auth_config.yaml 절대 경로."""
    # streamlit_app.py에서 호출되므로 cwd 기준으로 .streamlit/ 사용
    # 패키지 외부 파일이라 importlib.resources 미적용
    return Path(".streamlit/auth_config.yaml")


def _load_config() -> dict[str, Any] | None:
    path = _config_path()
    if not path.exists():
        return None
    import yaml

    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        logger.error("auth_config.yaml 로드 실패: %s", e)
        return None


def _show_setup_required() -> None:
    """auth_config.yaml 미존재 시 PO에게 셋업 안내."""
    st.error("🔐 인증 설정이 필요합니다.")
    st.markdown(
        """
        ### 셋업 절차 (1회)

        1. 터미널에서 프로젝트 루트로 이동
        2. 다음 명령 실행:

        ```bash
        python scripts/auth_setup.py
        ```

        3. 화면 안내에 따라 비밀번호 설정 (12자 이상)
        4. 본 페이지 새로고침

        **보안**: 평문 비밀번호는 저장되지 않습니다 (bcrypt 해시만).
        90일마다 위 명령 재실행으로 회전 권장.
        """
    )
    st.stop()


def require_login() -> None:
    """Streamlit 진입점에서 호출 — 인증 미통과 시 st.stop().

    PO 마스터 §G.4 + DECISIONS 6dim+7 (2026-04-27).
    """
    config = _load_config()
    if config is None:
        _show_setup_required()
        return  # st.stop() 후 도달 X (정적 분석 보조)

    import streamlit_authenticator as stauth

    # 0.4.2 API: positional 4개 (credentials, cookie_name, cookie_key, expiry_days)
    auth = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    # login()은 (name, auth_status, username) tuple 반환 — 0.4.2 호환
    auth.login(
        location="main",
        fields={
            "Form name": "KORMARC Auto 로그인",
            "Username": "사용자명",
            "Password": "비밀번호",
            "Login": "로그인",
        },
        max_login_attempts=5,
    )

    status = st.session_state.get("authentication_status")
    name = st.session_state.get("name")

    if status is False:
        st.error("❌ 사용자명 또는 비밀번호가 잘못되었습니다.")
        st.stop()
    elif status is None:
        st.warning("🔐 로그인이 필요합니다. 위 양식에 사용자명·비밀번호를 입력하세요.")
        st.stop()

    # 인증 성공 — 사이드바에 사용자 + 로그아웃 버튼
    with st.sidebar:
        st.divider()
        st.write(f"👤 **{name or '익명'}**")
        auth.logout(button_name="로그아웃", location="sidebar")
