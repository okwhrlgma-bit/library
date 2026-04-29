"""KORMARC Phase 1.5 자료유형 모듈 테스트 (ebook·ejournal·audiobook)."""

from __future__ import annotations

from kormarc_auto.kormarc.audiobook import (
    build_audiobook_fields,
)
from kormarc_auto.kormarc.audiobook import (
    derive_008_23 as audio_derive_008_23,
)
from kormarc_auto.kormarc.ebook import build_ebook_fields, derive_008_23
from kormarc_auto.kormarc.ejournal import (
    FREQUENCY_CODES,
    build_ejournal_fields,
    derive_008_18_21,
)

# ── 전자책 (ebook) ────────────────────────────────────────────────


def test_ebook_856_url_field():
    fields = build_ebook_fields({"url": "https://lib.example.kr/book/9788912345678.pdf"})
    tags = [f.tag for f in fields]
    assert "856" in tags


def test_ebook_538_format_field():
    fields = build_ebook_fields({"format": "PDF"})
    f538 = next((f for f in fields if f.tag == "538"), None)
    assert f538 is not None
    assert "PDF" in f538.subfields[0].value


def test_ebook_008_23_online_returns_o():
    assert derive_008_23("online") == "o"


def test_ebook_008_23_offline_returns_q():
    assert derive_008_23("offline") == "q"


# ── 전자저널 (ejournal) ──────────────────────────────────────────


def test_ejournal_022_issn_required():
    fields = build_ejournal_fields({"issn": "2234-5678"})
    f022 = next((f for f in fields if f.tag == "022"), None)
    assert f022 is not None
    assert f022.subfields[0].value == "2234-5678"


def test_ejournal_310_frequency():
    fields = build_ejournal_fields({"frequency": "월간"})
    f310 = next((f for f in fields if f.tag == "310"), None)
    assert f310 is not None
    assert "월간" in f310.subfields[0].value


def test_ejournal_362_first_issue():
    fields = build_ejournal_fields({"first_issue": "Vol.1 No.1 (2026.01)"})
    f362 = next((f for f in fields if f.tag == "362"), None)
    assert f362 is not None
    assert "~" in f362.subfields[0].value


def test_ejournal_frequency_code_mapping():
    assert FREQUENCY_CODES["monthly"] == "m"
    assert FREQUENCY_CODES["weekly"] == "w"
    assert FREQUENCY_CODES["quarterly"] == "q"


def test_ejournal_008_18_21_4chars():
    code = derive_008_18_21("monthly")
    assert len(code) == 4
    assert code.startswith("m")


# ── 오디오북 (audiobook) ─────────────────────────────────────────


def test_audiobook_007_field_present():
    fields = build_audiobook_fields({"narrator": "김연아"})
    f007 = next((f for f in fields if f.tag == "007"), None)
    assert f007 is not None


def test_audiobook_511_narrator():
    fields = build_audiobook_fields({"narrator": "김연아"})
    f511 = next((f for f in fields if f.tag == "511"), None)
    assert f511 is not None
    assert "김연아" in f511.subfields[0].value


def test_audiobook_538_format_duration():
    fields = build_audiobook_fields({"format": "MP3", "duration": "8시간"})
    f538 = next((f for f in fields if f.tag == "538"), None)
    assert f538 is not None
    assert "MP3" in f538.subfields[0].value
    assert "8시간" in f538.subfields[0].value


def test_audiobook_008_23_online_returns_o():
    assert audio_derive_008_23("online") == "o"


def test_audiobook_008_23_offline_returns_s():
    assert audio_derive_008_23("offline") == "s"
