"""Part 82 신규 모듈 테스트 (libsta·신입 사서 적응)."""

from __future__ import annotations

from datetime import date


def test_libsta_statistics_basic():
    from kormarc_auto.output.libsta_statistics import (
        LibstaStatistic,
        calculate_kpi_summary,
        export_to_libsta_csv,
    )

    stat = LibstaStatistic(
        library_code="LIB001",
        library_name="○○도서관",
        year=2026,
        month=4,
        new_books_count=300,
        total_books_count=50000,
        new_users_count=50,
        total_users_count=5000,
        loans_count=2000,
        returns_count=1950,
        visits_count=8000,
        program_participants=300,
        librarian_count=8,
        automation_records=270,  # 90% 자동화
    )

    csv_text = export_to_libsta_csv([stat])
    assert "○○도서관" in csv_text
    assert "300" in csv_text
    assert "도서관코드" in csv_text  # 헤더

    kpi = calculate_kpi_summary(stat)
    assert kpi["users_per_librarian"] == 625  # 5000/8
    assert kpi["automation_rate"] == 0.9
    assert kpi["new_books_per_librarian"] == 37
    assert 0 < kpi["loan_to_visit_ratio"] <= 1


def test_new_librarian_onboarding_basic():
    from kormarc_auto.intelligence.new_librarian_onboarding import (
        DEFAULT_STEPS,
        create_default_plan,
        estimate_productivity,
    )

    # 7단 표준
    assert len(DEFAULT_STEPS) >= 7
    critical = [s for s in DEFAULT_STEPS if s.is_critical]
    assert len(critical) >= 4

    # Plan 생성
    plan = create_default_plan(
        librarian_name="홍길동",
        sasagwan="○○도서관",
        start_date=date(2026, 5, 1),
    )

    # Day 1 = Day 1·2 단계 표시
    today_d1 = plan.get_today_steps(date(2026, 5, 1))
    assert len(today_d1) >= 1

    # Day 5 = 진행률
    progress = plan.progress_percentage(date(2026, 5, 5))
    assert 0 <= progress <= 100

    # 생산성 곡선 (우리 도구 = 70% 시작)
    assert estimate_productivity(0) == 0.7
    assert estimate_productivity(15) == 0.85
    assert estimate_productivity(60) == 0.95
    assert estimate_productivity(120) == 1.0
