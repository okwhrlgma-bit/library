#!/usr/bin/env bash
# PreToolUse 정규식 가드 (PO 가이드 §8.10) — chained command 우회 차단
# bypassPermissions 모드에서도 hook deny는 강제됨

INPUT=$(cat)
CMD=$(echo "$INPUT" | "/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe" -c "import sys, json; d=json.load(sys.stdin); print((d.get('tool_input') or {}).get('command') or '')")

# 절대 금지 패턴
PATTERNS=(
  '\brm[[:space:]]+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)[[:space:]]+(/|~|\$HOME|\*)'
  '\bmkfs\.'
  '\bdd[[:space:]]+if=.+of=/dev/'
  '\bgit([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+push.*--force\b'
  '\bgit.*reset[[:space:]]+--hard[[:space:]]+(origin|HEAD~)'
  '\bgit[[:space:]]+filter-branch\b'
  '\bgit[[:space:]]+filter-repo\b'
  'DROP[[:space:]]+(TABLE|DATABASE|SCHEMA)\b'
  'TRUNCATE[[:space:]]+TABLE\b'
  '\bFLUSHALL\b'
  '\bdb\.dropDatabase\('
  'KORMARC_EAST_ASIAN_ACTIVATED=1'
)

for pat in "${PATTERNS[@]}"; do
  if echo "$CMD" | grep -qE "$pat"; then
    "/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe" -c "import json, sys; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'irreversible-guard: ${pat//\'/} 차단 — ADR 0009 또는 자율-게이트 위반'}}))"
    exit 0
  fi
done
exit 0
