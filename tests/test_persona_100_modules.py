"""페르소나 100점 도달 4 신규 모듈 테스트 (Part 91)."""

from __future__ import annotations

# ============== 페르소나 04 (대학 분관) 100점 ==============


class TestLcshMapper:
    def test_extract_lcsh_humanities(self):
        from kormarc_auto.classification.lcsh_mapper import extract_lcsh_from_text

        result = extract_lcsh_from_text("한국문학과 역사 연구")
        assert any(m.lcsh_id == "sh85072898" for m in result)  # Korean literature
        assert any(m.lcsh_id == "sh85061212" for m in result)  # History

    def test_extract_lcsh_english(self):
        from kormarc_auto.classification.lcsh_mapper import extract_lcsh_from_text

        result = extract_lcsh_from_text("Introduction to philosophy and mathematics")
        assert any("Philosophy" in m.lcsh_term for m in result)
        assert any("Mathematics" in m.lcsh_term for m in result)

    def test_to_kormarc_650_with_lc_uri(self):
        from kormarc_auto.classification.lcsh_mapper import (
            LcshMatch,
            to_kormarc_650_subfields,
        )

        match = LcshMatch(keyword="역사", lcsh_term="History", lcsh_id="sh85061212")
        sub = to_kormarc_650_subfields(match)
        assert {"code": "a", "value": "History"} in sub
        assert {"code": "2", "value": "lcsh"} in sub
        assert any(s["code"] == "0" and "id.loc.gov" in s["value"] for s in sub)

    def test_add_lcsh_to_book_data_skip_when_no_match(self):
        from kormarc_auto.classification.lcsh_mapper import add_lcsh_to_book_data

        data = {"title": "12345 ABC"}
        result = add_lcsh_to_book_data(data)
        assert "lcsh_subjects" not in result


# ============== Alma MARCXML ==============


class TestAlmaXmlWriter:
    def test_record_to_alma_marcxml_basic(self):
        from pymarc import Field, Indicators, Record, Subfield

        from kormarc_auto.output.alma_xml_writer import record_to_alma_marcxml

        record = Record(force_utf8=True)
        record.add_field(Field(tag="008", data="220101s2026    ulk           kor"))
        record.add_field(
            Field(
                tag="245",
                indicators=Indicators("0", "0"),
                subfields=[Subfield(code="a", value="테스트 도서")],
            )
        )

        xml = record_to_alma_marcxml(record, library_code="MED01", holdings_location="MED")
        assert "<record" in xml
        assert "테스트 도서" in xml
        assert "MED01" in xml
        assert "MED" in xml

    def test_alma_xml_includes_holdings_852(self):
        from pymarc import Record

        from kormarc_auto.output.alma_xml_writer import record_to_alma_marcxml

        record = Record(force_utf8=True)
        xml = record_to_alma_marcxml(record, item_call_number="813.6/한31ㅈ")
        assert 'tag="852"' in xml
        assert "813.6/한31ㅈ" in xml

    def test_alma_holdings_locations_complete(self):
        from kormarc_auto.output.alma_xml_writer import ALMA_HOLDINGS_LOCATIONS

        # 의학분관 페르소나 04 핵심
        assert "MED" in ALMA_HOLDINGS_LOCATIONS
        assert "의학분관" in ALMA_HOLDINGS_LOCATIONS["MED"]


# ============== 페르소나 03 (P15) 100점 ==============


