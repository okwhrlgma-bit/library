"""Cycle 61 (ADR 0045 §C) — 3-단계 funnel 회귀.

사용자/추천자/결제자 분리 검증·LLM 호출 0·외부 858 옵트인 trial 임계.
"""

from __future__ import annotations

import pytest

from kormarc_auto.analytics.three_stage_funnel import (
    ADVOCATE_EVENTS,
    BUYER_EVENTS,
    USER_EVENTS,
    ThreeStageMetrics,
    calculate_three_stage,
    render_three_stage_summary,
    stage_health_signals,
)


class TestEventCatalog:
    def test_user_events_5(self):
        assert len(USER_EVENTS) >= 4
        assert "demo_start" in USER_EVENTS
        assert "signup" in USER_EVENTS
        assert "activation_100_records" in USER_EVENTS

    def test_advocate_events(self):
        assert "share_with_colleague" in ADVOCATE_EVENTS
        assert "loi_drafted" in ADVOCATE_EVENTS
        assert "champion_identified" in ADVOCATE_EVENTS

    def test_buyer_events(self):
        # 결제자 = 세금계산서·결제 인증·계약 등
        assert "tax_invoice_issued" in BUYER_EVENTS
        assert "payment_authorized" in BUYER_EVENTS
        assert "contract_signed" in BUYER_EVENTS
        assert "first_payment_received" in BUYER_EVENTS

    def test_no_event_overlap(self):
        # 3 단계 = 분리 (외부 858 보고서 결제자 ≠ 사용자)
        user = set(USER_EVENTS)
        advocate = set(ADVOCATE_EVENTS)
        buyer = set(BUYER_EVENTS)
        assert user.isdisjoint(advocate)
        assert advocate.isdisjoint(buyer)
        assert user.isdisjoint(buyer)


class TestCalculateThreeStage:
    def test_empty_events(self):
        m = calculate_three_stage([])
        assert m.user_count == 0
        assert m.advocate_count == 0
        assert m.buyer_count == 0
        assert m.user_to_advocate_pct == 0
        assert m.advocate_to_buyer_pct == 0
        assert m.user_to_buyer_pct == 0

    def test_user_only(self):
        events = [
            {"user_id": "u1", "event_name": "demo_start"},
            {"user_id": "u2", "event_name": "signup"},
        ]
        m = calculate_three_stage(events)
        assert m.user_count == 2
        assert m.advocate_count == 0
        assert m.buyer_count == 0

    def test_full_funnel(self):
        events = [
            {"user_id": "u1", "event_name": "demo_start"},
            {"user_id": "u1", "event_name": "share_with_colleague"},
            {"user_id": "u1", "event_name": "tax_invoice_issued"},
        ]
        m = calculate_three_stage(events)
        assert m.user_count == 1
        assert m.advocate_count == 1
        assert m.buyer_count == 1
        assert m.user_to_advocate_pct == 100.0
        assert m.user_to_buyer_pct == 100.0

    def test_typical_funnel_dropoff(self):
        # 100 사용자 → 30 추천자 → 6 결제자 (외부 858 옵트인 trial 6%)
        events = []
        for i in range(100):
            events.append({"user_id": f"u{i}", "event_name": "signup"})
        for i in range(30):
            events.append({"user_id": f"u{i}", "event_name": "share_with_colleague"})
        for i in range(6):
            events.append({"user_id": f"u{i}", "event_name": "first_payment_received"})

        m = calculate_three_stage(events)
        assert m.user_count == 100
        assert m.advocate_count == 30
        assert m.buyer_count == 6
        assert m.user_to_advocate_pct == 30.0
        assert m.advocate_to_buyer_pct == pytest.approx(20.0)
        assert m.user_to_buyer_pct == pytest.approx(6.0)

    def test_user_id_missing_skipped(self):
        events = [
            {"event_name": "signup"},  # user_id 없음
            {"user_id": "u1", "event_name": "signup"},
        ]
        m = calculate_three_stage(events)
        assert m.user_count == 1


class TestStageHealthSignals:
    def test_data_insufficient(self):
        m = ThreeStageMetrics(0, 0, 0, 0, 0, 0)
        s = stage_health_signals(m)
        assert "status" in s
        assert "데이터 부족" in s["status"]

    def test_all_below_threshold(self):
        # 모두 임계 미달 = 모두 ⚠
        m = ThreeStageMetrics(
            user_count=100,
            advocate_count=10,  # 10% (< 30%)
            buyer_count=1,  # 10% advocate→buyer (< 20%)
            user_to_advocate_pct=10.0,
            advocate_to_buyer_pct=10.0,
            user_to_buyer_pct=1.0,
        )
        s = stage_health_signals(m)
        assert "⚠" in s["user_to_advocate"]
        assert "⚠" in s["advocate_to_buyer"]
        assert "⚠" in s["overall"]

    def test_all_above_threshold(self):
        m = ThreeStageMetrics(
            user_count=100,
            advocate_count=40,
            buyer_count=10,
            user_to_advocate_pct=40.0,
            advocate_to_buyer_pct=25.0,
            user_to_buyer_pct=10.0,
        )
        s = stage_health_signals(m)
        assert "✅" in s["user_to_advocate"]
        assert "✅" in s["advocate_to_buyer"]
        assert "✅" in s["overall"]

    def test_zero_advocates_special_message(self):
        m = ThreeStageMetrics(
            user_count=10,
            advocate_count=0,
            buyer_count=0,
            user_to_advocate_pct=0,
            advocate_to_buyer_pct=0,
            user_to_buyer_pct=0,
        )
        s = stage_health_signals(m)
        assert "추천자 0건" in s["advocate_to_buyer"]


class TestRenderSummary:
    def test_renders_3_stages(self):
        m = ThreeStageMetrics(
            user_count=50,
            advocate_count=15,
            buyer_count=3,
            user_to_advocate_pct=30.0,
            advocate_to_buyer_pct=20.0,
            user_to_buyer_pct=6.0,
        )
        text = render_three_stage_summary(m)
        assert "사용자" in text
        assert "추천자" in text
        assert "결제자" in text
        assert "50" in text
        assert "15" in text
        assert "3" in text


class TestExternalReportInvariants:
    """외부 858 보고서·매출 보고서 임계 정합."""

    def test_advocate_threshold_30pct(self):
        # 사서 만족도·외부 보고서 P32 ≥ 30%
        m = ThreeStageMetrics(100, 25, 5, 25.0, 20.0, 5.0)
        s = stage_health_signals(m)
        assert "30%" in s["user_to_advocate"]

    def test_buyer_threshold_20pct(self):
        # 의사결정자 승인 ≥ 20%
        m = ThreeStageMetrics(100, 50, 5, 50.0, 10.0, 5.0)
        s = stage_health_signals(m)
        assert "20%" in s["advocate_to_buyer"]

    def test_overall_threshold_6pct(self):
        # 외부 858 옵트인 trial 표준 ≥ 6%
        m = ThreeStageMetrics(100, 30, 3, 30.0, 10.0, 3.0)
        s = stage_health_signals(m)
        assert "6%" in s["overall"]
