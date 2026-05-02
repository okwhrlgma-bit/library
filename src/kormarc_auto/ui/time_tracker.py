"""권당 시간 자동 측정·차트 모듈.

ADR-0068 (Part 45 §1 P1 매크로 사서 페인 직접 해결).

검증: P1 매크로 사서 가치 체감 시점 Day 3 → Day 1 즉시.
"이거 좋다" 순간 100건 일괄 5분 완료 + 권당 시간 차트.

Usage:
    from kormarc_auto.ui.time_tracker import track_processing, get_user_stats

    with track_processing() as t:
        # KORMARC 생성 작업
        result = build_kormarc_record(...)
    # t.duration_seconds 자동 기록

    stats = get_user_stats(user_id="...")
    st.metric("권당 평균", f"{stats.avg_seconds_per_record:.1f}초")
    st.metric("기존 대비 절감", f"{stats.savings_pct:.0%}")
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# 한국 사서 평균 KORMARC 작업 시간 (헌법 §0 정합)
BASELINE_MINUTES_PER_RECORD = 8.0  # 권당 8분 (수동 입력 기준)

STATS_DIR = Path(".cache/time_tracker")


@dataclass
class ProcessingEvent:
    """단일 KORMARC 생성 이벤트."""

    user_id: str
    isbn: str
    duration_seconds: float
    timestamp: float
    method: str  # "single" / "batch" / "photo"
    success: bool


@dataclass
class UserStats:
    """사용자별 누적 통계."""

    user_id: str
    total_records: int = 0
    total_seconds: float = 0.0
    successful_records: int = 0
    avg_seconds_per_record: float = 0.0
    savings_pct: float = 0.0
    today_records: int = 0
    week_records: int = 0
    method_breakdown: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_events(cls, user_id: str, events: list[ProcessingEvent]) -> UserStats:
        if not events:
            return cls(user_id=user_id)

        successful = [e for e in events if e.success]
        total_records = len(events)
        successful_records = len(successful)
        total_seconds = sum(e.duration_seconds for e in successful)
        avg_seconds = total_seconds / max(successful_records, 1)

        # 기존 8분 대비 절감 비율
        baseline_seconds = BASELINE_MINUTES_PER_RECORD * 60
        savings_pct = max(0.0, 1.0 - avg_seconds / baseline_seconds)

        # 오늘·이번 주 처리량
        now = time.time()
        day_seconds = 86400
        week_seconds = day_seconds * 7
        today_records = sum(1 for e in events if now - e.timestamp < day_seconds)
        week_records = sum(1 for e in events if now - e.timestamp < week_seconds)

        # method 분포
        method_breakdown: dict[str, int] = {}
        for e in successful:
            method_breakdown[e.method] = method_breakdown.get(e.method, 0) + 1

        return cls(
            user_id=user_id,
            total_records=total_records,
            total_seconds=total_seconds,
            successful_records=successful_records,
            avg_seconds_per_record=avg_seconds,
            savings_pct=savings_pct,
            today_records=today_records,
            week_records=week_records,
            method_breakdown=method_breakdown,
        )


@contextmanager
def track_processing(
    *,
    user_id: str = "anonymous",
    isbn: str = "",
    method: str = "single",
) -> Iterator[_Tracker]:
    """KORMARC 생성 시간 자동 측정 컨텍스트 매니저.

    Yields:
        _Tracker 객체. 컨텍스트 종료 시 duration·success 자동 기록.
    """
    tracker = _Tracker(user_id=user_id, isbn=isbn, method=method)
    start = time.perf_counter()
    try:
        yield tracker
        tracker.success = True
    except Exception:
        tracker.success = False
        raise
    finally:
        tracker.duration_seconds = time.perf_counter() - start
        _record_event(tracker)


@dataclass
class _Tracker:
    user_id: str
    isbn: str
    method: str
    duration_seconds: float = 0.0
    success: bool = False
    timestamp: float = field(default_factory=time.time)


def _record_event(tracker: _Tracker) -> None:
    """이벤트를 사용자별 JSONL 파일에 기록 (PII 마스킹·DSAR 정합)."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    user_file = STATS_DIR / f"{tracker.user_id}.jsonl"

    event = ProcessingEvent(
        user_id=tracker.user_id,
        isbn=tracker.isbn[:13],  # ISBN 표준 길이만
        duration_seconds=tracker.duration_seconds,
        timestamp=tracker.timestamp,
        method=tracker.method,
        success=tracker.success,
    )

    try:
        with user_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.__dict__, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("Time tracker 기록 실패: %s", e)


def get_user_stats(user_id: str) -> UserStats:
    """사용자별 누적 통계 조회 (Streamlit 대시보드 표시용)."""
    user_file = STATS_DIR / f"{user_id}.jsonl"
    if not user_file.exists():
        return UserStats(user_id=user_id)

    events: list[ProcessingEvent] = []
    try:
        with user_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(ProcessingEvent(**json.loads(line)))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Time tracker 읽기 실패: %s", e)
        return UserStats(user_id=user_id)

    return UserStats.from_events(user_id=user_id, events=events)


def render_time_dashboard(user_id: str) -> None:
    """Streamlit 권당 시간 대시보드 렌더링.

    P1 매크로 사서 가치 체감 직접 해결.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    stats = get_user_stats(user_id=user_id)

    if stats.successful_records == 0:
        st.info("아직 처리한 책이 없어요. 첫 ISBN을 입력해보세요.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "권당 평균 시간",
            f"{stats.avg_seconds_per_record:.1f}초",
            delta=f"-{(BASELINE_MINUTES_PER_RECORD * 60 - stats.avg_seconds_per_record):.0f}초 vs 기존",
            delta_color="inverse",
        )

    with col2:
        st.metric(
            "기존 대비 절감",
            f"{stats.savings_pct:.0%}",
            help="권당 8분 (수동 입력) 대비 자동화 절감 비율",
        )

    with col3:
        st.metric(
            "오늘 처리량",
            f"{stats.today_records}권",
            delta=f"이번 주 {stats.week_records}권",
        )

    # 절약된 누적 시간 (사서 동기부여)
    total_baseline_minutes = stats.successful_records * BASELINE_MINUTES_PER_RECORD
    actual_minutes = stats.total_seconds / 60
    saved_minutes = total_baseline_minutes - actual_minutes
    saved_hours = saved_minutes / 60

    if saved_hours >= 1:
        st.success(
            f"🎉 누적 **{saved_hours:.1f}시간** 절약했어요. "
            f"({stats.successful_records}권 처리, 기존 방식 대비)"
        )
    elif saved_minutes > 0:
        st.success(f"누적 **{saved_minutes:.0f}분** 절약. ({stats.successful_records}권 처리)")
