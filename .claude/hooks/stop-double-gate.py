#!/usr/bin/env python3
"""Stop hook 이중 게이트 — PO 가이드 §8.11.

종료 조건 둘 다 충족해야만 통과:
1. transcript 마지막 200줄에 `<<<TASK_COMPLETE>>>` 마커 존재
2. `pytest -q` 종료 코드 0
3. `binary_assertions.py --strict` 종료 코드 0 (19/19)

미충족 시 `decision: block` + reason → Claude가 작업 계속.

무한 루프 가드: `stop_hook_active=True`면 그냥 통과 (PO 가이드 §4.5-E).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)


def _block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    # 무한 루프 가드 — 두 번째 호출은 그냥 통과
    if data.get("stop_hook_active"):
        return 0

    transcript_path = data.get("transcript_path")
    if transcript_path and Path(transcript_path).exists():
        try:
            tail = subprocess.check_output(
                ["tail", "-200", transcript_path],
                stderr=subprocess.DEVNULL,
                timeout=10,
            ).decode("utf-8", errors="replace")
        except (subprocess.SubprocessError, OSError):
            tail = ""
        if "<<<TASK_COMPLETE>>>" not in tail:
            _block(
                "종료 마커 `<<<TASK_COMPLETE>>>` 없음. "
                "작업이 진짜 끝났는지 확인하고 응답 마지막 줄에 마커를 출력하세요."
            )

    # pytest
    pytest_res = subprocess.run(
        [str(PYTHON), "-m", "pytest", "-q", "--no-header"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if pytest_res.returncode != 0:
        tail = "\n".join(pytest_res.stdout.splitlines()[-30:])
        _block(f"pytest 실패. 종료 불가:\n```\n{tail}\n```")

    # 어셔션
    assert_res = subprocess.run(
        [str(PYTHON), str(ROOT / "scripts" / "binary_assertions.py"), "--strict"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    if assert_res.returncode != 0:
        tail = "\n".join(assert_res.stdout.splitlines()[-25:])
        _block(f"어셔션 실패. 종료 불가:\n```\n{tail}\n```")

    return 0


if __name__ == "__main__":
    sys.exit(main())
