"""Cycle 9 P13 — audit JSONL store 회귀 테스트."""

from __future__ import annotations

import pytest

from kormarc_auto.audit import (
    AuditEvent,
    append_event,
    delete_record,
    get_record_events,
    iter_all_events,
)
from kormarc_auto.audit.store import is_deleted, resolve_audit_dir


@pytest.fixture
def isolated_audit_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_AUDIT_DIR", str(tmp_path / "audit"))
    yield tmp_path / "audit"


def test_resolve_audit_dir_env_override(isolated_audit_dir):
    assert resolve_audit_dir() == isolated_audit_dir


def test_resolve_audit_dir_default(monkeypatch):
    monkeypatch.delenv("KORMARC_AUDIT_DIR", raising=False)
    p = resolve_audit_dir()
    assert p.name == "audit"
    assert p.parent.name == ".kormarc-auto"


def test_append_event_creates_jsonl(isolated_audit_dir):
    e = AuditEvent.now(record_id="9788937437076", action="create", user_id="사서 A")
    target = append_event(e)
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "9788937437076" in content
    assert content.endswith("\n")


def test_append_event_is_append_only(isolated_audit_dir):
    e1 = AuditEvent.now(record_id="X", action="create")
    e2 = AuditEvent.now(record_id="X", action="edit", field_tag="245")
    append_event(e1)
    append_event(e2)
    events = get_record_events("X")
    assert len(events) == 2
    assert events[0].action == "create"
    assert events[1].action == "edit"


def test_get_record_events_filters_by_id(isolated_audit_dir):
    append_event(AuditEvent.now(record_id="A", action="create"))
    append_event(AuditEvent.now(record_id="B", action="create"))
    append_event(AuditEvent.now(record_id="A", action="accept"))
    events_a = get_record_events("A")
    assert len(events_a) == 2
    assert all(e.record_id == "A" for e in events_a)


def test_iter_all_events_yields_all(isolated_audit_dir):
    append_event(AuditEvent.now(record_id="X", action="create"))
    append_event(AuditEvent.now(record_id="Y", action="create"))
    all_events = list(iter_all_events())
    assert len(all_events) == 2


def test_delete_record_adds_tombstone(isolated_audit_dir):
    append_event(AuditEvent.now(record_id="X", action="create"))
    tombstone = delete_record("X", user_id="사서 A")
    assert tombstone.action == "delete_request"
    assert is_deleted("X") is True
    # 원본 line 보존 (audit trail)
    events = get_record_events("X")
    assert len(events) == 2
    actions = [e.action for e in events]
    assert "create" in actions and "delete_request" in actions


def test_event_jsonl_round_trip(isolated_audit_dir):
    import json

    e = AuditEvent.now(
        record_id="9788937437076",
        action="regenerate",
        user_id="사서 B",
        model_string="claude-sonnet-4-6",
        input_hash="abc123",
        output_hash="def456",
        note="재생성 테스트",
    )
    line = e.to_jsonl()
    parsed = json.loads(line)
    assert parsed["record_id"] == "9788937437076"
    assert parsed["model_string"] == "claude-sonnet-4-6"
    assert parsed["note"] == "재생성 테스트"


def test_action_required_field():
    with pytest.raises(TypeError):
        AuditEvent.now(record_id="X")  # action 필수


def test_timestamp_iso_8601_utc(isolated_audit_dir):
    e = AuditEvent.now(record_id="X", action="create")
    assert e.timestamp.endswith("Z")
    assert "T" in e.timestamp


def test_extra_dict_persisted(isolated_audit_dir):
    e = AuditEvent.now(
        record_id="X", action="create", extra={"library": "PILOT 자관", "session": "abc"}
    )
    append_event(e)
    events = get_record_events("X")
    assert events[0].extra == {"library": "PILOT 자관", "session": "abc"}


def test_month_partition_isolation(isolated_audit_dir, tmp_path):
    """다른 월에 쓴 이벤트 = 다른 파일."""
    e1 = AuditEvent(record_id="X", action="create", timestamp="2026-05-01T00:00:00Z")
    e2 = AuditEvent(record_id="Y", action="create", timestamp="2026-06-01T00:00:00Z")
    append_event(e1)
    append_event(e2)
    months = list((tmp_path / "audit").iterdir())
    month_names = sorted(m.name for m in months if m.is_dir())
    assert month_names == ["2026-05", "2026-06"]
