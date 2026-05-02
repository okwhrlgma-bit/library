"""time_tracker 권당 시간 측정 테스트 (Part 47·51)."""

from __future__ import annotations

import json
import time

import pytest

from kormarc_auto.ui.time_tracker import (
    BASELINE_MINUTES_PER_RECORD,
    ProcessingEvent,
    UserStats,
    get_user_stats,
)


def test_baseline_constant_matches_constitution() -> None:
    """기준 권당 시간 = 헌법 §0 (8분 → 2분)."""
    assert BASELINE_MINUTES_PER_RECORD == 8.0


def test_track_processing_records_duration(tmp_path, monkeypatch) -> None:
    """track_processing 컨텍스트 매니저 = duration 자동 측정."""
    from kormarc_auto.ui import time_tracker as tt

    monkeypatch.setattr(tt, "STATS_DIR", tmp_path)

    user_id = "test_user_001"
    isbn = "9788937437076"

    with tt.track_processing(user_id=user_id, isbn=isbn, method="single"):
        time.sleep(0.05)  # 50ms 작업 시뮬

    user_file = tmp_path / f"{user_id}.jsonl"
    assert user_file.exists()

    with user_file.open("r", encoding="utf-8") as f:
        event = json.loads(f.readline())

    assert event["user_id"] == user_id
    assert event["isbn"] == isbn
    assert event["success"] is True
    assert 0.04 < event["duration_seconds"] < 1.0


def test_track_processing_marks_failure_on_exception(tmp_path, monkeypatch) -> None:
    """예외 발생 시 success=False 기록."""
    from kormarc_auto.ui import time_tracker as tt

    monkeypatch.setattr(tt, "STATS_DIR", tmp_path)

    user_id = "test_user_fail"

    with (
        pytest.raises(ValueError),
        tt.track_processing(user_id=user_id, isbn="123", method="single"),
    ):
        raise ValueError("test failure")

    user_file = tmp_path / f"{user_id}.jsonl"
    with user_file.open("r", encoding="utf-8") as f:
        event = json.loads(f.readline())

    assert event["success"] is False


def test_user_stats_savings_calculation() -> None:
    """절감율 계산 = 1 - actual / baseline."""
    events = [
        ProcessingEvent(
            user_id="u1",
            isbn="9788937437076",
            duration_seconds=120.0,  # 2분 (baseline 8분)
            timestamp=time.time(),
            method="single",
            success=True,
        )
    ]
    stats = UserStats.from_events(user_id="u1", events=events)
    assert stats.successful_records == 1
    assert stats.avg_seconds_per_record == 120.0
    # 1 - 120/(8*60) = 1 - 0.25 = 0.75
    assert abs(stats.savings_pct - 0.75) < 0.01


def test_user_stats_handles_empty_events() -> None:
    """이벤트 0건 = 기본 UserStats."""
    stats = UserStats.from_events(user_id="empty_user", events=[])
    assert stats.total_records == 0
    assert stats.successful_records == 0
    assert stats.savings_pct == 0.0


def test_get_user_stats_no_file_returns_empty(tmp_path, monkeypatch) -> None:
    """파일 없는 사용자 = 기본 UserStats."""
    from kormarc_auto.ui import time_tracker as tt

    monkeypatch.setattr(tt, "STATS_DIR", tmp_path)

    stats = get_user_stats(user_id="never_existed")
    assert stats.total_records == 0


def test_user_stats_method_breakdown() -> None:
    """method별 처리 분포 집계."""
    now = time.time()
    events = [
        ProcessingEvent(
            user_id="u", isbn="1", duration_seconds=60, timestamp=now, method="single", success=True
        ),
        ProcessingEvent(
            user_id="u", isbn="2", duration_seconds=60, timestamp=now, method="single", success=True
        ),
        ProcessingEvent(
            user_id="u", isbn="3", duration_seconds=60, timestamp=now, method="batch", success=True
        ),
        ProcessingEvent(
            user_id="u", isbn="4", duration_seconds=60, timestamp=now, method="photo", success=True
        ),
    ]
    stats = UserStats.from_events(user_id="u", events=events)
    assert stats.method_breakdown == {"single": 2, "batch": 1, "photo": 1}
