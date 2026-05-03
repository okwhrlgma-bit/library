"""모바일 sync API — Phase 2 Flutter 앱 ↔ FastAPI backend.

페르소나 03 (P15 순회사서) 100점 보완:
- Flutter 앱 = 오프라인 큐 누적 → 와이파이/셀룰러 회복 시 일괄 sync
- 본 모듈 = 서버 측 sync endpoint 로직 (FastAPI route는 server/app.py에서 import)
- 충돌 해결 = server-wins (자관 기존 데이터 우선) 기본 + per-tenant 정책

REST API 설계:
- POST /v1/mobile/sync/push — Flutter offline_queue → server bulk push
- GET  /v1/mobile/sync/pull/{tenant} — server → Flutter (자관 신규 .mrc 동기화)
- POST /v1/mobile/sync/resolve — 충돌 해결 (사서 검토 결과 반영)

Phase 2 Flutter 앱 별도 구현 시 본 endpoint 사용.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

ConflictStrategy = Literal["server_wins", "client_wins", "manual_review"]
SyncStatus = Literal["accepted", "rejected", "conflict", "duplicate"]


@dataclass(frozen=True)
class SyncPushRequest:
    """Flutter offline_queue → server push 요청 1건."""

    tenant_id: str
    client_item_id: int  # offline_queue.id
    payload_type: Literal["isbn", "barcode", "photo"]
    payload: dict[str, Any]
    client_timestamp: str  # ISO 8601 (Flutter 측 created_at)


@dataclass(frozen=True)
class SyncPushResponse:
    """server → Flutter 응답 1건."""

    client_item_id: int
    status: SyncStatus
    server_record_id: str | None = None  # 생성된 KORMARC 레코드 ID
    conflict_data: dict[str, Any] | None = None  # 충돌 시 server 측 기존 데이터
    error: str | None = None


@dataclass(frozen=True)
class SyncBatchResult:
    """일괄 push 결과 집계."""

    accepted: int = 0
    rejected: int = 0
    conflicts: int = 0
    duplicates: int = 0
    items: list[SyncPushResponse] = field(default_factory=list)
    sync_completed_at: str = ""


def detect_conflict(
    new_payload: dict[str, Any],
    existing_record: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    """충돌 감지 (ISBN 중복 + 핵심 필드 변경).

    Returns:
        (충돌 여부, 충돌 사유)
    """
    if existing_record is None:
        return False, None

    new_isbn = new_payload.get("isbn")
    existing_isbn = existing_record.get("isbn")
    if new_isbn and existing_isbn and new_isbn == existing_isbn:
        # 동일 ISBN 존재 → 중요 필드 변경 여부 검사
        for key in ("title", "author", "publisher", "kdc"):
            new_val = new_payload.get(key)
            existing_val = existing_record.get(key)
            if new_val and existing_val and new_val != existing_val:
                return True, f"필드 충돌: {key} (new={new_val} / existing={existing_val})"
        return False, None  # 동일 ISBN·동일 핵심 = 단순 중복

    return False, None


def resolve_conflict(
    new_payload: dict[str, Any],
    existing_record: dict[str, Any],
    strategy: ConflictStrategy = "server_wins",
) -> dict[str, Any]:
    """충돌 해결 (전략별 병합).

    - server_wins (기본): 기존 데이터 보존
    - client_wins: 신규 데이터 덮어쓰기
    - manual_review: SyncStatus=conflict 반환·사서 UI 검토
    """
    if strategy == "server_wins":
        return dict(existing_record)
    if strategy == "client_wins":
        merged = dict(existing_record)
        merged.update(new_payload)
        return merged
    # manual_review = caller가 SyncStatus.conflict 반환 책임
    return dict(existing_record)


def process_push_item(
    request: SyncPushRequest,
    existing_record: dict[str, Any] | None = None,
    conflict_strategy: ConflictStrategy = "server_wins",
) -> SyncPushResponse:
    """1건 push 처리 (충돌 감지 + 해결).

    실제 server는 이 함수를 호출 후 결과에 따라 DB write·KORMARC builder 호출.
    """
    is_conflict, reason = detect_conflict(request.payload, existing_record)

    if is_conflict and conflict_strategy == "manual_review":
        return SyncPushResponse(
            client_item_id=request.client_item_id,
            status="conflict",
            conflict_data=existing_record,
            error=reason,
        )

    # 동일 ISBN·동일 데이터 = 중복
    if (
        existing_record
        and not is_conflict
        and request.payload.get("isbn") == existing_record.get("isbn")
    ):
        return SyncPushResponse(
            client_item_id=request.client_item_id,
            status="duplicate",
            server_record_id=existing_record.get("id"),
        )

    # 정상 accept
    return SyncPushResponse(
        client_item_id=request.client_item_id,
        status="accepted",
        server_record_id=None,  # 실제 builder 호출 후 ID 채움
    )


def aggregate_batch_result(items: list[SyncPushResponse]) -> SyncBatchResult:
    """일괄 push 결과 집계."""
    return SyncBatchResult(
        accepted=sum(1 for i in items if i.status == "accepted"),
        rejected=sum(1 for i in items if i.status == "rejected"),
        conflicts=sum(1 for i in items if i.status == "conflict"),
        duplicates=sum(1 for i in items if i.status == "duplicate"),
        items=items,
        sync_completed_at=datetime.now(UTC).isoformat(),
    )


__all__ = [
    "ConflictStrategy",
    "SyncBatchResult",
    "SyncPushRequest",
    "SyncPushResponse",
    "SyncStatus",
    "aggregate_batch_result",
    "detect_conflict",
    "process_push_item",
    "resolve_conflict",
]
