"""3분 인터랙티브 온보딩 튜토리얼 (가상 책 1권 입력 시연).

Part 50 발견: P3 자원활동가·P6 학부모 첫 가입 활성화 (Just-in-Time +37%).
ADR (Part 44 §12) 정합.

5단계 흐름:
1. 가상 ISBN 자동 채움 (예시 책)
2. 자동 생성 결과 확인
3. 자관 prefix 추가 시연
4. KOLAS 반입 시뮬레이션
5. "축하합니다! 첫 책 완성"
"""
from __future__ import annotations

from dataclasses import dataclass

from kormarc_auto.ui.persona_vocabulary import t

# 시연용 가상 책 (실제 ISBN — 한국 대표 도서)
DEMO_ISBN = "9788937437076"  # 어린왕자 (열린책들)
DEMO_BOOK = {
    "isbn": DEMO_ISBN,
    "title": "어린왕자",
    "author": "앙투안 드 생텍쥐페리",
    "publisher": "열린책들",
    "year": "2007",
    "kdc": "863.2",
    "pages": "151",
}


@dataclass(frozen=True)
class TutorialStep:
    """튜토리얼 단계 정의."""

    step_no: int
    title: str
    body: str
    cta_label: str
    estimated_seconds: int


def get_tutorial_steps() -> list[TutorialStep]:
    """5단계 튜토리얼 (페르소나 어휘 자동 분기)."""
    return [
        TutorialStep(
            step_no=1,
            title=f"1. {t('input.isbn_label')} 시연",
            body=(
                f"가상 책 한 권으로 3분 안에 익혀보세요.\n\n"
                f"예시 ISBN: **{DEMO_ISBN}** (어린왕자 / 열린책들)\n\n"
                f"이 ISBN을 입력 칸에 자동으로 채워드렸어요. **시작 버튼**을 눌러주세요."
            ),
            cta_label="시작하기",
            estimated_seconds=20,
        ),
        TutorialStep(
            step_no=2,
            title=f"2. {t('result.title')}",
            body=(
                f"자동 생성된 정보를 확인해보세요:\n\n"
                f"- **제목**: {DEMO_BOOK['title']}\n"
                f"- **저자**: {DEMO_BOOK['author']}\n"
                f"- **출판사**: {DEMO_BOOK['publisher']}\n"
                f"- **출판년도**: {DEMO_BOOK['year']}\n"
                f"- **{t('term.kdc')}**: {DEMO_BOOK['kdc']} (외국문학)\n"
                f"- **쪽수**: {DEMO_BOOK['pages']}쪽\n\n"
                f"AI가 자동으로 채웠어요. 직접 확인하시고 다음 단계로 가요."
            ),
            cta_label="다음",
            estimated_seconds=40,
        ),
        TutorialStep(
            step_no=3,
            title="3. 우리 도서관만의 정보 추가",
            body=(
                "이 책이 우리 도서관 어디에 있는지 표시할 수 있어요.\n\n"
                "예시:\n"
                "- **자관 등록번호**: EQ20260001 (우리 도서관 일반자료실 첫 번째 책)\n"
                "- **별치 표시**: 있으면 입력 / 없으면 비워두기\n\n"
                "→ 우리 도서관 청구기호 자동 생성: `863.2/생894ㅇ`"
            ),
            cta_label="다음",
            estimated_seconds=40,
        ),
        TutorialStep(
            step_no=4,
            title=f"4. {t('system.import')} 시뮬레이션",
            body=(
                "이제 우리 도서관 시스템에 등록할 차례에요.\n\n"
                "**자동 생성된 .mrc 파일**을 다운로드해서 KOLAS·독서로DLS에 그대로 반입할 수 있어요.\n\n"
                "✅ KOLAS III 호환\n"
                "✅ 독서로DLS 호환\n"
                "✅ KORIBLE 호환 (대학도서관)\n"
                "✅ KOLISNET 종합목록 정합\n\n"
                "(이번 시연은 시뮬레이션이라 실제 반입은 X)"
            ),
            cta_label="시뮬레이션 보기",
            estimated_seconds=40,
        ),
        TutorialStep(
            step_no=5,
            title="5. ✓ 첫 책 완성",
            body=(
                "수고하셨어요. 어린왕자 한 권 완성했어요.\n\n"
                "방금 약 **2분**이 걸렸어요. (수동 입력 평균 8분)\n\n"
                "실제 사용 시:\n"
                "- ✓ 무료 50건까지 그대로 사용 가능\n"
                "- ✓ 결제는 50권 사용 후 결정\n"
                "- ✓ 모르는 부분 = 화면 우측 ⌨ 단축키·도움말 + 사서 가이드(텍스트)\n\n"
                "준비되시면 **첫 진짜 ISBN**을 입력해보세요."
            ),
            cta_label="진짜 책 등록 시작",
            estimated_seconds=40,
        ),
    ]


def render_onboarding_tutorial() -> None:
    """Streamlit 5단계 튜토리얼 위젯.

    P3·P6 첫 가입 활성화 +37% (Just-in-Time onboarding 검증).
    건너뛰기 가능·다시 보기 옵션.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    if st.session_state.get("tutorial_completed", False):
        with st.expander("🎓 튜토리얼 다시 보기"):
            _render_tutorial_steps()
        return

    if st.session_state.get("tutorial_skipped", False):
        if st.button("🎓 튜토리얼 보기 (3분, 가상 책으로 시연)"):
            st.session_state["tutorial_skipped"] = False
            st.rerun()
        return

    # 첫 실행 — 권유 화면
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #f0f9ff 0%, #ddeeff 100%);
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 16px;
        ">
            <h2 style="margin-top: 0;">🎓 처음이신가요?</h2>
            <p style="font-size: 15px; color: #4b5563;">
                3분 안에 가상 책 한 권으로 사용법을 익혀보세요.
                건너뛰셔도 언제든 다시 시작할 수 있어요.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("✨ 3분 튜토리얼 시작", type="primary", use_container_width=True):
            st.session_state["tutorial_started"] = True
            st.session_state["tutorial_step"] = 1
            st.rerun()
    with col2:
        if st.button("나중에", use_container_width=True):
            st.session_state["tutorial_skipped"] = True
            st.rerun()

    if st.session_state.get("tutorial_started"):
        _render_tutorial_steps()


def _render_tutorial_steps() -> None:
    """진행 중인 튜토리얼 단계 렌더링."""
    try:
        import streamlit as st
    except ImportError:
        return

    steps = get_tutorial_steps()
    current_step = st.session_state.get("tutorial_step", 1)

    if current_step > len(steps):
        st.session_state["tutorial_completed"] = True
        st.session_state["tutorial_started"] = False
        st.success("✓ 튜토리얼을 완료했어요. 이제 진짜 책을 등록해보세요.")
        return

    step = steps[current_step - 1]

    # 진행률 표시
    st.progress(current_step / len(steps), text=f"단계 {current_step}/{len(steps)}")

    st.markdown(f"### {step.title}")
    st.markdown(step.body)
    st.caption(f"⏱ 약 {step.estimated_seconds}초")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button(step.cta_label, type="primary", use_container_width=True):
            st.session_state["tutorial_step"] = current_step + 1
            st.rerun()
    with col2:
        if st.button("건너뛰기", use_container_width=True):
            st.session_state["tutorial_skipped"] = True
            st.session_state["tutorial_started"] = False
            st.rerun()
