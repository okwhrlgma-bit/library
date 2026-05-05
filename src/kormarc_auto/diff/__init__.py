"""갈래 A Cycle 14A (P16·T4-5) — visible diff (재생성 변경 가시화).

목표: 사서 신뢰 = 무엇이 변했는지 명시·결정론 (Cycle 8) 정합 = 동일 입력 → empty diff
"""

from kormarc_auto.diff.mrc_diff import (
    DiffEntry,
    DiffSummary,
    DiffType,
    diff_records,
    format_diff_text,
    is_empty_diff,
)

__all__ = [
    "DiffEntry",
    "DiffSummary",
    "DiffType",
    "diff_records",
    "format_diff_text",
    "is_empty_diff",
]
