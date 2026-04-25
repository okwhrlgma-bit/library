"""분실·파손도서 처리 (583 처리 이력 + 자관 통계).

근거: PO 자료 「내숲 종합 자료관리대장」 (오배가·보수·대출저조·분실·파손 5종 시트).

KORMARC 583 (처리 이력):
  ▾a 처리 행위 (분실·파손·보수·제적·이관)
  ▾c 일자
  ▾h 권한·근거
  ▾i 양·범위
  ▾l 상태
  ▾x 비공개 메모

자관 처리 흐름:
1. 분실·파손 발견 → 583 ▾a 추가
2. 일정 기간 후 보수·재구매·제적 결정
3. 583 추가 (행위·일자)
4. 자관 통계 자동 누적
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Any

from pymarc import Field, Indicators, Record, Subfield

logger = logging.getLogger(__name__)

_lock = Lock()

# 처리 행위 표준
ACTION_TYPES = {
    "lost": "분실",
    "damaged": "파손",
    "repair": "보수",
    "deaccession": "제적",
    "transfer": "이관",
    "missorted": "오배가",
    "low_circulation": "대출저조",
}


def _log_path() -> Path:
    path = Path(os.getenv("KORMARC_LOSS_DAMAGE_LOG", "logs/loss_damage.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def add_583_processing(
    record: Record,
    *,
    action: str,
    date: str | None = None,
    authority: str | None = None,
    extent: str | None = None,
    status: str | None = None,
    private_note: str | None = None,
) -> None:
    """583 처리 이력 추가.

    Args:
        action: 'lost'/'damaged'/'repair'/'deaccession'/'transfer'/'missorted'
        date: 일자 (YYYYMMDD 또는 YYYY-MM-DD)
        authority: 결정 권한·근거 (예: '관장 결재 2024-07-15')
        extent: 양·범위 (예: '1책', '12-15p')
        status: 상태 (예: '수리 후 보존', '폐기')
        private_note: 비공개 메모 (▾x)
    """
    label = ACTION_TYPES.get(action, action)
    sf = [Subfield(code="a", value=label)]
    if date:
        sf.append(Subfield(code="c", value=date))
    if authority:
        sf.append(Subfield(code="h", value=authority))
    if extent:
        sf.append(Subfield(code="i", value=extent))
    if status:
        sf.append(Subfield(code="l", value=status))
    if private_note:
        sf.append(Subfield(code="x", value=private_note))

    record.add_field(
        Field(tag="583", indicators=Indicators("1", " "), subfields=sf)
    )


def log_processing_event(
    *,
    isbn: str,
    registration_no: str | None,
    action: str,
    note: str | None = None,
) -> dict[str, Any]:
    """자관 처리 이력 누적 (분실·파손 통계용)."""
    entry = {
        "ts": int(time.time()),
        "isbn": isbn,
        "registration_no": registration_no,
        "action": action,
        "label": ACTION_TYPES.get(action, action),
        "note": note,
    }
    with _lock, _log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def stats_by_action() -> dict[str, int]:
    """처리 행위별 누적 (PO 자관 보고서용)."""
    path = _log_path()
    if not path.exists():
        return {}
    counts: dict[str, int] = {}
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    label = e.get("label") or e.get("action") or "?"
                    counts[label] = counts.get(label, 0) + 1
                except json.JSONDecodeError:
                    continue
    except OSError:
        return {}
    return counts
