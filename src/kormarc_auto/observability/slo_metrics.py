"""SLO 메트릭 — M5 관측성 (PIPA SLA 99.5/99.9/99.95% 측정).

PO 명령 (12-섹션 §9.2): "SLA tier 측정 가능 = 관측성 필수"

핵심 SLO:
- p95 ISBN→.mrc 처리 시간 ≤ 5초 (5초 약속 정합)
- 외부 API 호출 성공률 ≥ 99%
- 결제 흐름 단계별 성공률 ≥ 99.5%
- 가용률 99.5% (Phase 1) / 99.9% (Phase 2) / 99.95% (Phase 3)

데이터 모델:
- structured logging = JSON (request_id·tenant_id·persona·plan)
- in-memory rolling window (최근 1,000 요청)
- /metrics Prometheus 형식 (옵션·외부 export)
"""

from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

MetricCategory = Literal["isbn_to_mrc", "external_api", "payment", "vision_ocr"]


@dataclass(frozen=True)
class MetricSample:
    """단일 측정값."""

    category: MetricCategory
    duration_ms: float
    success: bool
    timestamp: str  # ISO 8601
    tenant_id: str | None = None
    error: str | None = None
    metadata: dict | None = None


@dataclass
class SloRollingWindow:
    """rolling window 1,000건 측정."""

    capacity: int = 1000
    samples: deque[MetricSample] = field(default_factory=deque)

    def record(self, sample: MetricSample) -> None:
        if len(self.samples) >= self.capacity:
            self.samples.popleft()
        self.samples.append(sample)

    def percentile(self, category: MetricCategory, p: float) -> float | None:
        """p (0.0~1.0) 분위수 (예: 0.95 = p95)."""
        durations = [s.duration_ms for s in self.samples if s.category == category and s.success]
        if not durations:
            return None
        sorted_d = sorted(durations)
        idx = int(p * (len(sorted_d) - 1))
        return sorted_d[idx]

    def success_rate(self, category: MetricCategory) -> float | None:
        """카테고리 성공률 (0.0~1.0)."""
        cat = [s for s in self.samples if s.category == category]
        if not cat:
            return None
        return sum(1 for s in cat if s.success) / len(cat)

    def avg(self, category: MetricCategory) -> float | None:
        durations = [s.duration_ms for s in self.samples if s.category == category and s.success]
        if not durations:
            return None
        return statistics.mean(durations)

    def count(self, category: MetricCategory) -> int:
        return sum(1 for s in self.samples if s.category == category)


# 글로벌 rolling window (싱글톤·서버 프로세스당 1개)
_global_window = SloRollingWindow()


def record_metric(
    category: MetricCategory,
    duration_ms: float,
    success: bool,
    *,
    tenant_id: str | None = None,
    error: str | None = None,
    metadata: dict | None = None,
) -> None:
    """전역 metric 기록."""
    sample = MetricSample(
        category=category,
        duration_ms=duration_ms,
        success=success,
        timestamp=datetime.now(UTC).isoformat(),
        tenant_id=tenant_id,
        error=error,
        metadata=metadata,
    )
    _global_window.record(sample)


def get_slo_summary() -> dict:
    """현재 SLO 상태 요약 (대시보드·헬스체크용)."""
    summary: dict = {}
    for cat in ("isbn_to_mrc", "external_api", "payment", "vision_ocr"):
        cat_typed: MetricCategory = cat  # type: ignore[assignment]
        count = _global_window.count(cat_typed)
        if count == 0:
            summary[cat] = {"count": 0, "status": "no_data"}
            continue
        p95 = _global_window.percentile(cat_typed, 0.95)
        p99 = _global_window.percentile(cat_typed, 0.99)
        success_rate = _global_window.success_rate(cat_typed)
        avg = _global_window.avg(cat_typed)
        summary[cat] = {
            "count": count,
            "p95_ms": round(p95, 2) if p95 else None,
            "p99_ms": round(p99, 2) if p99 else None,
            "avg_ms": round(avg, 2) if avg else None,
            "success_rate": round(success_rate, 4) if success_rate else None,
        }
    summary["window_size"] = len(_global_window.samples)
    summary["timestamp"] = datetime.now(UTC).isoformat()
    return summary


def check_slo_violations() -> list[dict]:
    """SLO 위반 체크 (1주 100% 환불 자동 트리거 후보)."""
    violations: list[dict] = []
    summary = get_slo_summary()

    # ISBN→.mrc p95 ≤ 5초 (5,000ms)
    isbn = summary.get("isbn_to_mrc", {})
    if isbn.get("p95_ms") and isbn["p95_ms"] > 5000:
        violations.append(
            {
                "slo": "isbn_to_mrc_p95_5s",
                "actual_ms": isbn["p95_ms"],
                "threshold_ms": 5000,
                "severity": "high",
            }
        )

    # 외부 API 성공률 ≥ 99%
    ext = summary.get("external_api", {})
    if ext.get("success_rate") and ext["success_rate"] < 0.99:
        violations.append(
            {
                "slo": "external_api_success_99",
                "actual_rate": ext["success_rate"],
                "threshold_rate": 0.99,
                "severity": "medium",
            }
        )

    # 결제 성공률 ≥ 99.5%
    pay = summary.get("payment", {})
    if pay.get("success_rate") and pay["success_rate"] < 0.995:
        violations.append(
            {
                "slo": "payment_success_995",
                "actual_rate": pay["success_rate"],
                "threshold_rate": 0.995,
                "severity": "high",  # 결제 실패 = 매출 직격
            }
        )

    return violations


def reset_window() -> None:
    """window 초기화 (테스트·배포 후)."""
    _global_window.samples.clear()


def to_prometheus_format() -> str:
    """Prometheus /metrics 포맷 출력."""
    lines: list[str] = ["# HELP kormarc_slo SLO metrics", "# TYPE kormarc_slo gauge"]
    summary = get_slo_summary()
    for cat in ("isbn_to_mrc", "external_api", "payment", "vision_ocr"):
        m = summary.get(cat, {})
        if m.get("count", 0) > 0:
            for stat in ("p95_ms", "p99_ms", "avg_ms", "success_rate"):
                val = m.get(stat)
                if val is not None:
                    lines.append(f'kormarc_slo{{category="{cat}",stat="{stat}"}} {val}')
    return "\n".join(lines) + "\n"


__all__ = [
    "MetricCategory",
    "MetricSample",
    "SloRollingWindow",
    "check_slo_violations",
    "get_slo_summary",
    "record_metric",
    "reset_window",
    "to_prometheus_format",
]
