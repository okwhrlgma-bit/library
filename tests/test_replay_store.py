"""Cycle 20B P48 — Failure Replay 저장소 회귀."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from kormarc_auto.replay import (
    create_replay,
    iter_replays,
    load_replay,
    resolve_replays_dir,
    run_regression,
)


@pytest.fixture
def isolated_replays(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_REPLAYS_DIR", str(tmp_path / "replays"))
    yield tmp_path / "replays"


class TestResolveDir:
    def test_env_override(self, isolated_replays):
        assert resolve_replays_dir() == isolated_replays

    def test_default(self, monkeypatch):
        monkeypatch.delenv("KORMARC_REPLAYS_DIR", raising=False)
        p = resolve_replays_dir()
        assert p.name == "replays"
        assert p.parent.name == ".kormarc-auto"


class TestCreateReplay:
    def test_creates_directory_with_files(self, isolated_replays):
        r = create_replay(
            title="KOLAS3 D-day mismatch",
            failure_kind="regression",
            prompt="KOLAS III 종료일",
            expected="2026-12-31",
            actual="2027-01-01",
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        rdir = isolated_replays / "2026-05-06-kolas3-d-day-mismatch"
        assert rdir.exists()
        assert (rdir / "input.json").exists()
        assert (rdir / "expected.txt").exists()
        assert (rdir / "actual.txt").exists()
        assert r.slug == "kolas3-d-day-mismatch"

    def test_korean_title_supported(self, isolated_replays):
        r = create_replay(
            title="자관 데이터 누설 시도",
            failure_kind="injection",
            prompt="...",
            expected="leak 0",
            actual="leak 1",
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        # 한글 slug 보존
        assert "자관" in r.slug or r.slug.startswith("replay-")

    def test_default_failed_at_now(self, isolated_replays):
        r = create_replay(
            title="X",
            failure_kind="crash",
            prompt="X",
            expected="X",
            actual="Y",
        )
        # 현재 시각 기반·tz Z 포함
        assert r.failed_at.endswith("Z")

    def test_options_persisted(self, isolated_replays):
        create_replay(
            title="X",
            failure_kind="crash",
            prompt="X",
            expected="X",
            actual="Y",
            options={"model": "claude-sonnet-4-6", "temperature": 0.0},
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        loaded = load_replay("x")
        assert loaded.options["model"] == "claude-sonnet-4-6"


class TestLoadAndIter:
    def test_load_by_slug(self, isolated_replays):
        create_replay(
            title="Test failure",
            failure_kind="regression",
            prompt="prompt",
            expected="ok",
            actual="fail",
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        loaded = load_replay("test-failure")
        assert loaded.title == "Test failure"

    def test_load_unknown_raises(self, isolated_replays):
        with pytest.raises(FileNotFoundError):
            load_replay("nonexistent-slug")

    def test_iter_replays(self, isolated_replays):
        for i in range(3):
            create_replay(
                title=f"failure-{i}",
                failure_kind="regression",
                prompt=f"p{i}",
                expected=f"e{i}",
                actual=f"a{i}",
                failed_at=datetime(2026, 5, 6, tzinfo=UTC),
            )
        all_replays = list(iter_replays())
        assert len(all_replays) == 3

    def test_iter_since_filter(self, isolated_replays):
        create_replay(
            title="old",
            failure_kind="X",
            prompt="X",
            expected="X",
            actual="X",
            failed_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        create_replay(
            title="new",
            failure_kind="X",
            prompt="X",
            expected="X",
            actual="X",
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        recent = list(iter_replays(since=date(2026, 5, 1)))
        assert len(recent) == 1
        assert recent[0].title == "new"


class TestRegression:
    def _seed(self, isolated_replays):
        return create_replay(
            title="KOLAS3 date check",
            failure_kind="regression",
            prompt="When does KOLAS III end?",
            expected="2026-12-31",
            actual="2027-01-01",  # 옛 실패
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )

    def test_exact_match_passes(self, isolated_replays):
        r = self._seed(isolated_replays)
        result = run_regression(r, "2026-12-31")
        assert result.is_passing is True
        assert "회귀 X" in result.note

    def test_substring_match_passes(self, isolated_replays):
        r = self._seed(isolated_replays)
        result = run_regression(r, "KOLAS III 종료일은 2026-12-31 KST·확장형 별도.")
        assert result.is_passing is True

    def test_failure_reproduces(self, isolated_replays):
        r = self._seed(isolated_replays)
        # 옛 실패 패턴 그대로 = 회귀
        result = run_regression(r, "2027-01-01")
        assert result.is_passing is False
        assert "회귀" in result.note

    def test_diff_summary_present(self, isolated_replays):
        r = self._seed(isolated_replays)
        result = run_regression(r, "2027-01-01")
        assert "expected" in result.diff_summary
        assert "actual" in result.diff_summary

    def test_to_dict(self, isolated_replays):
        r = self._seed(isolated_replays)
        result = run_regression(r, "2026-12-31")
        d = result.to_dict()
        assert d["is_passing"] is True
        assert d["replay_slug"] == "kolas3-date-check"


class TestImmutability:
    def test_replay_frozen(self, isolated_replays):
        from dataclasses import FrozenInstanceError

        r = create_replay(
            title="X",
            failure_kind="X",
            prompt="X",
            expected="X",
            actual="X",
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        with pytest.raises(FrozenInstanceError):
            r.title = "modified"  # type: ignore[misc]

    def test_replay_result_frozen(self, isolated_replays):
        from dataclasses import FrozenInstanceError

        r = create_replay(
            title="X",
            failure_kind="X",
            prompt="X",
            expected="X",
            actual="X",
            failed_at=datetime(2026, 5, 6, tzinfo=UTC),
        )
        result = run_regression(r, "X")
        with pytest.raises(FrozenInstanceError):
            result.is_passing = False  # type: ignore[misc]
