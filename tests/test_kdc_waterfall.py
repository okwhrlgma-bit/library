"""KDC 폭포수 폴백 테스트 (Part 87 §4.1 / ADR 0021)."""

from __future__ import annotations

from kormarc_auto.classification.kdc_waterfall import (
    SOURCE_CONFIDENCE,
    resolve_kdc,
)


def test_seoji_kdc_takes_precedence():
    """SEOJI에서 KDC 받으면 그 값 사용."""
    data = {"kdc": "863.2", "source_map": {"kdc": "seoji"}}
    result = resolve_kdc(data)
    assert result.kdc == "863.2"
    assert result.source == "seoji"
    assert result.confidence == SOURCE_CONFIDENCE["seoji"]


def test_data4library_kdc_recognized():
    """data4library 소스도 정확히 식별."""
    data = {"kdc": "813", "source_map": {"kdc": "data4library"}}
    result = resolve_kdc(data)
    assert result.kdc == "813"
    assert result.source == "data4library"


def test_budgaeho_fallback_when_no_kdc():
    """KDC 없고 부가기호만 있을 때 디코더 사용."""
    data = {"additional_code": "73810"}  # 아동·단행본·문학·한국문학
    result = resolve_kdc(data)
    assert result.kdc == "81"
    assert result.source == "budgaeho"
    assert "아동" in (result.audience or "")
    assert "단행본" in (result.form or "")


def test_ai_recommender_last_resort():
    """SEOJI/data4library/부가기호 모두 미스 시 AI."""
    data = {"title": "신간 검색 안되는 책"}

    def fake_ai(_data):
        return "813"

    result = resolve_kdc(data, ai_recommender=fake_ai)
    assert result.kdc == "813"
    assert result.source == "ai"
    assert result.confidence == SOURCE_CONFIDENCE["ai"]


def test_all_sources_miss():
    """폴백 전부 실패 시 missing."""
    result = resolve_kdc({"title": "데이터 없음"})
    assert result.kdc is None
    assert result.source == "missing"
    assert result.confidence == 0.0


def test_ai_exception_falls_through():
    """AI 호출 예외 시 missing으로 fall through."""

    def broken_ai(_data):
        raise RuntimeError("AI 서비스 다운")

    result = resolve_kdc({"title": "X"}, ai_recommender=broken_ai)
    assert result.source == "missing"


def test_budgaeho_invalid_falls_to_ai():
    """부가기호 형식 불일치 시 다음 단계로."""
    data = {"additional_code": "ABC"}

    def fake_ai(_data):
        return "999"

    result = resolve_kdc(data, ai_recommender=fake_ai)
    assert result.source == "ai"
