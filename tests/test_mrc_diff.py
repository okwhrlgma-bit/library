"""Cycle 14A P16 — visible diff 회귀."""

from __future__ import annotations

from kormarc_auto.diff import (
    DiffEntry,
    diff_records,
    format_diff_text,
    is_empty_diff,
)


def _rec(fields: list[dict]) -> dict:
    return {"fields": fields}


class TestEmptyDiff:
    """결정론 정합 (Cycle 8 ADR 0028)."""

    def test_identical_records_empty_diff(self):
        rec = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "어린 왕자"}]}])
        d = diff_records(rec, rec)
        assert is_empty_diff(d) is True
        assert d.total_changes == 0

    def test_empty_diff_text(self):
        rec = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "X"}]}])
        d = diff_records(rec, rec)
        assert "변경 사항 없음" in format_diff_text(d)


class TestAddedField:
    def test_added_field_detected(self):
        before = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "X"}]}])
        after = _rec(
            [
                {"tag": "245", "subfields": [{"code": "a", "value": "X"}]},
                {"tag": "650", "subfields": [{"code": "a", "value": "한국문학"}]},
            ]
        )
        d = diff_records(before, after)
        assert d.added_count == 1
        assert d.entries[0].diff_type == "added"
        assert d.entries[0].field_tag == "650"


class TestRemovedField:
    def test_removed_field_detected(self):
        before = _rec(
            [
                {"tag": "245", "subfields": [{"code": "a", "value": "X"}]},
                {"tag": "490", "subfields": [{"code": "a", "value": "총서"}]},
            ]
        )
        after = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "X"}]}])
        d = diff_records(before, after)
        assert d.removed_count == 1
        assert d.entries[0].diff_type == "removed"


class TestChangedField:
    def test_changed_subfield_detected(self):
        before = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "옛 표제"}]}])
        after = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "새 표제"}]}])
        d = diff_records(before, after)
        assert d.changed_count == 1
        e = d.entries[0]
        assert e.before == "옛 표제"
        assert e.after == "새 표제"


class TestControlField:
    def test_control_field_008_diff(self):
        before = _rec([{"tag": "008", "data": "260101s2026    ulk           kor d"}])
        after = _rec([{"tag": "008", "data": "260201s2026    ulk           kor d"}])
        d = diff_records(before, after)
        assert d.total_changes == 1


class TestFormat:
    def test_format_includes_change_count(self):
        before = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "X"}]}])
        after = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "Y"}]}])
        text = format_diff_text(diff_records(before, after))
        assert "1건" in text
        assert "X" in text and "Y" in text

    def test_diff_entry_to_text_added(self):
        e = DiffEntry(diff_type="added", field_tag="650", subfield_code="a", after="문학")
        text = e.to_text()
        assert text.startswith("+")
        assert "650$a" in text
        assert "문학" in text

    def test_diff_entry_to_text_removed(self):
        e = DiffEntry(diff_type="removed", field_tag="490", subfield_code="a", before="총서")
        text = e.to_text()
        assert text.startswith("-")

    def test_diff_entry_to_text_changed(self):
        e = DiffEntry(
            diff_type="changed",
            field_tag="245",
            subfield_code="a",
            before="옛",
            after="새",
        )
        text = e.to_text()
        assert text.startswith("~")
        assert "→" in text


class TestApiDict:
    def test_api_dict_complete(self):
        before = _rec([{"tag": "245", "subfields": [{"code": "a", "value": "X"}]}])
        after = _rec(
            [
                {"tag": "245", "subfields": [{"code": "a", "value": "Y"}]},
                {"tag": "650", "subfields": [{"code": "a", "value": "Z"}]},
            ]
        )
        api = diff_records(before, after).to_api_dict()
        assert api["total_changes"] == 2
        assert api["added"] == 1
        assert api["changed"] == 1
        assert api["is_empty"] is False
        assert len(api["entries"]) == 2


class TestPymarcSupport:
    def test_pymarc_record_supported(self):
        from pymarc import Field, Record, Subfield

        rec1 = Record()
        rec1.add_field(
            Field(
                tag="245", indicators=[" ", " "], subfields=[Subfield(code="a", value="어린 왕자")]
            )
        )
        rec2 = Record()
        rec2.add_field(
            Field(
                tag="245", indicators=[" ", " "], subfields=[Subfield(code="a", value="어린 왕자")]
            )
        )
        d = diff_records(rec1, rec2)
        assert is_empty_diff(d) is True
