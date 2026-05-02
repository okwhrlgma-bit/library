"""책단비 자동 라벨 생성기 테스트 (ADR-0020)."""

from __future__ import annotations

from pathlib import Path

from kormarc_auto.chaekdanbi.auto_label_generator import (
    ChaekdanbiLabel,
    from_kormarc_dict,
    generate_label,
    generate_label_text,
)


def _sample_label() -> ChaekdanbiLabel:
    return ChaekdanbiLabel(
        title="작별하지 않는다",
        author="한강",
        isbn="9788936434120",
        registration_no="EQ012345",
        call_number="813.7-한31ㅈ",
        target_library="은평구립도서관",
        request_date="2026-05-01",
        return_date="2026-05-15",
    )


def test_label_text_contains_core_fields():
    text = generate_label_text(_sample_label())
    assert "작별하지 않는다" in text
    assert "한강" in text
    assert "9788936434120" in text
    assert "EQ012345" in text
    assert "813.7-한31ㅈ" in text
    assert "은평구립도서관" in text
    assert "2026-05-01" in text


def test_label_text_includes_source_library_default():
    text = generate_label_text(_sample_label())
    assert "○○도서관" in text


def test_label_text_includes_note_when_present():
    label = ChaekdanbiLabel(
        title="t", author="a", isbn="i", registration_no="r",
        call_number="c", target_library="L", request_date="2026-05-01",
        note="이용자 픽업 예정",
    )
    text = generate_label_text(label)
    assert "이용자 픽업 예정" in text


def test_label_text_includes_extra_kv():
    label = ChaekdanbiLabel(
        title="t", author="a", isbn="i", registration_no="r",
        call_number="c", target_library="L", request_date="2026-05-01",
        extra={"이용자": "홍길동"},
    )
    text = generate_label_text(label)
    assert "홍길동" in text


def test_from_kormarc_dict_maps_basic_fields():
    record = {
        "title": "소년이 온다",
        "author": "한강",
        "isbn": "9788936434559",
        "registration_no": "EQ099999",
        "call_number": "813.7-한31ㅅ",
    }
    label = from_kormarc_dict(record, target_library="은평구립도서관", request_date="2026-05-02")
    assert label.title == "소년이 온다"
    assert label.registration_no == "EQ099999"
    assert label.target_library == "은평구립도서관"


def test_from_kormarc_dict_handles_reg_no_alias():
    record = {"title": "t", "author": "a", "isbn": "i", "reg_no": "EQ001"}
    label = from_kormarc_dict(record, target_library="L", request_date="2026-05-01")
    assert label.registration_no == "EQ001"


def test_generate_label_produces_file(tmp_path: Path):
    out = generate_label(_sample_label(), tmp_path / "label.hwpx")
    assert out.exists()
    # python-hwpx 미설치 환경에서는 .txt 폴백
    assert out.suffix in (".hwpx", ".txt")
    text = out.read_text(encoding="utf-8") if out.suffix == ".txt" else None
    if text is not None:
        assert "작별하지 않는다" in text


def test_generate_label_creates_parent_dir(tmp_path: Path):
    out = generate_label(_sample_label(), tmp_path / "nested" / "x" / "label.hwpx")
    assert out.exists()
