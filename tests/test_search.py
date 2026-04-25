"""api/search.py 통합 검색 테스트 (mock)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.api import search as search_mod  # noqa: E402


def test_empty_query_returns_empty():
    assert search_mod.search_by_query("") == []
    assert search_mod.search_by_query("   ") == []


@patch("kormarc_auto.api.search.kakao")
@patch("kormarc_auto.api.search.aladin")
@patch("kormarc_auto.api.search.nl_korea")
def test_search_dedups_by_isbn(mock_nl, mock_al, mock_kk):
    """같은 ISBN을 두 소스가 반환하면 dedup."""
    mock_nl.search_by_query.return_value = [
        {
            "isbn": "9788936434120",
            "title": "작별하지 않는다",
            "author": "한강",
            "publisher": "창비",
            "publication_year": "2021",
            "source": "nl_korea",
            "confidence": 0.95,
        }
    ]
    mock_al.search_by_query.return_value = [
        {
            "isbn": "9788936434120",
            "title": "작별하지 않는다",
            "author": "한강",
            "publisher": "창비",
            "source": "aladin",
            "confidence": 0.80,
        }
    ]
    mock_kk.search_by_query.return_value = []

    results = search_mod.search_by_query("한강", limit=10)
    isbns = [r["isbn"] for r in results]
    assert isbns.count("9788936434120") == 1
    assert results[0]["source"] == "nl_korea"  # 신뢰도 높은 쪽 유지


@patch("kormarc_auto.api.search.kakao")
@patch("kormarc_auto.api.search.aladin")
@patch("kormarc_auto.api.search.nl_korea")
def test_search_falls_through_when_nl_fails(mock_nl, mock_al, mock_kk):
    """NL 실패해도 알라딘/카카오 시도."""
    from kormarc_auto.api.nl_korea import NLKoreaAPIError

    mock_nl.NLKoreaAPIError = NLKoreaAPIError
    mock_nl.search_by_query.side_effect = NLKoreaAPIError("boom")
    mock_al.search_by_query.return_value = [
        {"isbn": "9788932020789", "title": "작별인사", "source": "aladin", "confidence": 0.80}
    ]
    mock_kk.search_by_query.return_value = []

    results = search_mod.search_by_query("김영하", limit=10)
    assert len(results) == 1
    assert results[0]["isbn"] == "9788932020789"
