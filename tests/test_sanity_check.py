"""sanity-check 모듈 테스트 — PILOT 1주차 첫 30분 도구."""

from __future__ import annotations

from pathlib import Path

from kormarc_auto.librarian_helpers.sanity_check import (
    SanityReport,
    run_sanity_check,
)


def test_run_sanity_check_returns_report_for_empty_dir(tmp_path: Path):
    report = run_sanity_check(tmp_path)
    assert isinstance(report, SanityReport)
    assert report.file_count == 0
    assert report.record_count == 0
    assert report.integrity_pct == 0.0


def test_run_sanity_check_handles_missing_dir(tmp_path: Path):
    missing = tmp_path / "does_not_exist"
    report = run_sanity_check(missing)
    assert report.file_count == 0
    assert report.record_count == 0


def test_sanity_report_to_text_includes_core_sections(tmp_path: Path):
    report = run_sanity_check(tmp_path)
    text = report.to_text()
    assert "자관 .mrc 진단 보고서" in text
    assert "디렉토리" in text
    assert "정합률" in text
    assert "049 prefix 분포" in text


def test_sanity_report_threshold_passed_through(tmp_path: Path):
    report = run_sanity_check(tmp_path, prefix_threshold=2.5)
    assert report.prefix_summary.threshold_pct == 2.5


def test_sanity_report_real_mrc_directory_if_exists():
    """자관 D 드라이브가 마운트된 환경에서만 실행."""
    real_dir = Path("D:/내를건너서 숲으로 도서관/수서")
    if not real_dir.exists():
        return  # 자관 외 환경에서는 skip
    report = run_sanity_check(real_dir)
    # 자관 4-29 측정: 174 파일·3,383 레코드·99.82% 정합 (회귀 가드)
    assert report.file_count >= 100
    assert report.record_count >= 1000
    assert report.integrity_pct >= 99.0
