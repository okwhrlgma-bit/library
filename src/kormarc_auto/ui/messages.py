"""친근한 한국어 에러·안내 메시지 라이브러리.

ADR-0061 (Part 44 §1 + Part 45 P1~P6 페인 정합).

검증된 5 원칙 (NN/G·Pencil & Paper):
1. 사용자 비난 X (positive·non-judgmental)
2. 회복 방법 명시 (actionable next steps)
3. 평이한 언어 (KORMARC 전문 용어 회피 — 비전문가 모드)
4. 친근한 톤 (사서 동료처럼)
5. 유머는 신중히 (명료성 우선)

Usage:
    from kormarc_auto.ui.messages import show_error, show_info

    show_error("isbn_invalid")
    show_info("processing", count=100)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from kormarc_auto.ui.persona_vocabulary import get_persona_mode, t


@dataclass(frozen=True)
class Message:
    """에러·안내 메시지 구조."""

    title: str
    body: str
    action: str
    severity: str  # info / warning / error
    icon: str  # 이모지 또는 streamlit 아이콘


# 메시지 카탈로그 (페르소나 어휘 자동 분기)
MESSAGE_CATALOG: dict[str, dict[str, Any]] = {
    "isbn_invalid": {
        "title_key": "error.isbn_invalid.title",
        "body_key": "error.isbn_invalid.body",
        "action_key_lib": "ISBN 다시 입력",
        "action_key_ne": "다시 입력하기",
        "severity": "warning",
        "icon": "📖",
    },
    "api_timeout": {
        "title_key": "error.api_timeout.title",
        "body_key": "error.api_timeout.body",
        "action_key_lib": "지금 다시 시도",
        "action_key_ne": "다시 시도하기",
        "severity": "warning",
        "icon": "⏱️",
    },
    "api_all_failed": {
        "title": {
            "librarian": "외부 API 전체 폴백 실패",
            "non_expert": "외부 서비스 연결이 어려워요",
        },
        "body": {
            "librarian": "정보나루·국중도·알라딘·KOLISNET·카카오 모두 응답 X. 잠시 후 재시도 또는 수동 입력.",
            "non_expert": "책 정보를 가져오는 모든 곳에서 응답이 없어요. 잠시 후 다시 시도하거나 직접 입력해주세요.",
        },
        "action": {
            "librarian": "수동 입력으로 진행",
            "non_expert": "직접 입력하기",
        },
        "severity": "error",
        "icon": "🌐",
    },
    "network_error": {
        "title": {
            "librarian": "네트워크 연결 실패",
            "non_expert": "인터넷 연결을 확인해주세요",
        },
        "body": {
            "librarian": "WAN 연결 검증 X. ConnectionError·TimeoutError.",
            "non_expert": "와이파이 또는 LTE 연결 상태를 살펴봐주세요. 연결되면 자동으로 이어서 진행돼요.",
        },
        "action": {
            "librarian": "재시도",
            "non_expert": "연결 후 다시 시도",
        },
        "severity": "error",
        "icon": "📡",
    },
    "kormarc_validation_warning": {
        "title": {
            "librarian": "KORMARC 검증 경고",
            "non_expert": "사서 검토가 필요한 부분이 있어요",
        },
        "body": {
            "librarian": "{field} 필드 신뢰도 {confidence:.0%}. 사서 검토 권장. AI 추천: {suggestion}",
            "non_expert": "{field_friendly}이(가) 확실하지 않아요. 사서 선생님이 확인하면 더 정확해집니다. 추천: {suggestion}",
        },
        "action": {
            "librarian": "이대로 사용 / 수정",
            "non_expert": "그대로 사용 / 직접 수정",
        },
        "severity": "info",
        "icon": "🔍",
    },
    "permission_denied": {
        "title": {
            "librarian": "권한 부족",
            "non_expert": "이 기능은 관리자가 활성화해야 해요",
        },
        "body": {
            "librarian": "현재 계정 권한 X. 관리자(또는 PO) 문의 필요.",
            "non_expert": "도서관 관리자(또는 사서 선생님)께 문의해주세요. 자동으로 알림 보낼 수 있어요.",
        },
        "action": {
            "librarian": "관리자에게 알림 발송",
            "non_expert": "관리자에게 알리기",
        },
        "severity": "warning",
        "icon": "🔒",
    },
    "processing": {
        "title": {
            "librarian": "KORMARC 자동 생성 중",
            "non_expert": "책 정보를 등록하고 있어요",
        },
        "body": {
            "librarian": "{count}건 처리 중. 평균 {avg_time:.1f}초/건.",
            "non_expert": "{count}권 등록 중이에요. 한 권당 약 {avg_time:.1f}초 걸려요.",
        },
        "action": {
            "librarian": "취소",
            "non_expert": "잠시 멈추기",
        },
        "severity": "info",
        "icon": "⚙️",
    },
    "complete": {
        "title": {
            "librarian": "처리 완료",
            "non_expert": "다 됐어요!",
        },
        "body": {
            "librarian": "{count}건 KORMARC 생성. 권당 평균 {time_per_record:.1f}초 (기존 8분 대비 {savings_pct:.0%} 절감).",
            "non_expert": "{count}권 등록이 끝났어요. 한 권당 약 {time_per_record:.1f}초로, 기존보다 {savings_pct:.0%} 빠르게 끝났습니다.",
        },
        "action": {
            "librarian": ".mrc 다운로드",
            "non_expert": "파일 받기",
        },
        "severity": "info",
        "icon": "✅",
    },
}


def show_error(key: str, **kwargs: Any) -> Message:
    """에러 메시지 생성 (페르소나 어휘 자동 적용).

    Args:
        key: 메시지 카탈로그 키
        **kwargs: 메시지 포맷 인자 (예: count=100, field="245")

    Returns:
        Message dataclass (Streamlit st.error/warning/info에 전달).

    Streamlit 사용 예:
        msg = show_error("isbn_invalid")
        st.error(f"{msg.icon} **{msg.title}**\\n\\n{msg.body}")
        if st.button(msg.action):
            ...
    """
    if key not in MESSAGE_CATALOG:
        return Message(
            title=f"[MISSING: {key}]",
            body="메시지 카탈로그에 정의되지 않은 키입니다.",
            action="확인",
            severity="error",
            icon="❓",
        )

    entry = MESSAGE_CATALOG[key]
    mode = get_persona_mode()

    # title_key 방식 (vocabulary 활용) 또는 직접 dict 방식
    if "title_key" in entry:
        title = t(entry["title_key"], mode=mode)
        body = t(entry["body_key"], mode=mode)
        action = entry[f"action_key_{'lib' if mode == 'librarian' else 'ne'}"]
    else:
        title = entry["title"][mode]
        body_template = entry["body"][mode]
        action = entry["action"][mode]
        try:
            body = body_template.format(**kwargs)
        except KeyError:
            body = body_template

    return Message(
        title=title,
        body=body,
        action=action,
        severity=entry["severity"],
        icon=entry["icon"],
    )


def show_info(key: str, **kwargs: Any) -> Message:
    """정보 메시지 (show_error와 동일 인터페이스, severity만 info)."""
    return show_error(key, **kwargs)


# 친근한 톤 가이드라인 (자가 검증)
TONE_RULES = {
    "blame_user": ["잘못", "오류", "invalid", "illegal", "incorrect"],  # 회피 어휘
    "actionable_required": True,  # 모든 에러에 action 필수
    "plain_language_non_expert": True,  # 비전문가 모드: 전문 용어 X
    "humor_safe": False,  # 명료성 우선 (유머는 별도 채널)
}


def validate_message_tone(msg: Message) -> list[str]:
    """메시지 톤 자가 검증 (qa-validator·compliance-officer 통합용).

    Returns:
        위반 사항 리스트. 빈 리스트 = 통과.
    """
    violations = []

    for word in TONE_RULES["blame_user"]:
        if word in msg.body or word in msg.title:
            violations.append(f"사용자 비난 어휘: '{word}'")

    if not msg.action:
        violations.append("회복 행동(action) 누락")

    return violations
