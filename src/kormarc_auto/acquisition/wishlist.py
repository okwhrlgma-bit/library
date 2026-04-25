"""비치희망도서 수서 분석 — 알파스 03~05장 + 장서개발지침(제3판) §2 흡수.

사서 일과의 절반은 *수서 결정*. 페인포인트:
1. 이용자 신청 ISBN 100건 → 각각 자관 중복 체크 (수기)
2. 외부 가격·재고 확인 (NL Korea·알라딘·정보나루 → 다른 창)
3. KDC 균형 — 한 분야 편중 시 도서관 운영평가 감점

본 모듈은 ISBN 일괄 → 자관 중복 + 외부 메타 + KDC 분포 분석을 한 번에.

매출 영향: PO 사업화 플레이북 16번 "수작업 대행 월 30~100만원" — 본 모듈
도입 시 사서 1인이 시간내 처리 가능. 작은도서관·학교도서관 ICP 직타깃.
"""

from __future__ import annotations

import contextlib
import logging
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from kormarc_auto.api.aggregator import aggregate_by_isbn

logger = logging.getLogger(__name__)


# 장서개발지침 (NL Korea 제3판) 권장 — 1인 사서가 매월 균형 점검
# KDC 1자리 분류별 권장 비율 (공공도서관 표준)
KDC_BALANCE_TARGETS = {
    "0": (0.05, 0.08),  # 총류 5~8%
    "1": (0.05, 0.08),  # 철학
    "2": (0.05, 0.08),  # 종교
    "3": (0.10, 0.15),  # 사회과학
    "4": (0.05, 0.08),  # 자연과학
    "5": (0.10, 0.15),  # 기술과학
    "6": (0.05, 0.10),  # 예술
    "7": (0.05, 0.10),  # 언어
    "8": (0.20, 0.30),  # 문학 (가장 큰 비중)
    "9": (0.10, 0.15),  # 역사
}


@dataclass
class WishlistItem:
    """희망도서 1건 분석 결과."""

    isbn: str
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    publication_year: str | None = None
    kdc: str | None = None
    price_krw: int | None = None
    in_holdings: bool = False  # 자관 중복 보유 여부
    confidence: float = 0.0
    sources: list[str] | None = None
    error: str | None = None


def _holdings_by_isbn() -> dict[str, dict[str, Any]]:
    """자관 장서를 ISBN dict로. 없으면 빈 dict."""
    try:
        from kormarc_auto.inventory.library_db import search_local
    except ImportError:
        return {}
    by_isbn: dict[str, dict[str, Any]] = {}
    for rec in search_local("", limit=100000):
        isbn = str(rec.get("isbn") or "").replace("-", "")
        if isbn:
            by_isbn[isbn] = rec
    return by_isbn


def analyze_wishlist(
    isbns: Iterable[str],
    *,
    use_external: bool = True,
) -> list[WishlistItem]:
    """ISBN 리스트 → 자관 중복 + 외부 메타 분석.

    use_external=False면 자관 DB만 (오프라인).
    """
    by_isbn = _holdings_by_isbn()

    out: list[WishlistItem] = []
    for raw in isbns:
        clean = str(raw).replace("-", "").strip()
        if not clean:
            continue
        item = WishlistItem(isbn=clean)
        if clean in by_isbn:
            existing = by_isbn[clean]
            item.in_holdings = True
            item.title = existing.get("title")
            item.author = existing.get("author")
            item.kdc = existing.get("kdc")

        if use_external:
            try:
                book = aggregate_by_isbn(clean)
                item.title = item.title or book.get("title")
                item.author = item.author or book.get("author")
                item.publisher = book.get("publisher")
                item.publication_year = (
                    book.get("publication_year") or book.get("pub_year")
                )
                item.kdc = item.kdc or book.get("kdc")
                price = book.get("price") or book.get("price_krw")
                if price:
                    with contextlib.suppress(ValueError, TypeError):
                        item.price_krw = int(
                            str(price).replace(",", "").replace("원", "").strip()
                        )
                item.confidence = float(book.get("confidence", 0))
                item.sources = book.get("sources") or []
            except Exception as e:
                item.error = f"외부 조회 실패: {e}"
                logger.warning("희망도서 %s 조회 실패: %s", clean, e)

        out.append(item)
    return out


def kdc_distribution(items: Iterable[WishlistItem]) -> dict[str, int]:
    """KDC 1자리 분포 (희망도서 기준)."""
    c: Counter[str] = Counter()
    for it in items:
        if it.kdc:
            c[str(it.kdc)[0]] += 1
        else:
            c["?"] += 1
    return dict(c)


def kdc_balance_warnings(
    items: Iterable[WishlistItem],
    *,
    targets: dict[str, tuple[float, float]] | None = None,
) -> list[str]:
    """수서 분포가 권장 비율을 벗어나면 경고.

    예: 문학(8) 80% 편중 시 "문학 비중 80% — 권장 20~30% 초과".
    """
    targets = targets or KDC_BALANCE_TARGETS
    items_list = list(items)
    total = sum(1 for it in items_list if it.kdc)
    if total == 0:
        return []
    dist = kdc_distribution(items_list)
    warnings: list[str] = []
    for cls, (lo, hi) in targets.items():
        count = dist.get(cls, 0)
        ratio = count / total if total else 0
        if ratio > hi:
            warnings.append(
                f"KDC {cls} 비중 {ratio:.0%} ({count}/{total}) — "
                f"권장 {lo:.0%}~{hi:.0%} 초과 (장서개발지침 §2)"
            )
    return warnings


def summarize(items: list[WishlistItem]) -> dict[str, Any]:
    """수서 결정 요약 — 사서 보고서·결재서식용."""
    in_holdings = sum(1 for it in items if it.in_holdings)
    new_purchase = len(items) - in_holdings
    total_price = sum(it.price_krw for it in items if it.price_krw and not it.in_holdings)
    confidence_avg = (
        sum(it.confidence for it in items) / len(items) if items else 0
    )
    return {
        "total": len(items),
        "in_holdings": in_holdings,
        "new_purchase": new_purchase,
        "estimated_cost_krw": total_price,
        "kdc_distribution": kdc_distribution(items),
        "balance_warnings": kdc_balance_warnings(items),
        "average_confidence": round(confidence_avg, 2),
        "errors": [{"isbn": it.isbn, "error": it.error} for it in items if it.error],
    }


__all__ = [
    "KDC_BALANCE_TARGETS",
    "WishlistItem",
    "analyze_wishlist",
    "kdc_balance_warnings",
    "kdc_distribution",
    "summarize",
]
