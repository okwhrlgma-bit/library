"""Cycle 78 — B2C 메트릭 회귀."""

from __future__ import annotations

from kormarc_auto.b2c import (
    ACTIVATION_THRESHOLD_RECORDS,
    MRR_TARGET_MONTHLY_KRW,
    SubscriptionTier,
    calculate_mrr,
    calculate_time_saved_value,
    estimate_churn_risk,
    is_user_activated,
)
from kormarc_auto.b2c.metrics import make_demo_snapshot, render_summary


class TestSubscriptionTier:
    def test_4_tiers_exist(self):
        tiers = list(SubscriptionTier)
        assert len(tiers) == 4
        assert SubscriptionTier.FREE in tiers
        assert SubscriptionTier.PERSONAL in tiers
        assert SubscriptionTier.PRO in tiers
        assert SubscriptionTier.FOUNDING in tiers


class TestMRRCalculation:
    def test_zero_users(self):
        assert calculate_mrr() == 0

    def test_personal_only(self):
        assert calculate_mrr(personal_count=10) == 99_000

    def test_pro_only(self):
        assert calculate_mrr(pro_count=5) == 99_500

    def test_founding_50pct_discount(self):
        # ₩4,950 = 영구 50%
        assert calculate_mrr(founding_count=10) == 49_500

    def test_combined(self):
        # 100 personal + 50 pro + 100 founding = 990K + 995K + 495K = 2.48M
        mrr = calculate_mrr(personal_count=100, pro_count=50, founding_count=100)
        assert mrr == 100 * 9_900 + 50 * 19_900 + 100 * 4_950
        assert mrr == 2_480_000


class TestActivation:
    def test_below_threshold_not_activated(self):
        assert is_user_activated(records_processed=99, has_report=True) is False

    def test_at_threshold_with_report_activated(self):
        assert is_user_activated(records_processed=100, has_report=True) is True

    def test_above_threshold_no_report_not_activated(self):
        # 100권 처리·but 보고서 X = activation X (Lenny 2.5x 정합)
        assert is_user_activated(records_processed=500, has_report=False) is False

    def test_threshold_constant(self):
        assert ACTIVATION_THRESHOLD_RECORDS == 100


class TestTimeSavedValue:
    def test_100_records(self):
        result = calculate_time_saved_value(100)
        # 100권 × 6분 = 600분 = 10시간 = ₩200,000 (시급 ₩20K)
        assert result["minutes_saved"] == "600분"
        assert "10.0시간" in result["hours_saved"]
        assert "200,000" in result["krw_saved"]

    def test_roi_with_saas(self):
        result = calculate_time_saved_value(100)
        # ₩200K 절감 / ₩9,900 SaaS = 약 20:1
        assert "20:1" in result["roi"] or "20" in result["roi"]

    def test_zero_records(self):
        result = calculate_time_saved_value(0)
        assert result["minutes_saved"] == "0분"

    def test_constitution_reference(self):
        result = calculate_time_saved_value(50)
        # 헌법 §0 = 권당 6분 절감 명시
        assert "6분" in result["context"] or "권당" in result["context"]


class TestChurnRisk:
    def test_active_under_14_days(self):
        assert estimate_churn_risk(days_since_last_use=5, records_processed=100) == "active"

    def test_onboarding_few_records(self):
        # records < 10·but 사용 중 = onboarding 단계
        assert estimate_churn_risk(days_since_last_use=3, records_processed=5) == "onboarding"

    def test_medium_d14_inactive(self):
        assert estimate_churn_risk(days_since_last_use=14, records_processed=100) == "medium"

    def test_high_d30(self):
        assert estimate_churn_risk(days_since_last_use=30, records_processed=100) == "high"

    def test_critical_d60(self):
        assert estimate_churn_risk(days_since_last_use=60, records_processed=100) == "critical"


class TestDemoSnapshot:
    def test_returns_valid_metrics(self):
        m = make_demo_snapshot()
        assert m.total_users == 50
        assert m.paid_users == 5
        assert m.free_users == 45
        assert m.mrr_krw == 5 * 9_900
        assert 0 <= m.target_progress_pct <= 100

    def test_render_includes_warning(self):
        m = make_demo_snapshot()
        text = render_summary(m)
        # invariant 11 정직 헤더 명시
        assert "정직 헤더" in text or "인터뷰 0건" in text or "시뮬" in text


class TestConstitutionInvariants:
    def test_target_mrr_reasonable(self):
        # ₩5M/월 = 시드 매출·SOM 500명 정합 (Cycle 68 ADR 0050)
        assert MRR_TARGET_MONTHLY_KRW == 5_000_000

    def test_no_user_pii_in_metrics(self):
        # SaaSMetrics dataclass = 카운트만·이메일·이름 X (헌법 §14·invariant 12)
        from dataclasses import fields

        from kormarc_auto.b2c import SaaSMetrics

        field_names = [f.name for f in fields(SaaSMetrics)]
        for forbidden in ("email", "name", "phone", "address"):
            assert forbidden not in field_names
