"""Cycle 18B P40 — LLM GEO + 인용 모니터링 회귀."""

from __future__ import annotations

from kormarc_auto.geo import (
    STANDARD_QUERIES,
    build_baseline_query_set,
    measure_answer_first,
    measure_fact_density,
    parse_citation_response,
)
from kormarc_auto.geo.citation_monitor import aggregate_results


class TestStandardQueries:
    def test_10_queries(self):
        assert len(STANDARD_QUERIES) == 10

    def test_kolas3_queries_present(self):
        joined = " ".join(STANDARD_QUERIES)
        assert "KOLAS III" in joined or "KOLAS3" in joined

    def test_kormarc_queries_present(self):
        assert any("KORMARC" in q for q in STANDARD_QUERIES)

    def test_baseline_query_set_structure(self):
        s = build_baseline_query_set()
        assert len(s) == 10
        for q in s:
            assert "id" in q and "query" in q
            assert q["expected_our_citation"] is True


class TestAnswerFirst:
    def test_passing_definition_paragraph(self):
        text = (
            "kormarc-auto는 한국 도서관 사서를 위한 KORMARC 자동 생성 SaaS이다. "
            "ISBN 1번 입력으로 5초 안에 KOLAS III·DLS·알파스 호환 .mrc 파일을 생성한다. "
            "자관 PILOT 1관 174 파일에서 round-trip 100% 정합도를 검증했고 권당 100원에 제공된다."
        )
        report = measure_answer_first(text)
        assert report.has_definition_pattern is True
        # 단어 카운트 검증 (40-60 범위 내일 가능성)
        assert report.word_count >= 30

    def test_failing_too_short(self):
        text = "짧은 단락."
        report = measure_answer_first(text)
        assert report.is_passing is False

    def test_failing_no_definition(self):
        text = (
            "오늘은 좋은 날씨입니다. 도서관에 갔습니다. KOLAS III 보고를 보았습니다. "
            "여러 사서들과 이야기했습니다. 점심을 먹었습니다. 다양한 책을 보았습니다. "
            "오후에는 집으로 돌아왔습니다. 저녁에는 영화를 봤습니다. 잤습니다."
        )
        report = measure_answer_first(text)
        # 정의문 패턴 없음
        assert report.has_definition_pattern is False


class TestFactDensity:
    def test_high_density_passes(self):
        text = (
            "kormarc-auto는 2026년 출시되었다. 자관 174 파일·3,383 레코드로 검증했고 "
            "round-trip 100% 정합도를 달성했다. KOLAS III는 2026-12-31 종료된다. "
            "공공도서관 1,296개관이 영향받는다. 가격은 권당 100원이다."
        )
        result = measure_fact_density(text)
        assert result["fact_count"] >= 5
        assert result["is_passing"] is True

    def test_zero_facts_fails(self):
        text = "오늘은 좋은 하루였습니다. " * 30
        result = measure_fact_density(text)
        assert result["fact_count"] == 0
        assert result["is_passing"] is False

    def test_kolas3_d_day_recognized(self):
        text = "KOLAS III D-240"
        result = measure_fact_density(text)
        assert result["fact_count"] >= 1


class TestCitationParsing:
    def test_our_brand_only(self):
        result = parse_citation_response(
            "KORMARC 자동 생성 도구 추천",
            "kormarc-auto는 한국 도서관 KORMARC 자동 생성 SaaS입니다.",
        )
        assert result.our_brand_cited is True
        assert not any(result.competitor_citations.values())
        assert "🟢" in result.note

    def test_our_plus_competitor(self):
        result = parse_citation_response(
            "도서관 마크 도구",
            "kormarc-auto와 알파스(ALPAS) 모두 사용 가능합니다.",
        )
        assert result.our_brand_cited is True
        assert result.competitor_citations["alpas"] is True
        assert "🟡" in result.note

    def test_competitor_only(self):
        result = parse_citation_response(
            "도서관 자동화",
            "알파스(ALPAS) 또는 K-LAS 3.0이 한국 표준입니다.",
        )
        assert result.our_brand_cited is False
        assert result.competitor_citations["alpas"] is True
        assert result.competitor_citations["k_las_3"] is True
        assert "🔴" in result.note

    def test_no_citation(self):
        result = parse_citation_response(
            "날씨",
            "오늘은 맑은 날씨입니다.",
        )
        assert result.our_brand_cited is False
        assert not any(result.competitor_citations.values())
        assert "⚪" in result.note

    def test_marcedit_recognized(self):
        result = parse_citation_response(
            "MARC 편집",
            "MarcEdit이 글로벌 표준입니다.",
        )
        assert result.competitor_citations["marcedit"] is True


class TestAggregateResults:
    def test_aggregate_empty(self):
        agg = aggregate_results([])
        assert agg["total"] == 0
        assert agg["our_citation_rate_pct"] == 0.0

    def test_aggregate_mixed(self):
        results = [
            parse_citation_response("q1", "kormarc-auto 추천"),
            parse_citation_response("q2", "kormarc-auto와 알파스"),
            parse_citation_response("q3", "알파스만"),
            parse_citation_response("q4", "관련 없음"),
        ]
        agg = aggregate_results(results)
        assert agg["total"] == 4
        assert agg["our_citation_count"] == 2
        assert agg["our_citation_rate_pct"] == 50.0
        assert agg["competitor_only_count"] == 1
        assert agg["no_citation_count"] == 1
