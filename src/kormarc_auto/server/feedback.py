"""베타 사서 피드백 수집.

`logs/feedback.jsonl` 한 줄씩 추가. PO가 매주 점검해 우선순위 재조정.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_lock = Lock()


def _log_path() -> Path:
    path = Path(os.getenv("KORMARC_FEEDBACK_LOG", "logs/feedback.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_feedback(
    *,
    api_key: str,
    rating: int,
    comment: str,
    category: str,
) -> dict[str, Any]:
    """피드백 1건 저장.

    Args:
        api_key: 보낸 사람 키 (해시로 저장)
        rating: 1~5 (0이면 미평가)
        comment: 자유 텍스트 (~2000자)
        category: bug/feature/ux/etc (~50자)

    Returns:
        저장된 entry (확인용, 키 해시만)
    """
    rating = max(0, min(5, rating))
    entry = {
        "ts": int(time.time()),
        "key_hash": hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16],
        "rating": rating,
        "category": category or "etc",
        "comment": comment,
    }
    with _lock:
        try:
            with _log_path().open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning("피드백 저장 실패: %s", e)
    return {"ok": True, "ts": entry["ts"], "key_hash": entry["key_hash"]}


def list_recent(limit: int = 50) -> list[dict[str, Any]]:
    """최근 N건 (관리자용)."""
    path = _log_path()
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError as e:
        logger.warning("피드백 로그 로드 실패: %s", e)
        return []
    return out[-limit:][::-1]
