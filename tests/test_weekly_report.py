"""Cycle 47 V3 Block 4 — weekly_report 회귀.

V3 §4.3 정합·통계 결정적 계산 검증·LLM 호출 0.
1주 데이터 부재 = graceful 메시지·있으면 메트릭 정확.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automation"))

from weekly_report import compute_metrics, render_markdown


def _ts(days_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()


class TestComputeMetricsEmpty:
    def test_no_rows_returns_error(self):
        m = compute_metrics([], {"daily": []})
        assert "error" in m
        assert "rows_found" in m

    def test_no_rows_includes_hint(self):
        m = compute_metrics([], {"daily": []})
        assert "Cycle 43" in m.get("hint", "")


class TestComputeMetricsBasic:
    def test_success_rate_all_completed(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(2)},
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(3)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M01_success_rate"] == 1.0
        assert m["cycles_total"] == 3

    def test_success_rate_mixed(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)},
            {"event": "cycle_end", "status": "BLOCKED", "ts": _ts(2)},
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(3)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M01_success_rate"] == pytest.approx(2 / 3)
        assert m["n_done"] == 2
        assert m["n_blocked"] == 1

    def test_done_blocked_ratio(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(2)},
            {"event": "cycle_end", "status": "BLOCKED", "ts": _ts(3)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M02_done_blocked_ratio"] == 2.0

    def test_done_blocked_ratio_zero_blocked(self):
        rows = [{"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)}]
        m = compute_metrics(rows, {"daily": []})
        # max(blocked, 1) division = M02 = n_done
        assert m["M02_done_blocked_ratio"] == 1.0

    def test_avg_iterations(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "iterations": 10, "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "iterations": 20, "ts": _ts(2)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M03_avg_iterations"] == 15.0


class TestComputeMetricsCost:
    def test_weekly_cost_from_usage_json(self):
        rows = [{"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)}]
        usage = {"daily": [{"cost_usd": 1.50}, {"cost_usd": 2.30}]}
        m = compute_metrics(rows, usage)
        assert m["M04_total_weekly_cost"] == pytest.approx(3.80)

    def test_weekly_cost_fallback_to_cycles(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "cost_usd": 0.50, "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "cost_usd": 1.20, "ts": _ts(2)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M04_total_weekly_cost"] == pytest.approx(1.70)

    def test_avg_cost_per_cycle(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "cost_usd": 1.00, "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "cost_usd": 3.00, "ts": _ts(2)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M04_avg_cost_per_cycle"] == pytest.approx(2.00)


class TestComputeMetricsCategoriesAndContext:
    def test_top_categories(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "category": "auth", "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "category": "auth", "ts": _ts(2)},
            {"event": "cycle_end", "status": "BLOCKED", "category": "payment", "ts": _ts(3)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M06_top_categories"]["auth"] == 2
        assert m["M06_top_categories"]["payment"] == 1

    def test_ctx_saturation_under_threshold(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "ctx_tokens": 50_000, "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "ctx_tokens": 100_000, "ts": _ts(2)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M09_ctx_saturation"] == 0.0

    def test_ctx_saturation_over_threshold(self):
        # V3 §4.2: 147k = 임계 (advertised 200k 대비 real ctx)
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "ctx_tokens": 50_000, "ts": _ts(1)},
            {"event": "cycle_end", "status": "COMPLETED", "ctx_tokens": 150_000, "ts": _ts(2)},
        ]
        m = compute_metrics(rows, {"daily": []})
        assert m["M09_ctx_saturation"] == 0.5


class TestRenderMarkdown:
    def test_empty_data_renders_warning(self):
        m = compute_metrics([], {"daily": []})
        md = render_markdown(m, [])
        assert "데이터 부족" in md
        assert "Weekly Ralph Report" in md

    def test_normal_data_renders_kpi(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "iterations": 5, "ts": _ts(1)},
        ]
        m = compute_metrics(rows, {"daily": [{"cost_usd": 0.50}]})
        md = render_markdown(m, [])
        assert "KPI" in md
        assert "Success rate" in md
        assert "100.0%" in md  # M01

    def test_low_success_triggers_action(self):
        rows = [{"event": "cycle_end", "status": "BLOCKED", "ts": _ts(1)}] * 10 + [
            {"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)}
        ]
        m = compute_metrics(rows, {"daily": []})
        md = render_markdown(m, [])
        assert "router unsafe" in md  # V3 §4.3 권장 액션

    def test_high_iterations_triggers_action(self):
        rows = [{"event": "cycle_end", "status": "COMPLETED", "iterations": 20, "ts": _ts(1)}] * 5
        m = compute_metrics(rows, {"daily": []})
        md = render_markdown(m, [])
        assert "PROMPT 분해" in md or "subagent" in md

    def test_high_cost_triggers_action(self):
        rows = [{"event": "cycle_end", "status": "COMPLETED", "cost_usd": 5.00, "ts": _ts(1)}]
        m = compute_metrics(rows, {"daily": []})
        md = render_markdown(m, [])
        assert "Haiku" in md  # cycle당 > $3 = Haiku 비중 ↑

    def test_ctx_saturation_triggers_action(self):
        rows = [
            {"event": "cycle_end", "status": "COMPLETED", "ctx_tokens": 150_000, "ts": _ts(1)}
        ] * 5
        m = compute_metrics(rows, {"daily": []})
        md = render_markdown(m, [])
        assert "서브에이전트 분리" in md or "ctx" in md


class TestV3Invariants:
    """V3 §4 핵심 invariants 검증."""

    def test_no_llm_call_in_compute(self):
        """13 메트릭 중 11 = 통계 결정적 (LLM 호출 0·V3 §4.10)."""
        # compute_metrics 함수 내 LLM 클라이언트 호출 X
        # anthropic·openai SDK import 0건 (의존성 0)
        import inspect

        import weekly_report as wr

        src = inspect.getsource(wr.compute_metrics)
        assert "anthropic" not in src.lower()
        assert "openai" not in src.lower()

    def test_threshold_70_pct(self):
        """V3 §4.2 M01 임계 = 70%."""
        # 70% 미달 = 권장 액션 발동
        rows = [{"event": "cycle_end", "status": "COMPLETED", "ts": _ts(1)}] * 6 + [
            {"event": "cycle_end", "status": "BLOCKED", "ts": _ts(1)}
        ] * 4
        m = compute_metrics(rows, {"daily": []})
        assert m["M01_success_rate"] == 0.6
        md = render_markdown(m, [])
        assert "router unsafe" in md
