"""갈래 B Cycle 19A (P49) — 비용 회귀 진단.

V2 §8.3 정합:
- 같은 작업이 어제 12K → 오늘 40K 토큰 = 회귀 알람
- 후보 원인: 모델 변경·코드 비대화·CLAUDE.md 비대화·루프 횟수 증가
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RegressionSeverity = Literal["normal", "watch", "alert", "critical"]


@dataclass(frozen=True)
class RegressionFinding:
    """회귀 진단 결과."""

    task_kind: str
    baseline_avg_tokens: float
    recent_avg_tokens: float
    pct_change: float
    severity: RegressionSeverity
    likely_causes: list[str]
    note: str

    def to_dict(self) -> dict:
        return {
            "task_kind": self.task_kind,
            "baseline_avg_tokens": self.baseline_avg_tokens,
            "recent_avg_tokens": self.recent_avg_tokens,
            "pct_change": self.pct_change,
            "severity": self.severity,
            "likely_causes": self.likely_causes,
            "note": self.note,
        }


def _severity_for(pct_change: float) -> RegressionSeverity:
    if pct_change <= 0.10:
        return "normal"
    if pct_change <= 0.30:
        return "watch"
    if pct_change <= 0.80:
        return "alert"
    return "critical"


def detect_token_regression(
    *,
    task_kind: str,
    baseline_token_samples: list[int],
    recent_token_samples: list[int],
) -> RegressionFinding:
    """task_kind 별 토큰 회귀 진단.

    Args:
        task_kind: "code-edit"·"refactor" 등
        baseline_token_samples: 기준 기간 (예: 직전 28일) 사용량 리스트
        recent_token_samples: 최근 기간 (예: 지난 7일) 사용량 리스트

    Returns:
        RegressionFinding (severity·likely_causes·note)
    """
    if not baseline_token_samples or not recent_token_samples:
        return RegressionFinding(
            task_kind=task_kind,
            baseline_avg_tokens=0,
            recent_avg_tokens=0,
            pct_change=0,
            severity="normal",
            likely_causes=[],
            note="데이터 부족",
        )

    baseline_avg = sum(baseline_token_samples) / len(baseline_token_samples)
    recent_avg = sum(recent_token_samples) / len(recent_token_samples)

    if baseline_avg == 0:
        return RegressionFinding(
            task_kind=task_kind,
            baseline_avg_tokens=0,
            recent_avg_tokens=recent_avg,
            pct_change=0,
            severity="normal",
            likely_causes=[],
            note="기준 평균 0",
        )

    pct = (recent_avg - baseline_avg) / baseline_avg
    severity = _severity_for(pct)

    # V2 §8.3 후보 원인
    causes: list[str] = []
    if severity in ("alert", "critical"):
        causes = [
            "모델 변경 (Anthropic API 자동 업데이트)",
            "코드베이스 비대화 (컨텍스트 자동 로딩 증가)",
            "CLAUDE.md / agent_docs 비대화 (프롬프트 드리프트)",
            "모델 사고 루프 증가 (도구 호출 더 많이)",
        ]
        if pct > 1.5:
            causes.append("⚠ 이상 패턴 = 즉시 사람 검토 + 회귀 진단 스크립트 실행")

    # 한국어 권고 note
    if severity == "normal":
        note = f"✓ 정상 (Δ {pct * 100:+.1f}%)"
    elif severity == "watch":
        note = f"🟡 모니터·Δ {pct * 100:+.1f}%·다음 주 재측정"
    elif severity == "alert":
        note = f"🔴 회귀 의심 (Δ {pct * 100:+.1f}%)·4 후보 원인 분리 검증 권장·V2 §8.3"
    else:
        note = f"⛔ 심각 회귀 (Δ {pct * 100:+.1f}%)·즉시 사람 검토·자율 사이클 일시 중단 권장"

    return RegressionFinding(
        task_kind=task_kind,
        baseline_avg_tokens=round(baseline_avg, 1),
        recent_avg_tokens=round(recent_avg, 1),
        pct_change=round(pct, 4),
        severity=severity,
        likely_causes=causes,
        note=note,
    )
