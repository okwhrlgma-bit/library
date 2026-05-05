#!/usr/bin/env bash
# Cycle 21 (V2 §3.1·차용) — PreCompact transcript 백업.
# 컨텍스트 압축 직전 = 대화 백업 (V2 §11 항상 해야 할 것).

INPUT_JSON=$(cat 2>/dev/null || echo "{}")
PYTHON="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python

BACKUP_DIR="$HOME/.kormarc-auto/transcripts"
mkdir -p "$BACKUP_DIR" 2>/dev/null

# transcript 추출 (있으면)
TRANSCRIPT=$(echo "$INPUT_JSON" | "$PYTHON" -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(json.dumps(d, ensure_ascii=False, indent=2)[:50000])  # 50KB cap
except Exception:
    print('{}')
" 2>/dev/null || echo "{}")

DATE=$(TZ='Asia/Seoul' date '+%Y-%m-%d-%H%M%S')
TARGET="$BACKUP_DIR/transcript-${DATE}.json"
echo "$TRANSCRIPT" > "$TARGET" 2>/dev/null

# 최신 20개만 보존 (디스크 무한 증가 차단)
ls -t "$BACKUP_DIR"/transcript-*.json 2>/dev/null | tail -n +21 | xargs -r rm 2>/dev/null

exit 0
