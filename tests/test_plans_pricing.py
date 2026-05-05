"""Cycle 11 P31 — 4 플랜 가격·할인 회귀."""

from __future__ import annotations

import pytest

from kormarc_auto.billing import (
    BUNDLE_DISCOUNTS,
    FOUNDING_MEMBER,
    PLANS,
    apply_bundle_discount,
    apply_cycle_discount,
    apply_founding_discount,
    calculate_quote,
    get_plan,
    list_plans,
)


class TestPlanCatalog:
    def test_5_plans_exist(self):
        assert set(PLANS.keys()) == {"free", "small", "school", "public", "enterprise"}

    def test_list_plans_returns_5(self):
        assert len(list_plans()) == 5

    def test_get_plan_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown plan"):
            get_plan("invalid")

    def test_default_prices_match_adr_0026(self):
        assert PLANS["small"].monthly_krw == 30000
        assert PLANS["school"].monthly_krw == 50000
        assert PLANS["public"].monthly_krw == 150000
        assert PLANS["enterprise"].monthly_krw == 300000
        assert PLANS["free"].monthly_krw == 0

    def test_free_50_records_per_month(self):
        # 외부 매출 보고서 P32 정합 (50건 freemium·옵트인)
        assert PLANS["free"].monthly_records == 50

    def test_enterprise_unlimited(self):
        assert PLANS["enterprise"].monthly_records >= 999_999_999
        assert PLANS["enterprise"].sso_audit_log is True
        assert PLANS["enterprise"].csap_environment is True

    def test_korean_library_law_naming(self):
        # 도서관법 정합 명명 (외부 858 출처 §4.1)
        assert "작은도서관" in PLANS["small"].label
        assert "학교도서관" in PLANS["school"].label
        assert "공공도서관" in PLANS["public"].label
        assert "기관" in PLANS["enterprise"].label


class TestEnvOverride:
    def test_env_override_small_price(self, monkeypatch):
        monkeypatch.setenv("KORMARC_PRICE_SMALL_KRW", "25000")
        # 모듈 재로드 필요
        import importlib

        from kormarc_auto.billing import plans

        importlib.reload(plans)
        assert plans.PLANS["small"].monthly_krw == 25000

        # 정합 복원
        monkeypatch.delenv("KORMARC_PRICE_SMALL_KRW", raising=False)
        importlib.reload(plans)


class TestBundleDiscount:
    def test_no_discount_for_1_branch(self):
        amount, pct = apply_bundle_discount(100_000, 1)
        assert amount == 100_000
        assert pct == 0.0

    def test_5_branch_10pct(self):
        amount, pct = apply_bundle_discount(100_000, 5)
        assert pct == 0.10
        assert amount == 90_000

    def test_10_branch_15pct(self):
        amount, pct = apply_bundle_discount(100_000, 10)
        assert pct == 0.15
        assert amount == 85_000

    def test_25_branch_20pct(self):
        amount, pct = apply_bundle_discount(100_000, 25)
        assert pct == 0.20
        assert amount == 80_000

    def test_100_branch_25pct_education_office(self):
        amount, pct = apply_bundle_discount(100_000, 100)
        assert pct == 0.25
        assert amount == 75_000

    def test_threshold_max_picked_when_multiple_apply(self):
        _amount, pct = apply_bundle_discount(100_000, 50)
        # 50 >= 25 = 20% 적용 (100+ 미달)
        assert pct == 0.20


class TestCycleDiscount:
    def test_monthly_no_discount(self):
        assert apply_cycle_discount(50_000, "monthly") == 50_000

    def test_quarterly_5pct_discount(self):
        # 50,000 × 3 × 0.95 = 142,500
        assert apply_cycle_discount(50_000, "quarterly") == 142_500

    def test_annual_17pct_discount(self):
        # 50,000 × 12 × 0.83 = 498,000 (ChartMogul 표준)
        assert apply_cycle_discount(50_000, "annual") == 498_000

    def test_unknown_cycle_raises(self):
        with pytest.raises(ValueError):
            apply_cycle_discount(50_000, "biennial")  # type: ignore[arg-type]


