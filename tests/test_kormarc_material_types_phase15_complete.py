"""KORMARC Phase 1.5 완성 — multimedia·thesis 테스트.

기존 ebook·ejournal·audiobook 3종 + multimedia·thesis 2종 = 9 자료유형
모듈 100% 커버 (KORMARC 2023.12 정합).
"""

from __future__ import annotations

from kormarc_auto.kormarc.multimedia import (
    MEDIA_TYPE_CODES,
    build_multimedia_fields,
    derive_008_33,
)
from kormarc_auto.kormarc.thesis import build_thesis_fields, format_502_text

# ── 멀티미디어 (multimedia) ────────────────────────────────────


def test_multimedia_007_dvd_field_present():
    fields = build_multimedia_fields({"format": "DVD"})
    f007 = next((f for f in fields if f.tag == "007"), None)
    assert f007 is not None
    assert f007.data == "vd"


def test_multimedia_007_streaming_returns_vz():
    fields = build_multimedia_fields({"format": "스트리밍"})
    f007 = next((f for f in fields if f.tag == "007"), None)
    assert f007 is not None
    assert f007.data == "vz"


def test_multimedia_300_includes_format_and_color():
    fields = build_multimedia_fields(
        {"format": "DVD", "unit_count": 2, "color": "흑백", "size_cm": "12 cm"}
    )
    f300 = next((f for f in fields if f.tag == "300"), None)
    assert f300 is not None
    assert "DVD 2매" in f300.subfields[0].value
    assert "흑백" in f300.subfields[1].value


def test_multimedia_306_runtime_minutes_int():
    fields = build_multimedia_fields({"runtime": 90})
    f306 = next((f for f in fields if f.tag == "306"), None)
    assert f306 is not None
    assert f306.subfields[0].value == "013000"


def test_multimedia_306_runtime_korean_minute_string():
    fields = build_multimedia_fields({"runtime": "125분"})
    f306 = next((f for f in fields if f.tag == "306"), None)
    assert f306 is not None
    assert f306.subfields[0].value == "020500"


def test_multimedia_306_runtime_colon_format():
    fields = build_multimedia_fields({"runtime": "1:45:30"})
    f306 = next((f for f in fields if f.tag == "306"), None)
    assert f306 is not None
    assert f306.subfields[0].value == "014530"


def test_multimedia_538_combines_signal_region_audio():
    fields = build_multimedia_fields({"signal": "NTSC", "region": "3", "audio_spec": "돌비 5.1"})
    f538 = next((f for f in fields if f.tag == "538"), None)
    assert f538 is not None
    val = f538.subfields[0].value
    assert "NTSC" in val
    assert "Region 3" in val
    assert "돌비 5.1" in val


def test_multimedia_856_url_when_streaming():
    fields = build_multimedia_fields({"url": "https://stream.example.kr/movie/123"})
    f856 = next((f for f in fields if f.tag == "856"), None)
    assert f856 is not None
    assert f856.subfields[0].value.startswith("https://")


def test_multimedia_008_33_video_returns_v():
    assert derive_008_33("video") == "v"


def test_multimedia_008_33_unknown_returns_space():
    assert derive_008_33("unknown_type") == " "


def test_multimedia_media_type_codes_required_keys():
    for key in ("video", "motion_picture", "slide", "photo", "graphic"):
        assert key in MEDIA_TYPE_CODES


# ── 학위논문 (thesis) ──────────────────────────────────────────


def test_thesis_502_master_degree_field():
    fields = build_thesis_fields({"degree": "석사", "institution": "서울대학교"})
    f502 = next((f for f in fields if f.tag == "502"), None)
    assert f502 is not None
    assert any(sf.value == "석사" for sf in f502.subfields if sf.code == "b")


def test_thesis_502_includes_department_and_year():
    fields = build_thesis_fields(
        {"degree": "박사", "institution": "서울대학교", "department": "교육학과", "year": 2026}
    )
    f502 = next((f for f in fields if f.tag == "502"), None)
    assert f502 is not None
    codes = {sf.code: sf.value for sf in f502.subfields}
    assert codes.get("d") == "교육학과"
    assert codes.get("g") == "2026"


def test_thesis_504_bibliography_when_present():
    fields = build_thesis_fields({"bibliography": "참고문헌: p. 200-210"})
    f504 = next((f for f in fields if f.tag == "504"), None)
    assert f504 is not None
    assert "200-210" in f504.subfields[0].value


def test_thesis_700_advisor_with_role():
    fields = build_thesis_fields({"advisor": "김지도"})
    f700 = next((f for f in fields if f.tag == "700"), None)
    assert f700 is not None
    codes = {sf.code: sf.value for sf in f700.subfields}
    assert codes.get("a") == "김지도"
    assert codes.get("e") == "지도"


def test_thesis_856_url_riss():
    fields = build_thesis_fields({"url": "https://www.riss.kr/link?id=T12345"})
    f856 = next((f for f in fields if f.tag == "856"), None)
    assert f856 is not None
    assert "riss" in f856.subfields[0].value


def test_format_502_text_full_korean():
    txt = format_502_text(
        {
            "degree": "석사",
            "institution": "서울대학교",
            "department": "교육학과",
            "year": 2026,
        }
    )
    assert txt == "학위논문(석사)--서울대학교 교육학과, 2026"


def test_format_502_text_minimal():
    txt = format_502_text({})
    assert txt == "학위논문"
