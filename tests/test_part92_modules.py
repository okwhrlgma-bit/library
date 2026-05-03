"""Part 92 신규 2 모듈 테스트 (정확도 disaggregation + LLM router)."""

from __future__ import annotations

# ============== 정확도 disaggregation ==============


class TestAccuracyDisaggregation:
    def test_calculate_descriptive_in_range(self):
        from kormarc_auto.evaluation.accuracy_disaggregation import (
            calculate_block_accuracy,
            is_in_realistic_range,
        )

        # 97% descriptive = 학술 ranges 내
        result = calculate_block_accuracy("descriptive", samples_total=1000, samples_matched=970)
        assert result.accuracy_pct == 97.0
        assert is_in_realistic_range(result) is True

    def test_calculate_subject_realistic_range(self):
        from kormarc_auto.evaluation.accuracy_disaggregation import (
            calculate_block_accuracy,
            is_in_realistic_range,
        )

        # subject = F1 0.35~0.79 ranges
        result = calculate_block_accuracy("subject", samples_total=1000, samples_matched=600)
        assert result.accuracy_pct == 60.0
        assert is_in_realistic_range(result) is True
        # 99%+ subject = 학술 ranges 초과
        bad = calculate_block_accuracy("subject", samples_total=1000, samples_matched=995)
        assert is_in_realistic_range(bad) is False

    def test_full_record_99_triggers_warning(self):
        from kormarc_auto.evaluation.accuracy_disaggregation import (
            build_disaggregated_report,
            calculate_block_accuracy,
        )

        block = calculate_block_accuracy("full_record", 100, 99)
        report = build_disaggregated_report("test-v1", {"full_record": block}, library_count=1)
        assert "ranges 초과" in report.headline_warning or "1관 한정" in report.headline_warning

    def test_marketing_safe_summary_includes_ranges(self):
        from kormarc_auto.evaluation.accuracy_disaggregation import (
            build_disaggregated_report,
            calculate_block_accuracy,
            render_marketing_safe_summary,
        )

        blocks = {
            "descriptive": calculate_block_accuracy("descriptive", 100, 97),
            "subject": calculate_block_accuracy("subject", 100, 60),
        }
        report = build_disaggregated_report("test-v1", blocks)
        summary = render_marketing_safe_summary(report)
        assert "descriptive" in summary
        assert "subject" in summary
        assert "97" in summary
        assert "학술 범위" in summary

    def test_realistic_ranges_all_blocks_defined(self):
        from kormarc_auto.evaluation.accuracy_disaggregation import REALISTIC_RANGES

        for blk in ("descriptive", "subject", "added_entries", "local", "full_record"):
            assert blk in REALISTIC_RANGES
            assert "min_pct" in REALISTIC_RANGES[blk]
            assert "max_pct" in REALISTIC_RANGES[blk]
            assert "anchor_papers" in REALISTIC_RANGES[blk]


# ============== LLM Provider Router ==============


class TestProviderRouter:
    def test_anthropic_blocked_for_public_govt(self):
        from kormarc_auto.llm.provider_router import select_provider

        providers = select_provider("public_govt", require_csap=True)
        assert "anthropic_direct" not in providers  # 행정망 차단

    def test_bedrock_seoul_for_public_govt(self):
        from kormarc_auto.llm.provider_router import select_provider

        providers = select_provider("public_govt", require_csap=True)
        assert "bedrock_seoul" in providers  # CSAP 인증
        assert "naver_hcx" in providers  # 도메스틱

    def test_public_govt_prioritizes_domestic(self):
        from kormarc_auto.llm.provider_router import select_provider

        providers = select_provider("public_govt", require_csap=True)
        # 첫 번째 = 도메스틱
        assert providers[0] in ("naver_hcx", "kt_midm")

    def test_personal_segment_includes_anthropic(self):
        from kormarc_auto.llm.provider_router import select_provider

        providers = select_provider("personal")
        assert "anthropic_direct" in providers

    def test_can_deploy_to_public(self):
        from kormarc_auto.llm.provider_router import can_deploy_to

        result = can_deploy_to("public_govt")
        assert result["csap_required"] is True
        assert result["ready"] is True
        assert result["primary_recommendation"] is not None

    def test_estimate_cost_segment(self):
        from kormarc_auto.llm.provider_router import estimate_segment_cost_won

        result = estimate_segment_cost_won("public_govt", requests_per_month=1000)
        assert result["segment"] == "public_govt"
        assert "by_provider" in result
        # lg_exaone = self-host = 0원
        assert result["by_provider"]["lg_exaone"]["monthly_won"] == 0

    def test_provider_meta_csap_completeness(self):
        from kormarc_auto.llm.provider_router import PROVIDER_META

        # anthropic_direct 외 모두 CSAP
        for pid, meta in PROVIDER_META.items():
            if pid == "anthropic_direct":
                assert meta["csap_certified"] is False
            else:
                assert meta["csap_certified"] is True
