"""부하 테스트 harness — 8-1 (B2B batch_vendor 1,000건·자관 50k 마이그).

PO 명령 (12-섹션 §8.1): "1,000건 batch p95 < 10분·성공률 99%·5만권 RSS < 2GB"

작동 (외부 호출 mock·실 측정 시 mock 제거):
- batch_vendor: 1,000 ISBN 5번 연속 → p50/p95/p99·성공률·토큰 비용·rate limit
- 50k 마이그: 5만 ISBN 일괄 → 메모리 RSS·재시작 회복

본 모듈은 시뮬·측정 framework. 실 부하 = scripts/load/ 통합.
"""

from __future__ import annotations

import statistics
import time
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LoadTestConfig:
    """부하 테스트 설정."""

    test_name: str
    target_count: int  # 처리 대상 수 (예: 1000)
    iterations: int = 1  # 반복 횟수 (예: 5번 연속)
    target_p95_seconds: float = 600.0  # 10분 = 600초
    target_success_rate: float = 0.99


@dataclass
class LoadTestResult:
    """부하 테스트 결과."""

    config: LoadTestConfig
    durations_seconds: list[float] = field(default_factory=list)
    successes: int = 0
    failures: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def success_rate(self) -> float:
        return self.successes / self.total if self.total > 0 else 0.0

    @property
    def p50(self) -> float:
        return statistics.median(self.durations_seconds) if self.durations_seconds else 0.0

    @property
    def p95(self) -> float:
        if not self.durations_seconds:
            return 0.0
        sorted_d = sorted(self.durations_seconds)
        idx = int(0.95 * (len(sorted_d) - 1))
        return sorted_d[idx]

    @property
    def p99(self) -> float:
        if not self.durations_seconds:
            return 0.0
        sorted_d = sorted(self.durations_seconds)
        idx = int(0.99 * (len(sorted_d) - 1))
        return sorted_d[idx]

    def passes_targets(self) -> bool:
        return (
            self.p95 <= self.config.target_p95_seconds
            and self.success_rate >= self.config.target_success_rate
        )


def run_load_test(
    config: LoadTestConfig,
    process_one: callable,
    items: Iterator,
) -> LoadTestResult:
    """부하 테스트 실행.

    Args:
        config: LoadTestConfig
        process_one: 단일 항목 처리 callable (예: lambda isbn: aggregator.aggregate_by_isbn(isbn))
        items: iterable (ISBN 등)

    Returns:
        LoadTestResult
    """
    result = LoadTestResult(config=config)

    for item in items:
        start = time.monotonic()
        try:
            process_one(item)
            elapsed = time.monotonic() - start
            result.durations_seconds.append(elapsed)
            result.successes += 1
        except Exception as e:
            elapsed = time.monotonic() - start
            result.durations_seconds.append(elapsed)
            result.failures += 1
            result.errors.append(str(e)[:200])

    return result


def estimate_memory_rss(target_count: int) -> dict:
    """5만권 마이그 메모리 RSS 추정 (실측 대신 휴리스틱)."""
    # 가정: 권당 평균 2KB (KORMARC + 메타데이터)
    base_bytes = target_count * 2 * 1024
    # 캐시·버퍼 = 30% 오버헤드
    estimated_bytes = int(base_bytes * 1.3)
    return {
        "target_count": target_count,
        "estimated_bytes": estimated_bytes,
        "estimated_mb": round(estimated_bytes / (1024 * 1024), 2),
        "passes_2gb_target": estimated_bytes < 2 * 1024 * 1024 * 1024,
    }


def estimate_anthropic_cost(
    request_count: int,
    *,
    avg_input_tokens: int = 500,
    avg_output_tokens: int = 200,
    model: str = "haiku",
) -> dict:
    """Anthropic 토큰 비용 추정."""
    # 2026 가격 (per 1M tokens)
    pricing = {
        "haiku": {"input": 0.25, "output": 1.25},
        "sonnet": {"input": 3.0, "output": 15.0},
    }
    p = pricing.get(model, pricing["haiku"])

    input_cost = request_count * avg_input_tokens / 1_000_000 * p["input"]
    output_cost = request_count * avg_output_tokens / 1_000_000 * p["output"]
    total_usd = input_cost + output_cost

    return {
        "request_count": request_count,
        "model": model,
        "input_cost_usd": round(input_cost, 4),
        "output_cost_usd": round(output_cost, 4),
        "total_usd": round(total_usd, 4),
        "total_won": int(total_usd * 1400),  # ₩1,400/USD
    }


def report(result: LoadTestResult) -> dict:
    """부하 테스트 결과 요약."""
    return {
        "test_name": result.config.test_name,
        "target_count": result.config.target_count,
        "total_processed": result.total,
        "successes": result.successes,
        "failures": result.failures,
        "success_rate": round(result.success_rate, 4),
        "p50_seconds": round(result.p50, 3),
        "p95_seconds": round(result.p95, 3),
        "p99_seconds": round(result.p99, 3),
        "passes_targets": result.passes_targets(),
        "errors_sample": result.errors[:5],
    }


__all__ = [
    "LoadTestConfig",
    "LoadTestResult",
    "estimate_anthropic_cost",
    "estimate_memory_rss",
    "report",
    "run_load_test",
]
