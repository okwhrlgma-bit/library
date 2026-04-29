"""매출·사서·LOI 트리거 모니터링 — ADR 0009 §33 활성화 자동 측정.

3개 트리거 측정:
1. **한국 매출 월 200만원 이상 (3개월 연속)** — `server.billing.aggregate_monthly` 활용
2. **베타 사서 누적 50명** — `logs/signups.jsonl` 카운트
3. **미국 LOI 1곳 이상** — `logs/us_loi.jsonl` 카운트 (PO 수동 기록)

매월 1일 자동 실행 권장 (Windows 작업 스케줄러). 3개 모두 충족 시:
- `logs/triggers/us_activation_ready.json` 생성
- PO에게 알림 (카카오톡 채널·이메일)

부수 효과:
- 매출 추세 분석 (월별 매출 + 사서별 비중 + 분기제 결제 영향)
- ADR 0004 SQLite 트리거 (동시 사서 20명+) 동시 측정
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# ADR 0009 트리거 임계값
KR_REVENUE_MONTHLY_KRW_MIN = 2_000_000
KR_REVENUE_CONSECUTIVE_MONTHS = 3
BETA_LIBRARIANS_MIN = 50
US_LOI_MIN = 1


def kr_monthly_revenues(months_back: int = 6) -> list[dict[str, Any]]:
    """최근 N개월 한국 매출 (server.billing 활용)."""
    try:
        from kormarc_auto.server.billing import aggregate_monthly
    except ImportError:
        return []

    today = date.today()
    out: list[dict[str, Any]] = []
    for i in range(months_back, 0, -1):
        # i개월 전 (timedelta 활용으로 연/월 wraparound 정확하게)
        target_month_offset = today.month - i
        y = today.year + ((target_month_offset - 1) // 12)
        m = ((target_month_offset - 1) % 12) + 1
        s = aggregate_monthly(y, m)
        out.append(
            {
                "year": y,
                "month": m,
                "revenue_krw": s.get("total_revenue_krw", 0),
                "records": s.get("total_records", 0),
            }
        )
    return out


def beta_librarian_count() -> int:
    """logs/signups.jsonl 카운트 (중복 이메일 제외)."""
    p = Path(os.getenv("KORMARC_SIGNUP_LOG", ROOT / "logs" / "signups.jsonl"))
    if not p.exists():
        return 0
    emails: set[str] = set()
    with p.open(encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            email = (e.get("email") or e.get("email_domain") or "").strip().lower()
            if email:
                emails.add(email)
    return len(emails)


def us_loi_count() -> int:
    """logs/us_loi.jsonl 카운트 (PO 수동 기록)."""
    p = ROOT / "logs" / "us_loi.jsonl"
    if not p.exists():
        return 0
    n = 0
    with p.open(encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("status") in (None, "active", "signed"):
                n += 1
    return n


def evaluate_us_trigger() -> dict[str, Any]:
    """ADR 0009 3개 트리거 평가."""
    revenues = kr_monthly_revenues(months_back=6)
    last3 = revenues[-3:] if len(revenues) >= 3 else revenues
    consecutive_ok = (
        len(last3) >= KR_REVENUE_CONSECUTIVE_MONTHS
        and all(r["revenue_krw"] >= KR_REVENUE_MONTHLY_KRW_MIN for r in last3)
    )

    librarians = beta_librarian_count()
    loi = us_loi_count()

    triggers = {
        "kr_revenue_3months": consecutive_ok,
        "beta_librarians_50plus": librarians >= BETA_LIBRARIANS_MIN,
        "us_loi_1plus": loi >= US_LOI_MIN,
    }
    all_ok = all(triggers.values())

    return {
        "revenues_recent": revenues,
        "kr_consecutive_count": sum(
            1 for r in last3 if r["revenue_krw"] >= KR_REVENUE_MONTHLY_KRW_MIN
        ),
        "beta_librarians": librarians,
        "us_loi": loi,
        "triggers": triggers,
        "all_triggers_met": all_ok,
        "evaluated_at": datetime.now().isoformat(),
    }


def evaluate_sqlite_trigger() -> dict[str, Any]:
    """ADR 0004 SQLite 마이그레이션 트리거 (동시 활성 20명+ 또는 usage.jsonl 100MB+)."""
    usage_log = Path(
        os.getenv("KORMARC_USAGE_LOG", ROOT / "logs" / "usage.jsonl")
    )
    log_size_mb = usage_log.stat().st_size / 1_048_576 if usage_log.exists() else 0

    # 최근 30일 활성 사서 (key_hash unique)
    active_keys: set[str] = set()
    if usage_log.exists():
        cutoff = int(time.time()) - 30 * 86400
        with usage_log.open(encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("ts", 0) >= cutoff and e.get("key_hash"):
                    active_keys.add(str(e["key_hash"]))

    return {
        "log_size_mb": round(log_size_mb, 2),
        "active_30d": len(active_keys),
        "should_migrate": log_size_mb >= 100 or len(active_keys) >= 20,
    }


def render_summary(report: dict[str, Any]) -> str:
    us = report["us_trigger"]
    sql = report["sqlite_trigger"]
    lines: list[str] = []
    lines.append("# 자율 트리거 보고서")
    lines.append(f"평가 시점: {us['evaluated_at']}")
    lines.append("")
    lines.append("## ADR 0009 미국 §33 활성화 트리거")
    lines.append(f"- 한국 매출 3개월 연속 200만원: {us['kr_consecutive_count']}/3 — {'✓' if us['triggers']['kr_revenue_3months'] else '❌'}")
    lines.append(f"- 베타 사서: {us['beta_librarians']}/{BETA_LIBRARIANS_MIN} — {'✓' if us['triggers']['beta_librarians_50plus'] else '❌'}")
    lines.append(f"- 미국 LOI: {us['us_loi']}/{US_LOI_MIN} — {'✓' if us['triggers']['us_loi_1plus'] else '❌'}")
    lines.append("")
    if us["all_triggers_met"]:
        lines.append("🟢 **3개 모두 충족** → ACTIVATED=True 변경 PR 작성 가능")
    else:
        lines.append("🟡 **트리거 미충족** — `marc21_east_asian.py` inactive 유지")
    lines.append("")
    lines.append("## ADR 0004 SQLite 마이그레이션 트리거")
    lines.append(f"- 활성 사서(30일): {sql['active_30d']} (≥20 시 트리거)")
    lines.append(f"- usage.jsonl 크기: {sql['log_size_mb']} MB (≥100 시 트리거)")
    lines.append(f"- 마이그레이션 필요: {'✓ 즉시' if sql['should_migrate'] else '⏳ 아직'}")
    lines.append("")
    lines.append("## 매출 추세")
    for r in us["revenues_recent"][-6:]:
        lines.append(f"- {r['year']}-{r['month']:02d}: {r['revenue_krw']:,}원 ({r['records']}건)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="ADR 0009·0004 자율 트리거")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    report = {
        "us_trigger": evaluate_us_trigger(),
        "sqlite_trigger": evaluate_sqlite_trigger(),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        text = render_summary(report)
        print(text)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
            print(f"\n✓ 보고서 저장: {args.output}")

    # 트리거 충족 시 알림 파일 자동 생성
    if report["us_trigger"]["all_triggers_met"]:
        out = ROOT / "logs" / "triggers" / "us_activation_ready.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
