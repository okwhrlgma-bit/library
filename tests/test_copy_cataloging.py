"""KOLIS-NET 카피 카탈로깅 테스트 (Part 87 §9 M7 / ADR 0021)."""

from __future__ import annotations

from kormarc_auto.classification.copy_cataloging import (
    CopyCatalogingResult,
    aggregate_subjects,
    copy_catalog_from_kolisnet,
    majority_vote_call_number,
    majority_vote_kdc,
)


def test_majority_vote_kdc_basic():
    """가장 흔한 KDC 선택."""
    items = [
        {"kdc": "813"},
        {"kdc": "813"},
        {"kdc": "863"},
        {"kdc": "813"},
    ]
    assert majority_vote_kdc(items) == "813"


def test_majority_vote_kdc_empty():
    assert majority_vote_kdc([]) is None
    assert majority_vote_kdc([{"title": "X"}]) is None  # KDC 키 없음


def test_majority_vote_call_number():
    items = [
        {"call_number": "813.6/한31ㅈ"},
        {"call_number": "813.6/한31ㅈ"},
        {"call_number": "813.6/김34ㅎ"},
    ]
    assert majority_vote_call_number(items) == "813.6/한31ㅈ"


def test_aggregate_subjects_top_n():
    """주제명 빈도 상위 N개."""
    items = [
        {"subjects": ["소설", "한국문학", "현대"]},
        {"subjects": ["소설", "한국문학"]},
        {"subjects": ["소설", "추리"]},
    ]
    result = aggregate_subjects(items, top_n=3)
    assert result[0] == "소설"  # 빈도 3
    assert "한국문학" in result
    assert len(result) == 3


def test_aggregate_subjects_string_input():
    """주제명이 string으로 들어와도 처리."""
    items = [{"subjects": "단일주제"}, {"subjects": "단일주제"}]
    result = aggregate_subjects(items)
    assert result == ["단일주제"]


def test_copy_catalog_from_kolisnet_match_5_plus():
    """5개관 이상 매칭 시 confidence = 1.0."""
    items = [
        {"kdc": "813.6", "call_number": "813.6/한31ㅈ", "subjects": ["소설"]},
        {"kdc": "813.6", "call_number": "813.6/한31ㅈ", "subjects": ["소설"]},
        {"kdc": "813.6", "call_number": "813.6/한31ㅈ", "subjects": ["한국문학"]},
        {"kdc": "813.6", "call_number": "813.6/한31ㅈ", "subjects": ["소설"]},
        {"kdc": "813.6", "call_number": "813.6/한31ㅈ", "subjects": ["현대"]},
    ]
    result = copy_catalog_from_kolisnet("9788937437076", items)
    assert isinstance(result, CopyCatalogingResult)
    assert result.matched_libraries == 5
    assert result.suggested_kdc == "813.6"
    assert result.suggested_call_number == "813.6/한31ㅈ"
    assert "소설" in result.suggested_subjects
    assert result.confidence == 1.0


def test_copy_catalog_from_kolisnet_no_match():
    """매칭 0건 = 폴백 위임."""
    result = copy_catalog_from_kolisnet("9789999999999", [])
    assert result.matched_libraries == 0
    assert result.suggested_kdc is None
    assert result.confidence == 0.0


def test_copy_catalog_partial_match_2_libs():
    """2개관 매칭 = confidence = 0.4."""
    items = [
        {"kdc": "813", "subjects": ["소설"]},
        {"kdc": "813", "subjects": ["문학"]},
    ]
    result = copy_catalog_from_kolisnet("9788937437076", items)
    assert result.matched_libraries == 2
    assert result.confidence == 0.4
    assert result.suggested_kdc == "813"


def test_consensus_distribution():
    """library_consensus = KDC 분포 dict."""
    items = [
        {"kdc": "813"},
        {"kdc": "813"},
        {"kdc": "863"},
    ]
    result = copy_catalog_from_kolisnet("X", items)
    assert result.library_consensus["matched"] == 3
    assert result.library_consensus["kdc_distribution"] == {"813": 2, "863": 1}
