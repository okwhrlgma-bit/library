"""오프라인 모드 큐 — Phase 2 Flutter 앱 backend.

페르소나 03 (P15 순회사서·1인 15~37교) deal-breaker:
- 학교 와이파이 미보장
- 교과서 창고·지하·시골 = 셀룰러 약함
- 이동 중 카메라 OCR·바코드 스캔 = 오프라인 큐 필수

작동 모델:
1. 오프라인 = 로컬 SQLite 큐에 ISBN/스캔/사진 누적
2. 셀룰러/와이파이 회복 시 = 자동 sync (REST API 일괄 push)
3. 충돌 해결 = server-wins (자관 기존 데이터 우선)
4. KOLAS 반입 폴더 = sync 후 자동 export (.mrc 파일)

데이터 모델:
- offline_queue: id·tenant_id·payload(JSON)·status·created_at·synced_at
- payload = {type: "isbn"/"barcode"/"photo", data: {...}}
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

QueueStatus = Literal["pending", "syncing", "synced", "failed"]


@dataclass(frozen=True)
class OfflineQueueItem:
    """오프라인 큐 1건."""

    id: int | None  # SQLite autoincrement
    tenant_id: str  # 자관 식별
    payload_type: Literal["isbn", "barcode", "photo"]
    payload: dict[str, Any]
    status: QueueStatus
    created_at: str  # ISO 8601
    synced_at: str | None = None
    error: str | None = None


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS offline_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    payload_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    synced_at TEXT,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_offline_queue_status
    ON offline_queue (tenant_id, status);
"""


def init_queue_db(db_path: Path) -> None:
    """SQLite 큐 DB 초기화."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def enqueue(
    db_path: Path,
    tenant_id: str,
    payload_type: Literal["isbn", "barcode", "photo"],
    payload: dict[str, Any],
) -> int:
    """오프라인 큐에 항목 추가 → autoincrement id 반환."""
    conn = sqlite3.connect(str(db_path))
    try:
        now = datetime.now(UTC).isoformat()
        cursor = conn.execute(
            "INSERT INTO offline_queue (tenant_id, payload_type, payload_json, status, created_at) "
            "VALUES (?, ?, ?, 'pending', ?)",
            (tenant_id, payload_type, json.dumps(payload, ensure_ascii=False), now),
        )
        conn.commit()
        return cursor.lastrowid or 0
    finally:
        conn.close()


def list_pending(db_path: Path, tenant_id: str, limit: int = 100) -> list[OfflineQueueItem]:
    """sync 대기 항목 조회 (FIFO)."""
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute(
            "SELECT id, tenant_id, payload_type, payload_json, status, created_at, synced_at, error "
            "FROM offline_queue WHERE tenant_id = ? AND status = 'pending' "
            "ORDER BY created_at ASC LIMIT ?",
            (tenant_id, limit),
        )
        rows = cursor.fetchall()
        return [
            OfflineQueueItem(
                id=r[0],
                tenant_id=r[1],
                payload_type=r[2],
                payload=json.loads(r[3]),
                status=r[4],
                created_at=r[5],
                synced_at=r[6],
                error=r[7],
            )
            for r in rows
        ]
    finally:
        conn.close()


def mark_synced(db_path: Path, item_id: int) -> None:
    """sync 완료 처리."""
    conn = sqlite3.connect(str(db_path))
    try:
        now = datetime.now(UTC).isoformat()
        conn.execute(
            "UPDATE offline_queue SET status = 'synced', synced_at = ? WHERE id = ?",
            (now, item_id),
        )
        conn.commit()
    finally:
        conn.close()


def mark_failed(db_path: Path, item_id: int, error: str) -> None:
    """sync 실패 처리 + 에러 기록."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "UPDATE offline_queue SET status = 'failed', error = ? WHERE id = ?",
            (error, item_id),
        )
        conn.commit()
    finally:
        conn.close()


def queue_stats(db_path: Path, tenant_id: str) -> dict[str, int]:
    """큐 통계 (status별 카운트)."""
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute(
            "SELECT status, COUNT(*) FROM offline_queue WHERE tenant_id = ? GROUP BY status",
            (tenant_id,),
        )
        return {row[0]: row[1] for row in cursor.fetchall()}
    finally:
        conn.close()


__all__ = [
    "SCHEMA_SQL",
    "OfflineQueueItem",
    "QueueStatus",
    "enqueue",
    "init_queue_db",
    "list_pending",
    "mark_failed",
    "mark_synced",
    "queue_stats",
]
