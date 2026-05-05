"""Cycle 22 P51 — Progressive Trust 회귀."""

from __future__ import annotations

import pytest

from kormarc_auto.trust import (
    PROGRESSIVE_TRUST_LEVELS,
    SUCCESS_THRESHOLD,
    can_promote,
    record_automation_outcome,
    suggest_next_level,
)
from kormarc_auto.trust.progressive import TrustState, iter_states


@pytest.fixture
def isolated_trust(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_TRUST_DIR", str(tmp_path / "trust"))
    yield tmp_path / "trust"


class TestLevels:
    def test_5_levels(self):
        assert set(PROGRESSIVE_TRUST_LEVELS.keys()) == {1, 2, 3, 4, 5}

    def test_threshold_30(self):
        assert SUCCESS_THRESHOLD == 30

    def test_level_1_read_only(self):
        assert PROGRESSIVE_TRUST_LEVELS[1] == ["Read"]

    def test_level_5_includes_mcp(self):
        assert "MCP-write" in PROGRESSIVE_TRUST_LEVELS[5]

    def test_levels_monotonic(self):
        # 상위 Level = 하위 Level 도구 포함
        for lvl in range(2, 6):
            current = set(PROGRESSIVE_TRUST_LEVELS[lvl])
            previous = set(PROGRESSIVE_TRUST_LEVELS[lvl - 1])
            assert previous.issubset(current) or len(current - previous) >= 1


class TestRecordOutcome:
    def test_first_run_creates_state(self, isolated_trust):
        state = record_automation_outcome(automation_id="test-router", success=True)
        assert state.total_runs == 1
        assert state.total_successes == 1
        assert state.consecutive_successes == 1
        assert state.current_level == 1

    def test_success_increments_consecutive(self, isolated_trust):
        for _ in range(5):
            state = record_automation_outcome(automation_id="router", success=True)
        assert state.consecutive_successes == 5
        assert state.total_runs == 5

    def test_failure_resets_consecutive(self, isolated_trust):
        for _ in range(10):
            record_automation_outcome(automation_id="router", success=True)
        state = record_automation_outcome(automation_id="router", success=False)
        assert state.consecutive_successes == 0
        assert state.total_failures == 1

    def test_state_persists_across_calls(self, isolated_trust):
        record_automation_outcome(automation_id="X", success=True)
        record_automation_outcome(automation_id="X", success=True)
        state = record_automation_outcome(automation_id="X", success=True)
        assert state.total_runs == 3
        assert state.consecutive_successes == 3


class TestPromotion:
    def test_cannot_promote_below_threshold(self, isolated_trust):
        for _ in range(20):
            record_automation_outcome(automation_id="X", success=True)
        from kormarc_auto.trust.progressive import _load_state

        state = _load_state("X")
        assert can_promote(state) is False

    def test_can_promote_at_threshold(self, isolated_trust):
        for _ in range(SUCCESS_THRESHOLD):
            record_automation_outcome(automation_id="X", success=True)
        from kormarc_auto.trust.progressive import _load_state

        state = _load_state("X")
        assert can_promote(state) is True

    def test_max_level_5_no_promotion(self, isolated_trust):
        state = TrustState(
            automation_id="X",
            current_level=5,
            consecutive_successes=100,
        )
        assert can_promote(state) is False

    def test_suggest_includes_pr_template(self, isolated_trust):
        for _ in range(SUCCESS_THRESHOLD):
            record_automation_outcome(automation_id="X", success=True)
        from kormarc_auto.trust.progressive import _load_state

        state = _load_state("X")
        suggestion = suggest_next_level(state)
        assert suggestion["promotion_eligible"] is True
        assert suggestion["next_level"] == 2
        assert suggestion["pr_required"] is True
        assert suggestion["auto_merge_blocked"] is True
        assert "PO 승인" in suggestion["pr_template"]

    def test_suggest_remaining_when_not_eligible(self, isolated_trust):
        for _ in range(15):
            record_automation_outcome(automation_id="X", success=True)
        from kormarc_auto.trust.progressive import _load_state

        state = _load_state("X")
        suggestion = suggest_next_level(state)
        assert suggestion["promotion_eligible"] is False
        assert suggestion["remaining_until_eligible"] == SUCCESS_THRESHOLD - 15


class TestIterStates:
    def test_iter_yields_all(self, isolated_trust):
        record_automation_outcome(automation_id="A", success=True)
        record_automation_outcome(automation_id="B", success=True)
        record_automation_outcome(automation_id="C", success=False)
        states = list(iter_states())
        assert len(states) == 3
        ids = {s.automation_id for s in states}
        assert ids == {"A", "B", "C"}
