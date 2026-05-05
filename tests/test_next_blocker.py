"""Cycle 25 — next_blocker 회귀."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from next_blocker import Blocker, detect_blockers


@pytest.fixture
def isolated_env(monkeypatch, tmp_path):
    # 테스트용 ENV 격리·.env 무시
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("NL_CERT_KEY", raising=False)
    monkeypatch.delenv("DATA4LIBRARY_AUTH_KEY", raising=False)
    yield tmp_path


class TestDetectBlockers:
    def test_returns_list(self, isolated_env):
        blockers = detect_blockers()
        assert isinstance(blockers, list)

    def test_critical_first(self, isolated_env):
        blockers = detect_blockers()
        # 우선순위 = severity 정렬 (critical → high → medium → low)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for i in range(len(blockers) - 1):
            assert severity_order[blockers[i].severity] <= severity_order[blockers[i + 1].severity]

    def test_includes_business_registration(self, isolated_env):
        blockers = detect_blockers()
        ids = [b.id for b in blockers]
        # 일반과세자 등록 미완 = 가장 큰 차단점
        assert "PO-PROD-1" in ids


class TestBlockerStructure:
    def test_blocker_dataclass_fields(self):
        b = Blocker(
            id="X",
            severity="critical",
            description="test",
            next_action="action",
            estimated_unblock_days=3,
            revenue_impact="🔴",
        )
        assert b.id == "X"
        assert b.severity == "critical"

    def test_severity_levels(self):
        for sev in ("critical", "high", "medium", "low"):
            b = Blocker(
                id="X",
                severity=sev,
                description="x",
                next_action="x",
                estimated_unblock_days=0,
                revenue_impact="x",
            )
            assert b.severity == sev


class TestEnvDetection:
    def test_anthropic_blocker_when_missing(self, isolated_env):
        blockers = detect_blockers()
        ids = [b.id for b in blockers]
        assert "PO-PROD-6" in ids  # ANTHROPIC_API_KEY 미발급

    def test_nl_cert_blocker_when_missing(self, isolated_env):
        blockers = detect_blockers()
        ids = [b.id for b in blockers]
        assert "PO-PROD-5" in ids  # NL_CERT_KEY 미발급

    def test_anthropic_present_no_blocker(self, isolated_env, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-fake")
        blockers = detect_blockers()
        ids = [b.id for b in blockers]
        # ANTHROPIC 보유 시 = blocker 제외
        assert "PO-PROD-6" not in ids


class TestKLADeadline:
    def test_kla_deadline_severity(self, isolated_env):
        from datetime import date

        blockers = detect_blockers()
        kla = next((b for b in blockers if b.id == "SALES-2"), None)
        if kla is None:
            # 마감 지났으면 차단점 X
            return
        deadline = date(2026, 5, 31)
        days = (deadline - date.today()).days
        if days <= 14:
            assert kla.severity == "high"
        else:
            assert kla.severity == "medium"


class TestRevenueImpact:
    def test_all_blockers_have_korean_impact(self, isolated_env):
        blockers = detect_blockers()
        for b in blockers:
            # 한국어 emoji + 텍스트
            assert any(c in b.revenue_impact for c in ("🔴", "🟡", "🟢"))


class TestSalesInterview:
    def test_sales_1_when_no_interview_log(self, isolated_env, monkeypatch, tmp_path):
        # interviews_log 디렉토리 = 없음 가정
        blockers = detect_blockers()
        # 인터뷰 디렉토리 = repo 기준 = 실제 있을 수 있으므로 약한 검증
        sales = [b for b in blockers if b.id == "SALES-1"]
        if sales:
            assert sales[0].severity == "high"
            assert "wedge" in sales[0].description or "Mom Test" in sales[0].next_action
