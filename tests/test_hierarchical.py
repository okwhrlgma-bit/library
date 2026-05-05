"""Cycle 34 — Hierarchical 멀티 에이전트 회귀."""

from __future__ import annotations

from kormarc_auto.consensus import (
    HierarchicalPlan,
    WorkUnit,
    assign_to_workers,
    decompose_into_units,
)


class TestDecompose:
    def test_creates_n_units(self):
        plan = decompose_into_units(goal="React class → 함수형 마이그레이션", file_count=10)
        assert len(plan.units) == 10

    def test_unit_id_zero_padded(self):
        plan = decompose_into_units(goal="X", file_count=5)
        assert plan.units[0].unit_id == "unit-001"
        assert plan.units[4].unit_id == "unit-005"

    def test_default_models_v2(self):
        plan = decompose_into_units(goal="X", file_count=1)
        assert plan.supervisor_model == "claude-opus-4-7"
        assert plan.worker_model == "claude-sonnet-4-6"
        assert plan.reviewer_model == "claude-sonnet-4-6"

    def test_default_4_parallel_workers(self):
        plan = decompose_into_units(goal="X", file_count=1)
        assert plan.parallel_workers == 4


class TestProgress:
    def _plan(self) -> HierarchicalPlan:
        return decompose_into_units(goal="X", file_count=4)

    def test_initial_all_pending(self):
        plan = self._plan()
        p = plan.progress()
        assert p["pending"] == 4
        assert p["completed"] == 0
        assert p["total"] == 4
        assert plan.is_complete() is False

    def test_complete_after_all_done(self):
        plan = self._plan()
        for u in plan.units:
            u.status = "completed"
        assert plan.is_complete() is True
        assert plan.all_passed() is True

    def test_partial_complete(self):
        plan = self._plan()
        plan.units[0].status = "completed"
        plan.units[1].status = "running"
        p = plan.progress()
        assert p["completed"] == 1
        assert p["running"] == 1
        assert p["pending"] == 2

    def test_failed_unit_blocks_all_passed(self):
        plan = self._plan()
        for u in plan.units:
            u.status = "completed"
        plan.units[0].status = "failed"
        assert plan.is_complete() is True  # complete = pending/running 없음
        assert plan.all_passed() is False


class TestEstimatedTokens:
    def test_total_includes_supervisor_and_reviewer(self):
        plan = decompose_into_units(goal="X", file_count=10, estimated_tokens_per_file=3000)
        # supervisor 5000 + 10 * 3000 + reviewer 8000 = 43,000
        assert plan.total_estimated_tokens() == 5000 + 30_000 + 8000


class TestAssignWorkers:
    def test_round_robin_assignment(self):
        plan = decompose_into_units(goal="X", file_count=10)
        workers = ["sonnet-1", "sonnet-2", "sonnet-3", "sonnet-4"]
        assign_to_workers(plan, workers)
        # 0→sonnet-1, 1→sonnet-2, 2→sonnet-3, 3→sonnet-4, 4→sonnet-1, ...
        assert plan.units[0].assigned_to == "sonnet-1"
        assert plan.units[3].assigned_to == "sonnet-4"
        assert plan.units[4].assigned_to == "sonnet-1"
        assert plan.units[7].assigned_to == "sonnet-4"

    def test_empty_workers_no_op(self):
        plan = decompose_into_units(goal="X", file_count=3)
        assign_to_workers(plan, [])
        for u in plan.units:
            assert u.assigned_to == ""


class TestUnitDict:
    def test_to_dict_complete(self):
        u = WorkUnit(unit_id="unit-001", description="X", estimated_tokens=3000)
        d = u.to_dict()
        for k in ("unit_id", "description", "estimated_tokens", "status", "assigned_to", "result"):
            assert k in d


class TestPlanDict:
    def test_to_dict_complete(self):
        plan = decompose_into_units(goal="React 마이그레이션", file_count=5)
        d = plan.to_dict()
        for k in (
            "goal",
            "units",
            "supervisor_model",
            "worker_model",
            "reviewer_model",
            "parallel_workers",
            "total_estimated_tokens",
            "progress",
            "is_complete",
            "all_passed",
        ):
            assert k in d
        assert len(d["units"]) == 5


class TestKormarcScenario:
    """V2 §3.3 정합·KORMARC 200 컴포넌트 마이그레이션 시나리오."""

    def test_kormarc_200_components(self):
        plan = decompose_into_units(
            goal="KORMARC 9 자료유형 builder 통합 (200 컴포넌트)",
            file_count=200,
            estimated_tokens_per_file=2000,
            parallel_workers=8,
        )
        # supervisor 5000 + 200×2000 + reviewer 8000 = 413,000 토큰
        assert plan.total_estimated_tokens() == 413_000
        assert plan.parallel_workers == 8
        assert len(plan.units) == 200
