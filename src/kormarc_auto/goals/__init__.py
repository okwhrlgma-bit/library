"""갈래 B Cycle 22 (P52·V2 §5) — Goal Decomposer 일일 자율 루프.

5계층 = Goal → Strategy → Initiative → Task → Action.
상위 3 = PO 결정·하위 2 = 자동.
"""

from kormarc_auto.goals.decomposer import (
    FORBIDDEN_ACTIONS,
    Action,
    GoalHierarchy,
    is_forbidden_action,
    suggest_daily_actions,
)

__all__ = [
    "FORBIDDEN_ACTIONS",
    "Action",
    "GoalHierarchy",
    "is_forbidden_action",
    "suggest_daily_actions",
]
