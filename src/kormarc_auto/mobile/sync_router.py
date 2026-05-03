"""FastAPI sync router — Flutter 모바일 앱 ↔ backend (페르소나 03 100점).

Routes:
- POST /v1/mobile/sync/push — Flutter offline_queue → server bulk push
- GET  /v1/mobile/sync/pull/{tenant_id} — server → Flutter (자관 신규 .mrc)
- POST /v1/mobile/sync/resolve/{client_item_id} — 충돌 해결 결과 push

server/app.py에서 include_router(sync_router) 등록 후 활성.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from kormarc_auto.mobile.sync_api import (
    SyncBatchResult,
    SyncPushRequest,
    SyncPushResponse,
    aggregate_batch_result,
    process_push_item,
    resolve_conflict,
)


def handle_push_batch(
    items: list[SyncPushRequest],
    existing_lookup: dict[str, dict[str, Any]] | None = None,
) -> SyncBatchResult:
    """일괄 push 처리 (FastAPI route handler 호출).

    Args:
        items: Flutter offline_queue → server push 요청 리스트
        existing_lookup: ISBN → 기존 record 조회 매핑 (DB 조회 결과)

    Returns:
        SyncBatchResult (accepted·rejected·conflicts·duplicates 집계)
    """
    existing_lookup = existing_lookup or {}
    responses: list[SyncPushResponse] = []

    for req in items:
        isbn = req.payload.get("isbn", "")
        existing = existing_lookup.get(isbn)
        resp = process_push_item(req, existing_record=existing)
        responses.append(resp)

    return aggregate_batch_result(responses)


def handle_pull(
    tenant_id: str,
    since: str | None = None,
    record_lookup: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """server → Flutter pull (since 이후 신규 .mrc).

    Args:
        tenant_id: 자관 식별
        since: ISO 8601 (이 시각 이후 변경분만)
        record_lookup: DB 조회 결과 (route handler가 주입)

    Returns:
        {tenant_id, since, records, pulled_at}
    """
    records = record_lookup or []
    return {
        "tenant_id": tenant_id,
        "since": since,
        "records": records,
        "pulled_at": datetime.now(UTC).isoformat(),
        "count": len(records),
    }


def handle_resolve(
    client_item_id: int,
    new_payload: dict[str, Any],
    existing_record: dict[str, Any],
    user_choice: str,  # "server_wins" / "client_wins" / "merge"
) -> dict[str, Any]:
    """사서 검토 후 충돌 해결 결과 적용.

    Args:
        client_item_id: Flutter 측 큐 항목 ID
        new_payload: Flutter에서 보낸 신규
        existing_record: server 기존
        user_choice: 사서 선택

    Returns:
        해결된 최종 record
    """
    if user_choice == "merge":
        # client_wins 후 server 비파괴 병합
        merged = dict(existing_record)
        merged.update(new_payload)
        return {
            "client_item_id": client_item_id,
            "resolved_record": merged,
            "strategy_used": "merge",
        }

    strategy = "client_wins" if user_choice == "client_wins" else "server_wins"
    resolved = resolve_conflict(new_payload, existing_record, strategy)  # type: ignore[arg-type]
    return {
        "client_item_id": client_item_id,
        "resolved_record": resolved,
        "strategy_used": strategy,
    }


# OpenAPI 스키마 가이드 (Flutter 앱 swagger codegen)
OPENAPI_SCHEMA: dict[str, Any] = {
    "POST /v1/mobile/sync/push": {
        "request": {
            "items": [
                {
                    "tenant_id": "string",
                    "client_item_id": "int",
                    "payload_type": "isbn|barcode|photo",
                    "payload": "object",
                    "client_timestamp": "ISO 8601",
                }
            ]
        },
        "response": {
            "accepted": "int",
            "rejected": "int",
            "conflicts": "int",
            "duplicates": "int",
            "items": [
                {
                    "client_item_id": "int",
                    "status": "accepted|rejected|conflict|duplicate",
                    "server_record_id": "string|null",
                    "conflict_data": "object|null",
                    "error": "string|null",
                }
            ],
        },
    },
    "GET /v1/mobile/sync/pull/{tenant_id}": {
        "query": {"since": "ISO 8601"},
        "response": {
            "tenant_id": "string",
            "since": "ISO 8601|null",
            "records": "array",
            "pulled_at": "ISO 8601",
            "count": "int",
        },
    },
    "POST /v1/mobile/sync/resolve/{client_item_id}": {
        "request": {
            "new_payload": "object",
            "existing_record": "object",
            "user_choice": "server_wins|client_wins|merge",
        },
        "response": {
            "client_item_id": "int",
            "resolved_record": "object",
            "strategy_used": "string",
        },
    },
}


__all__ = [
    "OPENAPI_SCHEMA",
    "handle_pull",
    "handle_push_batch",
    "handle_resolve",
]
