"""갈래 B Cycle 43A (V3 §3.7·외부 256 출처) — 3-Layer Cost Guard.

V3 Block 2 = Stream-json 파서 + Slack + Hard Stop·외부 watchdog.
실시간 차단 = (1) cost_supervisor + (2) PreToolUse hook + (3) Stop hook 3 계층.

원칙 (V3 §3 결론):
- Anthropic Admin Usage API = 5분 지연·하드 스톱 부적합 (사후 정산만)
- --max-budget-usd = 공식 cli-reference 미등재·보조만·단독 의존 금지
- 외부 watchdog = 1순위 하드 스톱 (이 모듈)

기존 모듈 정합:
- src/kormarc_auto/budget/tracker.py (Cycle 19A) = 일일 USD 예산 (장기 누적)
- automation/supervisor.py (Cycle 21 차용) = 멀티 프로젝트 큐 디스패치
- 본 모듈 = 세션 단위 stream-json 파싱·실시간 차단·Slack 알림 (단일 세션)

원본 출처: ghuntley.com/ralph + claude-saas-starter v1.1.0 + V3 §3.7.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# V3 §3.5 검증: 2026-05-06 기준 모델 가격 (USD per 1M tokens)
PRICING: dict[str, dict[str, float]] = {
    "claude-haiku-4-5": {
        "in": 1.00,
        "out": 5.00,
        "cache_read": 0.10,
        "cache_write_5m": 1.25,
    },
    "claude-sonnet-4-6": {
        "in": 3.00,
        "out": 15.00,
        "cache_read": 0.30,
        "cache_write_5m": 3.75,
    },
    "claude-opus-4-7": {
        "in": 5.00,
        "out": 25.00,
        "cache_read": 0.50,
        "cache_write_5m": 6.25,
    },
}

DEFAULT_STATE_FILE = Path(os.environ.get("CLAUDE_BUDGET_STATE", "/tmp/claude-budget.json"))


def price_lookup(model: str) -> dict[str, float]:
    """모델 string → 가격 dict (모르면 보수적·Opus 4.7 기준)."""
    for k, p in PRICING.items():
        if model.startswith(k):
            return p
    return PRICING["claude-opus-4-7"]


def cost_from_usage(model: str, usage: dict) -> float:
    """usage dict → USD 비용."""
    p = price_lookup(model)
    return (
        usage.get("input_tokens", 0) * p["in"]
        + usage.get("output_tokens", 0) * p["out"]
        + usage.get("cache_read_input_tokens", 0) * p["cache_read"]
        + usage.get("cache_creation_input_tokens", 0) * p["cache_write_5m"]
    ) / 1_000_000


def slack_post(webhook: str, text: str) -> None:
    """Slack webhook 알림. 실패해도 계속 진행."""
    if not webhook:
        return
    try:
        req = urllib.request.Request(
            webhook,
            data=json.dumps({"text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5).read()
    except Exception as e:
        print(f"[cost_supervisor] slack fail: {e}", file=sys.stderr)


def write_state(state_file: Path, data: dict) -> None:
    """atomic write (PreToolUse hook이 동시 read 안전)."""
    tmp = state_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(data))
    tmp.replace(state_file)


def parse_stream_event(line: str) -> dict | None:
    """stream-json NDJSON 한 줄 파싱."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def main() -> int:  # pragma: no cover (subprocess wrapper)
    ap = argparse.ArgumentParser(description="V3 §3.7 3-Layer Cost Guard (단일 세션 watchdog)")
    ap.add_argument("--soft", type=float, required=True, help="soft cap (warning)")
    ap.add_argument("--hard", type=float, required=True, help="hard cap (SIGTERM)")
    ap.add_argument("--per-iter", type=float, required=True, help="per-iteration max")
    ap.add_argument("--slack-webhook", default=os.environ.get("SLACK_WEBHOOK", ""))
    ap.add_argument("--state-file", default=str(DEFAULT_STATE_FILE), help="budget state file")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        print("usage: cost_supervisor.py --soft N --hard N --per-iter N -- claude -p ...")
        return 1

    state_file = Path(args.state_file)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr, bufsize=1, text=True)
    if proc.stdout is None:
        return 1

    cumulative = 0.0
    iter_cost = 0.0
    iteration = 0
    last_model = "unknown"
    soft_warned = False
    eighty_warned = False
    started = time.time()

    try:
        for raw in proc.stdout:
            ev = parse_stream_event(raw)
            if ev is None:
                continue
            etype = ev.get("type")
            esub = ev.get("subtype")

            if etype == "system" and esub == "init":
                last_model = ev.get("model", last_model)
                slack_post(
                    args.slack_webhook,
                    f":rocket: cost_supervisor start model={last_model} "
                    f"soft=${args.soft} hard=${args.hard}",
                )
            elif etype == "assistant":
                u = ev.get("message", {}).get("usage", {})
                if u:
                    delta = cost_from_usage(last_model, u)
                    cumulative += delta
                    iter_cost += delta
            elif etype == "result":
                # V3 §3.2: total_cost_usd = 공식값 (보정용)
                auth = ev.get("total_cost_usd")
                if auth is not None:
                    cumulative = auth
                iteration += 1
                slack_post(
                    args.slack_webhook,
                    f":checkered_flag: iter#{iteration} ${iter_cost:.4f} cumul=${cumulative:.4f}",
                )
                if iter_cost > args.per_iter:
                    slack_post(
                        args.slack_webhook,
                        f":warning: per-iter ${iter_cost:.2f} > ${args.per_iter}",
                    )
                    write_state(state_file, {"abort": True, "reason": "per_iter_cap"})
                    proc.terminate()
                    break
                iter_cost = 0.0

            pct = cumulative / args.hard if args.hard else 0
            if not soft_warned and cumulative >= args.soft:
                soft_warned = True
                slack_post(
                    args.slack_webhook,
                    f":warning: SOFT ${args.soft} hit (${cumulative:.4f})",
                )
            if not eighty_warned and pct >= 0.80:
                eighty_warned = True
                slack_post(
                    args.slack_webhook,
                    f":rotating_light: 80% ${cumulative:.4f}/${args.hard}",
                )
            if cumulative >= args.hard:
                slack_post(
                    args.slack_webhook,
                    ":octagonal_sign: HARD CAP <!channel> SIGTERM",
                )
                write_state(
                    state_file,
                    {"abort": True, "reason": "hard_cap", "cumulative": cumulative},
                )
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return 2
            write_state(
                state_file,
                {
                    "cumulative": cumulative,
                    "iteration": iteration,
                    "last_model": last_model,
                    "started": started,
                    "abort": False,
                },
            )
    except KeyboardInterrupt:
        proc.terminate()
        return 130

    rc = proc.wait()
    slack_post(
        args.slack_webhook,
        f":white_check_mark: end rc={rc} 총=${cumulative:.4f} iters={iteration}",
    )
    return rc


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
