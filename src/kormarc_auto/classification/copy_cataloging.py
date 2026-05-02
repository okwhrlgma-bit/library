"""KOLIS-NET 카피 카탈로깅 자동화 — Part 87 §9 M7 (2026-05-03).

핵심 통찰: 한국 사서의 실 워크플로우 70~80% = "KOLIS-NET 검색 → 복사 → 붙여넣기".
이를 자동화하면 새 시장 창출이 아니라 기존 노동의 시간만 빼앗는 가장 안전한 가치 제안.

폴백 통합:
1. KOLIS-NET 종합목록 검색 (kolisnet_compare.fetch_other_libraries)
2. 매칭 성공 시 = 다른 도서관 분류·청구기호·주제명 차용 (가중 다수결)
3. 매칭 실패 시 = aggregator 폭포수 + budgaeho_decoder + AI

사서 결정권 보장: copy_cataloging은 *추천*만. 사서가 최종 채택/수정.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CopyCatalogingResult:
    """카피 카탈로깅 추천 결과."""

    isbn: str
    matched_libraries: int  # 매칭된 다른 도서관 수
    suggested_kdc: str | None
    suggested_call_number: str | None  # 가장 흔한 청구기호 패턴
    suggested_subjects: list[str] = field(default_factory=list)  # 주제명 (650/653)
    confidence: float = 0.0  # 0.0~1.0 (매칭 도서관 수 비례)
    library_consensus: dict[str, Any] = field(default_factory=dict)  # 가중 분포


def majority_vote_kdc(items: list[dict[str, Any]]) -> str | None:
    """다른 도서관들의 KDC 가중 다수결.

    가중치: KDC 정확도 = 도서관 수 비례 (정수).
    """
    kdcs = [it.get("kdc") for it in items if it.get("kdc")]
    if not kdcs:
        return None
    counter = Counter(kdcs)
    return counter.most_common(1)[0][0]


def majority_vote_call_number(items: list[dict[str, Any]]) -> str | None:
    """청구기호 가장 흔한 패턴 (자관 prefix 무시·KDC + 저자기호만)."""
    patterns = [it.get("call_number") for it in items if it.get("call_number")]
    if not patterns:
        return None
    counter = Counter(patterns)
    return counter.most_common(1)[0][0]


def aggregate_subjects(items: list[dict[str, Any]], top_n: int = 5) -> list[str]:
    """주제명 누적 (650/653) → 빈도 상위 top_n."""
    all_subjects: list[str] = []
    for it in items:
        subjects = it.get("subjects") or it.get("subject_keywords") or []
        if isinstance(subjects, str):
            subjects = [subjects]
        all_subjects.extend(s for s in subjects if s)
    if not all_subjects:
        return []
    counter = Counter(all_subjects)
    return [s for s, _ in counter.most_common(top_n)]


def copy_catalog_from_kolisnet(
    isbn: str,
    kolisnet_items: list[dict[str, Any]] | None = None,
) -> CopyCatalogingResult:
    """KOLIS-NET 검색 결과 → 카피 카탈로깅 추천 생성.

    Args:
        isbn: 13자리 ISBN
        kolisnet_items: 사전 조회한 KOLIS-NET 결과
                        (None이면 호출 측이 kolisnet_compare.fetch_other_libraries 호출 후 전달)

    Returns:
        CopyCatalogingResult — 사서 검토용 추천
    """
    items = kolisnet_items or []
    matched = len(items)

    if matched == 0:
        logger.info("KOLIS-NET 매칭 0건: ISBN=%s — 폴백 폭포수로 위임", isbn)
        return CopyCatalogingResult(
            isbn=isbn,
            matched_libraries=0,
            suggested_kdc=None,
            suggested_call_number=None,
            confidence=0.0,
        )

    suggested_kdc = majority_vote_kdc(items)
    suggested_call = majority_vote_call_number(items)
    suggested_subjects = aggregate_subjects(items)

    # 신뢰도 = 매칭 도서관 수 / 5 (5개관 이상 = 1.0)
    confidence = min(matched / 5.0, 1.0)

    consensus = {
        "kdc_distribution": dict(Counter(it.get("kdc") for it in items if it.get("kdc"))),
        "subject_count": len(suggested_subjects),
        "matched": matched,
    }

    logger.info(
        "KOLIS-NET 카피 카탈로깅: ISBN=%s, 매칭=%d개관, KDC=%s, 신뢰도=%.2f",
        isbn,
        matched,
        suggested_kdc,
        confidence,
    )

    return CopyCatalogingResult(
        isbn=isbn,
        matched_libraries=matched,
        suggested_kdc=suggested_kdc,
        suggested_call_number=suggested_call,
        suggested_subjects=suggested_subjects,
        confidence=confidence,
        library_consensus=consensus,
    )


__all__ = [
    "CopyCatalogingResult",
    "aggregate_subjects",
    "copy_catalog_from_kolisnet",
    "majority_vote_call_number",
    "majority_vote_kdc",
]
