"""비치희망도서 수서 분석 단위 테스트."""

from __future__ import annotations

from unittest.mock import patch

from kormarc_auto.acquisition.wishlist import (
    KDC_BALANCE_TARGETS,
    WishlistItem,
    analyze_wishlist,
    kdc_balance_warnings,
    kdc_distribution,
    summarize,
)


def test_kdc_distribution():
    items = [
        WishlistItem(isbn="1", kdc="813.7"),
        WishlistItem(isbn="2", kdc="813.6"),
        WishlistItem(isbn="3", kdc="911.05"),
        WishlistItem(isbn="4", kdc=None),
    ]
    dist = kdc_distribution(items)
    assert dist["8"] == 2
    assert dist["9"] == 1
    assert dist["?"] == 1


def test_kdc_balance_warnings_lit_overflow():
    """문학 80% → 경고 (권장 20~30%)."""
    items = [WishlistItem(isbn=str(i), kdc="813") for i in range(8)] + [
        WishlistItem(isbn=str(i), kdc="500") for i in range(2)
    ]
    warnings = kdc_balance_warnings(items)
    assert any("KDC 8" in w for w in warnings)


def test_kdc_balance_warnings_no_kdc():
    items = [WishlistItem(isbn="1")]
    assert kdc_balance_warnings(items) == []


def test_summarize_combines_holdings_purchase():
    items = [
        WishlistItem(isbn="1", in_holdings=True, kdc="813"),
        WishlistItem(isbn="2", in_holdings=False, kdc="813", price_krw=15000),
        WishlistItem(isbn="3", in_holdings=False, kdc="813", price_krw=20000),
    ]
    s = summarize(items)
    assert s["total"] == 3
    assert s["in_holdings"] == 1
    assert s["new_purchase"] == 2
    assert s["estimated_cost_krw"] == 35000


def test_kdc_targets_complete():
    """0~9 모든 KDC 1자리 분류 권장 범위 정의."""
    for cls in "0123456789":
        assert cls in KDC_BALANCE_TARGETS


@patch("kormarc_auto.acquisition.wishlist._holdings_by_isbn")
@patch("kormarc_auto.acquisition.wishlist.aggregate_by_isbn")
def test_analyze_wishlist_marks_holdings(mock_agg, mock_holdings):
    """자관 보유 ISBN은 in_holdings=True."""
    mock_holdings.return_value = {
        "9788912345678": {"isbn": "9788912345678", "title": "기존도서", "kdc": "813.7"}
    }
    mock_agg.return_value = {
        "title": "기존도서",
        "publisher": "출판",
        "kdc": "813.7",
        "confidence": 0.9,
        "sources": ["nl"],
    }
    items = analyze_wishlist(["9788912345678", "9788999999999"])
    assert len(items) == 2
    assert items[0].in_holdings is True
    assert items[1].in_holdings is False


@patch("kormarc_auto.acquisition.wishlist._holdings_by_isbn")
def test_analyze_wishlist_no_external(mock_holdings):
    """use_external=False면 외부 호출 안 함."""
    mock_holdings.return_value = {}
    items = analyze_wishlist(["9788912345678"], use_external=False)
    assert len(items) == 1
    assert items[0].title is None
    assert items[0].in_holdings is False
