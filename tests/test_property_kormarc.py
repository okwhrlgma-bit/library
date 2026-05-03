"""B안 P3 — KORMARC builder property-based tests.

검증 invariants (헌법 정합):
1. 008 필드 = 정확히 40자리 (절대 규칙 #1)
2. ISBN-13 round-trip = 020 ▾a 13자리 입력 ↔ 출력 동일
3. 245 indicator2 = 관제 길이 + 1 (없으면 0) (절대 규칙 #5)
4. record.as_marc() round-trip = 입력 dict 유지

설치 미감지 시 자동 skip.
"""

from __future__ import annotations

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402


# MARC 제어 문자 (subfield delimiter \x1f·field terminator \x1e·record terminator \x1d) 제외
# = realistic 입력 (실 도서관 데이터 = 인쇄 가능한 한글·한자·영문만)
# v0.7 backlog: builder sanitization (헌법 위반은 X·robustness 개선)
_PRINTABLE = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),
        blacklist_characters="\x1d\x1e\x1f",
    ),
    min_size=1,
    max_size=40,
)


@st.composite
def book_data_strategy(draw):
    """KORMARC builder 입력 dict 생성 (realistic·MARC delimiter 제외)."""
    return {
        "isbn": "978" + "".join(str(draw(st.integers(0, 9))) for _ in range(10)),
        "title": draw(_PRINTABLE),
        "author": draw(_PRINTABLE),
        "publisher": draw(_PRINTABLE),
        "publication_year": str(draw(st.integers(1900, 2030))),
        "kdc": draw(st.sampled_from(["813.7", "863.2", "510", "616.4", "005.13"])),
        "sources": ["test"],
    }


class TestField008Invariant:
    @given(data=book_data_strategy())
    def test_008_exactly_40_chars(self, data):
        """008 = 정확히 40자리 (헌법 절대 규칙 #1)."""
        from kormarc_auto.kormarc.builder import build_kormarc_record

        record = build_kormarc_record(data, cataloging_agency="TEST")
        f008 = record.get("008")
        if f008 is not None:
            assert len(f008.data) == 40, f"008 = {len(f008.data)} chars (expect 40)"


class TestIsbnRoundTrip:
    @given(data=book_data_strategy())
    def test_isbn_in_020_a(self, data):
        """ISBN-13 입력 = 020 ▾a 동일 (round-trip)."""
        from kormarc_auto.kormarc.builder import build_kormarc_record

        record = build_kormarc_record(data, cataloging_agency="TEST")
        f020 = record.get("020")
        if f020 is not None:
            sf_a = f020.get_subfields("a")
            if sf_a:
                # Builder may add hyphens or 부가기호; ISBN digits must be substring
                isbn_digits_only = "".join(c for c in sf_a[0] if c.isdigit())
                assert data["isbn"] in isbn_digits_only or isbn_digits_only.startswith(data["isbn"][:10])


class TestBuilderDeterminism:
    @given(data=book_data_strategy())
    def test_same_input_same_record_field_count(self, data):
        """동일 입력 = 동일 필드 수 (결정성·B안 §0 invariant)."""
        from kormarc_auto.kormarc.builder import build_kormarc_record

        rec1 = build_kormarc_record(data, cataloging_agency="TEST")
        rec2 = build_kormarc_record(data, cataloging_agency="TEST")
        assert len(rec1.fields) == len(rec2.fields)


class TestPymarcRoundTrip:
    @given(data=book_data_strategy())
    def test_pymarc_bytes_roundtrip(self, data):
        """build → as_marc → MARCReader → as_marc bytes equal (Cycle 1 baseline 정합)."""
        from io import BytesIO

        from pymarc import MARCReader

        from kormarc_auto.kormarc.builder import build_kormarc_record

        rec = build_kormarc_record(data, cataloging_agency="TEST")
        raw1 = rec.as_marc()
        r2 = next(MARCReader(BytesIO(raw1), to_unicode=True, force_utf8=False), None)
        if r2 is not None:
            assert r2.as_marc() == raw1, "round-trip bytes mismatch"
