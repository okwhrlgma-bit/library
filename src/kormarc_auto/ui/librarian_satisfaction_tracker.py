"""사서 만족도 추적 (NPS·CSAT·CES) — PO 명령 2026-05-03 정합.

PO 비전: "사서가 편하고 쉽고 빠르게 사서 친화적·기존 모델 장점 보존"

사서 만족도 = PMF 핵심 지표.
NPS·CSAT·CES 자동 측정 + 페르소나별 분석 + Mem0 학습.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

SatisfactionMetric = Literal["nps", "csat", "ces"]


@dataclass(frozen=True)
class SatisfactionResponse:
    """사서 만족도 응답 1건."""

    librarian_id: str
    persona: str  # P1·P2·P14 등
    metric: SatisfactionMetric
    score: int  # NPS 0~10·CSAT 1~5·CES 1~5
    feedback: str = ""
    submitted_at: str = field(default_factory=lambda: datetime.now().isoformat())


def calculate_nps(scores: list[int]) -> dict:
    """NPS 계산 (Net Promoter Score).

    - 9~10 = Promoter
    - 7~8 = Passive
    - 0~6 = Detractor
    NPS = % Promoter - % Detractor
    """
    if not scores:
        return {"nps": 0, "promoters": 0, "passives": 0, "detractors": 0, "total": 0}

    promoters = sum(1 for s in scores if s >= 9)
    passives = sum(1 for s in scores if 7 <= s <= 8)
    detractors = sum(1 for s in scores if s <= 6)
    total = len(scores)

    nps = round((promoters / total - detractors / total) * 100)
    return {
        "nps": nps,
        "promoters": promoters,
        "promoter_pct": round(promoters / total * 100, 1),
        "passives": passives,
        "passive_pct": round(passives / total * 100, 1),
        "detractors": detractors,
        "detractor_pct": round(detractors / total * 100, 1),
        "total": total,
        "achieved_50": nps >= 50,  # B2C 우수
        "achieved_70": nps >= 70,  # 글로벌 상위
    }


def calculate_csat(scores: list[int]) -> dict:
    """CSAT (Customer Satisfaction) 계산.

    1~5 평가·평균 + 만족 비율 (4·5).
    """
    if not scores:
        return {"avg": 0, "satisfied_pct": 0, "total": 0}

    avg = round(sum(scores) / len(scores), 2)
    satisfied = sum(1 for s in scores if s >= 4)
    return {
        "avg": avg,
        "satisfied_pct": round(satisfied / len(scores) * 100, 1),
        "total": len(scores),
        "achieved_80": (satisfied / len(scores)) >= 0.8,  # 우수
    }


def calculate_ces(scores: list[int]) -> dict:
    """CES (Customer Effort Score) 계산.

    1 = 매우 쉬움 / 5 = 매우 어려움
    낮을수록 좋음 (≤2 우수).
    """
    if not scores:
        return {"avg": 0, "easy_pct": 0, "total": 0}

    avg = round(sum(scores) / len(scores), 2)
    easy = sum(1 for s in scores if s <= 2)
    return {
        "avg": avg,
        "easy_pct": round(easy / len(scores) * 100, 1),
        "total": len(scores),
        "achieved_low": avg <= 2.0,  # 우수
    }


def analyze_by_persona(responses: list[SatisfactionResponse]) -> dict:
    """페르소나별 만족도 분석.

    Returns:
        dict (페르소나별 NPS·CSAT·CES)
    """
    by_persona: dict[str, dict[str, list]] = {}
    for r in responses:
        persona = r.persona
        metric = r.metric
        if persona not in by_persona:
            by_persona[persona] = {"nps": [], "csat": [], "ces": []}
        by_persona[persona][metric].append(r.score)

    result = {}
    for persona, metrics in by_persona.items():
        result[persona] = {
            "nps": calculate_nps(metrics["nps"]),
            "csat": calculate_csat(metrics["csat"]),
            "ces": calculate_ces(metrics["ces"]),
        }
    return result


def render_satisfaction_survey(librarian_persona: str = "general") -> str:
    """Streamlit 사서 만족도 설문 (자관 onboarding 직후·매월).

    PO 정합: "사서가 만족할지 깐깐하게 예측" → 실제 측정.
    """
    try:
        import streamlit as st
    except ImportError:
        return ""

    st.markdown("### 📊 사서 만족도 설문 (1분)")
    st.caption("선생님 의견이 다음 사서들에게 큰 도움이 됩니다.")

    _nps = st.slider(
        "**NPS** — 동료 사서에게 추천하시겠어요? (0~10)",
        min_value=0, max_value=10, value=8,
        help="9~10 = 적극 추천 / 7~8 = 만족 / 0~6 = 개선 필요",
    )
    _csat = st.slider(
        "**만족도 (CSAT)** — kormarc-auto에 얼마나 만족하세요? (1~5)",
        min_value=1, max_value=5, value=4,
    )
    _ces = st.slider(
        "**사용 편의성 (CES)** — 사용이 얼마나 어려우신가요? (1=매우 쉬움 ~ 5=매우 어려움)",
        min_value=1, max_value=5, value=2,
    )
    feedback = st.text_area(
        "한 줄 의견 (선택)",
        placeholder="가장 좋았던 점·개선 권장",
    )

    if st.button("제출", type="primary"):
        st.success("감사합니다! 의견 = 다음 사서에게 도움이 되도록 활용됩니다.")
        return feedback or ""
    return ""


__all__ = [
    "SatisfactionMetric",
    "SatisfactionResponse",
    "analyze_by_persona",
    "calculate_ces",
    "calculate_csat",
    "calculate_nps",
    "render_satisfaction_survey",
]
