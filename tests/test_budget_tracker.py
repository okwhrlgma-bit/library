"""Cycle 19A P49 — 예산 추적 + 회귀 진단 회귀."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from kormarc_auto.budget import (
    DAILY_USD_BUDGET,
    BudgetTracker,
    UsageRecord,
    detect_token_regression,
)
from kormarc_auto.budget.tracker import append_record, iter_records


@pytest.fixture
def isolated_budget(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_BUDGET_DIR", str(tmp_path / "budget"))
    yield tmp_path / "budget"


class TestUsageRecord:
    def test_now_factory(self):
        r = UsageRecord.now(
            task_kind="code-edit",
            model="claude-sonnet-4-6",
            input_tokens=1000,
            output_tokens=500,
            cost_usd=0.012,
        )
        assert r.timestamp.endswith("Z")
        assert r.cost_usd == 0.012

    def test_jsonl_serializable(self):
        import json

        r = UsageRecord.now(task_kind="X", model="m", input_tokens=1, output_tokens=1, cost_usd=0.0)
        line = r.to_jsonl()
        parsed = json.loads(line)
        assert parsed["task_kind"] == "X"


class TestAppendAndIter:
    def test_append_creates_file(self, isolated_budget):
        r = UsageRecord.now(
            task_kind="code-edit",
            model="claude-sonnet-4-6",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
        )
        target = append_record(r)
        assert target.exists()

    def test_iter_yields_all(self, isolated_budget):
        for i in range(3):
            append_record(
                UsageRecord.now(
                    task_kind="X",
                    model="m",
                    input_tokens=i * 100,
                    output_tokens=i * 50,
                    cost_usd=0.001 * i,
                )
            )
        records = list(iter_records())
        assert len(records) == 3


class TestBudgetState:
    def _seed(self, *, cost_usd: float, isolated_budget):
        ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        append_record(
            UsageRecord(
                timestamp=ts,
                task_kind="X",
                model="m",
                input_tokens=1000,
                output_tokens=500,
                cost_usd=cost_usd,
            )
        )

    def test_normal_state(self, isolated_budget):
        self._seed(cost_usd=1.0, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        assert t.state() == "normal"
        assert t.should_block_session() is False

    def test_warning_at_70pct(self, isolated_budget):
        self._seed(cost_usd=14.5, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        # 14.5 / 20 = 72.5% = warning
        assert t.state() == "warning"

    def test_near_limit_at_90pct_blocks(self, isolated_budget):
        self._seed(cost_usd=18.5, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        # 92.5% = near_limit
        assert t.state() == "near_limit"
        assert t.should_block_session() is True

    def test_exceeded_blocks(self, isolated_budget):
        self._seed(cost_usd=25.0, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        assert t.state() == "exceeded"
        assert t.should_block_session() is True

    def test_remaining_budget(self, isolated_budget):
        self._seed(cost_usd=5.0, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        assert t.remaining_budget_usd() == 15.0

    def test_status_message_includes_emoji(self, isolated_budget):
        self._seed(cost_usd=1.0, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        msg = t.status_message()
        assert "🟢" in msg or "$1" in msg

    def test_to_api_dict_complete(self, isolated_budget):
        self._seed(cost_usd=5.0, isolated_budget=isolated_budget)
        t = BudgetTracker(daily_usd_budget=20.0)
        d = t.to_api_dict()
        for key in ("today_usd", "remaining_today_usd", "state", "should_block_session"):
            assert key in d


class TestRegression:
    def test_normal_no_regression(self):
        f = detect_token_regression(
            task_kind="code-edit",
            baseline_token_samples=[10000, 11000, 12000],
            recent_token_samples=[10500, 11500, 11800],
        )
        assert f.severity == "normal"
        assert "✓" in f.note

    def test_alert_50pct_increase(self):
        f = detect_token_regression(
            task_kind="refactor",
            baseline_token_samples=[10000] * 5,
            recent_token_samples=[15000] * 5,
        )
        # 50% 증가 = alert
        assert f.severity == "alert"
        assert len(f.likely_causes) >= 4

    def test_critical_regression(self):
        f = detect_token_regression(
            task_kind="research",
            baseline_token_samples=[12000] * 3,
            recent_token_samples=[40000] * 3,
        )
        # 12K → 40K = +233% = critical
        assert f.severity == "critical"
        assert any("이상 패턴" in c for c in f.likely_causes)

    def test_empty_data_returns_normal(self):
        f = detect_token_regression(
            task_kind="X", baseline_token_samples=[], recent_token_samples=[]
        )
        assert f.severity == "normal"
        assert f.pct_change == 0

    def test_likely_causes_includes_v2_section(self):
        f = detect_token_regression(
            task_kind="X",
            baseline_token_samples=[10000],
            recent_token_samples=[15000],
        )
        # V2 §8.3 4 후보 = 모델·코드·CLAUDE.md·루프
        joined = " ".join(f.likely_causes)
        assert "모델" in joined
        assert "CLAUDE.md" in joined or "프롬프트" in joined


class TestDefaultBudget:
    def test_default_is_20_usd(self):
        # ENV 미설정 시 = $20
        assert DAILY_USD_BUDGET >= 20.0 - 0.01
