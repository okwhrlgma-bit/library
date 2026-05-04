"""갈래 A Cycle 9 (P13·T4-2) — Persistent audit log.

PIPA §35 (열람권) + §36 (파기권) 정합·인공지능 기본법 §31 (AI 출처 표시) 정합.
"""

from kormarc_auto.audit.store import (
    AuditEvent,
    append_event,
    delete_record,
    get_record_events,
    iter_all_events,
    resolve_audit_dir,
)

__all__ = [
    "AuditEvent",
    "append_event",
    "delete_record",
    "get_record_events",
    "iter_all_events",
    "resolve_audit_dir",
]
