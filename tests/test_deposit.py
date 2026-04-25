"""납본 추적 단위 테스트."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.librarian_helpers import deposit  # noqa: E402


def test_record_and_list(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_DEPOSIT_LOG", str(tmp_path / "dep.jsonl"))
    deposit.record_deposit(
        title="테스트 자료",
        isbn="9788936434120",
        publication_date="2026-04-01",
        deposit_date="2026-04-15",
    )
    items = deposit.list_deposits()
    assert len(items) == 1
    assert items[0]["title"] == "테스트 자료"
    assert items[0]["copies"] == 2  # 법정 기본


def test_deposit_deadline():
    """발행 후 30일이 마감일."""
    d = deposit.deposit_deadline("2026-04-01")
    assert d == date(2026, 5, 1)


def test_find_overdue_deposits(tmp_path, monkeypatch):
    """발행 후 30일 초과 + 미납본인 자료를 찾아냄."""
    monkeypatch.setenv("KORMARC_DEPOSIT_LOG", str(tmp_path / "dep.jsonl"))

    # 1건은 이미 납본 완료
    deposit.record_deposit(
        title="이미 납본",
        isbn="111",
        publication_date="2026-01-01",
        deposit_date="2026-01-15",
    )

    # 자관 발행 자료 목록 (가상)
    expected = [
        {"title": "이미 납본", "isbn": "111", "publication_date": "2026-01-01"},
        {"title": "미납본 (마감 지남)", "isbn": "222", "publication_date": "2026-01-01"},
        {"title": "최근 발행 (마감 전)", "isbn": "333", "publication_date": "2026-04-20"},
    ]
    overdue = deposit.find_overdue_deposits(
        today=date(2026, 4, 25),
        expected_publications=expected,
    )

    isbns = {o["isbn"] for o in overdue}
    assert "222" in isbns  # 마감 지난 미납본
    assert "111" not in isbns  # 이미 납본
    assert "333" not in isbns  # 마감 전


def test_find_overdue_no_expected_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_DEPOSIT_LOG", str(tmp_path / "dep.jsonl"))
    assert deposit.find_overdue_deposits(expected_publications=None) == []
    assert deposit.find_overdue_deposits(expected_publications=[]) == []


def test_deposit_constants():
    """도서관법 상수 — 30일 보호."""
    assert deposit.DEPOSIT_DEADLINE_DAYS == 30
