"""갈래 B Cycle 13B (P33) — 월간 사용량 트래커.

게이트 (외부 매출 보고서 P33):
- 75% (40/50) pre-warning = 인앱 배너
- 100% (50/50) block = 결제 모달·402 Payment Required
- 24h grace period = 학교 행정실 결재 시간 고려 (즉시 차단 X)
- 다음달 1일 자동 초기화

상수 변경 = ADR 필수 (작은도서관 평균 신착 30-40권/월 기준).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Literal

PRE_WARNING_THRESHOLD: float = 0.80  # 80% 도달 시 인앱 배너
BLOCK_THRESHOLD: float = 1.00  # 100% 도달 시 결제 모달
GRACE_PERIOD_HOURS: int = 24  # 100% 후 24h 추가 처리 허용


QuotaState = Literal["normal", "pre_warning", "at_limit", "grace", "blocked"]


@dataclass(frozen=True)
class UsageEvent:
    """1건 KORMARC 생성 = 1 event."""

    user_id: str
    record_id: str
    timestamp: str  # ISO 8601 UTC
    plan_code: str = "free"


@dataclass
class QuotaTracker:
    """월별 사용량 + 상태 산정·idempotent record_id."""

    user_id: str
    plan_code: str
    monthly_limit: int  # plans.PLANS[plan_code].monthly_records
    current_count: int = 0
    grace_started_at: datetime | None = None
    seen_record_ids: set[str] = field(default_factory=set)

    def record_usage(self, record_id: str, *, now: datetime | None = None) -> bool:
        """사용량 +1 (멱등성·동일 record_id = 중복 카운트 X). True = 카운트 발생."""
        if record_id in self.seen_record_ids:
            return False
        self.seen_record_ids.add(record_id)
        self.current_count += 1
        return True

    def state(self, *, now: datetime | None = None) -> QuotaState:
        """현재 한도 상태."""
        if now is None:
            now = datetime.now(UTC)
        if self.monthly_limit == 0:
            return "normal"  # 무제한
        usage_pct = self.current_count / self.monthly_limit
        if usage_pct >= 1.0:
            if self.grace_started_at is None:
                # 100% 도달 직후 = grace 시작
                return "at_limit"
            elapsed_h = (now - self.grace_started_at).total_seconds() / 3600
            return "grace" if elapsed_h < GRACE_PERIOD_HOURS else "blocked"
        if usage_pct >= PRE_WARNING_THRESHOLD:
            return "pre_warning"
        return "normal"

    def start_grace(self, *, now: datetime | None = None) -> None:
        """100% 도달 시 grace 시작 (24h)."""
        if self.grace_started_at is None:
            self.grace_started_at = now or datetime.now(UTC)

    def reset_for_new_month(self) -> None:
        """매월 1일 자동 호출."""
        self.current_count = 0
        self.grace_started_at = None
        self.seen_record_ids.clear()

    def usage_pct(self) -> float:
        """진행률 (UI 게이지바·raw % UI 노출 금지·내부만)."""
        if self.monthly_limit == 0:
            return 0.0
        return min(1.0, self.current_count / self.monthly_limit)

    def remaining_records(self) -> int:
        return max(0, self.monthly_limit - self.current_count)

    def is_blocked(self, *, now: datetime | None = None) -> bool:
        return self.state(now=now) == "blocked"


def next_month_first_day(today: date | None = None) -> date:
    """다음달 1일 (자동 reset cron 기준)."""
    if today is None:
        today = date.today()
    if today.month == 12:
        return date(today.year + 1, 1, 1)
    return date(today.year, today.month + 1, 1)
