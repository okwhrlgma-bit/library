"""
automation/router.py
메타 라우터: 작업을 Haiku로 분류 → 적절한 모델/도구/턴수로 디스패치.

사용:
    python automation/router.py "auth 모듈에 rate limiting 추가"
    echo "버그 수정해" | python automation/router.py
"""

import asyncio
import json
import os
import sys
from dataclasses import dataclass
from typing import Literal

try:
    from claude_agent_sdk import ClaudeAgentOptions, query
except ImportError:
    print("ERROR: pip install claude-agent-sdk", file=sys.stderr)
    sys.exit(1)


TaskKind = Literal[
    "trivial",
    "code-edit",
    "refactor",
    "architecture",
    "research",
    "debug",
    "data-analysis",
    "unsafe",
]


@dataclass
class RouteDecision:
    kind: TaskKind
    model: str
    tools: list[str]
    max_turns: int
    permission_mode: str
    reason: str


CLASSIFIER_PROMPT = """\
다음 작업을 분류해. 반드시 JSON만 출력. 다른 텍스트 금지.

작업: {task}

스키마:
{{
  "kind": "trivial|code-edit|refactor|architecture|research|debug|data-analysis|unsafe",
  "reason": "왜 그 카테고리인지 한 줄"
}}

판단 기준:
- trivial: 1줄 답변 가능, 코드 변경 없음
- code-edit: 5파일 미만 작은 수정
- refactor: 5파일 이상 또는 구조 변경
- architecture: 신규 시스템 설계, 결정 필요
- research: 외부 정보 검색 필요
- debug: 에러 진단·재현·수정
- data-analysis: 데이터 처리·집계·시각화
- unsafe: 시크릿·결제·삭제·프로덕션 직접 영향, 가격 변경, DB 스키마 변경
"""


ROUTING_TABLE: dict[TaskKind, dict] = {
    "trivial": {
        "model": "claude-haiku-4-5",
        "tools": [],
        "max_turns": 1,
        "permission_mode": "acceptEdits",
    },
    "code-edit": {
        "model": "claude-sonnet-4-6",
        "tools": ["Read", "Edit", "Glob", "Grep"],
        "max_turns": 5,
        "permission_mode": "acceptEdits",
    },
    "refactor": {
        "model": "claude-sonnet-4-6",
        "tools": ["Read", "Edit", "Write", "Glob", "Grep", "Bash"],
        "max_turns": 15,
        "permission_mode": "acceptEdits",
    },
    "architecture": {
        "model": "claude-opus-4-7",
        "tools": ["Read", "Glob", "Grep", "WebSearch"],
        "max_turns": 8,
        "permission_mode": "ask",
    },
    "research": {
        "model": "claude-sonnet-4-6",
        "tools": ["WebSearch", "WebFetch", "Read", "Write"],
        "max_turns": 10,
        "permission_mode": "acceptEdits",
    },
    "debug": {
        "model": "claude-sonnet-4-6",
        "tools": ["Read", "Bash", "Edit", "Grep"],
        "max_turns": 12,
        "permission_mode": "acceptEdits",
    },
    "data-analysis": {
        "model": "claude-sonnet-4-6",
        "tools": ["Read", "Write", "Bash"],
        "max_turns": 8,
        "permission_mode": "acceptEdits",
    },
    "unsafe": {
        "model": "claude-sonnet-4-6",
        "tools": [],
        "max_turns": 0,
        "permission_mode": "ask",
    },
}


async def classify(task: str) -> RouteDecision:
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        allowed_tools=[],
        permission_mode="acceptEdits",
        system_prompt="너는 작업 분류기. 오직 JSON만 반환.",
    )
    raw = ""
    async for msg in query(prompt=CLASSIFIER_PROMPT.format(task=task), options=options):
        text = getattr(msg, "text", None) or getattr(msg, "content", None)
        if isinstance(text, str):
            raw += text

    # JSON 추출 (코드펜스 제거)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if "```" in cleaned[3:] else cleaned[3:]
    cleaned = cleaned.replace("json\n", "", 1).strip("`").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # 파싱 실패 시 안전하게 unsafe로
        return RouteDecision(
            kind="unsafe",
            reason=f"분류 파싱 실패: {raw[:100]}",
            **{k: v for k, v in ROUTING_TABLE["unsafe"].items()},
        )

    kind: TaskKind = parsed.get("kind", "unsafe")
    if kind not in ROUTING_TABLE:
        kind = "unsafe"

    cfg = ROUTING_TABLE[kind]
    return RouteDecision(
        kind=kind,
        reason=parsed.get("reason", ""),
        model=cfg["model"],
        tools=cfg["tools"],
        max_turns=cfg["max_turns"],
        permission_mode=cfg["permission_mode"],
    )


async def execute(task: str, decision: RouteDecision) -> int:
    if decision.kind == "unsafe":
        print(f"\n🚫 [STOP] unsafe: {decision.reason}", file=sys.stderr)
        print("사람 검토가 필요합니다. 다음 단계:", file=sys.stderr)
        print("  1. 작업이 실제로 안전한지 직접 확인", file=sys.stderr)
        print("  2. 안전하면 슬래시 커맨드 또는 직접 수동 실행", file=sys.stderr)

        # 웹훅 알림 (있으면)
        webhook = os.environ.get("HUMAN_REVIEW_QUEUE_URL", "")
        if webhook:
            try:
                import urllib.request

                payload = json.dumps(
                    {
                        "task": task,
                        "reason": decision.reason,
                        "kind": "unsafe-routing",
                    }
                ).encode()
                req = urllib.request.Request(
                    webhook,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
        return 2

    options = ClaudeAgentOptions(
        model=decision.model,
        allowed_tools=decision.tools,
        max_turns=decision.max_turns,
        permission_mode=decision.permission_mode,
    )
    async for msg in query(prompt=task, options=options):
        text = getattr(msg, "text", None) or getattr(msg, "content", None)
        if isinstance(text, str):
            print(text, end="", flush=True)
    print()
    return 0


async def main() -> int:
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        task = sys.stdin.read().strip()
    else:
        task = input("Task: ").strip()

    if not task:
        print("ERROR: empty task", file=sys.stderr)
        return 1

    decision = await classify(task)
    print(
        f"[ROUTED] kind={decision.kind} model={decision.model} max_turns={decision.max_turns}",
        file=sys.stderr,
    )
    print(f"[REASON] {decision.reason}", file=sys.stderr)
    print("---", file=sys.stderr)

    return await execute(task, decision)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
