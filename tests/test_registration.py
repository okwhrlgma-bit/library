"""등록번호 자동 부여·누락번호 검출 단위 테스트."""

from __future__ import annotations

import pytest

from kormarc_auto.librarian_helpers.registration import (
    assign_for_multivolume,
    find_missing_numbers,
    next_registration_number,
    parse_registration_number,
)


def test_parse_valid():
    r = parse_registration_number("EM0126" + "00123")
    assert r.kind == "EM"
    assert r.turn == 1
    assert r.year == 26
    assert r.serial == 123


def test_parse_invalid_format():
    with pytest.raises(ValueError):
        parse_registration_number("foo123")


def test_next_first_in_year():
    # 빈 DB → 첫 등록
    n = next_registration_number([], year=26)
    assert n == "EM" + "01" + "26" + "00001"
    assert n == "EM012600001"


def test_next_appends_max():
    existing = ["EM0126" + "00001", "EM0126" + "00005"]
    n = next_registration_number(existing, year=26)
    assert n.endswith("00006")


def test_next_fills_gap():
    # 1, 3, 5 → fill_gap True면 2 반환
    existing = [
        "EM0126" + "00001",
        "EM0126" + "00003",
        "EM0126" + "00005",
    ]
    n = next_registration_number(existing, year=26, fill_gap=True)
    assert n.endswith("00002")


def test_next_isolates_kind_year():
    # 다른 kind/year는 영향 없음
    existing = [
        "EM0125" + "00099",  # 다른 연도
        "BM0126" + "00099",  # 다른 kind
    ]
    n = next_registration_number(existing, year=26, kind="EM")
    assert n.endswith("00001")


def test_find_missing():
    existing = [f"EM0126{i:05d}" for i in (1, 2, 5, 7, 8)]
    missing = find_missing_numbers(existing, year=26)
    assert missing == [3, 4, 6]


def test_find_missing_empty():
    assert find_missing_numbers([], year=26) == []


def test_multivolume_5_books():
    base = {"title": "한국 도서관사", "author": "김도서"}
    results = assign_for_multivolume(base, volumes=5, year=26)
    assert len(results) == 5
    nums = [r["registration_number"] for r in results]
    assert all(n.startswith("EM0126") for n in nums)
    serials = [int(n[-5:]) for n in nums]
    assert serials == [1, 2, 3, 4, 5]
    assert results[0]["volume_label"] == "v.1"
    assert results[4]["marc_490_v"] == "5"


def test_multivolume_existing_offset():
    base = {"title": "전집", "author": "...."}
    existing = [f"EM0126{i:05d}" for i in (1, 2, 3)]
    results = assign_for_multivolume(base, volumes=2, year=26, existing=existing)
    serials = [int(r["registration_number"][-5:]) for r in results]
    assert serials == [4, 5]
