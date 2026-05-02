"""KDC 폴백 폭포수 — Part 87 §4.1 정식화 (2026-05-03).

폴백 순서:
1. SEOJI (nl_korea) — 가장 정확하나 2020-12-31 이후 KDC 미제공
2. data4library — 도서관 정보나루 KDC 보강
3. **부가기호 디코더** — EAN-13 add-on 5자리 → KDC 2자리 (0 API 호출·100% 정확)
4. AI 추천 (sub_recommender·classification.kdc_classifier) — 마지막 폴백
5. 사서 직접 입력

각 단계 결과를 source 추적·confidence 점수와 함께 반환.

Part 87 §4.2: 부가기호는 SEOJI 공백을 메우는 핵심 무비용 전략.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from kormarc_auto.classification.budgaeho_decoder import decode_budgaeho

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KdcResolution:
    """KDC 해결 결과 (어느 단계에서 어떤 신뢰도로 나왔는지)."""

    kdc: str | None
    source: str  # "seoji" / "data4library" / "budgaeho" / "ai" / "missing"
    confidence: float  # 0.0~1.0
    raw_input: str | None = None  # 출처 raw 데이터 (디버깅)
    audience: str | None = None  # 부가기호에서 추가 추출
    form: str | None = None


# 단계별 신뢰도 가중치
SOURCE_CONFIDENCE: dict[str, float] = {
    "seoji": 0.95,
    "data4library": 0.85,
    "budgaeho": 0.80,  # 1.5자리 정확·전체 KDC는 추가 보강 필요
    "ai": 0.60,  # AI 추천은 사서 검토 필수
    "missing": 0.0,
}


def resolve_kdc(
    book_data: dict[str, Any],
    *,
    ai_recommender=None,
) -> KdcResolution:
    """KDC 폭포수 폴백 해결.

    Args:
        book_data: aggregator 결과 dict (kdc·additional_code·source_map 등 포함)
        ai_recommender: 옵션. AI KDC 분류기 (마지막 폴백)

    Returns:
        KdcResolution (kdc·source·confidence·audience·form)
    """
    source_map = book_data.get("source_map") or {}

    # 1단계: SEOJI 또는 data4library에서 이미 KDC 있는지
    existing_kdc = book_data.get("kdc")
    if existing_kdc:
        kdc_source_origin = source_map.get("kdc", "seoji")
        if kdc_source_origin == "data4library":
            return KdcResolution(
                kdc=str(existing_kdc),
                source="data4library",
                confidence=SOURCE_CONFIDENCE["data4library"],
                raw_input=str(existing_kdc),
            )
        return KdcResolution(
            kdc=str(existing_kdc),
            source="seoji",
            confidence=SOURCE_CONFIDENCE["seoji"],
            raw_input=str(existing_kdc),
        )

    # 2단계: 부가기호 5자리 디코딩 (무비용)
    add_code = book_data.get("additional_code")
    if add_code:
        decoded = decode_budgaeho(str(add_code))
        if decoded:
            logger.info("KDC 폴백 = 부가기호 (raw=%s, kdc=%s)", decoded.raw, decoded.kdc_2digit)
            return KdcResolution(
                kdc=decoded.kdc_2digit,
                source="budgaeho",
                confidence=SOURCE_CONFIDENCE["budgaeho"],
                raw_input=decoded.raw,
                audience=decoded.target_audience,
                form=decoded.publication_form,
            )

    # 3단계: AI 추천 (옵션)
    if ai_recommender is not None:
        try:
            ai_result = ai_recommender(book_data)
            if ai_result and isinstance(ai_result, str):
                return KdcResolution(
                    kdc=ai_result,
                    source="ai",
                    confidence=SOURCE_CONFIDENCE["ai"],
                    raw_input=ai_result,
                )
        except Exception as e:
            logger.warning("AI KDC 추천 실패: %s", e)

    # 4단계: 모두 미스
    return KdcResolution(kdc=None, source="missing", confidence=0.0)


__all__ = [
    "SOURCE_CONFIDENCE",
    "KdcResolution",
    "resolve_kdc",
]
