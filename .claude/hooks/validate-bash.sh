#!/usr/bin/env bash
# Cycle 21 (V2 §10.1·차용) — PreToolUse Bash 위험 패턴 차단.
# exit 2 = 차단 + 모델에 사유 피드백.

INPUT_JSON=$(cat 2>/dev/null || echo "{}")
PYTHON="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python

CMD=$(echo "$INPUT_JSON" | "$PYTHON" -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print((d.get('tool_input') or {}).get('command') or '')
except Exception:
    print('')
" 2>/dev/null || echo "")

# 위험 패턴 (V2 §10.1)
DENY_PATTERNS=(
  'rm -rf /'
  'rm -rf ~'
  'rm -rf \*'
  'sudo'
  '> /dev/sd[a-z]'
  'curl .* \| (sh|bash)'
  'wget .* \| (sh|bash)'
  ':\(\)\{ :\|:& \};:'
  'mkfs'
  'dd if='
  'git push.*--force'
  'git reset --hard'
  'git filter-branch'
)

for pat in "${DENY_PATTERNS[@]}"; do
  if [[ "$CMD" =~ $pat ]]; then
    echo "DENIED (V2 §10.1): 패턴 '$pat' 매칭·안전한 대안 사용" >&2
    exit 2
  fi
done

# 프로덕션 명령 = /deploy 슬래시만 허용 (헌법 §0·ADR 0026)
PROD_PATTERNS=(
  'vercel --prod'
  'fly deploy'
  'railway up'
  'kubectl apply'
  'terraform apply'
  'ssh deploy@'
)

for pat in "${PROD_PATTERNS[@]}"; do
  if [[ "$CMD" == *"$pat"* ]]; then
    echo "DENIED: 프로덕션 명령은 /deploy 슬래시 커맨드만 (Cycle 21 차용)" >&2
    exit 2
  fi
done

exit 0
