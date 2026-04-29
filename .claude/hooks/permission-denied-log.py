#!/usr/bin/env python3
"""PermissionDenied hook — auto-mode 분류기 deny 시 우회 결정 자동 기록.

PO 5대 멈춤 패턴 §1 (모호한 결정) 자동 회피.

deny 발생 시:
- DECISIONS.md에 한 줄 기록 (날짜·도구·이유·우회 방향)
- 다음 자율 사이클이 같은 함정 회피

stdin: PermissionDenied 이벤트 (tool_name·tool_input·deny_reason)
stdout: 없음 (단순 누적)
"""

from __future__ import annotations

import contextlib
import json
import sys
import time
from pathlib import Path

with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = data.get("tool_name", "?")
    tool_input = data.get("tool_input") or {}
    deny_reason = (
        data.get("deny_reason")
        or data.get("permissionDecisionReason")
        or "auto-mode 분류기 거부"
    )

    # 입력 요약 (50자)
    summary = ""
    if tool_name == "Bash":
        summary = str(tool_input.get("command") or "")[:80]
    elif tool_name in ("Edit", "Write"):
        summary = str(tool_input.get("file_path") or "")[:80]
    else:
        summary = json.dumps(tool_input, ensure_ascii=False)[:80]

    decisions = ROOT / "DECISIONS.md"
    decisions.parent.mkdir(parents=True, exist_ok=True)
    if not decisions.exists():
        decisions.write_text(
            "# 야간 자율 결정 로그\n\n> 모호한 지점에서 더 안전·보수적 옵션을 선택한 근거.\n\n",
            encoding="utf-8",
        )

    ts = time.strftime("%Y-%m-%d %H:%M KST", time.localtime())
    entry = (
        f"\n## {ts} — PermissionDenied: {tool_name}\n"
        f"- 입력: `{summary}`\n"
        f"- 사유: {deny_reason}\n"
        f"- 우회: 다음 단계로 진행 (자율 게이트 §자동 우회)\n"
    )
    with decisions.open("a", encoding="utf-8") as f:
        f.write(entry)

    return 0


if __name__ == "__main__":
    sys.exit(main())
