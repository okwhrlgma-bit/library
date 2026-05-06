"""Cycle 47 (V3 Block 4·외부 256 출처) — Weekly Ralph Report.

V3 §4.3 정합 = 7일 audit.jsonl + git log + budget state → markdown 리포트.
13 핵심 메트릭 중 11 = pandas/numpy 결정적 계산 (Haiku 호출 0).

활성: audit.jsonl ≥ 7일 누적 (Cycle 43 hook 활성 후 1주).
미활성 = graceful 메시지 ("데이터 부족·N일 더 누적 필요").

원칙 (V3 §4.10):
- 통계로 풀리는 것 = 통계로 (LLM 금지)
- LLM은 자연어 라벨링·의미적 동치만 (Cycle 46 router_patcher와 통합)

실행:
    python3 automation/weekly_report.py          # report.md 생성
    python3 automation/weekly_report.py --json   # 메트릭 dict JSON 출력
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "audit.jsonl"
USAGE = ROOT / "usage.json"
PROGRESS = ROOT / "PROGRESS.md"
LEARNINGS = ROOT / "learnings.md"
OUT = ROOT / "report.md"

WEEK_START = datetime.now(UTC) - timedelta(days=7)


def load_audit() -> list[dict]:
    """audit.jsonl 7일치 로드. 부재 시 빈 리스트."""
    if not AUDIT.exists():
        return []
    rows: list[dict] = []
    with AUDIT.open(encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_str = r.get("ts", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue
            if ts < WEEK_START:
                continue
            rows.append(r)
    return rows


def load_usage() -> dict:
    """usage.json (수동 또는 ccusage·외부 자동 집계기)."""
    if USAGE.exists():
        try:
            return json.loads(USAGE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"daily": [], "by_model": {}}
    return {"daily": [], "by_model": {}}


def git_log_week() -> list[dict]:
    """최근 7일 git commit."""
    fmt = "%H%x09%an%x09%aI%x09%s"
    try:
        result = subprocess.run(
            ["git", "log", f"--since={WEEK_START.isoformat()}", f"--pretty=format:{fmt}"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=ROOT,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if not result.stdout:
        return []
    return [
        dict(zip(["sha", "author", "ts", "msg"], line.split("\t", 3), strict=False))
        for line in result.stdout.strip().splitlines()
        if line
    ]


def compute_metrics(rows: list[dict], usage: dict) -> dict[str, Any]:
    """13 핵심 메트릭 중 통계 결정적 계산 (V3 §4.2)."""
    if not rows:
        return {
            "error": "audit.jsonl 7일 데이터 부족",
            "rows_found": 0,
            "hint": "Cycle 43 audit-log.sh hook 활성 후 7일 누적 필요",
        }

    # cycle_end 이벤트만 추출 (V3 weekly_report 정합)
    cycles = [r for r in rows if r.get("event") == "cycle_end"]
    n_total = len(cycles)
    n_done = sum(1 for c in cycles if c.get("status") == "COMPLETED")
    n_block = sum(1 for c in cycles if c.get("status") == "BLOCKED")

    # 비용 (usage.json 또는 cycle_end payload·둘 다 가능)
    weekly_cost = sum(d.get("cost_usd", 0) for d in usage.get("daily", []))
    if weekly_cost == 0:
        weekly_cost = sum(c.get("cost_usd", 0) for c in cycles)

    # M03: 평균 반복
    iterations = [c.get("iterations", 0) for c in cycles if c.get("iterations")]
    avg_iter = sum(iterations) / len(iterations) if iterations else 0

    metrics: dict[str, Any] = {
        "rows_total": len(rows),
        "cycles_total": n_total,
        "M01_success_rate": n_done / max(n_total, 1),
        "M02_done_blocked_ratio": n_done / max(n_block, 1),
        "M03_avg_iterations": avg_iter,
        "M04_avg_cost_per_cycle": weekly_cost / max(n_total, 1),
        "M04_total_weekly_cost": weekly_cost,
        "n_done": n_done,
        "n_blocked": n_block,
    }

    # M06: 카테고리별 실패 분포
    categories = [c.get("category", "unknown") for c in cycles if c.get("category")]
    if categories:
        metrics["M06_top_categories"] = dict(Counter(categories).most_common(5))

    # M09: 컨텍스트 포화도 (147k 임계 = V3 §4.2)
    ctx_tokens = [c.get("ctx_tokens", 0) for c in cycles if c.get("ctx_tokens")]
    if ctx_tokens:
        n_saturated = sum(1 for t in ctx_tokens if t > 147_000)
        metrics["M09_ctx_saturation"] = n_saturated / len(ctx_tokens)

    return metrics


def render_markdown(metrics: dict, commits: list[dict]) -> str:
    """metrics + commits → markdown 리포트."""
    out = [f"# Weekly Ralph Report — {datetime.now(UTC).date().isoformat()}\n"]
    out.append(f"> 7일 윈도우: {WEEK_START.date().isoformat()} → 현재\n")

    if "error" in metrics:
        out.append("## ⚠ 데이터 부족\n")
        out.append(f"- 사유: {metrics['error']}")
        out.append(f"- 발견 row: {metrics.get('rows_found', 0)}")
        out.append(f"- 힌트: {metrics.get('hint', '')}\n")
        out.append("## Git commits (참고용)\n```")
        for c in commits[:10]:
            out.append(f"{c['sha'][:7]} {c['ts'][:10]} {c['msg'][:60]}")
        out.append("```")
        return "\n".join(out)

    out.append("## 1. KPI (V3 §4.2 13 메트릭)\n```")
    out.append(f"Rows total            : {metrics['rows_total']}")
    out.append(f"Cycles total          : {metrics['cycles_total']}")
    out.append(f"Success rate (M01)    : {metrics['M01_success_rate']:.1%}   임계 70%")
    out.append(f"DONE:BLOCKED (M02)    : {metrics['M02_done_blocked_ratio']:.2f} : 1")
    out.append(f"Avg iterations (M03)  : {metrics['M03_avg_iterations']:.1f}")
    out.append(f"Avg cost/cycle (M04)  : ${metrics['M04_avg_cost_per_cycle']:.3f}")
    out.append(f"Weekly spend          : ${metrics['M04_total_weekly_cost']:.2f}")
    if "M09_ctx_saturation" in metrics:
        out.append(f"Ctx saturation (M09)  : {metrics['M09_ctx_saturation']:.1%}")
    out.append("```\n")

    if "M06_top_categories" in metrics:
        out.append("## 2. 카테고리 분포 (M06)\n```")
        for cat, n in metrics["M06_top_categories"].items():
            out.append(f"  {cat:20s}: {n}")
        out.append("```\n")

    # 자동 권장 액션 (V3 §4.3 정합)
    actions = []
    if metrics["M01_success_rate"] < 0.7:
        actions.append(f"- ❌ 성공률 {metrics['M01_success_rate']:.0%} < 70% → router unsafe 추가")
    if metrics["M03_avg_iterations"] > 15:
        actions.append("- ⚠ 평균 반복 > 15 → PROMPT 분해/subagent 위임")
    if metrics["M04_avg_cost_per_cycle"] > 3:
        actions.append("- 💰 cycle당 > $3 → Haiku 비중 확대")
    if metrics.get("M09_ctx_saturation", 0) > 0.15:
        actions.append("- 🧠 ctx > 15% 포화 → 서브에이전트 분리")
    if not actions:
        actions.append("- ✅ 모든 임계 정상")

    out.append("## 3. 자동 권장 액션\n" + "\n".join(actions) + "\n")

    out.append(f"## 4. 주간 commits ({len(commits)}건)\n```")
    for c in commits[:15]:
        out.append(f"{c['sha'][:7]} {c['ts'][:10]} {c['msg'][:60]}")
    out.append("```")

    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="V3 Block 4 Weekly Report")
    ap.add_argument("--json", action="store_true", help="metrics dict JSON 출력")
    args = ap.parse_args()

    rows = load_audit()
    usage = load_usage()
    commits = git_log_week()
    metrics = compute_metrics(rows, usage)

    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        return 0

    md = render_markdown(metrics, commits)
    OUT.write_text(md, encoding="utf-8")
    print(f"✓ wrote {OUT} ({len(md)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
