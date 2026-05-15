"""Cron 자가 점검 (ADR 0063 정합·매 cycle 끝 자동).

매 cycle 끝 = cron 상태 확인·만료 24h 전 = 자동 재등록 권장.

실행:
    python scripts/cron_health_check.py
    python scripts/cron_health_check.py --json

원칙:
- LLM 호출 0·결정적 (V3 §4.10 정합)
- 외부 API 0
- 결과 = stdout + STATUS 알림 (옵션)
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta


def calculate_expiry(registered_iso: str, days: int = 7) -> datetime:
    """cron 만료 시간 계산 (등록일 + 7일)."""
    registered = datetime.fromisoformat(registered_iso.replace("Z", "+00:00"))
    return registered + timedelta(days=days)


def hours_until_expiry(expiry: datetime) -> float:
    """현재 → 만료 시간 (시간 단위)."""
    now = datetime.now(UTC)
    delta = expiry - now
    return round(delta.total_seconds() / 3600.0, 1)


def should_reregister(hours_left: float, threshold_hours: float = 24.0) -> bool:
    """재등록 여부 판단 (24h 미만 = 재등록 권장)."""
    return hours_left < threshold_hours


def status_report(
    job_id: str,
    cron_expression: str,
    registered_iso: str,
    prompt: str = "야간 자율 진행",
) -> dict[str, object]:
    """cron 상태 보고서 생성."""
    expiry = calculate_expiry(registered_iso)
    hours_left = hours_until_expiry(expiry)
    needs_reregister = should_reregister(hours_left)

    return {
        "job_id": job_id,
        "cron_expression": cron_expression,
        "registered": registered_iso,
        "expires_at": expiry.isoformat(),
        "hours_until_expiry": hours_left,
        "needs_reregister": needs_reregister,
        "next_action": (
            "CronCreate 자동 재등록 권장 (만료 24h 임박)"
            if needs_reregister
            else f"OK·만료 {hours_left:.0f}h 후 재등록"
        ),
        "prompt": prompt,
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = argv or sys.argv[1:]
    output_json = "--json" in args

    # 현재 cron (ADR 0062·0063 정합·CronList 결과 박제)
    report = status_report(
        job_id="ac6a2cd4",
        cron_expression="2-59/5 * * * *",
        registered_iso="2026-05-08T22:00:00+09:00",
    )

    if output_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n🤖 Cron 자가 점검 (ADR 0063·24/7 자동 작동 의무)\n")
        print(f"  Job ID: {report['job_id']}")
        print(f"  주기: {report['cron_expression']} (매 5분)")
        print(f"  등록: {report['registered']}")
        print(f"  만료: {report['expires_at']}")
        print(f"  남은 시간: {report['hours_until_expiry']}h")
        print(f"  상태: {report['next_action']}\n")

    return 0 if not report["needs_reregister"] else 1


if __name__ == "__main__":
    sys.exit(main())
