"""588 provenance + 결정성 모듈 테스트 (Part 92·94)."""

from __future__ import annotations


class TestProvenance588:
    def test_render_588_subfield_includes_essentials(self):
        from kormarc_auto.kormarc.provenance import ProvenanceStamp, render_588_subfield

        stamp = ProvenanceStamp(
            record_isbn="9788937437076",
            sources_used=["seoji", "data4library"],
        )
        text = render_588_subfield(stamp)
        assert "kormarc-auto" in text
        assert "seoji" in text
        assert "data4library" in text
        assert "claude-sonnet-4-6" in text
        assert "사서 검수" in text

    def test_stamp_to_kormarc_field(self):
        from kormarc_auto.kormarc.provenance import (
            ProvenanceStamp,
            stamp_to_kormarc_field,
        )

        stamp = ProvenanceStamp(record_isbn="9788937437076")
        field = stamp_to_kormarc_field(stamp)
        assert field["tag"] == "588"
        assert any(sf["code"] == "a" for sf in field["subfields"])
        assert any(sf["code"] == "5" for sf in field["subfields"])

    def test_librarian_reviewed_changes_text(self):
        from kormarc_auto.kormarc.provenance import ProvenanceStamp, render_588_subfield

        stamp_review = ProvenanceStamp(record_isbn="X", librarian_reviewed=True)
        stamp_pending = ProvenanceStamp(record_isbn="X", librarian_reviewed=False)
        assert "검수 완료" in render_588_subfield(stamp_review)
        assert "검수 필수" in render_588_subfield(stamp_pending)


class TestDeterminism:
    def test_deterministic_params(self):
        from kormarc_auto.kormarc.provenance import deterministic_anthropic_params

        params = deterministic_anthropic_params()
        assert params["temperature"] == 0.0
        assert params["top_p"] == 1.0

    def test_record_hash_stable(self):
        from kormarc_auto.kormarc.provenance import compute_record_hash

        data = {"isbn": "9788937437076", "title": "어린왕자"}
        h1 = compute_record_hash(data)
        h2 = compute_record_hash(data)
        assert h1 == h2  # 결정성

    def test_record_hash_changes_on_field_change(self):
        from kormarc_auto.kormarc.provenance import compute_record_hash

        data1 = {"isbn": "X", "title": "원본"}
        data2 = {"isbn": "X", "title": "변경"}
        assert compute_record_hash(data1) != compute_record_hash(data2)

    def test_visible_diff_identical(self):
        from kormarc_auto.kormarc.provenance import visible_diff_summary

        data = {"isbn": "X", "title": "동일"}
        diff = visible_diff_summary(data, data)
        assert diff["is_identical"] is True
        assert diff["changes_count"] == 0

    def test_visible_diff_detects_change(self):
        from kormarc_auto.kormarc.provenance import visible_diff_summary

        old = {"isbn": "X", "title": "원본", "kdc": "813"}
        new = {"isbn": "X", "title": "변경", "kdc": "813"}
        diff = visible_diff_summary(old, new)
        assert diff["is_identical"] is False
        assert diff["changes_count"] == 1
        assert diff["changes"][0]["field"] == "title"


class TestRecordAuditLog:
    def test_add_field_event_builds_hash_chain(self):
        from kormarc_auto.kormarc.provenance import (
            FieldProvenance,
            RecordAuditLog,
        )

        log = RecordAuditLog(record_isbn="9788937437076")
        log.add_field_event(
            FieldProvenance(field_tag="245", source="seoji", librarian_action="accepted")
        )
        log.add_field_event(
            FieldProvenance(field_tag="650", source="ai_inferred", librarian_action="edited")
        )
        assert len(log.audit_hash_chain) == 2
        assert log.audit_hash_chain[0] != log.audit_hash_chain[1]  # 체인 갱신

    def test_to_dict_serializable(self):
        from kormarc_auto.kormarc.provenance import (
            FieldProvenance,
            RecordAuditLog,
        )

        log = RecordAuditLog(record_isbn="X", librarian_id="lib_001")
        log.add_field_event(FieldProvenance(field_tag="245", source="seoji"))
        d = log.to_dict()
        assert d["record_isbn"] == "X"
        assert d["librarian_id"] == "lib_001"
        assert d["field_count"] == 1
        assert d["audit_chain_head"] is not None
