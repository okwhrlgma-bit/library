"""6-1 billing e2e + 3-1 5분 온보딩 테스트."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

# ============== 6-1 Billing ==============


class TestBilling:
    def test_within_free_quota(self):
        from kormarc_auto.evaluation.billing_e2e import BillingState, is_within_free_quota

        state = BillingState(
            tenant_id="LIB001", plan="free", status="paid", books_processed_this_month=10
        )
        assert is_within_free_quota(state) is True

    def test_over_free_quota(self):
        from kormarc_auto.evaluation.billing_e2e import BillingState, is_within_free_quota

        state = BillingState(
            tenant_id="LIB001", plan="free", status="paid", books_processed_this_month=51
        )
        assert is_within_free_quota(state) is False

    def test_metered_charge_after_quota(self):
        from kormarc_auto.evaluation.billing_e2e import (
            BillingState,
            calculate_book_charge,
        )

        state = BillingState(
            tenant_id="LIB001", plan="metered", status="paid", books_processed_this_month=51
        )
        assert calculate_book_charge(state) == 200  # Part 88 권당 200원

    def test_monthly_invoice_school_plan(self):
        from kormarc_auto.evaluation.billing_e2e import (
            BillingState,
            calculate_monthly_invoice,
        )

        state = BillingState(
            tenant_id="LIB001", plan="school", status="paid", books_processed_this_month=100
        )
        assert calculate_monthly_invoice(state) == 50_000  # 학교 정액

    def test_grace_transition_on_failure(self):
        from kormarc_auto.evaluation.billing_e2e import (
            BillingState,
            transition_on_payment_failure,
        )

        state = BillingState(tenant_id="LIB001", plan="school", status="paid")
        new_state = transition_on_payment_failure(state)
        assert new_state.status == "grace"
        assert new_state.grace_until is not None

    def test_blocked_after_grace(self):
        from kormarc_auto.evaluation.billing_e2e import (
            BillingState,
            transition_on_grace_expired,
        )

        state = BillingState(tenant_id="LIB001", plan="school", status="grace")
        new_state = transition_on_grace_expired(state)
        assert new_state.status == "blocked"
        assert new_state.blocked_at is not None

    def test_refund_eligible_within_7_days(self):
        from kormarc_auto.evaluation.billing_e2e import (
            BillingState,
            is_eligible_for_refund,
        )

        recent = datetime.now(UTC) - timedelta(days=3)
        state = BillingState(
            tenant_id="LIB001",
            plan="school",
            status="paid",
            last_payment_at=recent.isoformat(),
        )
        assert is_eligible_for_refund(state) is True

    def test_refund_expired_after_7_days(self):
        from kormarc_auto.evaluation.billing_e2e import (
            BillingState,
            is_eligible_for_refund,
        )

        old = datetime.now(UTC) - timedelta(days=10)
        state = BillingState(
            tenant_id="LIB001",
            plan="school",
            status="paid",
            last_payment_at=old.isoformat(),
        )
        assert is_eligible_for_refund(state) is False

    def test_admin_view_masks_tenant(self):
        from kormarc_auto.evaluation.billing_e2e import BillingState, mask_admin_view

        state = BillingState(tenant_id="LIB001-ABCDEFGHIJ", plan="school", status="paid")
        masked = mask_admin_view(state)
        assert "LIB001-ABCDEFG" not in masked["tenant_id_hash"]
        assert masked["tenant_id_hash"].endswith("HIJ")  # 끝 4자리만


# ============== 3-1 5분 온보딩 ==============


class TestOnboardingSmoke:
    def test_measure_step_success(self):
        from kormarc_auto.evaluation.onboarding_smoke import measure_step

        result = measure_step("setup", lambda: None)
        assert result.success is True
        assert result.duration_seconds >= 0

    def test_measure_step_failure(self):
        from kormarc_auto.evaluation.onboarding_smoke import measure_step

        def boom():
            raise RuntimeError("setup 실패")

        result = measure_step("setup", boom)
        assert result.success is False
        assert "setup 실패" in (result.error or "")

    def test_run_smoke_all_steps(self):
        from kormarc_auto.evaluation.onboarding_smoke import (
            OnboardingStep,
            run_smoke,
        )

        runners: dict[OnboardingStep, callable] = {
            "setup": lambda: None,
            "env_keys": lambda: None,
            "ui_boot": lambda: None,
            "prefix_discover": lambda: None,
            "first_isbn": lambda: None,
            "kolas_copy": lambda: None,
        }
        result = run_smoke(runners)
        assert len(result.steps) == 6
        assert result.all_succeeded is True
        assert result.passes_5min is True

    def test_run_smoke_stops_on_failure(self):
        from kormarc_auto.evaluation.onboarding_smoke import (
            OnboardingStep,
            run_smoke,
        )

        def boom():
            raise RuntimeError("ui boot 실패")

        runners: dict[OnboardingStep, callable] = {
            "setup": lambda: None,
            "env_keys": lambda: None,
            "ui_boot": boom,  # 3번째에서 중단
            "prefix_discover": lambda: None,
            "first_isbn": lambda: None,
            "kolas_copy": lambda: None,
        }
        result = run_smoke(runners)
        assert len(result.steps) == 3  # ui_boot까지만
        assert result.all_succeeded is False

    def test_regression_alert_when_fail(self):
        from kormarc_auto.evaluation.onboarding_smoke import (
            OnboardingResult,
            StepMeasurement,
            regression_alert_message,
        )

        result = OnboardingResult(
            steps=[StepMeasurement(step="setup", duration_seconds=400, success=True)],
        )
        msg = regression_alert_message(result)
        assert msg is not None
        assert "회귀" in msg

    def test_regression_no_alert_when_healthy(self):
        from kormarc_auto.evaluation.onboarding_smoke import (
            OnboardingResult,
            StepMeasurement,
            regression_alert_message,
        )

        result = OnboardingResult(
            steps=[
                StepMeasurement(step="setup", duration_seconds=10, success=True),
                StepMeasurement(step="env_keys", duration_seconds=20, success=True),
            ],
        )
        assert regression_alert_message(result) is None

    def test_report_includes_metrics(self):
        from kormarc_auto.evaluation.onboarding_smoke import (
            OnboardingResult,
            StepMeasurement,
            report,
        )

        result = OnboardingResult(
            steps=[
                StepMeasurement(step="setup", duration_seconds=30, success=True),
                StepMeasurement(step="ui_boot", duration_seconds=15, success=True),
            ],
        )
        r = report(result)
        assert r["passes_5min"] is True
        assert r["all_succeeded"] is True
        assert r["step_count"] == 2
        assert r["slowest_step"] == "setup"
