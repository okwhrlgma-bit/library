"""관리자 통계 — PO 대시보드용.

`/admin/stats` 응답 구성. 가입자·사용량·피드백·매출 환산.
"""

from __future__ import annotations

import json
import logging
import os
from collections import Counter
from pathlib import Path
from typing import Any

from kormarc_auto.constants import (
    PRICE_PER_RECORD_KRW,
    USAGE_DB_PATH,
    USAGE_LOG_PATH,
)

logger = logging.getLogger(__name__)


def build_stats() -> dict[str, Any]:
    """관리자 통계 종합."""
    from kormarc_auto.server.feedback import list_recent

    return {
        "users": _user_summary(),
        "usage_24h": _usage_in_window(24 * 3600),
        "usage_7d": _usage_in_window(7 * 24 * 3600),
        "usage_30d": _usage_in_window(30 * 24 * 3600),
        "signups_recent": _recent_signups(limit=20),
        "feedback_recent": list_recent(limit=20),
        "revenue_estimate_30d_krw": _usage_in_window(30 * 24 * 3600).get("ok_count", 0)
        * PRICE_PER_RECORD_KRW,
        "price_per_record_krw": PRICE_PER_RECORD_KRW,
        "sales_funnel": _sales_funnel_summary(),
    }


def _sales_funnel_summary() -> dict[str, Any]:
    """영업 funnel (가입→활성→한도→결제) + 페르소나별 분리 (KLA 슬라이드 데이터 ★)."""
    import sys
    root = Path(__file__).resolve().parent.parent.parent.parent
    scripts_dir = root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import sales_funnel  # type: ignore[import-not-found]
        import aggregate_interviews  # type: ignore[import-not-found]
    except ImportError:
        return {"error": "sales_funnel module not available"}

    signups_path = root / "logs" / "signups.jsonl"
    usage_path = root / "logs" / "usage.jsonl"
    signups = sales_funnel._load_jsonl(signups_path)
    usage = sales_funnel._load_jsonl(usage_path)
    metrics = sales_funnel.compute_funnel(signups, usage)

    # 페르소나별 funnel 분리 (PILOT 인터뷰 결과 활용)
    interviews = aggregate_interviews.load_interviews()
    by_persona = sales_funnel.funnel_by_persona(signups, usage, interviews)

    return {
        "overall": metrics.to_dict(),
        "by_persona": {p: m.to_dict() for p, m in by_persona.items()},
    }


def _user_summary() -> dict[str, Any]:
    path = Path(os.getenv("KORMARC_USAGE_DB", USAGE_DB_PATH))
    if not path.exists():
        return {"total_keys": 0, "total_used": 0, "total_remaining": 0, "top_users": []}
    try:
        db: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"total_keys": 0, "total_used": 0, "total_remaining": 0, "top_users": []}

    total_keys = len(db)
    total_used = sum(int(r.get("used", 0)) for r in db.values())
    total_remaining = sum(
        max(0, int(r.get("free_quota", 0)) - int(r.get("used", 0))) for r in db.values()
    )
    top = sorted(db.values(), key=lambda r: int(r.get("used", 0)), reverse=True)[:10]
    return {
        "total_keys": total_keys,
        "total_used": total_used,
        "total_remaining": total_remaining,
        "top_users": [
            {"key_hash": r.get("key_hash"), "used": r.get("used"), "quota": r.get("free_quota")}
            for r in top
        ],
    }


def _usage_in_window(seconds: int) -> dict[str, Any]:
    import time

    cutoff = time.time() - seconds
    path = Path(os.getenv("KORMARC_USAGE_LOG", USAGE_LOG_PATH))
    if not path.exists():
        return {"total": 0, "ok_count": 0, "fail_count": 0, "by_kind": {}}

    total = 0
    ok_count = 0
    fail_count = 0
    by_kind: Counter[str] = Counter()
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = int(entry.get("ts", 0))
                if ts < cutoff:
                    continue
                total += 1
                kind = entry.get("kind", "?")
                by_kind[kind] += 1
                if entry.get("ok"):
                    ok_count += 1
                else:
                    fail_count += 1
    except OSError:
        pass

    return {
        "total": total,
        "ok_count": ok_count,
        "fail_count": fail_count,
        "by_kind": dict(by_kind),
    }


def _recent_signups(limit: int = 20) -> list[dict[str, Any]]:
    path = Path(os.getenv("KORMARC_SIGNUP_LOG", "logs/signups.jsonl"))
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
    except OSError:
        return []
    return out[-limit:][::-1]
