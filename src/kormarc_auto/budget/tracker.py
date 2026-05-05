"""갈래 B Cycle 19A (P49) — 일일/주간/월간 예산 추적.

저장: ~/.kormarc-auto/budget/{YYYY-MM}/usage.jsonl (append-only·analytics와 분리)
ENV override:
- KORMARC_DAILY_USD_BUDGET (default = $20)
- KORMARC_BUDGET_DIR (default = ~/.kormarc-auto/budget)
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

DAILY_USD_BUDGET: float = float(os.getenv("KORMARC_DAILY_USD_BUDGET", "20.0"))

# V2 §8 임계 (PO 1인 SaaS·외부 V1 §11.2)
WARNING_PCT: float = 0.70  # 70% = 알람
PAUSE_PCT: float = 0.90  # 90% = 자율 일시 정지
WEEK_INCREASE_ALARM: float = 0.30  # 주 평균 +30% = 회귀 알람

BudgetState = Literal["normal", "warning", "near_limit", "exceeded"]


def resolve_budget_dir() -> Path:
    env = os.getenv("KORMARC_BUDGET_DIR")
    if env:
        return Path(env)
    return Path.home() / ".kormarc-auto" / "budget"


@dataclass(frozen=True)
class UsageRecord:
    """1 작업 = 1 record (audit·analytics와 분리·USD/토큰만)."""

    timestamp: str  # ISO 8601 UTC
    task_kind: str  # "code-edit" / "refactor" 등
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_seconds: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def now(cls, **kwargs: Any) -> UsageRecord:
        kwargs.setdefault("timestamp", datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"))
        return cls(**kwargs)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True) + "\n"


def _month_file(when: str | None = None) -> Path:
    if when is None:
        when = datetime.now(UTC).strftime("%Y-%m")
    elif len(when) >= 7:
        when = when[:7]
    target_dir = resolve_budget_dir() / when
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / "usage.jsonl"


def append_record(record: UsageRecord) -> Path:
    """JSONL append (덮어쓰기 차단·동시성 안전)."""
    target = _month_file(record.timestamp)
    with target.open("a", encoding="utf-8") as f:
        f.write(record.to_jsonl())
    return target


def iter_records(*, since_month: str | None = None) -> Iterator[UsageRecord]:
    base = resolve_budget_dir()
    if not base.exists():
        return
    for month_dir in sorted(base.iterdir()):
        if not month_dir.is_dir():
            continue
        if since_month and month_dir.name < since_month:
            continue
        rec_file = month_dir / "usage.jsonl"
        if not rec_file.exists():
            continue
        with rec_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield UsageRecord(**json.loads(line))
                except (json.JSONDecodeError, TypeError):
                    continue


@dataclass
class BudgetTracker:
    """예산 상태 산정 + 일일/주간/월간 집계."""

    daily_usd_budget: float = DAILY_USD_BUDGET

    def usage_for_date(self, target_date: date) -> float:
        """특정 날짜 USD 합계."""
        date_str = target_date.isoformat()
        month_str = date_str[:7]
        total = 0.0
        for r in iter_records(since_month=month_str):
            if r.timestamp.startswith(date_str):
                total += r.cost_usd
        return round(total, 4)

    def usage_today(self, *, now: datetime | None = None) -> float:
        if now is None:
            now = datetime.now(UTC)
        return self.usage_for_date(now.date())

    def usage_last_7_days(self, *, now: datetime | None = None) -> float:
        if now is None:
            now = datetime.now(UTC)
        end = now.date()
        total = 0.0
        for i in range(7):
            d = end - timedelta(days=i)
            total += self.usage_for_date(d)
        return round(total, 4)

    def state(self, *, now: datetime | None = None) -> BudgetState:
        """현재 상태 (normal/warning/near_limit/exceeded)."""
        used = self.usage_today(now=now)
        pct = used / self.daily_usd_budget if self.daily_usd_budget > 0 else 0
        if pct >= 1.0:
            return "exceeded"
        if pct >= PAUSE_PCT:
            return "near_limit"
        if pct >= WARNING_PCT:
            return "warning"
        return "normal"

    def remaining_budget_usd(self, *, now: datetime | None = None) -> float:
        used = self.usage_today(now=now)
        return round(max(0.0, self.daily_usd_budget - used), 4)

    def should_block_session(self, *, now: datetime | None = None) -> bool:
        """SessionStart hook이 호출·True 시 세션 차단."""
        return self.state(now=now) in ("near_limit", "exceeded")

    def status_message(self, *, now: datetime | None = None) -> str:
        used = self.usage_today(now=now)
        state = self.state(now=now)
        remaining = self.remaining_budget_usd(now=now)
        emoji = {
            "normal": "🟢",
            "warning": "🟡",
            "near_limit": "🔴",
            "exceeded": "⛔",
        }[state]
        return (
            f"{emoji} 오늘 ${used:.4f} / ${self.daily_usd_budget:.2f} "
            f"({state}·잔여 ${remaining:.4f})"
        )

    def to_api_dict(self, *, now: datetime | None = None) -> dict[str, Any]:
        return {
            "daily_usd_budget": self.daily_usd_budget,
            "today_usd": self.usage_today(now=now),
            "last_7_days_usd": self.usage_last_7_days(now=now),
            "remaining_today_usd": self.remaining_budget_usd(now=now),
            "state": self.state(now=now),
            "should_block_session": self.should_block_session(now=now),
            "status_message": self.status_message(now=now),
        }
