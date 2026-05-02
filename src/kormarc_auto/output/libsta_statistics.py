"""국가도서관통계시스템 (libsta.go.kr) 통계 자동 — Part 82 페인 #26 정합.

사서 페인 (Part 82):
- libsta = 매월 통계 입력 부담
- 시도 → 문체부 → libsta 3중 검증
- 1관당 30+ 지표 매월 = 사서 행정 시간 ↑

해결: kormarc-auto 처리 데이터 = libsta 형식 자동 변환·export.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass


@dataclass(frozen=True)
class LibstaStatistic:
    """libsta 통계 1건 (월·관별)."""

    library_code: str  # 자관 코드 (libsta 발급)
    library_name: str
    year: int
    month: int
    # 핵심 지표 (libsta 30+ 중 핵심 10)
    new_books_count: int = 0  # 신착 도서 수
    total_books_count: int = 0  # 누적 장서 수
    new_users_count: int = 0  # 신규 회원
    total_users_count: int = 0  # 누적 회원
    loans_count: int = 0  # 대출 건수
    returns_count: int = 0  # 반납 건수
    visits_count: int = 0  # 방문 건수
    program_participants: int = 0  # 프로그램 참여
    librarian_count: int = 0  # 사서 수
    automation_records: int = 0  # 자동화 처리 권수 (kormarc-auto 자동)


def export_to_libsta_csv(stats: list[LibstaStatistic]) -> str:
    """libsta CSV 형식 export.

    libsta 양식 (자치구·시도 보고용).
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "도서관코드", "도서관명", "년", "월",
        "신착도서", "누적장서", "신규회원", "누적회원",
        "대출", "반납", "방문", "프로그램참여",
        "사서수", "자동화처리권수",
    ])
    for s in stats:
        writer.writerow([
            s.library_code, s.library_name, s.year, s.month,
            s.new_books_count, s.total_books_count,
            s.new_users_count, s.total_users_count,
            s.loans_count, s.returns_count,
            s.visits_count, s.program_participants,
            s.librarian_count, s.automation_records,
        ])
    return buf.getvalue()


def calculate_kpi_summary(stat: LibstaStatistic) -> dict:
    """월별 KPI 요약 (libsta 평가 지표 정합).

    문체부 도서관 운영 평가 23 지표 정합.
    """
    # 1인당 봉사 인구 (libsta 핵심)
    per_librarian = stat.total_users_count // max(stat.librarian_count, 1)
    # 자동화율
    automation_rate = (
        stat.automation_records / max(stat.new_books_count, 1)
        if stat.new_books_count else 0
    )
    # 1인당 신착 처리 권수
    new_per_librarian = stat.new_books_count // max(stat.librarian_count, 1)

    return {
        "users_per_librarian": per_librarian,
        "automation_rate": round(automation_rate, 2),
        "new_books_per_librarian": new_per_librarian,
        "total_visits": stat.visits_count,
        "loan_to_visit_ratio": round(
            stat.loans_count / max(stat.visits_count, 1), 2
        ),
    }


__all__ = ["LibstaStatistic", "calculate_kpi_summary", "export_to_libsta_csv"]
