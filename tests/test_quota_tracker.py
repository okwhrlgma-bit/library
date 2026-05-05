"""Cycle 13B P33 — quota tracker + CTA 회귀."""

from __future__ import annotations

from datetime import UTC, datetime

from kormarc_auto.quota import (
    GRACE_PERIOD_HOURS,
    PRE_WARNING_THRESHOLD,
    QuotaTracker,
    UsageEvent,
    personalized_upgrade_cta,
    quota_warning_message,
)
from kormarc_auto.quota.cta import quota_block_message
from kormarc_auto.quota.tracker import next_month_first_day


class TestThresholds:
    def test_pre_warning_at_80pct(self):
        assert PRE_WARNING_THRESHOLD == 0.80

    def test_grace_period_24h(self):
        assert GRACE_PERIOD_HOURS == 24


class TestQuotaTracker:
    def _t(self, count: int = 0) -> QuotaTracker:
        return QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=count)

    def test_normal_state_below_80pct(self):
        t = self._t(count=39)
        assert t.state() == "normal"

    def test_pre_warning_at_40_of_50(self):
        t = self._t(count=40)
        # 40/50 = 80%
        assert t.state() == "pre_warning"

    def test_at_limit_at_50(self):
        t = self._t(count=50)
        assert t.state() == "at_limit"

    def test_grace_after_start(self):
        t = self._t(count=50)
        t.start_grace(now=datetime(2026, 5, 5, 12, 0, tzinfo=UTC))
        # 12h 후 = 아직 grace
        assert t.state(now=datetime(2026, 5, 6, 0, 0, tzinfo=UTC)) == "grace"

    def test_blocked_after_grace_24h(self):
        t = self._t(count=50)
        t.start_grace(now=datetime(2026, 5, 5, 12, 0, tzinfo=UTC))
        # 25h 후 = blocked
        assert t.state(now=datetime(2026, 5, 6, 13, 0, tzinfo=UTC)) == "blocked"


class TestRecordUsageIdempotent:
    def test_same_record_id_counted_once(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50)
        assert t.record_usage("isbn-9788937437076") is True
        assert t.record_usage("isbn-9788937437076") is False  # idempotent
        assert t.current_count == 1

    def test_different_record_ids_counted(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50)
        t.record_usage("a")
        t.record_usage("b")
        t.record_usage("c")
        assert t.current_count == 3


class TestReset:
    def test_reset_clears_count_and_grace(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=50)
        t.start_grace(now=datetime.now(UTC))
        t.record_usage("a")
        t.reset_for_new_month()
        assert t.current_count == 0
        assert t.grace_started_at is None
        assert len(t.seen_record_ids) == 0


class TestUsageMetrics:
    def test_remaining_records(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=30)
        assert t.remaining_records() == 20

    def test_remaining_records_zero_when_over(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=60)
        assert t.remaining_records() == 0

    def test_usage_pct_capped_at_1(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=100)
        assert t.usage_pct() == 1.0

    def test_unlimited_plan_no_state_change(self):
        t = QuotaTracker(user_id="u1", plan_code="enterprise", monthly_limit=0)
        assert t.state() == "normal"


class TestPersonalizedCTA:
    def test_cta_recommends_school_for_500_avg(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=500)
        cta = personalized_upgrade_cta(t)
        # 500 × 1.5 = 750 → school (2000 한도)
        assert cta.recommended_plan == "school"

    def test_cta_recommends_small_for_low_usage(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=50)
        cta = personalized_upgrade_cta(t)
        # 50 × 1.5 = 75 → small (500)
        assert cta.recommended_plan == "small"

    def test_cta_recommends_public_for_high_usage(self):
        t = QuotaTracker(user_id="u1", plan_code="school", monthly_limit=2000, current_count=2000)
        cta = personalized_upgrade_cta(t)
        # 2000 × 1.5 = 3000 → public (10000)
        assert cta.recommended_plan == "public"

    def test_cta_safety_margin_at_least_1_5x(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=300)
        cta = personalized_upgrade_cta(t)
        assert cta.safety_margin_x >= 1.5

    def test_cta_does_not_leak_other_libraries(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=50)
        cta = personalized_upgrade_cta(t, library_name_hint="OURLIB")
        # 본인 데이터만·다른 도서관 데이터 노출 X
        for forbidden in ("내를건너서", "내건숲", "은평구공공"):
            assert forbidden not in cta.body


class TestMessages:
    def test_warning_message_includes_remaining(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=40)
        msg = quota_warning_message(t)
        assert "10건" in msg or "10" in msg
        assert "40" in msg

    def test_block_message_includes_24h_grace(self):
        t = QuotaTracker(user_id="u1", plan_code="free", monthly_limit=50, current_count=50)
        msg = quota_block_message(t)
        assert "24시간" in msg
        assert "다음달" in msg


class TestNextMonth:
    def test_next_month_first_day(self):
        from datetime import date as d

        assert next_month_first_day(d(2026, 5, 5)) == d(2026, 6, 1)
        assert next_month_first_day(d(2026, 5, 31)) == d(2026, 6, 1)

    def test_next_month_year_rollover(self):
        from datetime import date as d

        assert next_month_first_day(d(2026, 12, 15)) == d(2027, 1, 1)


class TestUsageEvent:
    def test_event_immutable(self):
        from dataclasses import FrozenInstanceError

        import pytest

        e = UsageEvent(user_id="u1", record_id="isbn-X", timestamp="2026-05-05T00:00:00Z")
        assert e.user_id == "u1"
        with pytest.raises(FrozenInstanceError):
            e.user_id = "u2"  # type: ignore[misc]
