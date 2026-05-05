"""갈래 B Cycle 22 (P51·V2 §6.4) — Progressive Trust 권한 단계.

원칙 (V2 §6.4 정합):
- Level 1 = Read만
- Level 2 = + Edit
- Level 3 = + Write·Bash(npm:*)
- Level 4 = + Bash(*) (deny list 적용)
- Level 5 = + MCP write actions

승격 = 30회 연속 성공 → PR 자동 생성 (자동 승격 X·PO 승인 필수).
"""

from kormarc_auto.trust.progressive import (
    PROGRESSIVE_TRUST_LEVELS,
    SUCCESS_THRESHOLD,
    AutomationRecord,
    TrustLevel,
    TrustState,
    can_promote,
    record_automation_outcome,
    suggest_next_level,
)

__all__ = [
    "PROGRESSIVE_TRUST_LEVELS",
    "SUCCESS_THRESHOLD",
    "AutomationRecord",
    "TrustLevel",
    "TrustState",
    "can_promote",
    "record_automation_outcome",
    "suggest_next_level",
]
