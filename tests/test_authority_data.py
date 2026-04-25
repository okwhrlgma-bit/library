"""전거 데이터 (100/110/111) 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

from pymarc import Record

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.kormarc.authority_data import (  # noqa: E402
    add_corporate_author_field,
    add_meeting_author_field,
    add_personal_author_field,
    parse_author_string_full,
)


def test_personal_with_dates():
    r = Record(force_utf8=True, leader="00000nam a2200000   4500")
    add_personal_author_field(r, name="한강", birth_year=1970, role="저자")
    f100 = r.get_fields("100")
    assert f100
    sf = {sf.code: sf.value for sf in f100[0].subfields}
    assert sf.get("a") == "한강"
    assert sf.get("d", "").startswith("1970")
    assert sf.get("e") == "저자"


def test_personal_dynasty():
    r = Record(force_utf8=True, leader="00000nam a2200000   4500")
    add_personal_author_field(r, name="이순신", dynasty="조선")
    f100 = r.get_fields("100")
    assert f100
    sf = {sf.code: sf.value for sf in f100[0].subfields}
    assert sf.get("f") == "조선"


def test_corporate():
    r = Record(force_utf8=True, leader="00000nam a2200000   4500")
    add_corporate_author_field(r, name="한국도서관협회", subordinate="편집부")
    f110 = r.get_fields("110")
    assert f110
    sf = {sf.code: sf.value for sf in f110[0].subfields}
    assert sf.get("a") == "한국도서관협회"
    assert sf.get("b") == "편집부"


def test_meeting():
    r = Record(force_utf8=True, leader="00000nam a2200000   4500")
    add_meeting_author_field(r, name="한국도서관대회", number="제5회", date="2024")
    f111 = r.get_fields("111")
    assert f111


def test_parse_dates():
    r = parse_author_string_full("한강 (1970-)")
    assert r["name"] == "한강"
    assert r["birth_year"] == "1970"


def test_parse_dynasty():
    r = parse_author_string_full("이순신 (조선)")
    assert r["name"] == "이순신"
    assert r["dynasty"] == "조선"


def test_parse_multiple():
    r = parse_author_string_full("김철수 ; 박영희")
    assert r["name"] == "김철수"
    assert "박영희" in r["additional"]
