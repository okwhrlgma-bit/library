"""갈래 A Cycle 9 (P13) — JSONL append-only audit store.

PIPA §35 (정보주체 열람권) + §36 (파기 요청권) 정합:
- 위치: ~/.kormarc-auto/audit/{YYYY-MM}/records.jsonl
- append-only (덮어쓰기 차단)
- 파기 요청 시 = soft delete (tombstone event 추가·원본 line은 보존하지 않음)
- 보관: 7년 (PIPA + 도서관 거래 보관 통상)

헌법 §10 추가 정합 (Cycle 9 신설): "AI 생성 사실은 KORMARC 588 + audit log에 명시한다"

기존 kormarc/provenance.py RecordAuditLog (in-memory) ≠ 본 모듈 (persistent).
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


def resolve_audit_dir() -> Path:
    """audit 루트 = $KORMARC_AUDIT_DIR 또는 ~/.kormarc-auto/audit/"""
    env = os.getenv("KORMARC_AUDIT_DIR")
    if env:
        return Path(env)
    return Path.home() / ".kormarc-auto" / "audit"


AuditAction = Literal["create", "regenerate", "edit", "accept", "reject", "delete_request"]


@dataclass(frozen=True)
class AuditEvent:
    """Per-record audit event (append-only·JSONL line 1건)."""

    record_id: str  # ISBN-13 또는 자관 등록번호 hash
    action: AuditAction
    timestamp: str  # ISO 8601 UTC
    user_id: str | None = None
    model_string: str | None = None
    input_hash: str | None = None
    output_hash: str | None = None
    field_tag: str | None = None  # PATCH 시 어떤 필드 (245·650 등)
    note: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def now(cls, **kwargs: Any) -> AuditEvent:
        kwargs.setdefault("timestamp", datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"))
        return cls(**kwargs)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True) + "\n"


def _month_file(when: str | None = None) -> Path:
    """월별 파티션 = audit/{YYYY-MM}/records.jsonl"""
    if when is None:
        when = datetime.now(UTC).strftime("%Y-%m")
    elif len(when) >= 7:
        when = when[:7]  # ISO datetime → YYYY-MM
    audit_dir = resolve_audit_dir() / when
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir / "records.jsonl"


def append_event(event: AuditEvent) -> Path:
    """JSONL line append (덮어쓰기 차단·O_APPEND)."""
    target = _month_file(event.timestamp)
    # append-only mode·동시성 안전 (POSIX append guarantee·Windows 본래 line < PIPE_BUF 안전)
    with target.open("a", encoding="utf-8") as f:
        f.write(event.to_jsonl())
    return target


def iter_all_events() -> Iterator[AuditEvent]:
    """모든 월별 파일 순회 (감사 추적용)."""
    base = resolve_audit_dir()
    if not base.exists():
        return
    for month_dir in sorted(base.iterdir()):
        if not month_dir.is_dir():
            continue
        rec_file = month_dir / "records.jsonl"
        if not rec_file.exists():
            continue
        with rec_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield AuditEvent(**data)
                except (json.JSONDecodeError, TypeError):
                    continue


def get_record_events(record_id: str) -> list[AuditEvent]:
    """특정 record_id의 모든 이벤트 반환 (PIPA §35 열람권)."""
    return [e for e in iter_all_events() if e.record_id == record_id]


def delete_record(record_id: str, user_id: str | None = None) -> AuditEvent:
    """PIPA §36 파기 요청 = tombstone event 추가 (원본 line은 보존·법적 추적 가능)."""
    tombstone = AuditEvent.now(
        record_id=record_id,
        action="delete_request",
        user_id=user_id,
        note="PIPA §36 파기 요청·향후 조회 시 redact 처리",
    )
    append_event(tombstone)
    return tombstone


def is_deleted(record_id: str) -> bool:
    """delete_request 이벤트 존재 여부."""
    return any(e.action == "delete_request" for e in get_record_events(record_id))
