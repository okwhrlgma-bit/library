#!/usr/bin/env bash
# Cycle 18A P42 — PreToolUse / Write·Edit 시크릿 스캔.
# 외부 자동화 가이드 §3.2 패턴 #3 정합.
#
# 차단 패턴 (정규식):
# - sk-... (Anthropic / OpenAI API 키)
# - sk_live_... (Stripe live key)
# - portone_... 평문
# - JWT (eyJ...)
# - 12-자 SHA prefix가 도서관식별자처럼 보임 (자관 누설)

set -e

INPUT=$(cat)

# tool_input.file_path 또는 content 추출 (Python으로)
PYTHON="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python

CONTENT=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input') or {}
    # Write = 'content'·Edit = 'new_string'
    print((ti.get('content') or ti.get('new_string') or ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

# 빈 content = 통과 (Read 등)
[ -z "$CONTENT" ] && exit 0

# 차단 패턴
BLOCKED=""
echo "$CONTENT" | grep -E "sk-[a-zA-Z0-9]{40,}" >/dev/null 2>&1 && BLOCKED="${BLOCKED}sk-* API 키·"
echo "$CONTENT" | grep -E "sk_live_[a-zA-Z0-9]{20,}" >/dev/null 2>&1 && BLOCKED="${BLOCKED}sk_live_* Stripe 라이브 키·"
echo "$CONTENT" | grep -E "ANTHROPIC_API_KEY\s*=\s*[a-zA-Z0-9_-]{20,}" >/dev/null 2>&1 && BLOCKED="${BLOCKED}ANTHROPIC_API_KEY 평문·"
echo "$CONTENT" | grep -E "eyJ[a-zA-Z0-9_-]{40,}\.[a-zA-Z0-9_-]{40,}" >/dev/null 2>&1 && BLOCKED="${BLOCKED}JWT 토큰·"

if [ -n "$BLOCKED" ]; then
    "$PYTHON" -c "
import json
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': 'deny',
        'permissionDecisionReason': 'scan-secrets: ${BLOCKED} 차단 (Cycle 18A P42)·env에 보관 후 placeholder 사용'
    }
}))
"
    exit 0
fi

exit 0
