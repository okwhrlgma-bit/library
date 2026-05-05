#!/usr/bin/env bash
# Cycle 18A P42 — PostToolUse / Edit·Write 자동 포맷.
# 외부 자동화 가이드 §3.2 패턴 #2 정합.
#
# Python 파일 = ruff format + ruff check --fix.
# 실패해도 silent (편집 자체는 보존·async).

set -e

INPUT=$(cat 2>/dev/null || echo "{}")
PYTHON="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python

FILE_PATH=$(echo "$INPUT" | "$PYTHON" -c "
import sys, json
try:
    d = json.load(sys.stdin)
    fp = (d.get('tool_response') or {}).get('filePath') or (d.get('tool_input') or {}).get('file_path') or ''
    print(fp)
except Exception:
    print('')
" 2>/dev/null || echo "")

[ -z "$FILE_PATH" ] && exit 0

# kormarc-auto 외부 = skip
case "$FILE_PATH" in
    *kormarc-auto*) ;;
    *) exit 0 ;;
esac

# Python 파일만 ruff
case "$FILE_PATH" in
    *.py)
        "$PYTHON" -m ruff format "$FILE_PATH" 2>/dev/null || true
        "$PYTHON" -m ruff check --fix "$FILE_PATH" 2>/dev/null || true
        ;;
    *) ;;
esac

exit 0
