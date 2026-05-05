"""갈래 B Cycle 12 (P37) — KOLAS III 마이그레이션 캠페인.

D-240 골든윈도우 (2026-12-31 KOLAS III 표준형 종료).
외부 매출 성장 보고서 P37 정합.
"""

from kormarc_auto.migration.countdown import (
    KOLAS3_END_DATE,
    Diagnosis,
    DiagnosisAnswer,
    MigrationUrgency,
    days_until_kolas3_end,
    diagnose_migration,
    timeline_actions_for_remaining_days,
)
from kormarc_auto.migration.press_release import (
    generate_press_release,
)

__all__ = [
    "KOLAS3_END_DATE",
    "Diagnosis",
    "DiagnosisAnswer",
    "MigrationUrgency",
    "days_until_kolas3_end",
    "diagnose_migration",
    "generate_press_release",
    "timeline_actions_for_remaining_days",
]
