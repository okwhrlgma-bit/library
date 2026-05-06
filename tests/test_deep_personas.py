"""Cycle 61 (Part 96·ADR 0045) — 8 ICP 페르소나 깊이 시뮬 회귀.

LLM 호출 0·통계 결정적·인터뷰 가설 우선순위 도출.
"""

from __future__ import annotations

import pytest

from kormarc_auto.personas import (
    EIGHT_ICP_PERSONAS,
    PMF_THRESHOLD,
    app_coverage_matrix,
    find_underserved_personas,
    score_app_for_persona,
)
from kormarc_auto.personas.deep_simulation import (
    cumulative_market_pmf,
    render_persona_summary,
)


class TestEightICPPersonas:
    def test_count_eight(self):
        assert len(EIGHT_ICP_PERSONAS) == 8

    def test_unique_ids(self):
        ids = [p.id for p in EIGHT_ICP_PERSONAS]
        assert len(set(ids)) == 8
        assert ids == ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]

    def test_payment_intent_range(self):
        for p in EIGHT_ICP_PERSONAS:
            assert 0 <= p.payment_intent <= 100

    def test_payment_authority_range(self):
        for p in EIGHT_ICP_PERSONAS:
            assert 0 <= p.payment_authority <= 100

    def test_market_size_positive(self):
        for p in EIGHT_ICP_PERSONAS:
            assert p.market_size > 0

    def test_p1_largest_market(self):
        # P1 작은도서관 = 6,830관 = 가장 큰 segment
        p1 = next(p for p in EIGHT_ICP_PERSONAS if p.id == "P1")
        assert p1.market_size == 6_830

    def test_p5_minimum_market(self):
        # P5 자관 = 1관 (PO 자관·N=1)
        p5 = next(p for p in EIGHT_ICP_PERSONAS if p.id == "P5")
        assert p5.market_size == 1

    def test_payment_authority_split(self):
        """결제 의향 vs 결제 권한 분리 (Cycle 61 핵심 통찰)."""
        # P1: intent 90·authority 10 = 큰 격차
        p1 = next(p for p in EIGHT_ICP_PERSONAS if p.id == "P1")
        assert p1.payment_intent - p1.payment_authority >= 50
        # P8: intent 90·authority 90 = 격차 적음 (도서관장 = 결제권)
        p8 = next(p for p in EIGHT_ICP_PERSONAS if p.id == "P8")
        assert abs(p8.payment_intent - p8.payment_authority) <= 10


class TestScoreAppForPersona:
    def test_score_within_range(self):
        for p in EIGHT_ICP_PERSONAS:
            s = score_app_for_persona(p)
            assert 0 <= s.ui_score <= 100
            assert 0 <= s.feature_score <= 100
            assert 0 <= s.price_score <= 100
            assert 0 <= s.sales_score <= 100
            assert 0 <= s.legal_score <= 100
            assert 0 <= s.total_pmf <= 100

    def test_p5_highest_pmf(self):
        # P5 자관 PILOT = PO 본인 = PMF 95+ (편향)
        p5 = next(p for p in EIGHT_ICP_PERSONAS if p.id == "P5")
        s = score_app_for_persona(p5)
        assert s.total_pmf >= 90

    def test_p3_lowest_pmf(self):
        # P3 공공 계약직 = CSAP·결제권 0·월급제 = PMF 낮음
        p3 = next(p for p in EIGHT_ICP_PERSONAS if p.id == "P3")
        s = score_app_for_persona(p3)
        assert s.total_pmf < 70  # PMF threshold 미달

    def test_gaps_identified(self):
        for p in EIGHT_ICP_PERSONAS:
            s = score_app_for_persona(p)
            assert len(s.gaps) >= 1


class TestAppCoverageMatrix:
    def test_returns_eight_scores(self):
        matrix = app_coverage_matrix()
        assert len(matrix) == 8

    def test_persona_ids_match(self):
        matrix = app_coverage_matrix()
        ids = [s.persona_id for s in matrix]
        assert set(ids) == {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"}


class TestUnderservedPersonas:
    def test_p3_underserved(self):
        # P3 공공 계약직 = PMF < 70 = underserved
        underserved = find_underserved_personas(threshold=PMF_THRESHOLD)
        ids = [p.id for p in underserved]
        assert "P3" in ids

    def test_p5_not_underserved(self):
        # P5 자관 PILOT = PMF 95+
        underserved = find_underserved_personas(threshold=PMF_THRESHOLD)
        ids = [p.id for p in underserved]
        assert "P5" not in ids


class TestCumulativeMarketPMF:
    def test_pmf_pass_market_calculation(self):
        market = cumulative_market_pmf()
        assert market["total_market"] > 0
        assert market["pmf_pass_market"] >= 0
        assert market["pmf_fail_market"] >= 0
        assert market["pmf_pass_market"] + market["pmf_fail_market"] == market["total_market"]

    def test_pmf_pass_pct_in_range(self):
        market = cumulative_market_pmf()
        assert 0 <= market["pmf_pass_pct"] <= 100


class TestPersonaSummaryRender:
    def test_renders_all_eight(self):
        text = render_persona_summary()
        for p in EIGHT_ICP_PERSONAS:
            assert p.id in text

    def test_warning_about_simulation(self):
        # Cycle 61 정직 헤더: 가설·인터뷰 X
        text = render_persona_summary()
        assert "가설" in text or "시뮬" in text
        assert "SALES-1" in text or "인터뷰" in text


class TestConstitutionInvariants:
    """Cycle 61 = 페르소나 시뮬 ≠ 실 인터뷰 (ADR 0046 후보 invariant 11)."""

    def test_simulation_warning_in_summary(self):
        text = render_persona_summary()
        # ⚠ 또는 "시뮬"·"가설" = 정직 헤더 필수
        assert any(marker in text for marker in ["⚠", "시뮬", "가설", "0건"])

    def test_messages_persona_specific(self):
        # 8 페르소나 = 다른 영업 메시지 (단일 메시지 위반 회피)
        messages = [p.primary_message for p in EIGHT_ICP_PERSONAS]
        assert len(set(messages)) >= 7  # P5 PO 자관 외 7개 모두 다름

    def test_payment_channel_diversification(self):
        # 5 결제 채널 = 분리 (외부 858 보고서 정합)
        channels = [p.sales_channel for p in EIGHT_ICP_PERSONAS]
        # 최소 5 다른 채널 (자치구·학교장터·공공·KERIS·KLMA)
        unique_count = len({c.split("·")[0] for c in channels})
        assert unique_count >= 4


@pytest.fixture
def all_scores():
    return app_coverage_matrix()


class TestPMFDistribution:
    def test_at_least_two_personas_pmf_pass(self, all_scores):
        # P5 + P2 또는 P8 = 최소 2 페르소나 PMF 정합
        passing = [s for s in all_scores if s.total_pmf >= PMF_THRESHOLD]
        assert len(passing) >= 2

    def test_at_least_one_underserved(self, all_scores):
        # P3 = 반드시 underserved (계약직·결제권 X)
        failing = [s for s in all_scores if s.total_pmf < PMF_THRESHOLD]
        assert len(failing) >= 1
