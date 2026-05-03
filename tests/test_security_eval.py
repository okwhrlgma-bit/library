"""9-1 redaction + 2-2 cross-library + 8-1 load test 테스트."""

from __future__ import annotations

# ============== 9-1 Redaction ==============


class TestRedaction:
    def test_email_masked(self):
        from kormarc_auto.security.redaction import redact_text

        result = redact_text("Contact: librarian@example.com please")
        assert "@" in result
        assert "librarian" not in result
        assert "example" not in result

    def test_phone_kr_masked(self):
        from kormarc_auto.security.redaction import redact_text

        result = redact_text("전화 010-1234-5678 입니다")
        assert "010" in result
        assert "1234" not in result
        assert "5678" in result

    def test_anthropic_key_masked(self):
        from kormarc_auto.security.redaction import redact_text

        result = redact_text("API key: sk-ant-api03-AbCdEf123456789012345678901234567890")
        assert "REDACTED" in result
        assert "AbCdEf" not in result

    def test_card_masked(self):
        from kormarc_auto.security.redaction import redact_text

        result = redact_text("결제 카드: 1234-5678-9012-3456")
        assert "1234" not in result.split("****-****-****-")[0] or "****" in result
        assert "3456" in result

    def test_rrn_masked(self):
        from kormarc_auto.security.redaction import redact_text

        result = redact_text("주민번호 901231-1234567")
        assert "901231" not in result
        assert "1234567" not in result

    def test_safe_error_response(self):
        from kormarc_auto.security.redaction import safe_error_response

        err = ValueError("Failed for user@example.com with key sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXX")
        resp = safe_error_response(err)
        assert resp["error"]["code"] == "ValueError"
        assert "user" not in resp["error"]["message"]
        assert "REDACTED" in resp["error"]["message"]

    def test_redaction_filter_logging(self):
        import logging

        from kormarc_auto.security.redaction import RedactionFilter

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="user@gmail.com 010-1234-5678",
            args=(),
            exc_info=None,
        )
        f = RedactionFilter()
        f.filter(record)
        assert "user" not in record.msg
        assert "1234" not in record.msg


# ============== 2-2 Cross-library Simulation ==============


class TestCrossLibrarySim:
    def test_swap_prefix(self):
        from kormarc_auto.evaluation.cross_library_simulation import swap_prefix

        record = {"title": "테스트", "registration_no_prefix": "EQ"}
        swapped = swap_prefix(record, "school")
        assert swapped["registration_no_prefix"] == "SC"
        assert swapped["title"] == "테스트"  # 보존

    def test_simulate_persona_accuracy(self):
        from kormarc_auto.evaluation.cross_library_simulation import (
            simulate_persona_accuracy,
        )

        records = [{"title": f"책 {i}", "registration_no_prefix": "ORIG"} for i in range(10)]
        result = simulate_persona_accuracy(records, "school")
        assert result.persona == "school"
        assert result.total_records == 10
        assert result.accuracy >= 0.9  # 모두 swap 성공

    def test_run_full_simulation_5_personas(self):
        from kormarc_auto.evaluation.cross_library_simulation import run_full_simulation

        records = [{"title": f"X{i}", "registration_no_prefix": "ORIG"} for i in range(20)]
        results = run_full_simulation(records)
        assert len(results) == 5  # 5 페르소나
        for _persona, result in results.items():
            assert result.total_records == 20

    def test_summary_meets_95_target(self):
        from kormarc_auto.evaluation.cross_library_simulation import (
            run_full_simulation,
            summary_report,
        )

        records = [{"title": f"X{i}", "registration_no_prefix": "ORIG"} for i in range(50)]
        results = run_full_simulation(records, apply_prefix_discover=True)
        summary = summary_report(results)
        assert summary["personas_count"] == 5
        assert summary["target_95_met"] is True


# ============== 8-1 Load Test ==============


class TestLoadTest:
    def test_run_load_test_collects_metrics(self):
        from kormarc_auto.evaluation.load_test import (
            LoadTestConfig,
            run_load_test,
        )

        cfg = LoadTestConfig(test_name="test", target_count=10)
        items = list(range(10))
        result = run_load_test(cfg, lambda x: x * 2, iter(items))

        assert result.total == 10
        assert result.successes == 10
        assert result.failures == 0
        assert result.success_rate == 1.0

    def test_run_load_test_handles_failures(self):
        from kormarc_auto.evaluation.load_test import (
            LoadTestConfig,
            run_load_test,
        )

        def flaky(x):
            if x % 3 == 0:
                raise RuntimeError("flaky")
            return x

        cfg = LoadTestConfig(test_name="flaky", target_count=10)
        result = run_load_test(cfg, flaky, iter(range(10)))
        assert result.successes > 0
        assert result.failures > 0
        assert len(result.errors) > 0

    def test_estimate_memory_rss_50k(self):
        from kormarc_auto.evaluation.load_test import estimate_memory_rss

        result = estimate_memory_rss(50_000)
        # 50k × 2KB × 1.3 = 약 130MB
        assert result["estimated_mb"] < 500
        assert result["passes_2gb_target"] is True

    def test_estimate_anthropic_cost_haiku(self):
        from kormarc_auto.evaluation.load_test import estimate_anthropic_cost

        result = estimate_anthropic_cost(1000, model="haiku")
        assert result["model"] == "haiku"
        assert result["total_usd"] > 0
        assert result["total_won"] > 0

    def test_p95_calculation(self):
        from kormarc_auto.evaluation.load_test import (
            LoadTestConfig,
            run_load_test,
        )

        # 100 items·시간 = item 값 / 1000 (ms 단위로 변환 X·시뮬)
        cfg = LoadTestConfig(test_name="p95", target_count=100)
        result = run_load_test(cfg, lambda x: None, iter(range(100)))
        assert result.p95 >= 0
        assert result.p99 >= result.p95
        assert result.p99 >= result.p50
