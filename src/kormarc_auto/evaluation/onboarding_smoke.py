"""5분 온보딩 smoke harness — 3-1 (PILOT 5관 모집 핵심).

PO 명령 (12-섹션 §3.1): "신규 사서 5분 안에 첫 .mrc 출력 + KOLAS 반입 보장"

6 단계 시간 측정:
1. setup-once.bat 실행 (Python·venv·의존성)
2. .env 4 키 입력
3. start-ui.bat 부팅
4. 자관 .mrc 디렉토리 → 049 prefix 자동 발견
5. ISBN 1건 입력 → .mrc 출력
6. KOLAS 반입 폴더 복사

총 < 5분 (300초) = PASS / 초과 = 가장 느린 단계 backlog P0.
매일 cron 자동 실행 = CHANGELOG_NIGHT.md 회귀 알림.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

OnboardingStep = Literal[
    "setup",
    "env_keys",
    "ui_boot",
    "prefix_discover",
    "first_isbn",
    "kolas_copy",
]


# 단계별 목표 시간 (초)
STEP_TARGETS_SECONDS: dict[OnboardingStep, float] = {
    "setup": 60.0,  # setup-once.bat
    "env_keys": 60.0,  # .env 입력
    "ui_boot": 30.0,  # Streamlit 부팅
    "prefix_discover": 60.0,  # 자관 prefix 자동
    "first_isbn": 60.0,  # ISBN 1건 처리
    "kolas_copy": 30.0,  # 폴더 복사
}

TOTAL_TARGET_SECONDS = 300.0  # 5분


@dataclass
class StepMeasurement:
    """단계 1개 측정."""

    step: OnboardingStep
    duration_seconds: float
    success: bool
    error: str | None = None


@dataclass
class OnboardingResult:
    """전체 온보딩 시뮬 결과."""

    steps: list[StepMeasurement] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str = ""

    @property
    def total_seconds(self) -> float:
        return sum(s.duration_seconds for s in self.steps)

    @property
    def passes_5min(self) -> bool:
        return self.total_seconds <= TOTAL_TARGET_SECONDS

    @property
    def slowest_step(self) -> StepMeasurement | None:
        if not self.steps:
            return None
        return max(self.steps, key=lambda s: s.duration_seconds)

    @property
    def all_succeeded(self) -> bool:
        return all(s.success for s in self.steps)

    def step_over_target(self) -> list[StepMeasurement]:
        """목표 시간 초과 단계 (backlog 후보)."""
        return [s for s in self.steps if s.duration_seconds > STEP_TARGETS_SECONDS[s.step]]


def measure_step(
    step: OnboardingStep,
    func: Callable[[], None],
) -> StepMeasurement:
    """단계 1개 시간 측정·예외 처리."""
    start = time.monotonic()
    try:
        func()
        elapsed = time.monotonic() - start
        return StepMeasurement(step=step, duration_seconds=elapsed, success=True)
    except Exception as e:
        elapsed = time.monotonic() - start
        return StepMeasurement(
            step=step, duration_seconds=elapsed, success=False, error=str(e)[:200]
        )


def run_smoke(
    step_runners: dict[OnboardingStep, Callable[[], None]],
) -> OnboardingResult:
    """전체 6 단계 실행.

    Args:
        step_runners: 단계 → 호출 callable. 없는 단계는 skip.

    Returns:
        OnboardingResult
    """
    result = OnboardingResult()
    steps_order: list[OnboardingStep] = [
        "setup",
        "env_keys",
        "ui_boot",
        "prefix_discover",
        "first_isbn",
        "kolas_copy",
    ]

    for step in steps_order:
        runner = step_runners.get(step)
        if runner is None:
            continue
        measurement = measure_step(step, runner)
        result.steps.append(measurement)
        if not measurement.success:
            break  # 실패 단계 = 중단

    result.completed_at = datetime.now(UTC).isoformat()
    return result


def report(result: OnboardingResult) -> dict:
    """결과 보고서 (cron 알림용)."""
    slowest = result.slowest_step
    return {
        "total_seconds": round(result.total_seconds, 2),
        "passes_5min": result.passes_5min,
        "all_succeeded": result.all_succeeded,
        "step_count": len(result.steps),
        "slowest_step": slowest.step if slowest else None,
        "slowest_seconds": round(slowest.duration_seconds, 2) if slowest else 0,
        "over_target_steps": [
            {"step": s.step, "seconds": round(s.duration_seconds, 2)}
            for s in result.step_over_target()
        ],
        "started_at": result.started_at,
        "completed_at": result.completed_at,
    }


def regression_alert_message(result: OnboardingResult) -> str | None:
    """회귀 발생 시 알림 메시지 (None = 정상)."""
    if result.passes_5min and result.all_succeeded:
        return None
    msg_parts = ["⚠ 5분 온보딩 회귀 감지"]
    if not result.passes_5min:
        msg_parts.append(f"총 {result.total_seconds:.1f}초 (목표 300초)")
    if not result.all_succeeded:
        failed = [s for s in result.steps if not s.success]
        msg_parts.append(f"실패 단계: {[s.step for s in failed]}")
    over = result.step_over_target()
    if over:
        msg_parts.append(f"초과 단계: {[(s.step, round(s.duration_seconds, 1)) for s in over]}")
    return " | ".join(msg_parts)


__all__ = [
    "STEP_TARGETS_SECONDS",
    "TOTAL_TARGET_SECONDS",
    "OnboardingResult",
    "OnboardingStep",
    "StepMeasurement",
    "measure_step",
    "regression_alert_message",
    "report",
    "run_smoke",
]
