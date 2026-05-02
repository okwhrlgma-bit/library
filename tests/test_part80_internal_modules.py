"""Part 74·77·80 내부 모듈 통합 테스트."""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import pytest


def test_authority_control_basic():
    from pymarc import Record
    from kormarc_auto.kormarc.authority_control import add_authority_fields, detect_homonym

    record = Record()
    book_data = {
        "author": "홍길동",
        "authors": [
            {"name": "홍길동"},
            {"name": "김철수", "role": "editor"},
        ],
        "corporate_author": "한국문학협회",
    }
    add_authority_fields(book_data, record)
    tags = [f.tag for f in record.fields]
    assert "700" in tags  # 공동저자
    assert "710" in tags  # 단체저자

    # 동명이인
    result = detect_homonym("홍길동", [{"name": "홍길동"}, {"name": "홍길동"}])
    assert result is not None
    assert "동명이인" in result["warning"]


def test_subject_heading_basic():
    from pymarc import Record
    from kormarc_auto.kormarc.subject_heading import add_subject_headings

    record = Record()
    book_data = {"subject_keywords": ["한국문학", "현대소설", "서울"]}
    add_subject_headings(book_data, record)
    tags = [f.tag for f in record.fields]
    assert any(t.startswith("65") or t == "651" for t in tags)


def test_contents_summary_basic():
    from pymarc import Record
    from kormarc_auto.kormarc.contents_summary import add_contents_summary

    record = Record()
    book_data = {
        "contents": "1장 서론\n2장 본론\n3장 결론",
        "summary": "이 책은 도서관 자동화에 대한 연구입니다.",
    }
    add_contents_summary(book_data, record)
    tags = [f.tag for f in record.fields]
    assert "505" in tags
    assert "520" in tags


def test_series_uniform_title_basic():
    from pymarc import Record
    from kormarc_auto.kormarc.series_uniform_title import add_series_fields

    record = Record()
    book_data = {"series": "어린왕자 시리즈", "volume": 3}
    add_series_fields(book_data, record)
    tags = [f.tag for f in record.fields]
    assert "490" in tags
    assert "830" in tags


def test_responsibility_statement_basic():
    from kormarc_auto.kormarc.responsibility_statement import build_responsibility_statement, is_translation

    rs = build_responsibility_statement(
        {"author": "홍길동", "translator": "김철수", "illustrator": "이영희"}
    )
    assert "홍길동" in rs
    assert "김철수" in rs
    assert "옮김" in rs
    assert "그림" in rs

    assert is_translation({"translator": "김철수"}) is True
    assert is_translation({"author": "홍길동"}) is False


def test_inventory_check_basic(tmp_path: Path):
    from kormarc_auto.inventory.inventory_check import (
        InventoryItem,
        InventorySession,
        export_session_report,
    )

    session = InventorySession(sasagwan="테스트관")
    session.items = [
        InventoryItem(isbn="9788937437076", registration_no="EQ20260001", expected_location="811.7"),
        InventoryItem(isbn="9791164060238", registration_no="EQ20260002", expected_location="811.6"),
    ]
    assert session.mark_found("9788937437076") is True
    summary = session.summary()
    assert summary["total"] == 2
    assert summary["found"] == 1
    assert summary["missing"] == 1

    report_path = export_session_report(session, tmp_path / "report.md")
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "테스트관" in text
    assert "장서점검" in text


def test_personal_stats_dashboard_basic():
    from kormarc_auto.ui.personal_stats_dashboard import LibrarianStats, generate_evaluation_report

    stats = LibrarianStats(
        librarian_name="홍길동",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 3, 31),
        total_records=300,
        avg_minutes_per_record=1.0,
        automation_rate=0.95,
    )
    assert stats.time_saved_hours == 35.0  # (8-1)*300/60
    assert stats.equivalent_books == 262

    report = generate_evaluation_report(stats)
    assert "홍길동" in report
    assert "300" in report
    assert "사서 평가 가산점" in report


