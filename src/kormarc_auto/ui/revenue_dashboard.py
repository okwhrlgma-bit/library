"""갈래 B Cycle 37 — 매출 통합 대시보드 (Streamlit).

3 영역 통합:
1. 차단점 (Cycle 25 next_blocker)
2. 예산 (Cycle 19A BudgetTracker)
3. Funnel (Cycle 14B weekly_report)

실행: streamlit run src/kormarc_auto/ui/revenue_dashboard.py
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def render_dashboard() -> None:
    """Streamlit 진입점."""
    import streamlit as st

    st.set_page_config(page_title="kormarc-auto 매출 대시보드", layout="wide")
    st.title("📊 kormarc-auto 매출 대시보드")
    st.caption("Cycle 37 통합·차단점 + 예산 + Funnel·매일 5분 cadence (operations.md 정합)")

    col1, col2, col3 = st.columns(3)

    # 1. 차단점 (Cycle 25)
    with col1:
        st.subheader("🎯 매출 차단점")
        try:
            from next_blocker import detect_blockers

            blockers = detect_blockers()
            if not blockers:
                st.success("✓ 차단점 0건")
            else:
                st.warning(f"{len(blockers)}건 (우선순위순)")
                for b in blockers[:5]:
                    emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(b.severity, "⚪")
                    st.markdown(f"{emoji} **{b.id}** ({b.severity})")
                    st.caption(b.description[:80])
        except Exception as exc:
            st.caption(f"(blocker 모듈 미로드: {type(exc).__name__})")

    # 2. 예산 (Cycle 19A)
    with col2:
        st.subheader("💰 일일 예산")
        try:
            from kormarc_auto.budget import BudgetTracker

            t = BudgetTracker()
            d = t.to_api_dict()
            state_emoji = {
                "normal": "🟢",
                "warning": "🟡",
                "near_limit": "🔴",
                "exceeded": "⛔",
            }.get(d["state"], "⚪")
            st.metric(
                label="오늘 사용 (USD)",
                value=f"${d['today_usd']:.4f}",
                delta=f"잔여 ${d['remaining_today_usd']:.4f}",
            )
            st.markdown(f"{state_emoji} **{d['state']}**·예산 ${d['daily_usd_budget']:.2f}")
            st.caption(f"지난 7일: ${d['last_7_days_usd']:.4f}")
            if d["should_block_session"]:
                st.error("⛔ 세션 차단 임계 도달")
        except Exception as exc:
            st.caption(f"(budget 모듈 미로드: {type(exc).__name__})")

    # 3. Funnel (Cycle 14B)
    with col3:
        st.subheader("📈 Funnel (지난 7일)")
        try:
            from kormarc_auto.analytics import calculate_funnel
            from kormarc_auto.analytics.events import iter_events

            events = list(iter_events())
            if not events:
                st.info("이벤트 0건·Plausible event 시작 후 표시")
            else:
                m = calculate_funnel(events, period="last_7d")
                for step, count in m.counts_by_step.items():
                    pct = m.conversion_rate_pct.get(step, 0.0)
                    st.markdown(f"**{step}**: {count}건 ({pct:.1f}%)")
        except Exception as exc:
            st.caption(f"(funnel 모듈 미로드: {type(exc).__name__})")

    st.markdown("---")
    st.subheader("🚀 다음 액션 (자동 추천)")
    try:
        from next_blocker import detect_blockers

        blockers = detect_blockers()
        if blockers:
            top = blockers[0]
            st.markdown(f"**1순위**: {top.id} — {top.next_action}")
            st.caption(f"소요: {top.estimated_unblock_days}일·영향: {top.revenue_impact}")
    except Exception:
        pass

    st.caption(
        "정합: docs/external-dependencies-matrix-2026-05.md · "
        "agent_docs/operations.md · API: GET /blockers /accuracy /pricing"
    )


if __name__ == "__main__":
    render_dashboard()


def get_dashboard_summary() -> dict:
    """API/CLI 호출용 요약 dict (Streamlit 외부에서도 사용)."""
    out = {"blockers": [], "budget": {}, "funnel": {}}
    try:
        from next_blocker import detect_blockers

        out["blockers"] = [asdict(b) for b in detect_blockers()[:5]]
    except Exception:
        pass
    try:
        from kormarc_auto.budget import BudgetTracker

        out["budget"] = BudgetTracker().to_api_dict()
    except Exception:
        pass
    try:
        from kormarc_auto.analytics import calculate_funnel
        from kormarc_auto.analytics.events import iter_events

        events = list(iter_events())
        m = calculate_funnel(events, period="last_7d")
        out["funnel"] = {
            "counts_by_step": m.counts_by_step,
            "conversion_rate_pct": m.conversion_rate_pct,
        }
    except Exception:
        pass
    return out
