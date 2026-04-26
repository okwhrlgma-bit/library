"""Trust Counter 보고 — RSI Stage 1 출력.

`.claude/metrics/trust.json` 읽고:
- 신뢰도 ≥ 0.95 + n ≥ 20 → 자동 allow 후보 (Stage 2 진입 가능)
- 신뢰도 < 0.6 → deny 후보 (오작동 도구 식별)
- 그 외 → 관찰 (n 더 모아야)

매월 1회 실행 권장. PR 검토용 마크다운 출력.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
TRUST = ROOT / ".claude" / "metrics" / "trust.json"

AUTO_ALLOW_RATIO = 0.95
AUTO_ALLOW_N = 20
DENY_RATIO = 0.6


def _load() -> dict:
    if not TRUST.exists():
        return {}
    try:
        return json.loads(TRUST.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def render(db: dict) -> str:
    if not db:
        return "Trust 데이터 없음 — `.claude/hooks/post-trust.py`가 실행되어야 누적됨."

    rows = sorted(
        ((k, v) for k, v in db.items()),
        key=lambda kv: (kv[1].get("n", 0), kv[1].get("ratio", 0)),
        reverse=True,
    )

    auto_allow = [k for k, v in rows if v["ratio"] >= AUTO_ALLOW_RATIO and v["n"] >= AUTO_ALLOW_N]
    deny_candidates = [k for k, v in rows if v["ratio"] < DENY_RATIO and v["n"] >= 5]

    lines: list[str] = []
    lines.append("# Trust Counter Report (RSI Stage 1)")
    lines.append("")
    lines.append(f"Total tracked tools: {len(db)}")
    lines.append("")
    lines.append("## 자동 allow 후보 (ratio ≥ 0.95 + n ≥ 20)")
    if auto_allow:
        for k in auto_allow:
            v = db[k]
            lines.append(f"- ✓ `{k}` — {v['ratio']:.0%} ({v['success']}/{v['n']})")
    else:
        lines.append("- (없음 — 더 누적 필요)")
    lines.append("")
    lines.append("## deny 후보 (ratio < 0.6 + n ≥ 5)")
    if deny_candidates:
        for k in deny_candidates:
            v = db[k]
            lines.append(f"- ❌ `{k}` — {v['ratio']:.0%} ({v['success']}/{v['n']})")
    else:
        lines.append("- (없음 — 도구가 모두 정상)")
    lines.append("")
    lines.append("## 전체 (n 내림차순)")
    for k, v in rows:
        mark = "✓" if v["ratio"] >= 0.95 else ("⚠" if v["ratio"] >= 0.6 else "❌")
        lines.append(
            f"- {mark} `{k}` — {v['ratio']:.0%} ({v['success']}/{v['n']})"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    db = _load()

    if args.json:
        print(json.dumps(db, ensure_ascii=False, indent=2))
    else:
        text = render(db)
        print(text)
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
            print(f"\n✓ 저장: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
