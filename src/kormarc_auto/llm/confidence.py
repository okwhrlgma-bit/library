"""갈래 A Cycle 13A (P15·T4-4) — 카테고리형 신뢰 + top-2 signals.

목표:
- raw 확률 % UI/API/CLI 모두 금지 (헌법 §2 강화)
- 3 카테고리만: 확실 (green) / 검토 필요 (amber) / 불확실 (red)
- top-2 contributing signals 반환 (사서 판단 보조)

산정 기준 (외부 매출 보고서 P15 정합):
- 확실: ISBN-grounded + 외부 API 일치 + 모델 자체 신뢰도 > 0.9
- 검토 필요: ISBN-grounded·외부 API 부분 일치 또는 모델 신뢰도 0.7~0.9
- 불확실: ISBN 없음·외부 API 미존재·LLM 단독 추론 또는 모델 신뢰도 < 0.7

ADR 0031 박제·기존 field_status.ConfidenceLevel과 정합.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CategoryLabel = Literal["확실", "검토 필요", "불확실"]


# 신호별 가중치 (외부 보고서 P15·실측 후 ENV override 가능)
SIGNAL_WEIGHTS = {
    "isbn_grounded": 30,  # ISBN 존재 + 검증 통과
    "external_api_match": 25,  # NL Korea/Aladin/data4library 응답 일치
    "external_api_partial": 10,  # 부분 일치 (출판사 일치·표제 다름 등)
    "model_self_confidence_high": 20,  # LLM 자체 logprob > 0.9
    "model_self_confidence_mid": 10,  # 0.7~0.9
    "kdc_authority_match": 15,  # KDC 권위 파일 매칭
    "vision_ocr_supported": 10,  # 사진 OCR 지원
    "field_rule_based": 25,  # 008 fixed-position 등 규칙 기반
    "llm_inferred_only": -20,  # LLM 단독 추론 (감점)
    "ground_truth_unavailable": -15,  # ISBN/외부 API 미존재 (감점)
}


@dataclass(frozen=True)
class Signal:
    """기여 신호 (사서가 chip 클릭 시 detail panel)."""

    code: str
    description: str  # 한국어 (사서 친화)
    weight: int


@dataclass(frozen=True)
class ConfidenceResult:
    """카테고리형 신뢰 결과."""

    category: CategoryLabel
    top_signals: list[Signal]  # top 2

    def to_chip_dict(self) -> dict:
        """UI chip 렌더링 (raw % X)."""
        color = {"확실": "green", "검토 필요": "amber", "불확실": "red"}[self.category]
        icon = {"확실": "✓", "검토 필요": "ⓘ", "불확실": "⚠"}[self.category]
        return {
            "category": self.category,
            "color": color,
            "icon": icon,
            "signals": [
                {"code": s.code, "description": s.description, "weight": s.weight}
                for s in self.top_signals
            ],
        }


def _categorize_score(score: int) -> CategoryLabel:
    """점수 → 카테고리 (raw % 노출 X·내부 산정만)."""
    if score >= 60:
        return "확실"
    if score >= 30:
        return "검토 필요"
    return "불확실"


def calculate_confidence(signals_present: dict[str, bool]) -> ConfidenceResult:
    """신호 dict → 카테고리 + top-2 signals.

    Args:
        signals_present: {"isbn_grounded": True, "external_api_match": True, ...}

    Returns:
        ConfidenceResult (category·top_signals 2건·raw % X)
    """
    descriptions = {
        "isbn_grounded": "ISBN 검증 통과",
        "external_api_match": "외부 API 일치 (NL Korea·data4library)",
        "external_api_partial": "외부 API 부분 일치",
        "model_self_confidence_high": "AI 자체 신뢰도 높음",
        "model_self_confidence_mid": "AI 자체 신뢰도 중간",
        "kdc_authority_match": "KDC 권위 파일 매칭",
        "vision_ocr_supported": "표지 OCR 지원",
        "field_rule_based": "규칙 기반 (008 등)",
        "llm_inferred_only": "AI 단독 추론·검토 필요",
        "ground_truth_unavailable": "외부 검증 데이터 없음",
    }

    score = 0
    contributing: list[Signal] = []
    for code, present in signals_present.items():
        if not present:
            continue
        weight = SIGNAL_WEIGHTS.get(code, 0)
        score += weight
        contributing.append(
            Signal(code=code, description=descriptions.get(code, code), weight=weight)
        )

    # top-2 by absolute weight (감점도 표시)
    top_2 = sorted(contributing, key=lambda s: abs(s.weight), reverse=True)[:2]
    category = _categorize_score(score)
    return ConfidenceResult(category=category, top_signals=top_2)


def is_raw_percentage_in_text(text: str) -> bool:
    """헌법 §2 게이트 검증·텍스트에 raw % 노출 여부.

    검출 대상:
    - "92.3%"·"87%"·"신뢰도 0.87"·"확률 0.5"
    - "score 0.85"·"probability 90%"
    """
    import re

    patterns = [
        r"\b\d{1,3}\.\d{1,3}\s*%",  # "92.3%"
        r"\b\d{1,3}\s*%",  # "87%"
        r"신뢰도\s*[:=]?\s*0?\.\d+",  # "신뢰도 0.87"
        r"확률\s*[:=]?\s*0?\.\d+",  # "확률 0.5"
        r"확률\s*[:=]?\s*\d{1,3}\s*%",  # "확률 90%"
        r"score\s*[:=]?\s*0?\.\d+",  # "score 0.85"
        r"probability\s*[:=]?\s*\d+",  # "probability 90"
        r"confidence\s*[:=]?\s*0?\.\d+",  # "confidence 0.87"
    ]
    return any(re.search(pat, text, re.IGNORECASE) for pat in patterns)


__all__ = [
    "SIGNAL_WEIGHTS",
    "CategoryLabel",
    "ConfidenceResult",
    "Signal",
    "calculate_confidence",
    "is_raw_percentage_in_text",
]