class TestFoundingMember:
    def test_default_50pct_discount(self):
        assert FOUNDING_MEMBER.discount_pct == 0.50

    def test_seat_limit_100(self):
        assert FOUNDING_MEMBER.seat_limit == 100

    def test_annual_only_ltd_blocked(self):
        # 핵심 의사결정 #3: LTD 금지·연간결제 의무
        assert FOUNDING_MEMBER.annual_only is True
        assert FOUNDING_MEMBER.permanent_lock_in is True

    def test_apply_founding_50pct(self):
        assert apply_founding_discount(100_000, founding_member=True) == 50_000

    def test_apply_founding_off_no_change(self):
        assert apply_founding_discount(100_000, founding_member=False) == 100_000


class TestCalculateQuote:
    def test_simple_small_plan_monthly(self):
        q = calculate_quote(plan_code="small", branch_count=1, cycle="monthly")
        assert q["plan_code"] == "small"
        assert q["monthly_per_branch_krw"] == 30_000
        assert q["bundle_discount_pct"] == 0.0
        assert q["cycle_discount_pct"] == 0.0
        assert q["subtotal_krw"] == 30_000
        assert q["vat_krw"] == 3_000
        assert q["grand_total_krw"] == 33_000

    def test_public_plan_5_branch_annual(self):
        q = calculate_quote(plan_code="public", branch_count=5, cycle="annual")
        # 150,000 × 5 = 750,000 monthly
        # bundle 10% = 675,000
        # annual 17% = 675,000 × 12 × 0.83 = 6,723,000
        # VAT 10%
        assert q["bundle_discount_pct"] == 0.10
        assert q["cycle_discount_pct"] == 0.17
        assert q["subtotal_krw"] == 6_723_000
        assert q["vat_krw"] == 672_300
        assert q["grand_total_krw"] == 7_395_300

    def test_founding_member_stacked_with_annual(self):
        q = calculate_quote(
            plan_code="public", branch_count=1, cycle="annual", founding_member=True
        )
        # 150,000 × 1 = 150,000 → bundle 0% = 150,000
        # annual 17% = 150,000 × 12 × 0.83 = 1,494,000
        # founding 50% = 747,000
        assert q["founding_discount_pct"] == 0.50
        assert q["subtotal_krw"] == 747_000

    def test_70pct_discount_cap_enforced(self):
        # 묶음 25% + Founding 50% + annual 17% = ~71% = 70% 상한 적용
        q = calculate_quote(
            plan_code="public",
            branch_count=100,
            cycle="annual",
            founding_member=True,
        )
        assert q["total_discount_pct"] <= 0.70 + 0.001  # 부동소수 여유

    def test_vat_separate(self):
        q = calculate_quote(plan_code="small")
        assert q["vat_rate"] == 0.10
        assert q["grand_total_krw"] == q["subtotal_krw"] + q["vat_krw"]

    def test_quote_valid_30_days(self):
        q = calculate_quote(plan_code="small")
        assert q["valid_until_days"] == 30

    def test_currency_krw(self):
        q = calculate_quote(plan_code="small")
        assert q["currency"] == "KRW"

    def test_unknown_plan_raises(self):
        with pytest.raises(ValueError):
            calculate_quote(plan_code="invalid")


class TestExternalReportCompliance:
    """외부 매출 성장 보고서 P31 게이트 검증."""

    def test_annual_discount_within_industry_standard_16_17pct(self):
        # ChartMogul·Recurly·Notion 표준 = 16.7% (≈ 2개월 무료)
        assert apply_cycle_discount(100, "annual") == 996  # 100×12×0.83

    def test_no_lifetime_deal_in_plans(self):
        for plan in PLANS.values():
            assert "lifetime" not in plan.code.lower()
            assert "LTD" not in plan.label

    def test_recommended_plan_marked_in_label(self):
        # 외부 보고서 P31: "공공도서관 ⭐추천"
        assert "추천" in PLANS["public"].label

    def test_freemium_optin_no_credit_card_required(self):
        # 외부 보고서 P32: 옵트인 trial = 신용카드 미등록
        assert "신용카드 미등록" in PLANS["free"].description


class TestBundleDiscountTable:
    def test_5_thresholds_present(self):
        assert set(BUNDLE_DISCOUNTS.keys()) == {1, 5, 10, 25, 100}

    def test_monotonic_increasing(self):
        sorted_thresholds = sorted(BUNDLE_DISCOUNTS.keys())
        for i in range(len(sorted_thresholds) - 1):
            assert (
                BUNDLE_DISCOUNTS[sorted_thresholds[i]] <= BUNDLE_DISCOUNTS[sorted_thresholds[i + 1]]
            )
