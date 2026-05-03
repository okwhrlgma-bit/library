"""prompt_cache.py 테스트 — T2-4 (Part 92 §A.6).

검증:
- CachedSystemPrompt.to_anthropic_blocks() 구조 (cache_control 포함)
- build_kormarc_system_prompt persona 변형 (general·medical·school·academic·small)
- estimate_cache_savings 계산 (baseline vs cached·USD/KRW)
- 가격 테이블 정합 (Haiku $1·Sonnet $3·Opus $5)
"""

from __future__ import annotations

import pytest

from kormarc_auto.llm.prompt_cache import (
    FEW_SHOT_EXEMPLARS,
    KORMARC_FIELD_REFERENCE,
    CachedSystemPrompt,
    build_kormarc_system_prompt,
    estimate_cache_savings,
)


class TestCachedSystemPrompt:
    def test_default_ttl_5m(self):
        p = CachedSystemPrompt(text="hello")
        assert p.ttl == "5m"
        assert p.model_id == "claude-sonnet-4-6"

    def test_to_anthropic_blocks_structure(self):
        p = CachedSystemPrompt(text="prefix", ttl="1h")
        blocks = p.to_anthropic_blocks()
        assert len(blocks) == 1
        b = blocks[0]
        assert b["type"] == "text"
        assert b["text"] == "prefix"
        assert b["cache_control"] == {"type": "ephemeral", "ttl": "1h"}

    def test_5m_ttl_propagates(self):
        p = CachedSystemPrompt(text="x", ttl="5m")
        assert p.to_anthropic_blocks()[0]["cache_control"]["ttl"] == "5m"

    def test_frozen_dataclass(self):
        from dataclasses import FrozenInstanceError

        p = CachedSystemPrompt(text="x")
        with pytest.raises(FrozenInstanceError):
            p.text = "modified"  # type: ignore[misc]


class TestBuildKormarcSystemPrompt:
    def test_general_persona(self):
        p = build_kormarc_system_prompt(persona="general")
        assert "KORMARC" in p.text
        assert KORMARC_FIELD_REFERENCE in p.text
        assert FEW_SHOT_EXEMPLARS in p.text
        assert "temperature=0" in p.text

    def test_medical_persona_addendum(self):
        p = build_kormarc_system_prompt(persona="medical")
        assert "MeSH" in p.text
        assert "PubMed" in p.text

    def test_school_persona_addendum(self):
        p = build_kormarc_system_prompt(persona="school")
        assert "DLS 521" in p.text
        assert "BK" in p.text and "LR" in p.text

    def test_academic_persona_addendum(self):
        p = build_kormarc_system_prompt(persona="academic")
        assert "DDC 082" in p.text
        assert "LCSH" in p.text
        assert "Alma" in p.text

    def test_small_persona_addendum(self):
        p = build_kormarc_system_prompt(persona="small")
        assert "작은도서관" in p.text
        assert "1인" in p.text or "자원봉사" in p.text

    def test_unknown_persona_falls_back_to_general(self):
        p = build_kormarc_system_prompt(persona="unknown_xyz")
        assert "KORMARC" in p.text  # 기본 prefix 살아있음

    def test_ttl_1h_for_nightly_batch(self):
        p = build_kormarc_system_prompt(ttl="1h")
        assert p.ttl == "1h"

    def test_model_id_propagates(self):
        p = build_kormarc_system_prompt(model_id="claude-haiku-4-5-20251001")
        assert p.model_id == "claude-haiku-4-5-20251001"

    def test_prefix_has_substantive_content(self):
        """안정 prefix = field reference + few-shot + persona addendum.

        TODO(prompt_cache): docstring은 ~8K 토큰 목표하지만 현재 ~600 토큰.
        Haiku 4.5 cache minimum = 4096 토큰·Sonnet = 1024 토큰.
        v0.7에서 KORMARC field 35 → 80개·exemplars 3 → 8 확장 예정.
        """
        p = build_kormarc_system_prompt()
        assert 1500 < len(p.text) < 30000
        # 핵심 요소 모두 포함
        assert "008" in p.text and "245" in p.text and "KDC" in p.text


