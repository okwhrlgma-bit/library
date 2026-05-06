#!/usr/bin/env bash
# Cycle 43 (V3 Block 3) — PostToolUse audit.jsonl append-only 로그.
#
# V3 §3.2 정합 = 모든 도구 호출 1줄 JSON·주간 리포트 입력 자산.
# 위치: ./audit.jsonl (CLAUDE_AUDIT_FILE env override 가능).
# 형식: {ts, event:"tool_call", session_id, cycle_id, payload}
#
# 기존 audit/store.py (Cycle 9) = KORMARC 레코드 단위 audit log (별도 트랙).
# 본 hook = Claude Code 도구 호출 단위 (V3 weekly_report 입력).

set -euo pipefail

INPUT=$(cat 2>/dev/null || echo "{}")
AUDIT="${CLAUDE_AUDIT_FILE:-./audit.jsonl}"

# jq 없으면 minimal fallback (passthrough만)
if ! command -v jq >/dev/null 2>&1; then
  echo '{}'
  exit 0
fi

ENTRY=$(jq -nc \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg event "tool_call" \
  --arg session "${CLAUDE_SESSION_ID:-unknown}" \
  --arg cycle "${CLAUDE_CYCLE_ID:-unknown}" \
  --argjson input "$INPUT" \
  '{ts:$ts, event:$event, session_id:$session, cycle_id:$cycle, payload:$input}' 2>/dev/null || echo "")

if [[ -n "$ENTRY" ]]; then
  echo "$ENTRY" >> "$AUDIT" 2>/dev/null || true
fi

# passthrough — hook은 도구 호출 자체를 막지 않음
echo '{}'
