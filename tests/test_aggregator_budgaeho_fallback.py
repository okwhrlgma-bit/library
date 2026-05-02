"""aggregator KDC 폴백 (부가기호 디코더) 통합 테스트 (Part 87 / ADR 0021)."""

from __future__ import annotations

from unittest.mock import patch

from kormarc_auto.api import aggregator


def test_kdc_fallback_uses_budgaeho_when_seoji_misses():
    """SEOJI에 KDC가 없어도 부가기호에서 자동 추출."""
    fake_nl = {
        "isbn": "9788937437076",
        "title": "어린왕자",
        "author": "생텍쥐페리",
        "additional_code": "73810",  # 아동·단행본·문학·한국문학
        "confidence": 0.95,
        "attribution": "국립중앙도서관",
        # 의도적으로 kdc 없음
    }
    with (
        patch.object(aggregator.nl_korea, "fetch_by_isbn", return_value=fake_nl),
        patch.object(aggregator.aladin, "fetch_by_isbn", return_value=None),
        patch.object(aggregator.data4library, "fetch_keywords", return_value=[]),
    ):
        result = aggregator.aggregate_by_isbn("9788937437076")

    assert result["kdc"] == "81"  # 문학·한국문학
    assert result["kdc_source"] == "budgaeho_decoder"
    assert result["source_map"]["kdc"] == "budgaeho"
    assert "아동" in result["kdc_audience"]
    assert "단행본" in result["kdc_form"]


def test_kdc_from_seoji_takes_precedence_over_budgaeho():
    """SEOJI가 KDC를 제공하면 부가기호 폴백 X."""
    fake_nl = {
        "isbn": "9788937437076",
        "kdc": "863.2",  # SEOJI 제공
        "additional_code": "73810",  # 부가기호도 있지만
        "confidence": 0.95,
        "attribution": "국립중앙도서관",
    }
    with (
        patch.object(aggregator.nl_korea, "fetch_by_isbn", return_value=fake_nl),
        patch.object(aggregator.aladin, "fetch_by_isbn", return_value=None),
        patch.object(aggregator.data4library, "fetch_keywords", return_value=[]),
    ):
        result = aggregator.aggregate_by_isbn("9788937437076")

    assert result["kdc"] == "863.2"  # SEOJI 우선
    assert result.get("kdc_source") != "budgaeho_decoder"


def test_kdc_no_fallback_when_no_additional_code():
    """부가기호 없으면 KDC 폴백 시도 X (logger.info 발생 X)."""
    fake_nl = {
        "isbn": "9788937437076",
        "title": "테스트",
        "confidence": 0.95,
        "attribution": "NL",
        # kdc, additional_code 모두 없음
    }
    with (
        patch.object(aggregator.nl_korea, "fetch_by_isbn", return_value=fake_nl),
        patch.object(aggregator.aladin, "fetch_by_isbn", return_value=None),
        patch.object(aggregator.data4library, "fetch_keywords", return_value=[]),
    ):
        result = aggregator.aggregate_by_isbn("9788937437076")

    assert result.get("kdc") is None
    assert result.get("kdc_source") is None
