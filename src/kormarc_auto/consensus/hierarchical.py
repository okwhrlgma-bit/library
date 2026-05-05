"""갈래 B Cycle 34 (V2 §3.3) — Hierarchical 멀티 에이전트.

구조 = 감독자 (Opus·plan-only) → 작업자 (Sonnet·실행) × N → 검증자 (Sonnet) → 합치.
큰 마이그레이션 (200 컴포넌트 등)·며칠 → 몇 시간 단축 (Anthropic 내부 사례).

본 모듈 = scaffolding + 작업 분해 헬퍼.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

WorkerStatus = Literal["pending", "running", "completed", "failed"]


@dataclass
class WorkUnit:
    """작업자 1개에 할당되는 작업 단위."""

    unit_id: str
    description: str
    estimated_tokens: int = 5000
    status: WorkerStatus = "pending"
    assigned_to: str = ""  # "sonnet-worker-1" 등
    result: str = ""

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "description": self.description,
            "estimated_tokens": self.estimated_tokens,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "result": self.result,
        }


@dataclass
class HierarchicalPlan:
    """감독자가 분해한 전체 계획."""

    goal: str
    units: list[WorkUnit] = field(default_factory=list)
    supervisor_model: str = "claude-opus-4-7"
    worker_model: str = "claude-sonnet-4-6"
    reviewer_model: str = "claude-sonnet-4-6"
    parallel_workers: int = 4

    def total_estimated_tokens(self) -> int:
        # 감독자 + 작업자 N + 검증자
        worker_total = sum(u.estimated_tokens for u in self.units)
        supervisor = 5000  # plan 단계
        reviewer = 8000  # 합치 + 검증
        return supervisor + worker_total + reviewer

    def progress(self) -> dict[str, int]:
        counts = {"pending": 0, "running": 0, "completed": 0, "failed": 0}
        for u in self.units:
            counts[u.status] = counts.get(u.status, 0) + 1
        counts["total"] = len(self.units)
        return counts

    def is_complete(self) -> bool:
        return all(u.status in ("completed", "failed") for u in self.units)

    def all_passed(self) -> bool:
        return all(u.status == "completed" for u in self.units)

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "units": [u.to_dict() for u in self.units],
            "supervisor_model": self.supervisor_model,
            "worker_model": self.worker_model,
            "reviewer_model": self.reviewer_model,
            "parallel_workers": self.parallel_workers,
            "total_estimated_tokens": self.total_estimated_tokens(),
            "progress": self.progress(),
            "is_complete": self.is_complete(),
            "all_passed": self.all_passed(),
        }


def decompose_into_units(
    *,
    goal: str,
    file_count: int,
    estimated_tokens_per_file: int = 3000,
    parallel_workers: int = 4,
) -> HierarchicalPlan:
    """파일 수 기반 작업 분해 (마이그레이션·리팩터 시나리오)."""
    units = [
        WorkUnit(
            unit_id=f"unit-{i + 1:03d}",
            description=f"{goal} (파일 {i + 1}/{file_count})",
            estimated_tokens=estimated_tokens_per_file,
        )
        for i in range(file_count)
    ]
    return HierarchicalPlan(goal=goal, units=units, parallel_workers=parallel_workers)


def assign_to_workers(plan: HierarchicalPlan, worker_ids: list[str]) -> HierarchicalPlan:
    """작업 단위를 worker에 round-robin 할당."""
    if not worker_ids:
        return plan
    for i, unit in enumerate(plan.units):
        unit.assigned_to = worker_ids[i % len(worker_ids)]
    return plan
