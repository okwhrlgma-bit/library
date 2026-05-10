"""evaluate_pain_15 자동 평가 회귀 테스트 (Cycle 102).

ADR 0055·0058·0065·Cycle 101 룰 검증.
실 페인 4건 (#31·#1·P-017·P-018) 결과 회귀 보장.
"""

from __future__ import annotations

import sys
from pathlib import Path

# scripts/ 경로 등록
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evaluate_pain_15 import PainEvaluation, calculate_overall_score


def _make_eval(**overrides) -> PainEvaluation:
    """기본 평가 fixture (모두 통과·overrides로 변경)."""
    defaults: dict[str, object] = {
        "pain_id": "test",
        "pain_score": 8,
        "automation_score": 8,
        "revenue_score": 8,
        "payer_match": True,
        "solo_operatable": True,
        "no_government_competition": True,
        "founder_fit": True,
        "repeat_frequency": True,
        "lock_in": True,
        "no_legal_risk": True,
        "korea_global_both": True,
        "indie_benchmark": True,
        "adr_0052_compatible": True,
        "user_data_local": True,
        "mit_apache_license": True,
    }
    defaults.update(overrides)
    return PainEvaluation(**defaults)  # type: ignore[arg-type]


class TestBasicScoring:
    def test_perfect_score_go(self) -> None:
        # 24/30 + 12/12 = 40 + 50 = 90 → GO
        result = calculate_overall_score(_make_eval())
        assert result["decision"] == "GO"
        assert result["overall_score"] >= 75
        assert result["fail_reasons"] == []

    def test_zero_scores_no_go(self) -> None:
        result = calculate_overall_score(
            _make_eval(pain_score=0, automation_score=0, revenue_score=0)
        )
        assert result["decision"] == "NO_GO"


class TestThresholds:
    def test_go_threshold_75(self) -> None:
        # po 16/30 + autonomy 12/12 = 27 + 50 = 77 → GO
        result = calculate_overall_score(
            _make_eval(pain_score=5, automation_score=5, revenue_score=6)
        )
        assert result["decision"] == "GO"

    def test_maybe_60_to_74(self) -> None:
        # po 12/30 + autonomy 12/12 = 20 + 50 = 70 → MAYBE
        result = calculate_overall_score(
            _make_eval(pain_score=4, automation_score=4, revenue_score=4)
        )
        assert result["decision"] == "MAYBE"
        assert 60 <= int(result["overall_score"]) < 75

    def test_no_go_below_60(self) -> None:
        # po 9/30 + autonomy 9/12 = 15 + 38 = 53 → NO_GO
        result = calculate_overall_score(
            _make_eval(
                pain_score=3, automation_score=3, revenue_score=3,
                payer_match=False, solo_operatable=False, founder_fit=False,
            )
        )
        assert result["decision"] == "NO_GO"


class TestPenalties:
    def test_giant_competitor_penalty_minus_10(self) -> None:
        baseline = calculate_overall_score(_make_eval())
        with_penalty = calculate_overall_score(_make_eval(giant_competitor_billion=True))
        assert int(with_penalty["overall_score"]) == int(baseline["overall_score"]) - 10

    def test_government_free_penalty_minus_10(self) -> None:
        baseline = calculate_overall_score(_make_eval())
        with_penalty = calculate_overall_score(_make_eval(government_free_dominant=True))
        assert int(with_penalty["overall_score"]) == int(baseline["overall_score"]) - 10


class TestCycle101Rules:
    def test_double_penalty_forces_no_go(self) -> None:
        """이중 페널티 = NO_GO 자동 강제."""
        result = calculate_overall_score(
            _make_eval(
                giant_competitor_billion=True,
                government_free_dominant=True,
            )
        )
        assert result["decision"] == "NO_GO"
        assert any("이중 페널티" in str(p) for p in result["penalties"])

    def test_no_legal_risk_forces_no_go(self) -> None:
        """법적 위험 = NO_GO 자동 강제 (점수 무관)."""
        result = calculate_overall_score(_make_eval(no_legal_risk=False))
        assert result["decision"] == "NO_GO"


