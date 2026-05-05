"""Cycle 14B P34 — funnel + 주간 리포트 회귀."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from kormarc_auto.analytics import (
    EVENT_CATALOG,
    FUNNEL_STEPS,
    FunnelEvent,
    calculate_funnel,
    generate_weekly_report,
    record_event,
)
from kormarc_auto.analytics.events import _anon_id, iter_events


@pytest.fixture
def isolated_analytics(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_ANALYTICS_DIR", str(tmp_path / "analytics"))
    yield tmp_path / "analytics"


class TestAnonId:
    def test_same_email_same_hash(self):
        assert _anon_id("user@example.com") == _anon_id("user@example.com")

    def test_different_email_different_hash(self):
        assert _anon_id("a@example.com") != _anon_id("b@example.com")

    def test_anon_prefix(self):
        assert _anon_id("user@example.com").startswith("u-")

    def test_no_email_leak_in_hash(self):
        h = _anon_id("user@example.com")
        assert "user@example.com" not in h
        assert "@" not in h


class TestEventRecording:
    def test_event_factory_now(self):
        e = FunnelEvent.now("signup", user_email="a@example.com")
        assert e.name == "signup"
        assert e.anon_user_id.startswith("u-")
        assert "@" not in e.anon_user_id  # PIPA 정합

    def test_record_event_creates_jsonl(self, isolated_analytics):
        e = FunnelEvent.now("demo_start", user_email="a@example.com")
        target = record_event(e)
        assert target.exists()
        content = target.read_text(encoding="utf-8")
        assert "demo_start" in content
        assert "a@example.com" not in content  # leak 0

    def test_iter_events_yields_all(self, isolated_analytics):
        for name in ("demo_start", "signup", "activation"):
            record_event(FunnelEvent.now(name, user_email="a@example.com"))
        events = list(iter_events())
        assert len(events) == 3


class TestFunnelCalculation:
    def _make_events(self) -> list[FunnelEvent]:
        ts = "2026-05-05T00:00:00Z"
        return (
            [
                FunnelEvent(
                    name="demo_start", timestamp=ts, anon_user_id=f"u-{i}", plan_code="free"
                )
                for i in range(100)
            ]
            + [
                FunnelEvent(name="signup", timestamp=ts, anon_user_id=f"u-{i}", plan_code="free")
                for i in range(20)
            ]
            + [
                FunnelEvent(
                    name="activation", timestamp=ts, anon_user_id=f"u-{i}", plan_code="free"
                )
                for i in range(10)
            ]
            + [
                FunnelEvent(
                    name="upgrade_clicked", timestamp=ts, anon_user_id=f"u-{i}", plan_code="free"
                )
                for i in range(5)
            ]
            + [
                FunnelEvent(name="paid", timestamp=ts, anon_user_id=f"u-{i}", plan_code="small")
                for i in range(2)
            ]
        )

    def test_6_steps_in_catalog(self):
        assert len(FUNNEL_STEPS) == 6
        assert FUNNEL_STEPS[0] == "demo_start"
        assert FUNNEL_STEPS[-1] == "paid"

    def test_counts_correct(self):
        m = calculate_funnel(self._make_events())
        assert m.counts_by_step["demo_start"] == 100
        assert m.counts_by_step["signup"] == 20
        assert m.counts_by_step["paid"] == 2

    def test_unique_users_correct(self):
        m = calculate_funnel(self._make_events())
        assert m.unique_users_by_step["demo_start"] == 100
        assert m.unique_users_by_step["signup"] == 20

    def test_conversion_rates(self):
        m = calculate_funnel(self._make_events())
        # demo_start = 100% (첫 단계)
        assert m.conversion_rate_pct["demo_start"] == 100.0
        # signup / demo_start = 20/100 = 20%
        assert m.conversion_rate_pct["signup"] == 20.0
        # activation / signup = 10/20 = 50%
        assert m.conversion_rate_pct["activation"] == 50.0

    def test_to_markdown_includes_steps(self):
        m = calculate_funnel(self._make_events(), period="2026-05")
        md = m.to_markdown()
        for step in FUNNEL_STEPS:
            assert step in md
        assert "2026-05" in md

    def test_zero_prev_step_no_division_error(self):
        # signup만·demo_start = 0
        ts = "2026-05-05T00:00:00Z"
        events = [FunnelEvent(name="signup", timestamp=ts, anon_user_id="u-1", plan_code="free")]
        m = calculate_funnel(events)
        assert m.conversion_rate_pct["signup"] == 0.0


class TestWeeklyReport:
    def _gen_events(self, *, count_per_day: int = 5, days: int = 35) -> list[FunnelEvent]:
        base = datetime(2026, 5, 5, 0, 0, tzinfo=UTC)
        out = []
        for d in range(days):
            ts = (base - timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for i in range(count_per_day):
                out.append(
                    FunnelEvent(
                        name="demo_start",
                        timestamp=ts,
                        anon_user_id=f"u-d{d}-i{i}",
                        plan_code="free",
                    )
                )
        return out

    def test_report_has_header_and_table(self):
        events = self._gen_events()
        report = generate_weekly_report(events, now=datetime(2026, 5, 5, tzinfo=UTC))
        assert "주간 Funnel 리포트" in report
        assert "지난 7일" in report
        assert "직전 28일" in report

    def test_report_includes_recommendation(self):
        events = self._gen_events(count_per_day=0, days=0)
        report = generate_weekly_report(events, now=datetime(2026, 5, 5, tzinfo=UTC))
        # demo_start = 0 → SEO 점검 권고
        assert "SEO" in report or "트래픽" in report


class TestPipaCompliance:
    def test_event_no_email_in_jsonl(self, isolated_analytics):
        e = FunnelEvent.now("signup", user_email="leakemail@example.com")
        target = record_event(e)
        content = target.read_text(encoding="utf-8")
        assert "leakemail" not in content
        assert "@" not in content  # 이메일 leak 0

    def test_event_no_ip_field(self):
        e = FunnelEvent.now("demo_start", user_email="a@example.com")
        # IP·UA 필드 자체가 없음 (Plausible no-cookie 정합)
        from dataclasses import asdict

        d = asdict(e)
        assert "ip" not in d
        assert "user_agent" not in d
        assert "ua" not in d

    def test_event_catalog_size(self):
        # 6개 = funnel 단계 (외부 보고서 P34)
        assert len(EVENT_CATALOG) == 6
