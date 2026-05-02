"""사용자 친화 Streamlit 컴포넌트 모음.

Part 47·48 시급 + Part 57 도서관 환경 정합 (PO 명령 2026-05-02):
- CSV 양식 다운로드 버튼 (P1 매크로 사서)
- 무료 50건 큰 배지 (P3·P6 결제 압박 회피)
- 페르소나 선택·헤드라인
- 단축키·세션 보안·privacy mask·draft autosave (도서관 환경 12 정합)

음성 안내 (Web Speech API) = Part 57 deprecated:
도서관 = 정숙 환경 + 이용자 응대 = 음성 출력 부적합 (E2 UX 전문가 검증).
"""
from __future__ import annotations

from kormarc_auto.ui.persona_vocabulary import t

CSV_TEMPLATE_HEADER = (
    "ISBN,자관등록번호,복본기호,별치기호,권차,비고\n"
    "9788937437076,EQ20260001,c.1,,,수서 자료\n"
    "9791164060238,EQ20260002,c.1,WQ,v.1,시문학 별치\n"
)


def render_csv_template_download() -> None:
    """일괄 처리용 CSV 양식 다운로드 버튼.

    P1 매크로 사서 페인 직접 해결 (Part 45 §1):
    - 포기 가능성 15% → 5%
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.download_button(
        label=f"📋 {t('input.batch_label')} CSV 양식 다운로드",
        data=CSV_TEMPLATE_HEADER.encode("utf-8-sig"),  # Excel 한글 호환 BOM
        file_name="kormarc-auto-batch-template.csv",
        mime="text/csv",
        help="Excel·한셀에서 바로 열 수 있는 양식입니다. ISBN 열만 채우셔도 됩니다.",
    )


def render_free_tier_badge() -> None:
    """무료 50건 큰 배지.

    P3 자원활동가·P6 학부모 결제 압박 회피 (Part 45 §3·§6):
    - 가입 시 결제 거부감 → 가입 유지 ↑
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1f6feb 0%, #4a90e2 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            margin: 12px 0;
            box-shadow: 0 4px 6px rgba(31, 111, 235, 0.2);
        ">
            ✨ {t('pricing.free_badge')}<br>
            <span style="font-size: 14px; font-weight: 400; opacity: 0.95;">
                {t('pricing.no_pressure')}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_keyboard_shortcuts_help() -> None:
    """키보드 단축키 안내 패널 (사서 키보드 중심 작업 정합).

    Part 57: 도서관 사서 = 키보드 위주 (마우스 X) → 단축키 노출.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    with st.expander("⌨ 단축키 안내 (사서 빠른 작업용)"):
        st.markdown(
            """
            | 키 | 동작 |
            |----|----|
            | **Enter** | ISBN 입력 후 즉시 변환 |
            | **Tab / Shift+Tab** | 다음·이전 입력 칸 이동 |
            | **Ctrl+S** | 작업 중인 항목 임시 저장 (자동 저장도 30초마다) |
            | **Ctrl+Enter** | 일괄 텍스트 → 처리 시작 |
            | **Esc** | 모달·팝업 닫기 |
            | **Ctrl+P** | 청구기호 라벨 미리보기 |
            """
        )


def render_session_lock_notice(timeout_minutes: int = 15) -> None:
    """공용 PC 세션 자동 잠금 안내 (이용자 데이터 보호).

    Part 57 §3: 사서 PC = 공용·이용자 응대 중 자리 비움 → 자동 잠금 안내.
    실제 잠금은 streamlit_app.py에서 session_state.last_active 기준 timer.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.caption(
        f"🔒 **{timeout_minutes}분 동안 입력이 없으면 자동 잠금됩니다.** "
        f"이용자 응대 시 자리 비우셔도 안전합니다."
    )


def render_privacy_mask_toggle() -> bool:
    """이용자 옆 화면 보호 모드 토글.

    Part 57 §4: 카운터 옆 이용자 = 화면 시야 확보 → 민감 정보 마스킹.
    """
    try:
        import streamlit as st
    except ImportError:
        return False

    return st.toggle(
        "👁 화면 보호 모드 (이용자 옆 사용 시)",
        value=st.session_state.get("privacy_mask", False),
        help="ISBN·등록번호·이용자 정보를 ●●●●로 가립니다. 토글 OFF 시 즉시 복원.",
        key="privacy_mask",
    )


