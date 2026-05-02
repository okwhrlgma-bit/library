"""야간 사서 안전 프로토콜 — Part 82+ 페인 #41 정합 (P14 보강).

사서 페인 (P14 야간):
- 야간 단독 = 사고 위험
- 4-5명 정상 vs 1명 야간

해결: 자동 안전 체크리스트 + 비상 연락 + 위치 공유.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

CheckType = Literal["entry", "midnight", "exit", "emergency"]


# 야간 사서 안전 체크리스트 (NLK 권장 + KSLA 정합)
NIGHT_CHECKLIST = {
    "entry": [
        "출입문 잠금 확인",
        "보안 시스템 활성화",
        "비상 연락처 확인 (관장·경비)",
        "비상 약품·소화기 위치",
        "이용자 잔존 확인",
    ],
    "midnight": [
        "층별 점검 (이용자 잔존 X)",
        "전원·조명 정리",
        "대출·반납 정리",
        "도서관 자동 잠금 시간 확인",
    ],
    "exit": [
        "최종 점검 (모든 출입문)",
        "보안 시스템 활성화",
        "전원 차단",
        "관장에 퇴근 보고",
    ],
    "emergency": [
        "112·119 즉시 신고",
        "관장 즉시 보고",
        "이용자 안전 우선",
        "현장 보존",
    ],
}


@dataclass(frozen=True)
class SafetyCheck:
    """안전 점검 1건."""

    check_type: CheckType
    librarian_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_items: list[str] = field(default_factory=list)
    issues_found: list[str] = field(default_factory=list)


def get_checklist(check_type: CheckType) -> list[str]:
    """체크 유형별 항목 반환."""
    return NIGHT_CHECKLIST.get(check_type, [])


def render_safety_log(checks: list[SafetyCheck]) -> str:
    """안전 점검 일지 markdown (관장 보고용)."""
    lines = ["# 야간 안전 점검 일지", ""]
    for check in checks:
        lines.append(f"## {check.check_type} — {check.timestamp[:19]}")
        lines.append(f"사서: {check.librarian_name}")
        lines.append("### 완료 항목")
        for item in check.completed_items:
            lines.append(f"- ✅ {item}")
        if check.issues_found:
            lines.append("### 발견 이슈")
            for issue in check.issues_found:
                lines.append(f"- ⚠ {issue}")
        lines.append("")
    return "\n".join(lines)


def emergency_contact_info(library_config: dict) -> dict:
    """비상 연락처 자동 추출 (자관 config)."""
    return {
        "112": "범죄·긴급",
        "119": "화재·구급",
        "관장": library_config.get("director_phone", "(미설정)"),
        "경비실": library_config.get("security_phone", "(미설정)"),
        "kormarc-auto 지원": "okwhrlgma@gmail.com",
    }


__all__ = [
    "NIGHT_CHECKLIST",
    "CheckType",
    "SafetyCheck",
    "emergency_contact_info",
    "get_checklist",
    "render_safety_log",
]
