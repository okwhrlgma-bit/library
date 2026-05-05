"""갈래 B Cycle 14B (P34·외부 매출 보고서) — Funnel 측정 + 주간 리포트.

Plausible 호환·PIPA 정합 (개인정보 0개·IP/UA 익명화).
"""

from kormarc_auto.analytics.events import (
    EVENT_CATALOG,
    EventName,
    FunnelEvent,
    record_event,
)
from kormarc_auto.analytics.funnel import (
    FUNNEL_STEPS,
    FunnelMetrics,
    calculate_funnel,
)
from kormarc_auto.analytics.weekly_report import (
    generate_weekly_report,
)

__all__ = [
    "EVENT_CATALOG",
    "FUNNEL_STEPS",
    "EventName",
    "FunnelEvent",
    "FunnelMetrics",
    "calculate_funnel",
    "generate_weekly_report",
    "record_event",
]
