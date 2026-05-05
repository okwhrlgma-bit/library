"""
automation/proposer_critic.py
Proposer-Critic 패턴: Sonnet이 제안, Opus가 비평. 통과할 때까지 반복.

사용:
    python automation/proposer_critic.py "결제 핸들러에 idempotency 추가"
"""

import asyncio
import sys

try:
    from claude_agent_sdk import ClaudeAgentOptions, query
except ImportError:
    print("ERROR: pip install claude-agent-sdk", file=sys.stderr)
    sys.exit(1)


async def collect(prompt: str, options: ClaudeAgentOptions) -> str:
    out = ""
    async for msg in query(prompt=prompt, options=options):
        text = getattr(msg, "text", None) or getattr(msg, "content", None)
        if isinstance(text, str):
            out += text
    return out


async def propose(task: str, prior_feedback: str = "") -> str:
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=8,
        system_prompt="너는 빠르고 실용적인 구현 엔지니어. 작은 단위로 변경하고 테스트도 같이 추가해.",
    )
    prompt = task
    if prior_feedback:
        prompt = f"{task}\n\n[이전 시도와 리뷰 피드백]\n{prior_feedback}\n\n위 피드백을 반영해 다시 시도."
    return await collect(prompt, options)


async def critique(task: str, proposal: str) -> tuple[bool, str]:
    options = ClaudeAgentOptions(
        model="claude-opus-4-7",
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="ask",
        max_turns=4,
        system_prompt=(
            "너는 까다로운 시니어 리뷰어. 보안·엣지케이스·성능·테스트 누락을 본다. "
            "통과면 정확히 'OK'로 시작, 아니면 'REJECT:'로 시작하고 구체적 지적 3개 이내."
        ),
    )
    prompt = (
        f"작업: {task}\n\n"
        f"제안된 구현 결과:\n{proposal}\n\n"
        f"승인하는가? 'OK ...' 또는 'REJECT: ...'로 시작."
    )
    out = await collect(prompt, options)
    head = out.strip()[:20].upper()
    return (head.startswith("OK"), out)


async def loop(task: str, max_rounds: int = 3) -> int:
    proposal = await propose(task)
    feedback = ""
    for i in range(max_rounds):
        ok, feedback = await critique(task, proposal)
        if ok:
            print(f"\n✅ [라운드 {i + 1}] 승인됨")
            print(feedback[:500])
            return 0
        print(f"\n⚠️  [라운드 {i + 1}] 거부:")
        print(feedback[:500])
        proposal = await propose(task, prior_feedback=feedback)

    print(f"\n❌ 최대 라운드({max_rounds}) 초과. 사람 개입 필요.")
    print("마지막 피드백:")
    print(feedback)
    return 1


async def main() -> int:
    if len(sys.argv) <= 1:
        print("Usage: python proposer_critic.py '<작업>'", file=sys.stderr)
        return 1
    task = " ".join(sys.argv[1:])
    return await loop(task)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
