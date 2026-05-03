"""M5 멀티테넌시·관측성 테스트."""

from __future__ import annotations

import pytest

# ============== Tenant Isolation ==============


class TestTenantIsolation:
    def setup_method(self):
        from kormarc_auto.security.tenant_isolation import clear_tenant

        clear_tenant()

    def test_require_tenant_raises_when_unset(self):
        from kormarc_auto.security.tenant_isolation import (
            TenantNotSetError,
            require_tenant,
        )

        with pytest.raises(TenantNotSetError):
            require_tenant()

    def test_set_and_get_tenant(self):
        from kormarc_auto.security.tenant_isolation import (
            get_current_tenant,
            set_current_tenant,
        )

        set_current_tenant("LIB001")
        assert get_current_tenant() == "LIB001"

    def test_assert_tenant_match_passes_on_match(self):
        from kormarc_auto.security.tenant_isolation import (
            assert_tenant_match,
            set_current_tenant,
        )

        set_current_tenant("LIB001")
        assert_tenant_match("LIB001")  # raise X

    def test_assert_tenant_match_raises_on_mismatch(self):
        from kormarc_auto.security.tenant_isolation import (
            TenantMismatchError,
            assert_tenant_match,
            set_current_tenant,
        )

        set_current_tenant("LIB001")
        with pytest.raises(TenantMismatchError):
            assert_tenant_match("LIB002")

    def test_filter_by_tenant_excludes_other(self):
        from kormarc_auto.security.tenant_isolation import (
            filter_by_tenant,
            set_current_tenant,
        )

        set_current_tenant("LIB001")
        records = [
            {"id": 1, "tenant_id": "LIB001"},
            {"id": 2, "tenant_id": "LIB002"},
            {"id": 3, "tenant_id": "LIB001"},
        ]
        result = filter_by_tenant(records)
        assert len(result) == 2
        assert all(r["tenant_id"] == "LIB001" for r in result)

    def test_tenant_scoped_decorator_raises_when_unset(self):
        from kormarc_auto.security.tenant_isolation import (
            TenantNotSetError,
            tenant_scoped,
        )

        @tenant_scoped
        def get_data():
            return "data"

        with pytest.raises(TenantNotSetError):
            get_data()

    def test_tenant_scoped_decorator_passes_when_set(self):
        from kormarc_auto.security.tenant_isolation import (
            set_current_tenant,
            tenant_scoped,
        )

        @tenant_scoped
        def get_data():
            return "data"

        set_current_tenant("LIB001")
        assert get_data() == "data"

    def test_tenant_audit_log(self):
        from kormarc_auto.security.tenant_isolation import (
            get_tenant_audit_log,
            log_tenant_switch,
        )

        log_tenant_switch(None, "LIB001", "test_login")
        log_tenant_switch("LIB001", "LIB002", "admin_switch")
        log = get_tenant_audit_log()
        assert any(e["to"] == "LIB001" for e in log)
        assert any(e["to"] == "LIB002" for e in log)


# ============== SLO Metrics ==============


class TestSloMetrics:
    def setup_method(self):
        from kormarc_auto.observability.slo_metrics import reset_window

        reset_window()

    def test_record_and_summary(self):
        from kormarc_auto.observability.slo_metrics import (
            get_slo_summary,
            record_metric,
        )

        record_metric("isbn_to_mrc", duration_ms=100.0, success=True)
        record_metric("isbn_to_mrc", duration_ms=200.0, success=True)
        record_metric("isbn_to_mrc", duration_ms=500.0, success=False)

        summary = get_slo_summary()
        assert summary["isbn_to_mrc"]["count"] == 3
        assert summary["isbn_to_mrc"]["success_rate"] is not None

    def test_p95_calculation(self):
        from kormarc_auto.observability.slo_metrics import (
            get_slo_summary,
            record_metric,
        )

        for ms in range(1, 101):
            record_metric("isbn_to_mrc", duration_ms=float(ms), success=True)

        summary = get_slo_summary()
        # p95 of 1..100 = 95~96
        assert 90 <= summary["isbn_to_mrc"]["p95_ms"] <= 100

    def test_violation_detection_p95_over_5s(self):
        from kormarc_auto.observability.slo_metrics import (
            check_slo_violations,
            record_metric,
        )

        for _ in range(20):
            record_metric("isbn_to_mrc", duration_ms=10000.0, success=True)  # 10초

        violations = check_slo_violations()
        assert any(v["slo"] == "isbn_to_mrc_p95_5s" for v in violations)

    def test_violation_payment_success_under_995(self):
        from kormarc_auto.observability.slo_metrics import (
            check_slo_violations,
            record_metric,
        )

        for _ in range(95):
            record_metric("payment", duration_ms=100.0, success=True)
        for _ in range(5):
            record_metric("payment", duration_ms=100.0, success=False)

        violations = check_slo_violations()
        assert any(v["slo"] == "payment_success_995" for v in violations)

    def test_no_violation_when_healthy(self):
        from kormarc_auto.observability.slo_metrics import (
            check_slo_violations,
            record_metric,
        )

        for _ in range(100):
            record_metric("isbn_to_mrc", duration_ms=200.0, success=True)
            record_metric("payment", duration_ms=50.0, success=True)
            record_metric("external_api", duration_ms=300.0, success=True)

        violations = check_slo_violations()
        assert violations == []

    def test_prometheus_format(self):
        from kormarc_auto.observability.slo_metrics import (
            record_metric,
            to_prometheus_format,
        )

        record_metric("isbn_to_mrc", duration_ms=100.0, success=True)
        prom = to_prometheus_format()
        assert "kormarc_slo" in prom
        assert "isbn_to_mrc" in prom

    def test_rolling_window_capacity(self):
        from kormarc_auto.observability.slo_metrics import (
            get_slo_summary,
            record_metric,
        )

        # 1,500건 = 1,000건 capacity 초과 → 오래된 것 제거
        for i in range(1500):
            record_metric("isbn_to_mrc", duration_ms=float(i), success=True)

        summary = get_slo_summary()
        assert summary["isbn_to_mrc"]["count"] <= 1000
