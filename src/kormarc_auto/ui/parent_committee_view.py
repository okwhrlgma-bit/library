"""학부모 자원봉사 위원회 협업 화면.

Part 50 발견: P6 학부모 위원회 협업 부재 해결.

5명+ 위원회 동시 작업 + 사서교사 검수 큐 통합.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

CommitteeRole = Literal[
    "coordinator", "volunteer", "school_librarian", "teacher", "principal_observer"
]


@dataclass
class CommitteeMember:
    """위원회 구성원."""

    name: str
    role: CommitteeRole
    today_records: int = 0
    pending_review: int = 0
    last_active: datetime | None = None


@dataclass
class CommitteeSession:
    """오늘의 위원회 세션."""

    school_name: str
    session_date: datetime
    members: list[CommitteeMember] = field(default_factory=list)
    total_records_today: int = 0
    queued_for_review: int = 0


def render_committee_dashboard(session: CommitteeSession) -> None:
    """위원회 협업 대시보드.

    P6 학부모 자원봉사 페르소나:
    - 5명+ 위원회 실시간 작업 현황
    - 사서교사 검수 큐 통합
    - 학부모간 책임 분담 시각화
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(f"### 🤝 {session.school_name} 도서관 위원회")
    weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    sd = session.session_date
    date_str = (
        f"{sd.year}년 {sd.month}월 {sd.day}일 ({weekdays_kr[sd.weekday()]}) {sd.strftime('%H:%M')}"
    )
    st.caption(
        f"{date_str} · 위원 {len(session.members)}명 · 오늘 처리 {session.total_records_today}권"
    )

    # 위원별 작업 현황 카드 그리드
    if session.members:
        cols = st.columns(min(len(session.members), 4))
        for idx, member in enumerate(session.members):
            with cols[idx % 4]:
                role_label = _role_label(member.role)
                role_emoji = _role_emoji(member.role)
                status = _member_status(member)

                st.markdown(
                    f"""
                    <div style="
                        background: white;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        padding: 12px;
                        text-align: center;
                    ">
                        <div style="font-size: 24px;">{role_emoji}</div>
                        <div style="font-weight: 600; margin: 4px 0;">{member.name} 선생님</div>
                        <div style="font-size: 12px; color: #6b7280;">{role_label}</div>
                        <div style="font-size: 14px; margin-top: 8px;">
                            오늘 <strong>{member.today_records}</strong>권 ·
                            검수 대기 <strong>{member.pending_review}</strong>
                        </div>
                        <div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">{status}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # 사서교사 검수 큐 (사서교사 페르소나만 보임)
    try:
        from kormarc_auto.ui.persona_vocabulary import get_persona_mode

        if get_persona_mode() == "librarian":
            st.markdown("#### 📋 검수 큐 (사서교사용)")
            st.info(
                f"학부모·학생 위원이 등록한 신간 **{session.queued_for_review}권**이 검수를 기다리고 있어요. "
                "일괄 모드(B 단축키)로 5건씩 묶어 빠르게 검수할 수 있습니다."
            )
    except ImportError:
        pass

    # 학부모 위원용 안내 (책임 분리)
    st.success(
        "💡 **책임 분리 안내**: 위원 선생님이 입력한 책 정보는 도서관 선생님(사서교사)이 한번 더 확인해주세요. "
        "잘못 입력하셔도 안전해요. 30일 휴지통에 자동 보관됩니다."
    )


def _role_label(role: CommitteeRole) -> str:
    """역할 한글 라벨."""
    return {
        "coordinator": "위원회 위원장",
        "volunteer": "자원봉사 위원",
        "school_librarian": "사서교사",
        "teacher": "교사 위원",
        "principal_observer": "교장 (참관)",
    }.get(role, "위원")


def _role_emoji(role: CommitteeRole) -> str:
    return {
        "coordinator": "👥",
        "volunteer": "🌟",
        "school_librarian": "📚",
        "teacher": "🎓",
        "principal_observer": "👀",
    }.get(role, "🌟")


def _member_status(member: CommitteeMember) -> str:
    """위원 상태 표시."""
    if member.last_active is None:
        return "미접속"
    elapsed = (datetime.now() - member.last_active).total_seconds()
    if elapsed < 60:
        return "🟢 활동 중"
    elif elapsed < 600:
        return f"🟡 {int(elapsed / 60)}분 전"
    else:
        return f"🔴 {int(elapsed / 60)}분 전"


def render_committee_invite() -> None:
    """위원회 신규 위원 초대 화면."""
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown("#### 🤝 위원 초대")
    st.markdown(
        "위원회 동료 선생님을 초대해 함께 도서관을 운영해보세요. "
        "각자 자신의 ID로 로그인하시면 책임이 분리됩니다."
    )

    invite_email = st.text_input(
        "초대할 분 이메일",
        placeholder="parent.volunteer@school.kr",
        help="입력하신 이메일로 초대 링크가 발송됩니다.",
    )
    st.selectbox(
        "역할",
        options=["volunteer", "teacher", "school_librarian"],
        format_func=_role_label,
    )
    if st.button("✉️ 초대 메일 보내기"):
        st.success(f"{invite_email}로 초대 링크를 보냈어요. 7일 안에 가입하시면 됩니다.")


# 책임 분리 정책 (자원봉사·학부모 페인 직접 해결)
RESPONSIBILITY_POLICY = {
    "volunteer_can": [
        "ISBN 입력 (책 등록)",
        "사진 업로드 (책 표지)",
        "기본 정보 확인",
    ],
    "volunteer_cannot": [
        "KORMARC 검수 확정",
        "KOLAS 반입",
        "다른 위원 작업 삭제",
    ],
    "school_librarian_only": [
        "검수 큐 일괄 승인·반려",
        "KOLAS·DLS 반입",
        "위원 권한 관리",
        "결제·계약 관리",
    ],
}


def render_responsibility_guide() -> None:
    """책임 분리 안내 (P6 학부모 안심)."""
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown("#### 📋 위원별 책임 안내")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**자원봉사·학부모 위원이 할 수 있는 일**")
        for item in RESPONSIBILITY_POLICY["volunteer_can"]:
            st.markdown(f"- ✅ {item}")
        st.markdown("**할 수 없는 일 (안심)**")
        for item in RESPONSIBILITY_POLICY["volunteer_cannot"]:
            st.markdown(f"- 🔒 {item}")
    with col2:
        st.markdown("**도서관 선생님(사서교사)만 할 수 있는 일**")
        for item in RESPONSIBILITY_POLICY["school_librarian_only"]:
            st.markdown(f"- 🔑 {item}")
