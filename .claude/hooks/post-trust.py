#!/usr/bin/env python3
"""Trust Counter — PO 가이드 §5.6 RSI Stage 1.

매 PostToolUse에서 (도구·서브 명령) 단위 성공/실패 누적 →
`.claude/metrics/trust.json`에 저장.

향후 PreToolUse가 신뢰도 ≥ 0.95 + n ≥ 20이면 자동 allow,
< 0.6이면 deny (Stage 2 도입 시).

스토리지 형식:
{
  "Bash:pytest": {"success": 18, "fail": 0, "ratio": 1.0, "n": 18, "last_ts": ...},
  "Bash:git": {...},
  "Edit": {...}
}
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TRUST = ROOT / ".claude" / "metrics" / "trust.json"


def _key(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Bash":
        cmd = str(tool_input.get("command") or "")
        # 명령어 첫 단어 (절대 경로 빼고)
        first = cmd.strip().split()[0] if cmd.strip() else ""
        first = first.split("/")[-1] if "/" in first else first
        return f"Bash:{first or '?'}"
    return tool_name


def _is_ok(tool_response: dict) -> bool:
    """exit_code 0 + error 없으면 성공."""
    if not isinstance(tool_response, dict):
        return True  # 응답 형식 모르면 일단 성공으로
    if "exit_code" in tool_response:
        return tool_response.get("exit_code") == 0
    return not tool_response.get("error")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_name = data.get("tool_name", "?")
    tool_input = data.get("tool_input") or {}
    tool_response = data.get("tool_response") or {}

    key = _key(tool_name, tool_input)
    ok = _is_ok(tool_response)

    TRUST.parent.mkdir(parents=True, exist_ok=True)
    db: dict = {}
    if TRUST.exists():
        try:
            db = json.loads(TRUST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            db = {}

    rec = db.setdefault(key, {"success": 0, "fail": 0, "ratio": 0.0, "n": 0, "last_ts": 0})
    if ok:
        rec["success"] += 1
    else:
        rec["fail"] += 1
    rec["n"] = rec["success"] + rec["fail"]
    rec["ratio"] = rec["success"] / rec["n"] if rec["n"] else 0.0
    rec["last_ts"] = int(time.time())

    TRUST.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
