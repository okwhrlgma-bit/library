"""사서 보조 모듈 단위 테스트 — normalize·publisher·kdc_tree·subfield·romanization."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.librarian_helpers import (  # noqa: E402
    kdc_tree,
    normalize,
    publisher_db,
    romanization,
    subfield_input,
)


class TestNormalize:
    def test_year(self):
        assert normalize.normalize_year("2024년 5월") == "2024"
        assert normalize.normalize_year("") is None

    def test_pages(self):
        assert normalize.normalize_pages("300쪽") == "300 p."
        assert normalize.normalize_pages("345 p.") == "345 p."

    def test_size_wh(self):
        assert normalize.normalize_size("153x224") == "22 cm"

    def test_isbn(self):
        assert normalize.normalize_isbn("978-89-374-6278-8") == "9788937462788"
        assert normalize.normalize_isbn("12345") is None

    def test_split_authors(self):
        r = normalize.split_authors("김철수;박영희;이순자")
        assert r["primary"] == "김철수"
        assert "박영희" in r["additional"]

    def test_external_quote(self):
        r = normalize.split_authors("김철수 외 3")
        assert r["primary"] == "김철수"


class TestKdcTree:
    def test_search_kdc(self):
        results = kdc_tree.search_kdc("소설")
        assert any(code.startswith("8") for code, _ in results)

    def test_get_main(self):
        mains = kdc_tree.get_main_classes()
        assert len(mains) == 10
        assert ("800", "문학") in mains


class TestSubfieldInput:
    def test_dollar(self):
        assert subfield_input.expand_subfield_codes("$a작별") == "▾a작별"

    def test_double_slash(self):
        assert subfield_input.expand_subfield_codes("//a한강") == "▾a한강"

    def test_parse(self):
        r = subfield_input.parse_field_line("245 10 ▾a작별 ▾c/ 한강")
        assert r["tag"] == "245"
        assert r["ind1"] == "1"
        assert r["ind2"] == "0"
        assert ("a", "작별") in r["subfields"]


class TestRomanization:
    def test_simple(self):
        assert romanization.hangul_to_rr("한강").lower().startswith("hang")

    def test_looks_korean(self):
        assert romanization.looks_korean("한강")
        assert not romanization.looks_korean("Han Gang")

    def test_alalc_chars(self):
        out = romanization.hangul_to_alalc("김영하")
        # ALA-LC는 ŏ·ŭ 사용
        assert "ŏ" in out or "Y" in out


class TestPublisherDb:
    def test_extract_id(self, tmp_path, monkeypatch):
        monkeypatch.setenv("KORMARC_PUBLISHER_DB", str(tmp_path / "pub.json"))
        pid = publisher_db.extract_publisher_id("9788937462788")
        assert pid is not None
        assert len(pid) == 4

    def test_remember_lookup(self, tmp_path, monkeypatch):
        monkeypatch.setenv("KORMARC_PUBLISHER_DB", str(tmp_path / "pub.json"))
        publisher_db.remember_publisher(
            "9788937462788",
            publisher="민음사",
            publication_place="서울",
        )
        result = publisher_db.lookup_publisher("9788937462788")
        assert result is not None
        assert result["publisher"] == "민음사"

    def test_autocomplete(self, tmp_path, monkeypatch):
        monkeypatch.setenv("KORMARC_PUBLISHER_DB", str(tmp_path / "pub.json"))
        publisher_db.remember_publisher("9788937462788", publisher="민음사")
        publisher_db.remember_publisher("9788956055555", publisher="민중서관")
        matches = publisher_db.autocomplete_publishers("민")
        assert "민음사" in matches
