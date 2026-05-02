"""사서 직무 역량 측정 — Part 82+ 페인 #51 정합.

사서 페인:
- 1급·2급·준사서 분류 + 직무분석표·중요도·만족도 측정 부담
- KCI 학술 검증

해결: 직무 영역별 역량 점수 자동 + Personal Win 직결.
"""

from __future__ import annotations

from dataclasses import dataclass

COMPETENCY_AREAS = {
    "cataloging": "자료 정리 (KORMARC)",
    "classification": "분류 (KDC)",
    "acquisition": "수서·구입",
    "reference": "참고봉사·이용자 응대",
    "circulation": "대출·반납",
    "preservation": "보존·관리",
    "programs": "프로그램·행사",
    "marketing": "홍보·SNS",
    "administration": "행정·통계",
    "technology": "IT 시스템 활용",
}


@dataclass(frozen=True)
class CompetencyScore:
    """직무 영역 역량 점수."""

    area: str
    self_score: float  # 0~5 (사서 자기 평가)
    actual_score: float  # 0~5 (실측·자동)
    importance: float = 5.0  # 자관 중요도


def calculate_overall_competency(scores: list[CompetencyScore]) -> dict:
    """직무 영역 종합 역량."""
    if not scores:
        return {"overall": 0, "areas": {}}

    weighted_sum = sum(s.actual_score * s.importance for s in scores)
    weight_total = sum(s.importance for s in scores)
    overall = round(weighted_sum / max(weight_total, 1), 2)

    # 강점·약점
    sorted_areas = sorted(scores, key=lambda s: s.actual_score, reverse=True)
    strengths = [s.area for s in sorted_areas[:3]]
    weaknesses = [s.area for s in sorted_areas[-3:] if s.actual_score < 3.5]

    return {
        "overall": overall,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "areas": {s.area: round(s.actual_score, 2) for s in scores},
    }


def kormarc_auto_boost(area: str) -> float:
    """kormarc-auto 사용 = 영역별 자동 역량 boost.

    Returns:
        boost 점수 (0~2)
    """
    boosts = {
        "cataloging": 2.0,  # 메인 영역
        "classification": 1.5,
        "acquisition": 1.0,  # decision_helper
        "reference": 1.5,  # librarian_agent
        "preservation": 1.0,  # withdrawn·inventory
        "programs": 1.0,  # event_poster
        "marketing": 1.0,  # sns_marketing
        "administration": 2.0,  # libsta·evaluation_report
        "technology": 1.5,  # 일반 IT
    }
    return boosts.get(area, 0.5)


def generate_competency_report(scores: list[CompetencyScore], librarian_name: str) -> str:
    """역량 보고서 markdown (사서 평가·승진 자료)."""
    summary = calculate_overall_competency(scores)
    lines = [
        f"# {librarian_name} 선생님 직무 역량 보고서",
        "",
        f"> 종합 역량: **{summary['overall']:.2f} / 5.00**",
        "",
        "## 영역별 점수",
        "",
        "| 영역 | 점수 | kormarc-auto boost |",
        "|---|---:|---:|",
    ]
    for s in scores:
        boost = kormarc_auto_boost(s.area)
        lines.append(
            f"| {COMPETENCY_AREAS.get(s.area, s.area)} | {s.actual_score:.1f} | +{boost:.1f} |"
        )

    if summary["strengths"]:
        lines.extend(["", "## 강점 영역"])
        for area in summary["strengths"]:
            lines.append(f"- {COMPETENCY_AREAS.get(area, area)}")

    if summary["weaknesses"]:
        lines.extend(["", "## 보완 권장 영역"])
        for area in summary["weaknesses"]:
            lines.append(f"- {COMPETENCY_AREAS.get(area, area)} = 학습·교육 권장")

    lines.extend(
        [
            "",
            "## 사서 평가 가산점·승진 활용",
            "",
            "본 보고서는 사서 평가·승진 자료에 직접 활용 가능합니다.",
            "kormarc-auto 사용 = 자동 boost = 정량 평가 지표 ↑.",
        ]
    )

    return "\n".join(lines)


__all__ = [
    "COMPETENCY_AREAS",
    "CompetencyScore",
    "calculate_overall_competency",
    "generate_competency_report",
    "kormarc_auto_boost",
]
