"""납본 별지 제3호서식 단위 테스트."""

from __future__ import annotations

from datetime import date

import pytest

from kormarc_auto.legal.deposit_form import (
    DepositForm,
    build_deposit_form,
    deposit_deadline,
    render_deposit_form_pdf,
    required_copies,
)


def test_required_copies_government():
    form = DepositForm(
        title="공공기관 보고서",
        author="기획재정부",
        publisher="기획재정부",
        publication_date="2026-04-01",
        is_government=True,
    )
    assert required_copies(form) == 3


def test_required_copies_with_preservation():
    form = DepositForm(
        title="작은도서관 소식지",
        author="○○도서관",
        publisher="○○도서관",
        publication_date="2026-04-01",
        consents_preservation=True,
    )
    assert required_copies(form) == 1


def test_required_copies_default():
    form = DepositForm(
        title="자가출판 시집",
        author="홍길동",
        publisher="홍길동",
        publication_date="2026-04-01",
        consents_preservation=False,
    )
    assert required_copies(form) == 2


def test_deposit_deadline_string():
    d = deposit_deadline("2026-04-01")
    assert d == date(2026, 5, 1)


def test_deposit_deadline_date_obj():
    d = deposit_deadline(date(2026, 12, 1))
    assert d == date(2026, 12, 31)


def test_build_form_from_book_data():
    form = build_deposit_form(
        {
            "title": "한국 도서관 발전사",
            "author": "김도서",
            "publisher": "도서관출판사",
            "publication_year": "2026",
            "isbn": "9788912345678",
            "pages": "320",
        },
        publisher_address="서울 종로구",
        submitter_name="김도서",
    )
    assert form.title == "한국 도서관 발전사"
    assert form.publication_date == "2026-01-01"  # 연도만 → 1월 1일
    assert form.isbn == "9788912345678"
    assert form.submitter_name == "김도서"


def test_build_form_requires_title():
    with pytest.raises(ValueError):
        build_deposit_form({"author": "x"})


def test_render_pdf(tmp_path):
    pytest.importorskip("reportlab")
    form = DepositForm(
        title="테스트 자료집",
        author="테스트저자",
        publisher="테스트출판사",
        publication_date="2026-04-01",
        isbn="9788912345678",
        pages="100",
        price_krw=15000,
        publisher_address="서울 강남구",
        publisher_contact="02-1234-5678",
        submitter_name="홍길동",
    )
    out = render_deposit_form_pdf(form, output_path=tmp_path / "deposit.pdf")
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"
    assert out.stat().st_size > 1000  # 어느 정도 컨텐츠
