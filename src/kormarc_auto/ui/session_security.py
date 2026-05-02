"""공용 PC 세션 보안 (자동 잠금·draft 복구).

Part 57 §3·§6 (PO 명령 2026-05-02): 도서관 사서 PC = 공용·이용자 응대 중 자리
비움 → 자동 잠금. 인터럽트 후 복귀 시 작업 손실 방지 = draft autosave.
"""

from __future__ import annotations

import time
from typing import Any

DEFAULT_TIMEOUT_SECONDS = 15 * 60  # 15분
AUTOSAVE_INTERVAL_SECONDS = 30


def touch_activity() -> None:
    """사용자 입력·버튼 클릭 시 호출 (세션 활성 표시)."""
    try:
        import streamlit as st

        st.session_state["_last_active_ts"] = time.time()
    except ImportError:
        return


def is_session_expired(timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> bool:
    """타임아웃 초과 시 True (세션 잠금 트리거)."""
    try:
        import streamlit as st
    except ImportError:
        return False

    last = st.session_state.get("_last_active_ts")
    if last is None:
        touch_activity()
        return False
    return (time.time() - last) > timeout_seconds


def render_session_lock_screen() -> bool:
    """세션 만료 시 잠금 화면 표시. 잠금 상태면 True 반환 → 본 UI 차단."""
    try:
        import streamlit as st
    except ImportError:
        return False

    if not is_session_expired():
        return False

    st.warning("🔒 자리를 비우신 동안 자동 잠금되었어요.")
    st.caption("작성하시던 내용은 자동 저장되어 있어요. 비밀번호 또는 PIN 입력 시 복원됩니다.")

    pin = st.text_input("PIN (4자리)", type="password", max_chars=4, key="session_unlock_pin")
    if st.button("잠금 해제", type="primary"):
        if pin and pin == st.session_state.get("session_pin", "0000"):
            touch_activity()
            st.rerun()
        else:
            st.error("PIN이 일치하지 않아요. 다시 시도해주세요.")
    return True


def autosave_draft(key: str, value: Any) -> None:
    """작업 중 데이터 자동 저장 (인터럽트 복귀 시 복원).

    예: ISBN 입력 중 이용자 응대 시 자동 저장 → 복귀 시 그대로.
    """
    try:
        import streamlit as st

        now = time.time()
        last_save = st.session_state.get(f"_autosave_{key}_ts", 0)
        if (now - last_save) >= AUTOSAVE_INTERVAL_SECONDS:
            st.session_state[f"_draft_{key}"] = value
            st.session_state[f"_autosave_{key}_ts"] = now
    except ImportError:
        return


def restore_draft(key: str, default: Any = "") -> Any:
    """복귀 시 draft 복원."""
    try:
        import streamlit as st

        return st.session_state.get(f"_draft_{key}", default)
    except ImportError:
        return default


def render_draft_recovery_notice(key: str) -> bool:
    """복귀 시 임시 저장 복원 알림. 복원 선택 시 True."""
    try:
        import streamlit as st
    except ImportError:
        return False

    draft = st.session_state.get(f"_draft_{key}")
    if not draft:
        return False

    cols = st.columns([3, 1, 1])
    cols[0].caption(f"💾 작업 중이시던 내용이 있어요: `{str(draft)[:30]}...`")
    if cols[1].button("이어서", key=f"_restore_{key}"):
        return True
    if cols[2].button("새로", key=f"_discard_{key}"):
        st.session_state.pop(f"_draft_{key}", None)
        st.rerun()
    return False


__all__ = [
    "AUTOSAVE_INTERVAL_SECONDS",
    "DEFAULT_TIMEOUT_SECONDS",
    "autosave_draft",
    "is_session_expired",
    "render_draft_recovery_notice",
    "render_session_lock_screen",
    "restore_draft",
    "touch_activity",
]
