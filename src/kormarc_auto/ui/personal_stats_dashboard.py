"""사서 개인 통계 대시보드 (DT2) — Part 65 wow #4 + Part 70 갭 12.

사서 페인 (Part 70):
- Personal Win 메시지 X = 결제 의향 ↓
- 사서 평가 가산점 자료·승진 자료 X

해결: 사서 개인 통계 대시보드 자동.
- 이번 달·연간 처리 권수·시간·절감
- 사서 평가 가산점 자료 (PDF·분기)
- KLA·KSLA 발표 자료 자동
- 1주년·3주년 인증서
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

BASELINE_MINUTES_PER_RECORD = 8.0  # time_tracker.py와 동일


@dataclass(frozen=True)
class LibrarianStats:
    """사서 개인 통계 (월·연 누적)."""

    librarian_name: str
    period_start: date
    period_end: date
    total_records: int
    avg_minutes_per_record: float
    automation_rate: float  # 0.0~1.0 (AI·자동 비율)

    @property
    def time_saved_minutes(self) -> float:
        """절감 시간 (분)."""
        return self.total_records * (BASELINE_MINUTES_PER_RECORD - self.avg_minutes_per_record)

    @property
    def time_saved_hours(self) -> float:
        return self.time_saved_minutes / 60

    @property
    def equivalent_books(self) -> int:
        """절감 시간 = 추가 가능 권수 (베이스라인 8분/권)."""
        return int(self.time_saved_minutes / BASELINE_MINUTES_PER_RECORD)


def render_personal_dashboard(stats: LibrarianStats) -> None:
    """Streamlit 사서 개인 대시보드 (Personal Win 직격)."""
    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(f"### 📊 {stats.librarian_name} 선생님 통계")
    st.caption(
        f"{stats.period_start.year}년 {stats.period_start.month}월 ~ "
        f"{stats.period_end.year}년 {stats.period_end.month}월"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("처리 권수", f"{stats.total_records:,}권")
    col2.metric("절감 시간", f"{stats.time_saved_hours:.1f}시간")
    col3.metric("추가 가능", f"책 {stats.equivalent_books:,}권")

    st.markdown("#### 자동화율")
    st.progress(stats.automation_rate, text=f"{int(stats.automation_rate * 100)}% 자동")

    st.info(
        "**선생님 통계 = 사서 평가 가산점·KLA 발표·승진 자료에 활용 가능합니다.** "
        "분기 보고서·인증서 자동 발급."
    )


def generate_evaluation_report(stats: LibrarianStats) -> str:
    """사서 평가 가산점 자료 markdown 자동 생성 (관장 결재용)."""
    return f"""# {stats.librarian_name} 선생님 사서 업무 성과 보고서

> 기간: {stats.period_start.year}년 {stats.period_start.month}월 ~ {stats.period_end.year}년 {stats.period_end.month}월
> 자동 생성: kormarc-auto

## 정량 성과

| 지표 | 값 |
|---|---|
| 처리 권수 | **{stats.total_records:,}권** |
| 평균 권당 시간 | {stats.avg_minutes_per_record:.1f}분 |
| 절감 시간 | **{stats.time_saved_hours:.1f}시간** |
| 추가 처리 가능 | **책 {stats.equivalent_books:,}권** |
| 자동화율 | {int(stats.automation_rate * 100)}% |

## 사업 가치

- 권당 시간 단축: 8분 → {stats.avg_minutes_per_record:.1f}분
- 사서 본인 시간 = 이용자 응대·고급 업무에 집중 가능
- 도서관 운영 효율 ↑

## 도서관 평가 가산점 활용

본 보고서는 도서관 운영 평가·사서 평가 가산점 자료로 활용 가능합니다.
- 정량 평가 지표 정합 (문체부 도서관 운영 평가)
- 사서 KPI·승진 자료
- KLA·KSLA 발표 자료

> kormarc-auto = 사서 개인 통계 자동 = Personal Win 직격
"""


__all__ = [
    "BASELINE_MINUTES_PER_RECORD",
    "LibrarianStats",
    "generate_evaluation_report",
    "render_personal_dashboard",
]