def mask_sensitive(value: str, *, visible_chars: int = 4) -> str:
    """민감 정보 마스킹 (privacy mode ON 시).

    예: 9788937437076 → 9788●●●●●●●●●
    """
    try:
        import streamlit as st

        if not st.session_state.get("privacy_mask", False):
            return value
    except ImportError:
        return value

    if len(value) <= visible_chars:
        return "●" * len(value)
    return value[:visible_chars] + "●" * (len(value) - visible_chars)


def render_lite_mode_toggle() -> bool:
    """노후 PC·저사양 호환 lite 모드 (애니메이션·그림자 제거).

    Part 57 §7: 도서관 PC 60% = 노후 (Windows 7·10 잔존) → 가벼운 렌더링.
    """
    try:
        import streamlit as st
    except ImportError:
        return False

    lite = st.toggle(
        "⚡ 가벼운 모드 (오래된 PC용)",
        value=st.session_state.get("lite_mode", False),
        help="애니메이션·그림자·hover 효과를 끕니다. 화면이 더 빠르게 떠요.",
        key="lite_mode",
    )

    if lite:
        st.markdown(
            """
            <style>
            * { transition: none !important; animation: none !important; }
            .stButton button:hover { transform: none !important; box-shadow: none !important; }
            .candidate-card:hover { box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    return lite


def render_status_3layer(*, status: str, message: str) -> None:
    """색·아이콘·텍스트 3중 시각 알림 (색맹·고대비 호환).

    Part 57 §12: 색상 단일 의존 X → 색 + 아이콘 + 명확 텍스트 동시.
    KWCAG 1.4.1 (색에만 의존 X) 정합.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    icons = {
        "success": ("✅", "#38A169", "성공"),
        "warning": ("⚠", "#D69E2E", "주의"),
        "error": ("⛔", "#C53030", "실패"),
        "info": ("ℹ", "#2C5282", "안내"),
    }
    icon, color, label = icons.get(status, ("ℹ", "#2C5282", "안내"))

    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {color};
            background: white;
            padding: 12px 16px;
            border-radius: 6px;
            margin: 8px 0;
            display: flex;
            gap: 12px;
            align-items: flex-start;
        ">
            <div style="font-size: 20px;" aria-hidden="true">{icon}</div>
            <div>
                <div style="font-weight: 600; color: {color}; font-size: 14px;">[{label}]</div>
                <div style="color: #1A202C; font-size: 15px; margin-top: 2px;">{message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_persona_selector() -> str | None:
    """가입 시·설정 화면에서 페르소나 선택 위젯.

    선택 결과 → session_state["persona"] + ["persona_mode"] 자동 동기화.
    """
    try:
        import streamlit as st

        from kormarc_auto.ui.persona_vocabulary import set_persona_mode
    except ImportError:
        return None

    options = {
        "macro_librarian": "정사서 — Excel 매크로 사용 중",
        "school_librarian": "사서교사 — 학교도서관",
        "contract_librarian": "1년 계약직 사서",
        "university_librarian": "대학도서관 사서",
        "general_librarian": "일반 사서 (기타)",
        "volunteer": "자원봉사자 — 사서 자격증 없음",
        "parent_volunteer": "학부모 자원봉사",
        "student_helper": "학생 도우미",
    }

    persona = st.selectbox(
        "사용자 유형",
        options=list(options.keys()),
        format_func=lambda k: options[k],
        key="persona_selector",
        help="유형에 따라 화면 안내 어휘가 자동 변경됩니다 (사서 표준 ↔ 일상 어휘).",
    )

    if persona:
        set_persona_mode(persona)

    return persona


def render_user_friendly_hero() -> None:
    """페르소나 모드별 사용자 친화 헤드라인.

    홈 화면 5초 발견 룰 + 사서 친화 언어 (PO 명령 정합).
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(
        f"""
        <div style="text-align: center; padding: 24px 0;">
            <h1 style="margin: 0 0 8px; font-size: 28px;">
                {t('home.title')}
            </h1>
            <p style="margin: 0; color: #6b7280; font-size: 16px;">
                {t('home.subtitle')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