class TestEstimateCacheSavings:
    def test_baseline_calculation_sonnet(self):
        r = estimate_cache_savings(
            monthly_calls=1000,
            avg_input_tokens=8000,
            avg_output_tokens=200,
            cache_hit_rate=0.0,  # cache 0% = baseline
            model_id="claude-sonnet-4-6",
        )
        # 1000 calls × 8000 input × $3/MTok = $24
        # 1000 calls × 200 output × $15/MTok = $3
        # baseline = $27
        assert r["baseline_usd"] == pytest.approx(27.0, abs=0.01)

    def test_85pct_cache_hit_savings(self):
        r = estimate_cache_savings(
            monthly_calls=1000,
            avg_input_tokens=8000,
            avg_output_tokens=200,
            cache_hit_rate=0.85,
            model_id="claude-sonnet-4-6",
        )
        # 90% off가 가능하다고 docstring 주장 — 실제 계산 검증
        # 150 write × 8000 × $3/MTok × 1.25 = $4.5
        # 850 read × 8000 × $3/MTok × 0.10 = $2.04
        # 1000 × 200 × $15/MTok = $3.0
        # cached = $9.54
        assert r["cached_usd"] == pytest.approx(9.54, abs=0.01)
        assert r["savings_usd"] == pytest.approx(17.46, abs=0.01)
        # 약 65% 절감 (input 단독 90%·output 미절감 포함)
        assert 60 < r["savings_pct"] < 70

    def test_haiku_pricing(self):
        r = estimate_cache_savings(
            monthly_calls=100,
            avg_input_tokens=8000,
            avg_output_tokens=200,
            cache_hit_rate=0.0,
            model_id="claude-haiku-4-5-20251001",
        )
        # 100 × 8000 × $1/MTok + 100 × 200 × $5/MTok = $0.8 + $0.1 = $0.9
        assert r["baseline_usd"] == pytest.approx(0.9, abs=0.01)

    def test_opus_pricing(self):
        r = estimate_cache_savings(
            monthly_calls=100,
            avg_input_tokens=8000,
            avg_output_tokens=200,
            cache_hit_rate=0.0,
            model_id="claude-opus-4-7",
        )
        # 100 × 8000 × $5/MTok + 100 × 200 × $25/MTok = $4.0 + $0.5 = $4.5
        assert r["baseline_usd"] == pytest.approx(4.5, abs=0.01)

    def test_won_conversion(self):
        r = estimate_cache_savings(monthly_calls=1000, cache_hit_rate=0.85)
        # ₩1400/$
        expected_won = int(r["savings_usd"] * 1400)
        assert r["savings_won"] == expected_won

    def test_zero_calls_no_division_error(self):
        r = estimate_cache_savings(monthly_calls=0, cache_hit_rate=0.85)
        assert r["baseline_usd"] == 0
        assert r["savings_pct"] == 0

    def test_unknown_model_falls_back_to_sonnet(self):
        r1 = estimate_cache_savings(monthly_calls=100, model_id="unknown-model")
        r2 = estimate_cache_savings(monthly_calls=100, model_id="claude-sonnet-4-6")
        assert r1["baseline_usd"] == r2["baseline_usd"]

    def test_dict_keys_complete(self):
        r = estimate_cache_savings(monthly_calls=100)
        for key in (
            "monthly_calls",
            "model_id",
            "baseline_usd",
            "cached_usd",
            "savings_usd",
            "savings_pct",
            "savings_won",
        ):
            assert key in r


class TestRealWorldScenarios:
    """Part 92 §A.6 영업 시나리오 검증."""

    def test_nightly_batch_174_records(self):
        """자관 174 disaggregation 재측정 (월 1회·1h TTL)."""
        r = estimate_cache_savings(
            monthly_calls=174,
            avg_input_tokens=8000,
            avg_output_tokens=500,
            cache_hit_rate=0.99,  # 174/174 1회 = 1 write·173 read
            model_id="claude-sonnet-4-6",
        )
        assert r["savings_usd"] > 0
        assert r["savings_pct"] > 50

    def test_interactive_streamlit_5m_ttl(self):
        """사서 ISBN 1건 (interactive·5m TTL)."""
        # 1관·월 100건·85% hit (사서 1명 sustained 사용)
        r = estimate_cache_savings(
            monthly_calls=100,
            avg_input_tokens=8000,
            avg_output_tokens=300,
            cache_hit_rate=0.85,
            model_id="claude-sonnet-4-6",
        )
        # 200관 PILOT 기준 합산 절감 = 영업 자료 인용 가능
        assert r["savings_won"] > 0
