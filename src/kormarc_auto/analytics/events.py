"""갈래 B Cycle 14B (P34) — Funnel 이벤트 정의 + PIPA 호환 익명 기록.

원칙:
- 개인정보 0개 (이메일·이름·IP raw 송출 X)
- 사용자 식별 = 익명 hash (SHA-256 12자)
- 도서관부호 익명화 (페르소나 ID·자관 prefix 0)
- Plausible custom events 호환 (no cookies)
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

EventName = Literal[
    "demo_start",  # KORMARC_DEMO_MODE 진입
    "signup",  # 무료 회원가입
    "activation",  # 100건 + 보고서 1회 (Lenny Rachitsky)
    "quota_warning",  # 80% 도달
    "quota_at_limit",  # 100% 도달
    "upgrade_clicked",  # 업그레이드 CTA 클릭
    "paid",  # 결제 성공 (Cycle 15+ P30)
    "kolas3_diagnosis_completed",  # 자가진단 완료 (Cycle 12 P37)
    "kolas3_lead_submitted",  # 마이그레이션 리드
    "regenerate",  # 재생성 (visible diff Cycle 14A)
]


# 6단 Funnel (외부 매출 보고서 P34 정합)
EVENT_CATALOG: list[EventName] = [
    "demo_start",
    "signup",
    "activation",
    "quota_warning",
    "upgrade_clicked",
    "paid",
]


def _anon_id(value: str) -> str:
    """SHA-256 12자 익명 hash·역산 X·PIPA 정합."""
    if not value:
        return "anon-empty"
    return "u-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True)
class FunnelEvent:
    """1 funnel 이벤트 = JSONL 1 line (PIPA 호환 익명)."""

    name: EventName
    timestamp: str  # ISO 8601 UTC
    anon_user_id: str  # SHA-256 hash·이메일 raw X
    plan_code: str = "free"  # free / small / school / public / enterprise
    library_type_hint: str | None = None  # "small" / "school" / "public" / None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def now(
        cls,
        name: EventName,
        *,
        user_email: str = "",
        plan_code: str = "free",
        library_type_hint: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> FunnelEvent:
        return cls(
            name=name,
            timestamp=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            anon_user_id=_anon_id(user_email),
            plan_code=plan_code,
            library_type_hint=library_type_hint,
            extra=extra or {},
        )


def _events_dir() -> Path:
    """이벤트 저장 = $KORMARC_ANALYTICS_DIR 또는 ~/.kormarc-auto/analytics/"""
    env = os.getenv("KORMARC_ANALYTICS_DIR")
    if env:
        return Path(env)
    return Path.home() / ".kormarc-auto" / "analytics"


def record_event(event: FunnelEvent) -> Path:
    """JSONL append-only 이벤트 기록 (월별 파티션)."""
    import json

    when = event.timestamp[:7]  # YYYY-MM
    target_dir = _events_dir() / when
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "events.jsonl"
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False, sort_keys=True) + "\n")
    return target


def iter_events(*, since_month: str | None = None):
    """모든 월별 events.jsonl 순회 (since_month YYYY-MM 이상만)."""
    import json

    base = _events_dir()
    if not base.exists():
        return
    for month_dir in sorted(base.iterdir()):
        if not month_dir.is_dir():
            continue
        if since_month and month_dir.name < since_month:
            continue
        ev_file = month_dir / "events.jsonl"
        if not ev_file.exists():
            continue
        with ev_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield FunnelEvent(**data)
                except (json.JSONDecodeError, TypeError):
                    continue
