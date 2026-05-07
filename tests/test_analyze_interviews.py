"""Cycle 73 — 인터뷰 분석 도구 회귀.

LLM 호출 0·통계 결정적·Mom Test 결정 트리 정합.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from analyze_interviews import (
    _next_action,
    aggregate_results,
    render_text_report,
)


def _make_interview(score: int, persona: str = "P1", b2c: str = "예") -> dict:
    return {
        "file": "test.md",
        "interview_id": "A",
        "persona_match": persona,
        "score": score,
        "payment_intent_b2c": b2c,
        "payment_intent_b2b": "모름",
        "competitor": ["MarcEdit"],
        "valid": True,
    }


class TestAggregateResults:
    def test_empty_returns_status(self):
        agg = aggregate_results([])
        assert agg["n"] == 0
        assert "데이터 부족" in agg["status"]

    def test_5_high_scores_decision(self):
        interviews = [_make_interview(4) for _ in range(5)]
        agg = aggregate_results(interviews)
        assert agg["n"] == 5
        assert agg["average_score"] == 4.0
        assert "✅" in agg["decision"]
        assert "PILOT" in agg["next_action"]

    def test_5_low_scores_decision(self):
        interviews = [_make_interview(1) for _ in range(5)]
        agg = aggregate_results(interviews)
        assert agg["average_score"] == 1.0
        assert "❌" in agg["decision"]
        assert "MarcEdit 모델" in agg["next_action"]

    def test_middle_scores_decision(self):
        interviews = [_make_interview(3) for _ in range(5)]
        agg = aggregate_results(interviews)
        assert agg["average_score"] == 3.0
        assert "🟡" in agg["decision"]

    def test_b2c_yes_count(self):
        interviews = [
            _make_interview(4, b2c="예"),
            _make_interview(4, b2c="예"),
            _make_interview(4, b2c="예"),
            _make_interview(4, b2c="아니오"),
            _make_interview(4, b2c="모름"),
        ]
        agg = aggregate_results(interviews)
        assert agg["b2c_payment_yes"] == 3
        assert agg["b2c_payment_yes_pct"] == 60.0

    def test_persona_distribution(self):
        interviews = [
            _make_interview(4, persona="P1"),
            _make_interview(4, persona="P1"),
            _make_interview(4, persona="P8"),
        ]
        agg = aggregate_results(interviews)
        assert agg["persona_distribution"]["P1"] == 2
        assert agg["persona_distribution"]["P8"] == 1

    def test_competitor_frequency(self):
        interviews = [
            {**_make_interview(4), "competitor": ["MarcEdit", "KOLAS III"]},
            {**_make_interview(4), "competitor": ["MarcEdit"]},
        ]
        agg = aggregate_results(interviews)
        assert agg["competitor_frequency"]["MarcEdit"] == 2
        assert agg["competitor_frequency"]["KOLAS III"] == 1


class TestNextActionTree:
    def test_high_score_high_b2c_pivot_to_b2c(self):
        interviews = [_make_interview(4) for _ in range(5)]
        action = _next_action(4.0, 4, interviews)
        assert "B2C 진행" in action

    def test_high_score_low_b2c_pivot_to_b2b(self):
        interviews = [_make_interview(4) for _ in range(5)]
        action = _next_action(4.0, 1, interviews)
        assert "B2B" in action

    def test_low_score_marcedit_model(self):
        interviews = [_make_interview(1) for _ in range(5)]
        action = _next_action(1.0, 0, interviews)
        assert "MarcEdit" in action

    def test_no_data_returns_template_action(self):
        action = _next_action(0, 0, [])
        assert "TEMPLATE" in action


class TestRenderReport:
    def test_empty_renders_warning(self):
        agg = aggregate_results([])
        text = render_text_report(agg)
        assert "데이터 부족" in text
        assert "TEMPLATE" in text

    def test_5_results_renders_full_report(self):
        interviews = [_make_interview(4) for _ in range(5)]
        agg = aggregate_results(interviews)
        text = render_text_report(agg)
        assert "N = 5명" in text
        assert "평균 점수" in text
        assert "결정:" in text
        assert "페르소나 분포" in text
        assert "결제 의향" in text


class TestInvariantCompliance:
    """invariant 11 (페르소나 시뮬 ≠ 인터뷰)·invariant 2 (자관 누설 X) 정합."""

    def test_no_real_names_or_libraries_in_template(self):
        """TEMPLATE.md = 익명 코드만·실명 X."""
        template_path = (
            Path(__file__).resolve().parent.parent
            / "docs"
            / "research"
            / "librarian-interviews-2026-05"
            / "TEMPLATE.md"
        )
        if template_path.exists():
            text = template_path.read_text(encoding="utf-8", errors="replace")
            # invariant 2 정합 = 실명·근무지 X·익명 ID만 명시
            assert "익명" in text
            assert "invariant 2" in text or "실명" in text

    def test_invariant_11_activation_message(self):
        """분석 결과 = "1차 자료·invariant 11 활성" 명시."""
        interviews = [_make_interview(4) for _ in range(5)]
        agg = aggregate_results(interviews)
        text = render_text_report(agg)
        assert "invariant 11" in text or "1차 자료" in text or "정직 헤더" in text
