"""갈래 B Cycle 14B (P34) — 주간 funnel 리포트 (월요일 09:00 KST cron).

산출물:
- markdown 본문
- 코호트 비교 (지난 주 vs 4주 평균)
- 슬랙·이메일 발송 hooks (외부 키 ENV)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from kormarc_auto.analytics.events import FunnelEvent
from kormarc_auto.analytics.funnel import FUNNEL_STEPS, calculate_funnel


def _filter_window(
    events: list[FunnelEvent], *, start: datetime, end: datetime
) -> list[FunnelEvent]:
    out = []
    for ev in events:
        try:
            ts = datetime.strptime(ev.timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        except ValueError:
            continue
        if start <= ts < end:
            out.append(ev)
    return out


def generate_weekly_report(events: list[FunnelEvent], *, now: datetime | None = None) -> str:
    """주간 markdown 리포트 (지난 7일 vs 직전 4주 평균)."""
    if now is None:
        now = datetime.now(UTC)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    # 지난 주 (now - 7d ~ now)
    last_week_start = now - timedelta(days=7)
    last_week_events = _filter_window(events, start=last_week_start, end=now)
    last_week = calculate_funnel(last_week_events, period="last_7d")

    # 직전 4주 (now - 35d ~ now - 7d)
    prev_4w_start = now - timedelta(days=35)
    prev_4w_end = last_week_start
    prev_4w_events = _filter_window(events, start=prev_4w_start, end=prev_4w_end)
    prev_4w = calculate_funnel(prev_4w_events, period="prev_28d")

    lines = [
        f"# 주간 Funnel 리포트 ({now.strftime('%Y-%m-%d')} 기준)",
        "",
        "## 지난 7일 vs 직전 28일 평균",
        "",
        "| 단계 | 7일 | 28일 평균/주 | 변화 |",
        "|---|---:|---:|---:|",
    ]
    for step in FUNNEL_STEPS:
        last = last_week.counts_by_step.get(step, 0)
        prev_avg = prev_4w.counts_by_step.get(step, 0) / 4  # 주당 평균
        delta = last - prev_avg
        delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
        lines.append(f"| {step} | {last} | {prev_avg:.1f} | {delta_str} |")

    lines += [
        "",
        "## 단계별 conversion (지난 7일)",
        "",
        last_week.to_markdown(),
        "",
        "## 다음 액션 (자동 추천)",
    ]

    # 자동 권고 (단순 규칙)
    if last_week.unique_users_by_step.get("demo_start", 0) == 0:
        lines.append("- 🚨 demo_start = 0 = 트래픽 0·SEO/PR 점검")
    elif last_week.conversion_rate_pct.get("signup", 0) < 10:
        lines.append("- ⚠ demo → signup < 10% = 데모 onboarding UX 개선·5분 위저드 점검")
    elif last_week.conversion_rate_pct.get("activation", 0) < 50:
        lines.append("- ⚠ signup → activation < 50% = activation 정의 점검 (100건 + 보고서)")
    elif last_week.conversion_rate_pct.get("paid", 0) < 5:
        lines.append("- ⚠ upgrade → paid < 5% = 결제 flow 점검·CTA 개인화 강화 (P33)")
    else:
        lines.append("- ✓ funnel 정상·다음 사이클 = 트래픽 확장 (P35 SEO·P37 KOLAS3)")

    return "\n".join(lines)
