"""사서 보고서 (output.reports) PDF 생성 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

reportlab = pytest.importorskip("reportlab")

from kormarc_auto.output import reports  # noqa: E402


def test_acquisition_announcement(tmp_path):
    items = [
        {
            "title": "작별하지 않는다",
            "author": "한강",
            "publisher": "문학동네",
            "publication_year": "2021",
            "call_number": "813.7 한31ㅈ",
            "summary": "제주 4·3을 다룬 장편소설.",
        },
        {
            "title": "소년이 온다",
            "author": "한강",
            "publisher": "창비",
            "publication_year": "2014",
        },
    ]
    out = reports.make_acquisition_announcement(
        items,
        title="2026년 4월 신착",
        library_name="테스트도서관",
        output_path=str(tmp_path / "ann.pdf"),
    )
    assert out.exists()
    assert out.stat().st_size > 0
    # PDF 매직 바이트
    assert out.read_bytes()[:4] == b"%PDF"


def test_monthly_report(tmp_path, monkeypatch):
    """월간 보고서 — 빈 인덱스에서도 빈 통계로 PDF 생성."""
    monkeypatch.setenv("KORMARC_LIBRARY_INDEX", str(tmp_path / "idx.jsonl"))
    out = reports.make_monthly_report(
        library_name="테스트도서관",
        year=2026,
        month=4,
        output_path=str(tmp_path / "monthly.pdf"),
    )
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"


def test_validation_report_empty_list(tmp_path):
    """파일 목록이 비어도 요약 페이지가 생성되어야 함."""
    out = reports.make_validation_report(
        [],
        output_path=str(tmp_path / "val.pdf"),
    )
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"


def test_validation_report_with_real_mrc(tmp_path):
    """실제 .mrc 파일 1개로 검증 리포트 생성 (커버리지)."""
    pymarc = pytest.importorskip("pymarc")

    rec = pymarc.Record(force_utf8=True, leader="00000nam a2200000   4500")
    rec.add_field(pymarc.Field(tag="008", data=" " * 40))
    rec.add_field(
        pymarc.Field(
            tag="245",
            indicators=pymarc.Indicators("0", "0"),
            subfields=[pymarc.Subfield(code="a", value="테스트")],
        )
    )
    mrc_path = tmp_path / "sample.mrc"
    mrc_path.write_bytes(rec.as_marc())

    out = reports.make_validation_report(
        [mrc_path],
        output_path=str(tmp_path / "val.pdf"),
    )
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"


def test_korean_font_fallback(tmp_path):
    """한글 폰트 탐지 — 환경에 따라 KoreanFont 또는 Helvetica."""
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(tmp_path / "x.pdf"))
    font = reports._korean_font(c)
    assert font in {"KoreanFont", "Helvetica"}
