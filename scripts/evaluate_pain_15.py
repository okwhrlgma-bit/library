"""15 요건 페인 평가 자동 (PO 명령 2026-05-08·Cycle 95).

ADR 0055 + 0058 + 0064 + 신규 ADR 0065 통합·15 요건 매트릭스.
LLM 호출 0·결정적 (V3 §4.10 정합).

실행:
    python scripts/evaluate_pain_15.py < pain.json
    python scripts/evaluate_pain_15.py --demo
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class PainEvaluation:
    """15 요건 평가 결과 + 페널티 (Cycle 100 보강)."""

    pain_id: str
    pain_score: int  # PO 1: 페인·귀찮음 (0~10)
    automation_score: int  # PO 2: set-and-forget (0~10)
    revenue_score: int  # PO 3: 수익성 (0~10)
    payer_match: bool  # 4: 결제권자 = 결제자
    solo_operatable: bool  # 5: 1인 PO 가능
    no_government_competition: bool  # 6: 정부·거대 무료 잠식 X
    founder_fit: bool  # 7: PO = 사용자
    repeat_frequency: bool  # 8: 반복 사용 (1회성 X)
    lock_in: bool  # 9: 락인 메커니즘
    no_legal_risk: bool  # 10: 법적 위험 X
    korea_global_both: bool  # 11: 한국 + 글로벌
    indie_benchmark: bool  # 12: 인디 검증 1+
    adr_0052_compatible: bool  # 13: 코딩 외 X 정합
    user_data_local: bool  # 14: 헌법 §14 정합
    mit_apache_license: bool  # 15: 라이선스 가능
    # Cycle 100 신규 페널티 (보수 보정)
    giant_competitor_billion: bool = False  # 시가총액 $1B+ 거대 점유 (Duolingo·Stripe 등)
    government_free_dominant: bool = False  # 정부 무료 도구 직접 잠식 (HUG·홈택스 등)
    # Cycle 115 v6 신규 (작은 시장 보수 보정)
    market_sam_under_10k: bool = False  # SAM < 10,000명 = 작은 시장 (한국 인디·niche)


def calculate_overall_score(eval: PainEvaluation) -> dict[str, int | str]:
    """15 요건 종합 점수."""
    # PO 3 요건 (가중치 ↑·각 0~10·합 30)
    po_score = eval.pain_score + eval.automation_score + eval.revenue_score
    po_max = 30

    # 자율 12 요건 (boolean·합 12)
    autonomy_checks = [
        eval.payer_match,
        eval.solo_operatable,
        eval.no_government_competition,
        eval.founder_fit,
        eval.repeat_frequency,
        eval.lock_in,
        eval.no_legal_risk,
        eval.korea_global_both,
        eval.indie_benchmark,
        eval.adr_0052_compatible,
        eval.user_data_local,
        eval.mit_apache_license,
    ]
    autonomy_score = sum(autonomy_checks)
    autonomy_max = 12

    # 종합 (PO 3 = 50%·자율 12 = 50%)
    po_weighted = (po_score / po_max) * 50
    autonomy_weighted = (autonomy_score / autonomy_max) * 50
    overall = round(po_weighted + autonomy_weighted)

    # Cycle 100 페널티 (거대 사업자·정부 잠식)
    penalties = []
    if eval.giant_competitor_billion:
        overall -= 10
        penalties.append("거대 사업자 $1B+ 정면 경쟁·-10")
    if eval.government_free_dominant:
        overall -= 10
        penalties.append("정부 무료 직접 잠식·-10")

    overall = max(0, overall)

    # 결정 (Cycle 101 v3·108 v5·115 v6 보강)
    if eval.giant_competitor_billion and eval.government_free_dominant:
        decision = "NO_GO"
        penalties.append("이중 페널티 (거대 + 정부) = NO_GO 강제")
    elif not eval.no_legal_risk:
        decision = "NO_GO"
    elif eval.giant_competitor_billion and eval.market_sam_under_10k:
        # Cycle 115 v6: 거대 사업자 + 작은 시장 = NO_GO 강제
        decision = "NO_GO"
        penalties.append("거대 + 작은 시장 (SAM < 10K) = NO_GO 강제 (v6)")
    elif not eval.founder_fit and not eval.indie_benchmark:
        decision = "NO_GO"
        penalties.append("founder fit X + 인디 검증 X = NO_GO 강제 (보수)")
    elif overall >= 75:
        decision = "GO"
    elif overall >= 60:
        decision = "MAYBE"
    else:
        decision = "NO_GO"

    return {
        "pain_id": eval.pain_id,
        "po_score": po_score,
        "po_max": po_max,
        "autonomy_score": autonomy_score,
        "autonomy_max": autonomy_max,
        "overall_score": overall,
        "decision": decision,
        "fail_reasons": _collect_fail_reasons(eval),
        "penalties": penalties,
    }


def _collect_fail_reasons(eval: PainEvaluation) -> list[str]:
    """실패 요건 목록."""
    reasons = []
    if eval.pain_score < 5:
        reasons.append("PO 1: 페인 약함 (< 5)")
    if eval.automation_score < 5:
        reasons.append("PO 2: 자동화 어려움 (< 5)")
    if eval.revenue_score < 5:
        reasons.append("PO 3: 수익성 약함 (< 5)")
    if not eval.payer_match:
        reasons.append("4: 결제권자 ≠ 결제자")
    if not eval.solo_operatable:
        reasons.append("5: 1인 PO 운영 X")
    if not eval.no_government_competition:
        reasons.append("6: 정부·거대 무료 잠식")
    if not eval.no_legal_risk:
        reasons.append("10: 법적 위험 (변호사·세무사·의료법)")
    if not eval.indie_benchmark:
        reasons.append("12: 인디 검증 사례 X")
    return reasons


def demo() -> None:
    """예시 평가 (3 케이스: #31 GO·#1 MAYBE·P-017 NO_GO 자동 분류)."""
    samples = [
        PainEvaluation(
            pain_id="P-2026-004 (#31 freelancer-tax)",
            pain_score=9,
            automation_score=8,
            revenue_score=9,
            payer_match=True,
            solo_operatable=True,
            no_government_competition=True,
            founder_fit=False,
            repeat_frequency=True,
            lock_in=True,
            no_legal_risk=True,
            korea_global_both=False,
            indie_benchmark=True,
            adr_0052_compatible=True,
            user_data_local=True,
            mit_apache_license=True,
        ),
        PainEvaluation(
            pain_id="P-2026-016 (#1 kormarc-auto)",
            pain_score=9,
            automation_score=9,
            revenue_score=5,
            payer_match=False,
            solo_operatable=True,
            no_government_competition=False,
            founder_fit=True,
            repeat_frequency=True,
            lock_in=True,
            no_legal_risk=True,
            korea_global_both=False,
            indie_benchmark=False,
            adr_0052_compatible=True,
            user_data_local=True,
            mit_apache_license=True,
        ),
        PainEvaluation(
            pain_id="P-2026-017 (영어 학습·Cycle 100 페널티 검증)",
            pain_score=8,
            automation_score=9,
            revenue_score=7,
            payer_match=True,
            solo_operatable=True,
            no_government_competition=False,
            founder_fit=False,
            repeat_frequency=True,
            lock_in=False,
            no_legal_risk=True,
            korea_global_both=True,
            indie_benchmark=False,  # Duolingo $9B = 반례
            adr_0052_compatible=True,
            user_data_local=True,
            mit_apache_license=True,
            giant_competitor_billion=True,  # ✨ Duolingo $9B 페널티
        ),
    ]
    for sample in samples:
        result = calculate_overall_score(sample)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("---")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = argv or sys.argv[1:]
    if "--demo" in args:
        demo()
        return 0

    print("사용: python scripts/evaluate_pain_15.py --demo")
    print("(JSON 입력 모드 = 다음 cycle)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