class TestSyncApi:
    def test_detect_conflict_no_existing(self):
        from kormarc_auto.mobile.sync_api import detect_conflict

        is_conflict, _ = detect_conflict({"isbn": "X"}, None)
        assert is_conflict is False

    def test_detect_conflict_same_isbn_different_title(self):
        from kormarc_auto.mobile.sync_api import detect_conflict

        new = {"isbn": "9788937437076", "title": "신규 제목"}
        existing = {"isbn": "9788937437076", "title": "기존 제목"}
        is_conflict, reason = detect_conflict(new, existing)
        assert is_conflict is True
        assert reason and "title" in reason

    def test_resolve_conflict_server_wins(self):
        from kormarc_auto.mobile.sync_api import resolve_conflict

        new = {"isbn": "X", "title": "신규"}
        existing = {"isbn": "X", "title": "기존"}
        result = resolve_conflict(new, existing, "server_wins")
        assert result["title"] == "기존"

    def test_resolve_conflict_client_wins(self):
        from kormarc_auto.mobile.sync_api import resolve_conflict

        new = {"isbn": "X", "title": "신규"}
        existing = {"isbn": "X", "title": "기존"}
        result = resolve_conflict(new, existing, "client_wins")
        assert result["title"] == "신규"

    def test_process_push_item_accepted(self):
        from kormarc_auto.mobile.sync_api import SyncPushRequest, process_push_item

        req = SyncPushRequest(
            tenant_id="LIB001",
            client_item_id=1,
            payload_type="isbn",
            payload={"isbn": "9788937437076"},
            client_timestamp="2026-05-03T00:00:00Z",
        )
        resp = process_push_item(req, existing_record=None)
        assert resp.status == "accepted"

    def test_process_push_item_duplicate(self):
        from kormarc_auto.mobile.sync_api import SyncPushRequest, process_push_item

        req = SyncPushRequest(
            tenant_id="LIB001",
            client_item_id=1,
            payload_type="isbn",
            payload={"isbn": "9788937437076"},
            client_timestamp="2026-05-03T00:00:00Z",
        )
        existing = {"isbn": "9788937437076", "id": "rec_42"}
        resp = process_push_item(req, existing_record=existing)
        assert resp.status == "duplicate"
        assert resp.server_record_id == "rec_42"

    def test_aggregate_batch_result(self):
        from kormarc_auto.mobile.sync_api import (
            SyncPushResponse,
            aggregate_batch_result,
        )

        items = [
            SyncPushResponse(client_item_id=1, status="accepted"),
            SyncPushResponse(client_item_id=2, status="accepted"),
            SyncPushResponse(client_item_id=3, status="duplicate"),
            SyncPushResponse(client_item_id=4, status="conflict"),
        ]
        result = aggregate_batch_result(items)
        assert result.accepted == 2
        assert result.duplicates == 1
        assert result.conflicts == 1
        assert result.sync_completed_at != ""


# ============== 페르소나 01·02 100점 ==============


class TestDecisionMakerPdf:
    def test_calculate_roi_basic(self):
        from kormarc_auto.output.decision_maker_pdf import (
            DecisionMakerProfile,
            calculate_roi,
        )

        profile = DecisionMakerProfile(
            library_name="테스트 도서관",
            librarian_name="홍길동",
            decision_maker_role="행정실장",
            annual_book_count=1000,
        )
        roi = calculate_roi(profile)
        # 1000권 × 6.5분 = 6,500분 = 약 108시간
        assert 100 <= roi.annual_hours_saved <= 110
        assert roi.annual_savings_won > 0
        assert roi.payback_months > 0
        assert roi.roi_multiple > 0

    def test_render_decision_pdf_html_includes_essentials(self):
        from kormarc_auto.output.decision_maker_pdf import (
            DecisionMakerProfile,
            render_decision_pdf_html,
        )

        profile = DecisionMakerProfile(
            library_name="○○중학교 도서관",
            librarian_name="김지원",
            decision_maker_role="행정실장",
            annual_book_count=500,
        )
        html = render_decision_pdf_html(profile)
        assert "○○중학교 도서관" in html
        assert "행정실장" in html
        assert "ROI" in html or "절감" in html
        assert "PIPA" in html
        assert "PILOT" in html
        # A4 결재 양식
        assert "@page" in html
        assert "기안" in html


# ============== 페르소나 04 추가 (DDC + LCSH 통합) ==============


class TestDdcLcshMeshIntegration:
    def test_book_data_supports_3_classification_systems(self):
        """대학도서관 = KDC + DDC + LCSH/MeSH 동시 지원 (페르소나 04 100점)."""
        from kormarc_auto.classification.ddc_classifier import add_ddc_to_book_data
        from kormarc_auto.classification.lcsh_mapper import add_lcsh_to_book_data
        from kormarc_auto.classification.mesh_mapper import add_mesh_to_book_data

        # 의학 인문 혼합 (대학원 의료윤리 책)
        data = {
            "title": "의료윤리와 철학",
            "summary": "의학 전공자를 위한 윤리학 입문",
            "kdc": "510",
        }

        # 3 단계 적용
        data = add_ddc_to_book_data(data)
        data = add_mesh_to_book_data(data)
        data = add_lcsh_to_book_data(data)

        # KDC + DDC 동시
        assert data.get("kdc") == "510"
        assert data.get("ddc", "").startswith("6")  # KDC 5 → DDC 6

        # MeSH (의학) + LCSH (윤리·철학) 동시
        assert "mesh_subjects" in data or "lcsh_subjects" in data
