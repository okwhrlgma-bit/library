"""Cycle 19B P32 — 5분 위저드 + activation 회귀."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from kormarc_auto.onboarding import (
    ACTIVATION_THRESHOLD_RECORDS,
    WIZARD_STEPS,
    advance_step,
    check_activation,
    initial_state,
    is_at_risk_of_churn,
    is_complete,
)
from kormarc_auto.onboarding.activation import trial_end_trigger
from kormarc_auto.onboarding.wizard import progress_percentage


class TestWizardSteps:
    def test_6_steps_in_catalog(self):
        # 5 단계 + complete
        assert len(WIZARD_STEPS) == 6
        assert WIZARD_STEPS[0] == "library_code"
        assert WIZARD_STEPS[-1] == "complete"

    def test_initial_state(self):
        s = initial_state("u1")
        assert s.current_step == "library_code"
        assert s.user_id == "u1"
        assert s.completed_at is None

    def test_full_5_step_flow(self):
        s = initial_state("u1")
        s = advance_step(s, step_data={"library_code": "OURLIB"})
        assert s.current_step == "classification"

        s = advance_step(s, step_data={"classification_system": "KDC6"})
        assert s.current_step == "hanja_880"

        s = advance_step(s, step_data={"enable_hanja_880": True})
        assert s.current_step == "output_format"

        s = advance_step(s, step_data={"output_formats": ["DLS", "KOLAS"]})
        assert s.current_step == "first_isbn"

        s = advance_step(s, step_data={"first_isbn": "9788937437076"})
        assert s.current_step == "complete"
        assert is_complete(s) is True

    def test_invalid_library_code_raises(self):
        s = initial_state("u1")
        with pytest.raises(ValueError, match="자관코드"):
            advance_step(s, step_data={"library_code": ""})

    def test_invalid_classification_raises(self):
        s = initial_state("u1")
        s.current_step = "classification"
        with pytest.raises(ValueError, match="분류체계"):
            advance_step(s, step_data={"classification_system": "INVALID"})

    def test_invalid_isbn_raises(self):
        s = initial_state("u1")
        s.current_step = "first_isbn"
        with pytest.raises(ValueError, match="ISBN-13"):
            advance_step(s, step_data={"first_isbn": "123"})

    def test_invalid_output_format_raises(self):
        s = initial_state("u1")
        s.current_step = "output_format"
        with pytest.raises(ValueError, match="지원"):
            advance_step(s, step_data={"output_formats": ["INVALID"]})

    def test_complete_idempotent(self):
        s = initial_state("u1")
        s.current_step = "complete"
        s.completed_at = "2026-05-06T00:00:00Z"
        # 재호출 안전
        result = advance_step(s, step_data={})
        assert result.current_step == "complete"

    def test_progress_percentage(self):
        s = initial_state("u1")
        # library_code = 0%
        assert progress_percentage(s) == 0
        s.current_step = "complete"
        assert progress_percentage(s) == 100


class TestActivation:
    def _signed_up(self, days_ago: int) -> datetime:
        return datetime.now(UTC) - timedelta(days=days_ago)

    def test_threshold_100_records(self):
        assert ACTIVATION_THRESHOLD_RECORDS == 100

    def test_activated_at_100_records(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(5),
            records_processed=100,
            reports_generated=1,
        )
        assert s.is_activated is True
        assert s.churn_risk == "safe"

    def test_not_activated_below_threshold(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(5),
            records_processed=50,
            reports_generated=1,
        )
        assert s.is_activated is False

    def test_safe_within_3_days(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(2),
            records_processed=0,
            reports_generated=0,
        )
        assert s.churn_risk == "safe"

    def test_watch_at_d7_with_activity(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(6),
            records_processed=20,
            reports_generated=0,
        )
        assert s.churn_risk == "watch"

    def test_at_risk_d10(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(10),
            records_processed=5,
            reports_generated=0,
        )
        assert s.churn_risk == "at_risk"
        assert is_at_risk_of_churn(s) is True

    def test_lost_d20_no_activity(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(20),
            records_processed=0,
            reports_generated=0,
        )
        assert s.churn_risk == "lost"
        assert is_at_risk_of_churn(s) is True

    def test_next_action_korean(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(10),
            records_processed=5,
            reports_generated=0,
        )
        assert "🔴" in s.next_action or "전화" in s.next_action

    def test_to_dict_complete(self):
        s = check_activation(
            user_id="u1",
            signed_up_at=self._signed_up(5),
            records_processed=100,
            reports_generated=1,
        )
        d = s.to_dict()
        for key in (
            "user_id",
            "is_activated",
            "records_processed",
            "churn_risk",
            "next_action",
        ):
            assert key in d


class TestTrialEnd:
    def test_d_minus_7_trigger(self):
        signed_up = datetime.now(UTC) - timedelta(days=7)
        msg = trial_end_trigger(signed_up_at=signed_up, trial_days=14)
        assert msg is not None
        assert "D-7" in msg

    def test_d_minus_3_trigger(self):
        signed_up = datetime.now(UTC) - timedelta(days=11)
        msg = trial_end_trigger(signed_up_at=signed_up, trial_days=14)
        assert msg is not None
        assert "D-3" in msg

    def test_d_zero_trigger(self):
        signed_up = datetime.now(UTC) - timedelta(days=14)
        msg = trial_end_trigger(signed_up_at=signed_up, trial_days=14)
        assert msg is not None
        assert "D-0" in msg or "freemium" in msg

    def test_no_trigger_d_minus_5(self):
        signed_up = datetime.now(UTC) - timedelta(days=9)
        msg = trial_end_trigger(signed_up_at=signed_up, trial_days=14)
        assert msg is None
