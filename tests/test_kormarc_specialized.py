"""특화 KORMARC 모듈 단위 테스트 — serial·non_book·rare_book·material_type·marc21 conversion."""

from __future__ import annotations

import sys
from pathlib import Path

from pymarc import Record

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.conversion import marc21  # noqa: E402
from kormarc_auto.kormarc import material_type, non_book, rare_book, serial  # noqa: E402


class TestSerial:
    def test_issn(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        serial.add_issn(r, "12345678")
        f = r.get_fields("022")
        assert f
        sf = next(s for s in f[0].subfields if s.code == "a")
        assert sf.value == "1234-5678"

    def test_frequency_detect(self):
        assert serial.detect_frequency_from_title("월간 도서관") == "월간"
        assert serial.detect_frequency_from_title("계간 시문학") == "계간"

    def test_volume(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        serial.add_volume_designation(r, start="제1권 (2024)")
        assert r.get_fields("362")


class TestNonBook:
    def test_007_ebook(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        non_book.add_007(r, "ebook")
        f007 = r.get("007")
        assert f007 is not None
        assert f007.data.startswith("cr")

    def test_url(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        non_book.add_electronic_resource_url(r, url="https://example.kr/book")
        assert r.get_fields("856")

    def test_thesis(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        non_book.add_thesis_note(r, degree="박사학위", institution="서울대학교")
        f502 = r.get_fields("502")
        assert f502


class TestRareBook:
    def test_title_with_format(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        rare_book.add_rare_book_title(
            r, title_hanja="論語", title_korean="논어", format_type="wood_print"
        )
        f245 = r.get_fields("245")
        assert f245
        # 한글 변형 246
        assert r.get_fields("246")

    def test_publication_ganji(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        rare_book.add_rare_book_publication(
            r, place="한양", publisher="홍문관", year="1697", ganji="崇禎四丁丑"
        )
        f260 = r.get_fields("260")
        assert f260

    def test_extent_yeop(self):
        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        rare_book.add_extent_yeop(r, leaves=42, size_cm="30 cm")
        f300 = r.get_fields("300")
        assert f300


class TestMaterialType:
    def test_detect_basic(self):
        assert material_type.detect_material_type({"title": "전자책 가이드"}) == "ebook"
        assert material_type.detect_material_type({"title": "월간 도서관"}) == "serial_current"

    def test_book_default(self):
        assert material_type.detect_material_type({"title": "작별하지 않는다"}) == "book_single"

    def test_codes(self):
        codes = material_type.get_codes("book_single")
        assert codes.ldr_06 == "a"
        assert codes.ldr_07 == "m"
        assert codes.field_008_06 == "s"


class TestMarc21Conversion:
    def test_kormarc_to_marc21_drop(self):
        from pymarc import Field, Indicators, Subfield

        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        r.add_field(
            Field(
                tag="950",
                indicators=Indicators("0", " "),
                subfields=[Subfield(code="b", value="₩15000")],
            )
        )
        new = marc21.kormarc_to_marc21(r, drop_korea_specific=True)
        assert not new.get_fields("950")

    def test_warnings(self):
        from pymarc import Field, Indicators, Subfield

        r = Record(force_utf8=True, leader="00000nam a2200000   4500")
        r.add_field(
            Field(
                tag="049",
                indicators=Indicators("0", " "),
                subfields=[Subfield(code="l", value="K000001")],
            )
        )
        warnings = marc21.get_conversion_warnings(r, "marc21")
        assert any("049" in w for w in warnings)
