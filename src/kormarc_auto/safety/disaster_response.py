"""도서관 재난 대응 매뉴얼 — Part 82+ 페인 #48 정합.

사서 페인:
- 자연재해 (지진·침수·화재·정전) = 자료 보호 부담
- 한국 도서관 = 재난 매뉴얼 부족 (일본 JLA 사례 참조)
- 코로나 = 비대면 + 방역 부담

해결: 6 재난 유형별 표준 매뉴얼 + 자동 체크리스트.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DisasterType = Literal[
    "earthquake",   # 지진
    "flood",        # 침수
    "fire",         # 화재
    "power_outage", # 정전
    "pandemic",     # 팬데믹
    "typhoon",      # 태풍·강풍
]


# 재난 유형별 표준 대응 (JLA + KISA + NLK 정합)
RESPONSE_PROTOCOL = {
    "earthquake": {
        "immediate": [
            "이용자·사서 안전 우선 (책상 아래 대피)",
            "출입문·비상구 확보",
            "고층 자료실 = 책장 사이 X",
        ],
        "after": [
            "이용자 인원 점검",
            "건물 손상 확인",
            "귀중 자료 안전 확인",
            "전기·가스 차단",
        ],
    },
    "flood": {
        "immediate": [
            "지하·1층 자료 = 즉시 위층 이동",
            "전기 차단",
            "출입 통제",
        ],
        "after": [
            "젖은 자료 = 동결 보존 (NLK 자료보존과 자문)",
            "건물 점검",
            "보험 신고",
        ],
    },
    "fire": {
        "immediate": [
            "119 즉시 신고",
            "이용자 즉시 대피 (안내 방송)",
            "비상구 안내",
            "초기 진화 시도 (소화기·CO2)",
        ],
        "after": [
            "인원 점검",
            "현장 보존",
            "자료 손실 평가",
        ],
    },
    "power_outage": {
        "immediate": [
            "비상 조명 활성화",
            "이용자 안내 방송 (대체 = 호각·확성기)",
            "엘리베이터 이용 X",
            "PC·서버 데이터 보호",
        ],
        "after": [
            "복구 대기·이용자 안전 우선",
            "한전 신고",
        ],
    },
    "pandemic": {
        "immediate": [
            "방역 매뉴얼 활성화",
            "마스크·소독제 비치",
            "거리 두기 안내",
            "비대면 서비스 (북 드라이브스루·우편) 활성",
        ],
        "after": [
            "확진자 발생 시 = 즉시 보건소 신고",
            "방역 강화",
            "이용자 안내",
        ],
    },
    "typhoon": {
        "immediate": [
            "출입문·창문 잠금",
            "옥외 시설 정리",
            "조기 폐관 결정",
        ],
        "after": [
            "건물 점검",
            "외부 자료 확인",
        ],
    },
}


@dataclass(frozen=True)
class DisasterChecklist:
    """재난 대응 체크리스트."""

    disaster_type: DisasterType
    immediate_actions: list[str]
    after_actions: list[str]
    emergency_contacts: dict[str, str]


def get_protocol(disaster_type: DisasterType) -> DisasterChecklist:
    """재난 유형별 매뉴얼 자동."""
    protocol = RESPONSE_PROTOCOL.get(disaster_type, {})
    return DisasterChecklist(
        disaster_type=disaster_type,
        immediate_actions=protocol.get("immediate", []),
        after_actions=protocol.get("after", []),
        emergency_contacts={
            "112": "범죄·긴급",
            "119": "화재·구급",
            "120": "다산콜센터·민원",
            "1577-0050": "기상청",
            "한전": "지역별 한전 본부",
            "관장": "(자관 설정)",
        },
    )


def render_response_card(disaster_type: DisasterType) -> str:
    """재난 대응 카드 markdown (사서 즉시 사용 가능)."""
    checklist = get_protocol(disaster_type)
    lines = [
        f"# 🚨 {disaster_type.upper()} 대응 매뉴얼",
        "",
        "## 1. 즉시 조치",
    ]
    for i, action in enumerate(checklist.immediate_actions, 1):
        lines.append(f"{i}. {action}")

    lines.extend(["", "## 2. 사후 조치"])
    for i, action in enumerate(checklist.after_actions, 1):
        lines.append(f"{i}. {action}")

    lines.extend(["", "## 3. 비상 연락처"])
    for k, v in checklist.emergency_contacts.items():
        lines.append(f"- **{k}**: {v}")

    return "\n".join(lines)


__all__ = [
    "RESPONSE_PROTOCOL",
    "DisasterChecklist",
    "DisasterType",
    "get_protocol",
    "render_response_card",
]
