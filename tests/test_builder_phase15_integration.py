"""Phase 1.5 자료유형 모듈 → builder 통합 테스트.

build_kormarc_record()가 자료유형 자동 감지 + 해당 모듈 build_*_fields() 자동 호출.
"""

from __future__ import annotations

from kormarc_auto.kormarc.builder import build_kormarc_record
from kormarc_auto.kormarc.material_type import detect_material_type


def _tags(record) -> list[str]:
    return [f.tag for f in record.get_fields()]


# ── ebook 통합 ──────────────────────────────────────────────────


def test_builder_integrates_ebook_when_format_pdf():
    record = build_kormarc_record(
        {
            "isbn": "9788912345678",
            "title": "전자책 테스트",
            "format": "PDF",
            "url": "https://lib.example.kr/book.pdf",
        },
        auto_validate=False,
    )
    f538 = next((f for f in record.get_fields("538")), None)
    f856 = next((f for f in record.get_fields("856")), None)
    assert f538 is not None
    assert "PDF" in f538.subfields[0].value
    assert f856 is not None
    assert f856.subfields[0].value.endswith(".pdf")


def test_builder_integrates_audiobook_when_narrator_present():
    record = build_kormarc_record(
        {
            "isbn": "9788912345679",
            "title": "오디오북 테스트",
            "narrator": "김연아",
            "format": "MP3",
            "duration": "8시간",
        },
        auto_validate=False,
    )
    f511 = next((f for f in record.get_fields("511")), None)
    f538 = next((f for f in record.get_fields("538")), None)
    assert f511 is not None
    assert "김연아" in f511.subfields[0].value
    assert f538 is not None
    assert "MP3" in f538.subfields[0].value


def test_builder_integrates_multimedia_when_runtime_present():
    record = build_kormarc_record(
        {
            "isbn": "9788912345680",
            "title": "DVD 테스트",
            "format": "DVD",
            "runtime": 120,
        },
        auto_validate=False,
    )
    f306 = next((f for f in record.get_fields("306")), None)
    assert f306 is not None
    assert f306.subfields[0].value == "020000"


def test_builder_integrates_ejournal_when_issn_present():
    record = build_kormarc_record(
        {
            "title": "전자저널 테스트",
            "issn": "2234-5678",
            "frequency": "월간",
            "first_issue": "Vol.1 No.1 (2026.01)",
        },
        auto_validate=False,
    )
    f022 = next((f for f in record.get_fields("022")), None)
    f310 = next((f for f in record.get_fields("310")), None)
    assert f022 is not None
    assert f022.subfields[0].value == "2234-5678"
    assert f310 is not None
    assert "월간" in f310.subfields[0].value


def test_builder_integrates_thesis_when_degree_present():
    record = build_kormarc_record(
        {
            "isbn": "9788912345681",
            "title": "학위논문 테스트",
            "degree": "박사",
            "institution": "서울대학교",
            "department": "교육학과",
            "year": 2026,
            "advisor": "김지도",
        },
        auto_validate=False,
    )
    f502 = next((f for f in record.get_fields("502")), None)
    f700_advisor = [
        f
        for f in record.get_fields("700")
        if any(sf.code == "e" and sf.value == "지도" for sf in f.subfields)
    ]
    assert f502 is not None
    codes = {sf.code: sf.value for sf in f502.subfields}
    assert codes.get("b") == "박사"
    assert codes.get("c") == "서울대학교"
    assert len(f700_advisor) == 1


def test_builder_default_book_unaffected_by_phase15():
    record = build_kormarc_record(
        {"isbn": "9788912345682", "title": "일반 단행본", "author": "한강"},
        auto_validate=False,
    )
    tags = _tags(record)
    # Phase 1.5 특화 태그는 없어야 함
    assert "511" not in tags  # 낭독자
    assert "306" not in tags  # 재생시간
    assert "502" not in tags  # 학위논문
    assert "022" not in tags  # ISSN
    # 핵심 단행본 태그는 있어야 함
    assert "245" in tags
    assert "020" in tags


# ── detect_material_type 신규 분기 ──────────────────────────────


def test_detect_ejournal_when_issn():
    assert detect_material_type({"title": "온라인", "issn": "2234-5678"}) == "ejournal"


def test_detect_multimedia_when_runtime():
    assert detect_material_type({"title": "x", "runtime": 90}) == "multimedia"


def test_detect_rare_book_when_keyword():
    assert detect_material_type({"title": "조선왕조 고서"}) == "rare_book"


def test_detect_thesis_priority_over_others():
    assert detect_material_type({"title": "박사학위 논문"}) == "thesis"
