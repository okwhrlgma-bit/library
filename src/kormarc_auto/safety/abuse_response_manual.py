"""사서 폭언·민원 표준 응대 매뉴얼 — Part 77 정합 (서울시 7대 지침 + NLK).

사서 페인 (Part 77):
- 67.9% 폭언 경험 + 14.9% 성희롱·성추행
- 응대 일관성 X = 사서 자기 보호 X
- 표준 매뉴얼 X = 매번 결정 부담

해결: 표준 응대 자동·NLK 「도서관이용자 응대서비스 매뉴얼」 정합.
"""

from __future__ import annotations

from typing import Literal

ResponseLevel = Literal["calm", "warning", "escalate", "incident"]


# NLK 응대 매뉴얼 + 서울시 7대 지침 정합 표준 응대
RESPONSE_TEMPLATES = {
    "verbal_abuse": {
        "calm": (
            "선생님, 차분히 말씀해주시면 더 잘 도와드릴 수 있어요. "
            "어떤 점이 불편하셨는지 천천히 말씀해주세요."
        ),
        "warning": (
            "선생님, 도서관 이용 규칙에 따라 정중한 의사소통을 부탁드립니다. "
            "계속하시면 응대를 중단할 수 있음을 안내드립니다."
        ),
        "escalate": (
            "본 응대는 자동 기록되었습니다. 도서관 운영 정책에 따라 관리자에게 인계됩니다."
        ),
        "incident": (
            "응대 중단합니다. 관리자가 곧 안내드릴 예정이며, "
            "본 사건은 사서 보호를 위해 자동 기록됩니다."
        ),
    },
    "sexual_harassment": {
        "calm": "선생님의 발언이 부적절합니다. 도서관 이용에 도움 드릴 수 있는 부분만 말씀해주세요.",
        "warning": "이런 발언은 즉시 중단해주세요. 계속 시 신고됩니다.",
        "escalate": "성희롱은 법적 처벌 대상입니다. 본 응대는 즉시 기록·신고됩니다.",
        "incident": "응대 즉시 중단·기록·신고됩니다. 사서 보호가 우선입니다.",
    },
    "complaint": {
        "calm": (
            "선생님께 불편을 드려 죄송합니다. 어떤 부분이 마음에 안 드셨는지 "
            "구체적으로 말씀해주시면 개선하겠습니다."
        ),
        "warning": "선생님 의견 잘 들었습니다. 관리자에게 정확히 전달드리겠습니다.",
        "escalate": "관리자에게 즉시 인계합니다. 답변 받으실 수 있도록 연락처 부탁드립니다.",
        "incident": "관리자 직접 응대로 전환합니다.",
    },
    "physical_threat": {
        "calm": "선생님, 즉시 중단해주세요.",
        "warning": "물리적 위협은 즉시 신고됩니다. 응대 중단합니다.",
        "escalate": "112 신고됩니다. 관리자가 안내드립니다.",
        "incident": "112·관리자 즉시 호출. 사서 안전이 최우선입니다.",
    },
}


def get_response(
    *,
    incident_type: str,
    level: ResponseLevel = "calm",
) -> str:
    """표준 응대 답변 자동.

    Args:
        incident_type: verbal_abuse·sexual_harassment·complaint·physical_threat
        level: calm (1차)·warning (2차)·escalate (3차)·incident (즉시 신고)

    Returns:
        표준 응대 텍스트 (사서 = 그대로 사용 = 일관성·법적 보호)
    """
    templates = RESPONSE_TEMPLATES.get(incident_type, RESPONSE_TEMPLATES["complaint"])
    return templates.get(level, templates["calm"])


def determine_escalation_level(
    *,
    repeat_count: int = 1,
    severity: int = 1,  # 1~5
    abuse_type: str = "verbal_abuse",
) -> ResponseLevel:
    """반복·심각도 기반 자동 escalation.

    - 1차 = calm (대부분)
    - 2차·심각도 ≥3 = warning
    - 3차·심각도 ≥4 = escalate
    - 성희롱·물리적 위협·심각도 5 = 즉시 incident
    """
    if abuse_type in ("sexual_harassment", "physical_threat"):
        return "incident"
    if severity >= 5:
        return "incident"
    if repeat_count >= 3 or severity >= 4:
        return "escalate"
    if repeat_count >= 2 or severity >= 3:
        return "warning"
    return "calm"


__all__ = [
    "RESPONSE_TEMPLATES",
    "ResponseLevel",
    "determine_escalation_level",
    "get_response",
]
