"""Pattern Library — RSI Stage 2 (PO 가이드 §5.6).

매 commit 후 git diff에서 재사용 가능한 패턴 추출 →
`.claude/patterns/<이름>.md`로 저장. 누적 후 사용 빈도 top-5는
`.claude/skills/`로 자동 승격 후보.

추출 대상:
- 새 모듈 + 단위 테스트 ≥3건 패턴 (testCreated)
- 신규 어셔션 추가 패턴 (assertionAdded)
- 신규 ADR 패턴 (adrAdded)
- 신규 hook 패턴 (hookAdded)

저장 형식 (`.claude/patterns/<유형>-<날짜>.md`):
```
---
pattern: testCreated
date: YYYY-MM-DD
files: [...]
commit: <hash>
description: ...
---
[diff 핵심 발췌]
```

매주 1회 실행 권장. 누적 데이터로 자율 우선순위 자동 갱신.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PATTERNS_DIR = ROOT / ".claude" / "patterns"


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout


def _classify_diff(files: list[str]) -> list[str]:
    """diff 파일 목록 → 적용 가능한 패턴 유형들."""
    types: list[str] = []
    has_test = any(f.startswith("tests/") and f.endswith(".py") for f in files)
    has_src = any(f.startswith("src/") and f.endswith(".py") for f in files)
    has_assertion = any(f == "scripts/binary_assertions.py" for f in files)
    has_adr = any(f.startswith("docs/adr/") and re.match(r".*\d{4}-.+\.md$", f) for f in files)
    has_hook = any(f.startswith(".claude/hooks/") for f in files)
    has_agent = any(f.startswith(".claude/agents/") and f.endswith(".md") for f in files)
    has_rule = any(f.startswith(".claude/rules/") and f.endswith(".md") for f in files)

    if has_test and has_src:
        types.append("testCreated")
    if has_assertion:
        types.append("assertionAdded")
    if has_adr:
        types.append("adrAdded")
    if has_hook:
        types.append("hookAdded")
    if has_agent:
        types.append("agentAdded")
    if has_rule:
        types.append("ruleAdded")
    return types


def extract_recent(*, n_commits: int = 20) -> list[dict]:
    """최근 N commit에서 패턴 추출. 이미 있는 패턴은 skip."""
    PATTERNS_DIR.mkdir(parents=True, exist_ok=True)

    log = _git(["log", "--format=%H|%s|%ad", "--date=short", f"-{n_commits}"])
    extracted: list[dict] = []

    for line in log.splitlines():
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        sha, subject, date = parts
        sha_short = sha[:8]
        files_text = _git(["show", "--stat", "--format=", sha])
        files = [
            line_.strip().split(" | ")[0].strip()
            for line_ in files_text.splitlines()
            if " | " in line_
        ]
        types = _classify_diff(files)
        if not types:
            continue

        for ptype in types:
            out = PATTERNS_DIR / f"{ptype}-{sha_short}.md"
            if out.exists():
                continue
            content = (
                f"---\n"
                f"pattern: {ptype}\n"
                f"commit: {sha_short}\n"
                f"date: {date}\n"
                f"subject: {subject}\n"
                f"files: {files[:10]}\n"
                f"---\n\n"
                f"## 변경 요약\n{subject}\n\n"
                f"## 파일 ({len(files)}건)\n" + "\n".join(f"- `{f}`" for f in files[:20]) + "\n"
            )
            out.write_text(content, encoding="utf-8")
            extracted.append({"pattern": ptype, "commit": sha_short, "files_count": len(files)})

    return extracted


def summary() -> dict:
    """패턴 유형별 빈도 + top-5 SKILL 승격 후보."""
    PATTERNS_DIR.mkdir(parents=True, exist_ok=True)
    by_type: dict[str, int] = {}
    for p in PATTERNS_DIR.glob("*.md"):
        ptype = p.name.split("-")[0]
        by_type[ptype] = by_type.get(ptype, 0) + 1
    ranked = sorted(by_type.items(), key=lambda kv: -kv[1])
    return {
        "total_patterns": sum(by_type.values()),
        "by_type": dict(ranked),
        "promotion_candidates": [k for k, v in ranked if v >= 3][:5],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commits", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    if not args.summary_only:
        extracted = extract_recent(n_commits=args.commits)
        if args.json:
            print(json.dumps(extracted, ensure_ascii=False, indent=2))
        else:
            print(f"신규 패턴 {len(extracted)}건 추출")
            for e in extracted:
                print(f"  · {e['pattern']} ({e['commit']}, files {e['files_count']})")

    s = summary()
    if args.json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
    else:
        print()
        print(f"## 누적 요약 (총 {s['total_patterns']}건)")
        for k, v in s["by_type"].items():
            print(f"  · {k}: {v}건")
        if s["promotion_candidates"]:
            print(f"\n## SKILL 승격 후보 (≥3건): {', '.join(s['promotion_candidates'])}")

    # 누적 메트릭 (Stage 3 ratchet 입력)
    metrics_path = ROOT / "logs" / "evals" / "patterns.jsonl"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {"ts": int(datetime.now().timestamp()), **s},
                ensure_ascii=False,
            )
            + "\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
