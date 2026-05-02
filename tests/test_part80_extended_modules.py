"""Part 80 확장 모듈 테스트 (5 신규)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest


def test_interlibrary_5systems_basic():
    from kormarc_auto.interlibrary.interlibrary_5systems import (
        System,
        SYSTEM_DATABASE,
        recommend_system,
        get_info,
    )

    # 5 시스템 모두 등록
    assert len(SYSTEM_DATABASE) == 5
    assert System.CHAEK_BADA in SYSTEM_DATABASE
    assert System.CHAEK_NARAE in SYSTEM_DATABASE

    # 장애인 = 책나래 우선
    rec = recommend_system(is_disabled_user=True)
    assert rec[0] == System.CHAEK_NARAE

    # 은평구민 = 책단비 우선
    rec_e = recommend_system(is_eunpyeong_user=True)
    assert System.CHAEK_DANBI in rec_e[:2]

    # 책바다 = 5,200원
    bada = get_info(System.CHAEK_BADA)
    assert bada.cost_won == 5200

    # 책나래 = 무료
    narae = get_info(System.CHAEK_NARAE)
    assert narae.cost_won == 0


def test_marc_importer_marcxml():
    from kormarc_auto.ingest.marc_importer import import_marcxml

    xml = '''<?xml version="1.0"?>
<collection xmlns="http://www.loc.gov/MARC21/slim">
  <record>
    <leader>00000nam a2200000   4500</leader>
    <controlfield tag="001">12345</controlfield>
    <datafield tag="245" ind1="1" ind2="0">
      <subfield code="a">어린왕자</subfield>
    </datafield>
  </record>
</collection>'''

    records = import_marcxml(xml)
    assert len(records) == 1
    assert records[0]["leader"] == "00000nam a2200000   4500"
    assert any(c["tag"] == "001" for c in records[0]["control_fields"])


def test_marc_importer_mods():
    from kormarc_auto.ingest.marc_importer import import_mods

    mods_xml = '''<?xml version="1.0"?>
<modsCollection xmlns="http://www.loc.gov/mods/v3">
  <mods>
    <titleInfo><title>어린왕자</title></titleInfo>
    <name><namePart>생텍쥐페리</namePart></name>
    <originInfo>
      <publisher>열린책들</publisher>
      <dateIssued>2007</dateIssued>
    </originInfo>
    <identifier type="isbn">9788937437076</identifier>
  </mods>
</modsCollection>'''

    records = import_mods(mods_xml)
    assert len(records) >= 1
    assert records[0].get("title") == "어린왕자"
    assert records[0].get("isbn") == "9788937437076"


def test_new_subject_learner_basic():
    from kormarc_auto.classification.new_subject_learner import (
        detect_new_subject,
        is_new_subject_book,
        NEW_SUBJECTS_KDC,
    )

    # AI 책
    book = {"title": "ChatGPT 활용 입문", "description": "인공지능 LLM 활용"}
    assert is_new_subject_book(book) is True
    recs = detect_new_subject(book)
    assert len(recs) > 0
    assert any(r.kdc_code == "004.7" for r in recs)
    assert all(r.needs_review for r in recs)  # 신주제 = 항상 사서 검토

    # 일반 책
    book_general = {"title": "어린왕자"}
    assert is_new_subject_book(book_general) is False

    # 매핑 확인
    assert "ai" in NEW_SUBJECTS_KDC
    assert "블록체인" in NEW_SUBJECTS_KDC


def test_library_evaluation_report_basic():
    from kormarc_auto.output.library_evaluation_report import (
        LibraryEvaluationData,
        generate_evaluation_report,
    )

    data = LibraryEvaluationData(
        library_name="PILOT 1관",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        total_records_processed=1500,
        avg_processing_minutes=1.0,
        automation_rate=0.95,
        librarian_count=8,
        librarian_satisfaction=8.5,
        error_rate=0.001,
        user_response_count=300,
        incident_count=0,
    )

    report = generate_evaluation_report(data)
    assert "PILOT 1관" in report
    assert "1,500" in report
    assert "도서관 평가 가산점" in report
    assert "감정노동" in report
    assert "서울시 7대 지침" in report


def test_pain_discovery_system_basic(tmp_path: Path):
    from kormarc_auto.intelligence.pain_discovery import (
        Pain,
        ICEScore,
        calculate_ice,
        prioritize,
        PainDiscoverySystem,
    )

    pain = Pain(
        description="KORMARC 입력 부담",
        category="cataloging",
        channel="interview",
        impact_minutes_per_week=480,  # 8h/주
        librarian_count_estimated=5000,
        confidence_count=5,
    )
    score = calculate_ice(pain)
    assert score.impact >= 1
    assert score.confidence == 5
    assert score.total > 0

    # System
    system = PainDiscoverySystem(tmp_path / "pains")
    system.add_pain(pain)
    pain2 = Pain(
        description="감정노동",
        category="emotional_labor",
        channel="academic",
        impact_minutes_per_week=120,
        librarian_count_estimated=10000,
        confidence_count=5,
    )
    system.add_pain(pain2)

    top = system.report_top(n=10)
    assert len(top) == 2
    assert top[0][1].total >= top[1][1].total  # 정렬

    cataloging_pains = system.report_by_category("cataloging")
    assert len(cataloging_pains) == 1
