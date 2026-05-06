#!/usr/bin/env bash
# Cycle 43 (V3 §3.7 Block 2 Layer 2) — PreToolUse 비용 캡 차단.
#
# State file = cost_supervisor.py가 매 turn write·여기서 read.
# abort=true 또는 cumulative >= CLAUDE_HARD_CAP = exit 2 (deny + 모델 피드백).
# 80%+ = additionalContext로 경고 (allow).

set -euo pipefail
STATE="${CLAUDE_BUDGET_STATE:-/tmp/claude-budget.json}"
HARD="${CLAUDE_HARD_CAP:-20.00}"

INPUT=$(cat 2>/dev/null || echo "{}")

if [[ ! -f "$STATE" ]]; then
  echo '{}'
  exit 0
fi

# jq 없으면 silent passthrough (안전 기본값)
if ! command -v jq >/dev/null 2>&1; then
  echo '{}'
  exit 0
fi

ABORT=$(jq -r '.abort // false' < "$STATE" 2>/dev/null || echo "false")
CUMUL=$(jq -r '.cumulative // 0' < "$STATE" 2>/dev/null || echo "0")

# Hard cap 또는 abort 플래그 = deny
if [[ "$ABORT" == "true" ]] || awk -v c="$CUMUL" -v h="$HARD" 'BEGIN{exit !(c>=h)}'; then
  jq -nc --arg r "budget exceeded: \$$CUMUL >= \$$HARD" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 2
fi

# 80% 도달 = additionalContext 경고 (allow)
if awk -v c="$CUMUL" -v h="$HARD" 'BEGIN{exit !(c >= 0.8*h)}'; then
  jq -nc --arg m "BUDGET WARNING: \$$CUMUL of \$$HARD. Wrap up." \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"allow",additionalContext:$m}}'
  exit 0
fi

echo '{}'
