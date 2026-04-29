#!/usr/bin/env python3
"""PostCompact hook — 컨텍스트 압축 후 핵심 룰 자동 reinject.

PO 가이드 5대 멈춤 패턴 §4 (컨텍스트 한계·auto-compaction)에서 핵심 룰이
사라지는 문제 회피.

압축 후 다음 4 항목을 additionalContext로 다시 주입:
1. CLAUDE.md §6 자율성 4단계 + 종료 마커 + 5대 멈춤 회피
2. learnings.md 마지막 30 줄 (직전 세션 학습)
3. .claude/rules/autonomy-gates.md 캐시카우 평가축
4. 어셔션 통과율 (binary_assertions --json 결과)

stdin: PostCompact 이벤트 (압축 요약 포함)
stdout: hookSpecificOutput.additionalContext
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
from pathlib import Path

with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def _read_section(path: Path, max_lines: int = 50) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def _assertion_summary() -> str:
    try:
        proc = subprocess.run(
            [str(PYTHON), str(ROOT / "scripts" / "binary_assertions.py"), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            cwd=ROOT,
        )
        if proc.returncode != 0:
            return "어셔션 평가 실패"
        try:
            data = json.loads(proc.stdout.strip().split("\n")[-1])
            return f"어셔션 {data.get('passed', '?')}/{data.get('total', '?')} ({data.get('rate', 0):.0%})"
        except (json.JSONDecodeError, IndexError):
            return "어셔션 결과 파싱 실패"
    except (subprocess.SubprocessError, OSError):
        return "어셔션 실행 실패"


def main() -> int:
    with contextlib.suppress(json.JSONDecodeError):
        json.load(sys.stdin)

    rules = _read_section(ROOT / ".claude" / "rules" / "autonomy-gates.md", 40)
    learnings_tail = _read_section(ROOT / "learnings.md", 30)
    assertion = _assertion_summary()

    context = f"""## 컨텍스트 압축 후 자동 재주입 (PostCompact hook)

### 캐시카우 평가축 (절대 우선)
- §0 사서 마크 시간 단축 (8분 → 2분)
- §12 사서 본인 예산 결제 의향 ↑ (캐시카우 직결)
- 평가축 음수면 commit 거부

### 종료 규약
- `<<<TASK_COMPLETE>>>` 마커 + pytest 통과 + 어셔션 100% = 종료 게이트

### 5대 멈춤 패턴 회피
- 모호한 결정 → 보수적 + DECISIONS.md
- 테스트 3회 실패 → SKIPPED.md + 다음
- 자가 디버그 루프 → 30 iter 한계
- 컨텍스트 한계 → 이 PostCompact가 자동 해결
- 의존성 실패 → 새 의존성 금지

### 현재 상태
- {assertion}
- 야간 모드: 항상 활성 (acceptEdits + irreversible-guard 7 패턴)

### 자율 게이트 (마지막 40줄)
{rules}

### learnings 직전 학습 (마지막 30줄)
{learnings_tail}
"""

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostCompact",
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
