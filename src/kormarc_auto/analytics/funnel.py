"""갈래 B Cycle 14B (P34) — 6단 funnel 계산.

ChartMogul·OpenView 2025 정합:
- 6단: visit → demo_start → signup → activation → quota_warning → upgrade_clicked → paid
- 단계별 conversion %·코호트별 (월·플랜·도서관 유형)
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from kormarc_auto.analytics.events import EVENT_CATALOG, EventName, FunnelEvent

FUNNEL_STEPS: list[EventName] = list(EVENT_CATALOG)


@dataclass
class FunnelMetrics:
    """funnel 통계 결과."""

    period: str  # "2026-05" 또는 "all"
    counts_by_step: dict[str, int] = field(default_factory=dict)
    unique_users_by_step: dict[str, int] = field(default_factory=dict)
    conversion_rate_pct: dict[str, float] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [
            f"# Funnel ({self.period})",
            "",
            "| 단계 | 이벤트 수 | 고유 사용자 | 직전 → conversion |",
            "|---|---:|---:|---:|",
        ]
        for step in FUNNEL_STEPS:
            cnt = self.counts_by_step.get(step, 0)
            uniq = self.unique_users_by_step.get(step, 0)
            conv = self.conversion_rate_pct.get(step, 0.0)
            conv_str = f"{conv:.1f}%" if step != FUNNEL_STEPS[0] else "—"
            lines.append(f"| {step} | {cnt} | {uniq} | {conv_str} |")
        return "\n".join(lines)


def calculate_funnel(events: list[FunnelEvent], *, period: str = "all") -> FunnelMetrics:
    """이벤트 목록 → 6단 funnel 계산.

    conversion = 단계 N의 unique users / 단계 N-1 unique users (직전 비율).
    """
    counts: Counter[str] = Counter()
    users_by_step: dict[str, set[str]] = defaultdict(set)

    for ev in events:
        counts[ev.name] += 1
        users_by_step[ev.name].add(ev.anon_user_id)

    counts_dict = {step: counts.get(step, 0) for step in FUNNEL_STEPS}
    uniq_dict = {step: len(users_by_step.get(step, set())) for step in FUNNEL_STEPS}

    conv: dict[str, float] = {}
    for i, step in enumerate(FUNNEL_STEPS):
        if i == 0:
            conv[step] = 100.0  # 첫 단계 = 100%
            continue
        prev_step = FUNNEL_STEPS[i - 1]
        prev_count = uniq_dict.get(prev_step, 0)
        cur_count = uniq_dict.get(step, 0)
        if prev_count == 0:
            conv[step] = 0.0
        else:
            conv[step] = round(cur_count / prev_count * 100, 2)

    return FunnelMetrics(
        period=period,
        counts_by_step=counts_dict,
        unique_users_by_step=uniq_dict,
        conversion_rate_pct=conv,
    )