def test_library_knowledge_base_basic(tmp_path: Path):
    from kormarc_auto.intelligence.library_knowledge_base import (
        LibraryDecision,
        LibraryKnowledgeBase,
    )

    kb = LibraryKnowledgeBase(tmp_path / "kb")
    kb.learn(
        LibraryDecision(
            sasagwan="테스트관",
            decision_type="prefix",
            context="EQ vs CQ 결정",
            decision="EQ=일반·CQ=아동",
            reason="자관 정책",
        )
    )
    results = kb.query("테스트관", "EQ", limit=5)
    assert len(results) == 1
    assert "EQ" in results[0].decision

    handover = kb.export_handover("테스트관")
    assert "테스트관" in handover
    assert "EQ" in handover


def test_incident_logger_basic(tmp_path: Path):
    from kormarc_auto.safety.incident_logger import (
        Incident,
        IncidentLogger,
        detect_abuse,
    )

    logger = IncidentLogger(tmp_path / "incidents")
    h = logger.log(
        Incident(
            sasagwan="테스트관",
            librarian_name="홍길동",
            incident_type="verbal_abuse",
            description="폭언 발생",
            severity=3,
        )
    )
    assert len(h) == 64  # SHA-256 hex

    summary = logger.quarterly_summary("테스트관", datetime.now().year, ((datetime.now().month - 1) // 3) + 1)
    assert summary["total"] == 1
    assert summary["by_type"]["verbal_abuse"] == 1

    # 폭언 감지
    assert detect_abuse("안녕하세요") is None
    abuse = detect_abuse("씨발 빨리 해")
    assert abuse is not None
    assert abuse["type"] == "verbal_abuse"


def test_librarian_agent_basic(tmp_path: Path):
    from kormarc_auto.intelligence.librarian_agent import LibrarianAgent

    agent = LibrarianAgent(
        sasagwan="테스트관",
        kb_dir=tmp_path / "kb",
        incident_dir=tmp_path / "incidents",
    )
    # 표준 질문 매칭
    resp = agent.ask("008 필드 자리수가 몇이야?")
    assert "40자리" in resp.answer

    # 이용자 일반 응대
    resp_user = agent.respond_to_patron("운영시간이 어떻게 돼요?")
    assert "운영시간" in resp_user.answer

    # 폭언 감지
    resp_abuse = agent.respond_to_patron("씨발 빨리 좀 해")
    assert resp_abuse.incident_detected is True
    assert resp_abuse.needs_librarian is True


def test_accessibility_books_basic():
    from kormarc_auto.kormarc.accessibility_books import build_accessibility_fields

    book_data = {"isbn": "9788937437076", "title": "어린왕자"}

    for atype in ["braille", "large_print", "tactile", "daisy", "sign_language"]:
        fields = build_accessibility_fields(book_data, accessibility_type=atype)
        assert len(fields) > 0
        tags = [f.tag for f in fields]
        # 공통: 538 (자료유형 명시)
        assert "538" in tags


def test_export_formats_basic():
    from kormarc_auto.output.export_formats import (
        export_marcxml,
        export_mods,
        export_jsonld,
        export_oai_pmh,
    )

    record_data = {
        "title": "어린왕자",
        "author": "앙투안 드 생텍쥐페리",
        "publisher": "열린책들",
        "year": 2007,
        "isbn": "9788937437076",
        "kdc": "863.2",
    }

    marcxml = export_marcxml(record_data)
    assert "<record" in marcxml

    mods = export_mods(record_data)
    assert "어린왕자" in mods
    assert "<mods" in mods

    jsonld = export_jsonld(record_data)
    data = json.loads(jsonld)
    assert data["@type"] == "Book"
    assert data["name"] == "어린왕자"

    oai = export_oai_pmh(record_data)
    assert "oai_dc" in oai


def test_label_printer_basic():
    from kormarc_auto.output.label_printer import (
        render_label_html,
        render_label_batch_html,
        LABEL_DIMENSIONS_MM,
    )

    html = render_label_html(
        call_number="시문학811.7/ㅇ676ㅁ",
        barcode_value="EQ20260001",
        library_name="○○도서관",
    )
    assert "○○도서관" in html
    assert "시문학811.7" in html
    assert "EQ20260001" in html

    # 일괄
    items = [
        {"call_number": "811/ㅇ001", "barcode_value": "EQ001"},
        {"call_number": "812/ㅇ002", "barcode_value": "EQ002"},
    ]
    batch = render_label_batch_html(items, library_name="○○도서관")
    assert "EQ001" in batch
    assert "EQ002" in batch
    assert "(2건)" in batch

    assert "avery_l7160" in LABEL_DIMENSIONS_MM
