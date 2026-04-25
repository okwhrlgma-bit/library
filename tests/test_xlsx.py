"""xlsx 출력 단위 테스트 — 사서가 가장 많이 쓰는 형식."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

openpyxl = pytest.importorskip("openpyxl")

from kormarc_auto.output.xlsx_writer import (  # noqa: E402
    DEFAULT_COLUMNS,
    write_books_xlsx,
    write_isbn_template_xlsx,
)


def test_template_creates_file(tmp_path):
    out = write_isbn_template_xlsx(output_path=tmp_path / "tpl.xlsx")
    assert out.exists()
    wb = openpyxl.load_workbook(out)
    assert "ISBN 입력" in wb.sheetnames
    assert "사용법" in wb.sheetnames
    # A1 헤더가 'ISBN'으로 시작
    ws = wb["ISBN 입력"]
    assert "ISBN" in str(ws.cell(1, 1).value)


def test_books_xlsx_writes_rows(tmp_path):
    books = [
        {
            "isbn": "9788936434120",
            "title": "작별하지 않는다",
            "author": "한강",
            "publisher": "문학동네",
            "publication_year": "2021",
            "kdc": "813.7",
            "confidence": 0.92,
            "source": "nl_korea",
        },
        {
            "isbn": "9788932020789",
            "title": "채식주의자",
            "author": "한강",
            "kdc": "813.7",
        },
    ]
    out = write_books_xlsx(books, output_path=tmp_path / "books.xlsx")
    assert out.exists()

    wb = openpyxl.load_workbook(out)
    ws = wb.active
    # 1행 헤더 + 2건 데이터
    assert ws.max_row == 3
    # ISBN이 A2/A3에 있는지
    assert ws.cell(2, 1).value == "9788936434120"
    assert ws.cell(3, 1).value == "9788932020789"
    # 메타 시트
    assert "메타" in wb.sheetnames
    assert wb["메타"]["B2"].value == 2  # 총 건수


def test_books_xlsx_handles_list_value(tmp_path):
    """저자가 리스트인 경우 ';' 결합."""
    books = [{"isbn": "111", "author": ["한강", "김영하"]}]
    out = write_books_xlsx(books, output_path=tmp_path / "list.xlsx")
    wb = openpyxl.load_workbook(out)
    ws = wb.active
    # 저자 컬럼 위치 찾기
    author_col = next(i for i, (k, _) in enumerate(DEFAULT_COLUMNS, 1) if k == "author")
    assert "한강" in str(ws.cell(2, author_col).value)
    assert "김영하" in str(ws.cell(2, author_col).value)


def test_books_xlsx_empty_list(tmp_path):
    out = write_books_xlsx([], output_path=tmp_path / "empty.xlsx")
    assert out.exists()
    wb = openpyxl.load_workbook(out)
    ws = wb.active
    assert ws.max_row == 1  # 헤더만


def test_default_columns_has_essentials():
    """기본 컬럼에 ISBN·표제·저자·KDC가 포함되어야 함."""
    keys = {k for k, _ in DEFAULT_COLUMNS}
    for required in ["isbn", "title", "author", "kdc", "confidence"]:
        assert required in keys, f"필수 컬럼 누락: {required}"
