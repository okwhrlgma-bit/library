"""PMF 검증 인프라 (Sean Ellis 테스트·CAC·LTV·10단어 가치) — 페인 #52 정합.

PO 비전 = 캐시카우 660만 / Phase 3.
PMF 검증 = 다음 단계 결정 (scale-up vs pivot).

검증 기준:
- Sean Ellis 테스트 ≥40% ("제품 없으면 못 살아")
- CAC < LTV (LTV/CAC ≥3 권장)
- 10단어 이내 가치 전달
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeanEllisResult:
    """Sean Ellis 테스트 결과."""

    very_disappointed_pct: float  # "제품 없으면 매우 실망" %
    somewhat_disappointed_pct: float  # "약간 실망" %
    not_disappointed_pct: float  # "실망 X" %
    sample_size: int
    pmf_achieved: bool  # ≥40% = True


def evaluate_sean_ellis(
    *,
    very_count: int,
    somewhat_count: int,
    not_count: int,
) -> SeanEllisResult:
    """Sean Ellis 테스트 평가.

    Args:
        very_count: "제품 없으면 매우 실망" 응답 수
        somewhat_count: "약간 실망"
        not_count: "실망 X"

    Returns:
        SeanEllisResult (PMF 달성 여부)
    """
    total = very_count + somewhat_count + not_count
    if total == 0:
        return SeanEllisResult(0, 0, 0, 0, False)

    very_pct = round(very_count / total * 100, 1)
    return SeanEllisResult(
        very_disappointed_pct=very_pct,
        somewhat_disappointed_pct=round(somewhat_count / total * 100, 1),
        not_disappointed_pct=round(not_count / total * 100, 1),
        sample_size=total,
        pmf_achieved=very_pct >= 40.0,  # Sean Ellis 기준
    )


@dataclass(frozen=True)
class UnitEconomics:
    """단위 경제 (CAC·LTV)."""

    cac_won: float  # 고객 획득 비용
    ltv_won: float  # 평생 가치
    monthly_arpu: float  # 월 평균 매출
    avg_lifetime_months: float
    payback_months: float
    healthy: bool  # LTV/CAC ≥3


def evaluate_unit_economics(
    *,
    cac_won: float,
    monthly_arpu: float,
    avg_lifetime_months: float,
) -> UnitEconomics:
    """단위 경제 평가."""
    ltv = monthly_arpu * avg_lifetime_months
    payback = cac_won / max(monthly_arpu, 1)
    return UnitEconomics(
        cac_won=cac_won,
        ltv_won=ltv,
        monthly_arpu=monthly_arpu,
        avg_lifetime_months=avg_lifetime_months,
        payback_months=payback,
        healthy=(ltv / max(cac_won, 1)) >= 3.0,
    )


def evaluate_value_proposition(message: str) -> dict:
    """10단어 이내 가치 전달 검증.

    Args:
        message: 가치 메시지

    Returns:
        dict (단어 수·통과 여부·권장)
    """
    words = message.split()
    word_count = len(words)
    return {
        "word_count": word_count,
        "passes_10_word_test": word_count <= 10,
        "message": message,
        "recommendation": "10단어 이내 권장" if word_count > 10 else "통과",
    }


@dataclass(frozen=True)
class PMFReport:
    """PMF 종합 보고."""

    sean_ellis: SeanEllisResult
    unit_econ: UnitEconomics
    value_check: dict
    overall_pmf: bool


def generate_pmf_report(
    sean_ellis: SeanEllisResult,
    unit_econ: UnitEconomics,
    value_message: str,
) -> PMFReport:
    """종합 PMF 보고 (3 기준)."""
    value_check = evaluate_value_proposition(value_message)
    overall = sean_ellis.pmf_achieved and unit_econ.healthy and value_check["passes_10_word_test"]
    return PMFReport(
        sean_ellis=sean_ellis,
        unit_econ=unit_econ,
        value_check=value_check,
        overall_pmf=overall,
    )


__all__ = [
    "PMFReport",
    "SeanEllisResult",
    "UnitEconomics",
    "evaluate_sean_ellis",
    "evaluate_unit_economics",
    "evaluate_value_proposition",
    "generate_pmf_report",
]
