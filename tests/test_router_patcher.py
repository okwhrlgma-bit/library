"""Cycle 53 V3 Block 5 — router_patcher AST 회귀.

V3 §4.5 정합·통계 결정적·LLM 호출 0·자동 머지 X (PR 브랜치만).
정규식 X·AST 패치 + 백업 검증.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automation"))

from router_patcher import (
    MIN_SAMPLES,
    RECOVER_RATE,
    UNSAFE_RATE,
    CategoryStats,
    category_block_rates,
    compute_updates,
)


def _ts(days_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()


class TestCategoryBlockRates:
    def test_below_min_samples_excluded(self):
        rows = [{"event": "cycle_end", "category": "auth", "status": "BLOCKED"}] * 5
        stats = category_block_rates(rows)
        # 5건 < MIN_SAMPLES(20) = 통계 의미 없음·제외
        assert stats == []

    def test_meets_min_samples_included(self):
        rows = [{"event": "cycle_end", "category": "auth", "status": "BLOCKED"}] * 25
        stats = category_block_rates(rows)
        assert len(stats) == 1
        assert stats[0].category == "auth"
        assert stats[0].n == 25
        assert stats[0].blocked == 25
        assert stats[0].block_rate == 1.0

    def test_mixed_categories(self):
        rows = (
            [{"event": "cycle_end", "category": "auth", "status": "BLOCKED"}] * 22
            + [{"event": "cycle_end", "category": "refactor", "status": "COMPLETED"}] * 30
            + [{"event": "cycle_end", "category": "docs", "status": "COMPLETED"}]
            * 15  # MIN_SAMPLES 미달
        )
        stats = category_block_rates(rows)
        cats = [s.category for s in stats]
        assert "auth" in cats
        assert "refactor" in cats
        assert "docs" not in cats  # 15 < 20

    def test_sorted_by_block_rate_desc(self):
        rows = [{"event": "cycle_end", "category": "low", "status": "COMPLETED"}] * 25 + [
            {"event": "cycle_end", "category": "high", "status": "BLOCKED"}
        ] * 25
        stats = category_block_rates(rows)
        assert stats[0].category == "high"
        assert stats[1].category == "low"


class TestComputeUpdates:
    def test_unsafe_promotion(self, monkeypatch):
        # 50% blocked = >= UNSAFE_RATE(40%)
        s = CategoryStats(category="payment", n=30, blocked=15, block_rate=0.50)
        # mock get_current_policies → "auto"
        import router_patcher as rp

        monkeypatch.setattr(rp, "get_current_policies", lambda: {"payment": "auto"})
        updates = compute_updates([s])
        assert len(updates) == 1
        assert updates[0].new_policy == "unsafe"
        assert updates[0].old_policy == "auto"

    def test_recovery_to_auto(self, monkeypatch):
        # 5% blocked·n=30 = <= RECOVER_RATE(10%) and n >= MIN_SAMPLES
        s = CategoryStats(category="docs", n=30, blocked=2, block_rate=2 / 30)
        import router_patcher as rp

        monkeypatch.setattr(rp, "get_current_policies", lambda: {"docs": "human"})
        updates = compute_updates([s])
        assert len(updates) == 1
        assert updates[0].new_policy == "auto"

    def test_no_change_in_middle(self, monkeypatch):
        # 25% = 중간·변경 X
        s = CategoryStats(category="refactor", n=40, blocked=10, block_rate=0.25)
        import router_patcher as rp

        monkeypatch.setattr(rp, "get_current_policies", lambda: {"refactor": "human"})
        updates = compute_updates([s])
        assert updates == []

    def test_no_change_when_already_unsafe(self, monkeypatch):
        # 이미 unsafe·여전히 50% = 변경 X
        s = CategoryStats(category="payment", n=30, blocked=15, block_rate=0.50)
        import router_patcher as rp

        monkeypatch.setattr(rp, "get_current_policies", lambda: {"payment": "unsafe"})
        updates = compute_updates([s])
        assert updates == []

    def test_threshold_constants(self):
        # V3 §4.5 임계 = 40% / 10% / 20 samples
        assert UNSAFE_RATE == 0.40
        assert RECOVER_RATE == 0.10
        assert MIN_SAMPLES == 20


class TestV3SafetyInvariants:
    """V3 §6.1 자기 수정 안전장치."""

    def test_no_llm_dependency(self):
        """LLM 호출 0·통계 결정적 (V3 §4.10)."""
        import inspect

        import router_patcher as rp

        src = inspect.getsource(rp.compute_updates)
        assert "anthropic" not in src.lower()
        assert "openai" not in src.lower()

    def test_no_regex_in_patch(self):
        """V3 §4.5 = AST 패치 + 백업·정규식 X."""
        import inspect

        import router_patcher as rp

        src = inspect.getsource(rp.patch_router)
        # re.sub 또는 re.compile 없어야 함
        assert "re.sub" not in src
        assert "re.compile" not in src
        # ast 사용 확인
        assert "ast.parse" in src or "ast.walk" in src

    def test_create_pr_branch_naming(self):
        """auto/router-patch-{ts} 브랜치 형식 (V2 §6.1 자기 수정 PR)."""
        import inspect

        import router_patcher as rp

        src = inspect.getsource(rp.create_pr_branch)
        assert "auto/router-patch-" in src