class TestCycle108RulesV5:
    """v5: founder_fit X + indie_benchmark X = NO_GO 강제."""

    def test_no_founder_no_indie_forces_no_go(self) -> None:
        result = calculate_overall_score(
            _make_eval(
                pain_score=10, automation_score=10, revenue_score=10,
                founder_fit=False,
                indie_benchmark=False,
            )
        )
        assert result["decision"] == "NO_GO"
        assert any("founder fit X + 인디 검증 X" in str(p) for p in result["penalties"])

    def test_only_founder_fit_passes_v5(self) -> None:
        result = calculate_overall_score(
            _make_eval(founder_fit=True, indie_benchmark=False)
        )
        assert result["decision"] in {"GO", "MAYBE"}

    def test_only_indie_benchmark_passes_v5(self) -> None:
        result = calculate_overall_score(
            _make_eval(founder_fit=False, indie_benchmark=True)
        )
        assert result["decision"] in {"GO", "MAYBE"}


class TestCycle115RulesV6:
    """v6: giant_competitor + market_sam_under_10k = NO_GO 강제."""

    def test_giant_plus_small_market_forces_no_go(self) -> None:
        """거대 + 작은 시장 = NO_GO (P-023 인디 SEO 패턴)."""
        result = calculate_overall_score(
            _make_eval(
                pain_score=8, automation_score=7, revenue_score=7,
                founder_fit=True,
                indie_benchmark=True,
                giant_competitor_billion=True,
                market_sam_under_10k=True,
            )
        )
        assert result["decision"] == "NO_GO"
        assert any("v6" in str(p) for p in result["penalties"])

    def test_giant_only_passes_v6(self) -> None:
        """거대 사업자 단독 = v6 X (페널티만·점수 의존)."""
        result = calculate_overall_score(
            _make_eval(
                founder_fit=True,
                indie_benchmark=True,
                giant_competitor_billion=True,
                market_sam_under_10k=False,
            )
        )
        # v6 강제 X·페널티 -10만 적용
        assert "v6" not in str(result.get("penalties", []))


class TestRegressionRealApps:
    """실 페인 4건 회귀 (분류 정확성 보장)."""

    def test_freelancer_tax_helper_go(self) -> None:
        result = calculate_overall_score(
            _make_eval(
                pain_id="#31",
                pain_score=9, automation_score=8, revenue_score=9,
                founder_fit=False, korea_global_both=False,
            )
        )
        assert result["decision"] == "GO"
        assert int(result["overall_score"]) == 85

    def test_kormarc_auto_maybe(self) -> None:
        result = calculate_overall_score(
            _make_eval(
                pain_id="#1",
                pain_score=9, automation_score=9, revenue_score=5,
                payer_match=False,
                no_government_competition=False,
                korea_global_both=False,
                indie_benchmark=False,
            )
        )
        assert result["decision"] == "MAYBE"

    def test_english_learning_with_giant_penalty(self) -> None:
        result = calculate_overall_score(
            _make_eval(
                pain_id="P-017 영어 학습",
                pain_score=8, automation_score=9, revenue_score=7,
                no_government_competition=False,
                founder_fit=False,
                lock_in=False,
                indie_benchmark=False,
                giant_competitor_billion=True,  # Duolingo $9B
            )
        )
        # Cycle 108 v5: founder X + indie X = NO_GO 강제 (이전 MAYBE 63 → NO_GO)
        assert result["decision"] == "NO_GO"

    def test_foreign_resident_admin_no_go(self) -> None:
        result = calculate_overall_score(
            _make_eval(
                pain_id="P-018 외국인 행정",
                pain_score=8, automation_score=8, revenue_score=6,
                no_government_competition=False,
                founder_fit=False,
                repeat_frequency=False,
                lock_in=False,
                no_legal_risk=False,  # ❌ 행정사법·변호사법
                indie_benchmark=False,
            )
        )
        assert result["decision"] == "NO_GO"
