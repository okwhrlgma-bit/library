"""Cycle 10A P14 — field_status 회귀."""

from __future__ import annotations

from kormarc_auto.kormarc.field_status import (
    FieldState,
    RecordReviewState,
    can_transition,
)


class TestTransitions:
    def test_idempotent_same_status(self):
        assert can_transition("accepted", "accepted") is True

    def test_ai_to_accept(self):
        assert can_transition("ai_generated", "accepted") is True

    def test_ai_to_reject(self):
        assert can_transition("ai_generated", "rejected") is True

    def test_ai_to_edit(self):
        assert can_transition("ai_generated", "edited") is True

    def test_pending_to_any(self):
        for tgt in ("ai_generated", "accepted", "rejected", "edited"):
            assert can_transition("pending", tgt) is True

    def test_rejected_can_regenerate_back_to_ai(self):
        assert can_transition("rejected", "ai_generated") is True

    def test_invalid_transition_pending_to_pending_idempotent(self):
        assert can_transition("pending", "pending") is True


class TestFieldState:
    def test_default_status_ai_generated(self):
        fs = FieldState(tag="245", value="어린 왕자")
        assert fs.status == "ai_generated"
        assert fs.confidence == "검토 필요"

    def test_transition_ai_to_accepted(self):
        fs = FieldState(tag="245", value="어린 왕자")
        assert fs.transition("accepted") is True
        assert fs.status == "accepted"

    def test_transition_with_new_value(self):
        fs = FieldState(tag="245", value="어린 왕자")
        assert fs.transition("edited", new_value="어린 왕자 (개정판)") is True
        assert fs.value == "어린 왕자 (개정판)"
        assert fs.status == "edited"

    def test_to_api_dict_includes_ui_hint(self):
        fs = FieldState(tag="245", value="x")
        d = fs.to_api_dict()
        assert "ui_hint" in d
        assert d["ui_hint"]["icon"] == "ⓘ"

    def test_ui_hint_changes_on_accept(self):
        fs = FieldState(tag="245", value="x")
        fs.transition("accepted")
        assert fs.to_api_dict()["ui_hint"]["icon"] == "✓"

    def test_confidence_levels_3_categories(self):
        # 헌법 §2 강화·raw % X·3 카테고리만
        for c in ("확실", "검토 필요", "불확실"):
            fs = FieldState(tag="245", value="x", confidence=c)
            assert fs.confidence == c


class TestRecordReviewState:
    def _make_record(self) -> RecordReviewState:
        rrs = RecordReviewState(record_id="9788937437076")
        for tag, val in [("245", "어린 왕자"), ("100", "생텍쥐페리"), ("260", "민음사")]:
            rrs.add_field(FieldState(tag=tag, value=val))
        return rrs

    def test_progress_counts(self):
        rrs = self._make_record()
        p = rrs.progress()
        assert p["total"] == 3
        assert p["ai_generated"] == 3
        assert p["reviewed"] == 0

    def test_fully_reviewed_after_all_accept(self):
        rrs = self._make_record()
        for fs in rrs.fields:
            fs.transition("accepted")
        assert rrs.is_fully_reviewed() is True
        p = rrs.progress()
        assert p["accepted"] == 3
        assert p["reviewed"] == 3

    def test_partial_review(self):
        rrs = self._make_record()
        rrs.fields[0].transition("accepted")
        assert rrs.is_fully_reviewed() is False
        assert rrs.progress()["reviewed"] == 1

    def test_reject_all_escape_hatch(self):
        rrs = self._make_record()
        changed = rrs.reject_all()
        assert changed == 3
        for fs in rrs.fields:
            assert fs.status == "rejected"

    def test_to_api_dict_full(self):
        rrs = self._make_record()
        d = rrs.to_api_dict()
        assert d["record_id"] == "9788937437076"
        assert len(d["fields"]) == 3
        assert "progress" in d
        assert d["fully_reviewed"] is False
