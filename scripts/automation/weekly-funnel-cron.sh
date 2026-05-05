#!/usr/bin/env bash
# Cycle 22 (P44·V2 §10.5) — 주간 funnel 리포트 cron (월 09:00 KST).
# P34 weekly_report.py 통합·슬랙/이메일 발송 hook.

set -euo pipefail

REPO="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto"
cd "$REPO"

PYTHON="$REPO/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python

DATE=$(TZ='Asia/Seoul' date '+%Y-%m-%d')
OUTPUT="$REPO/docs/automation/reports/weekly-${DATE}.md"
mkdir -p "$REPO/docs/automation/reports"

"$PYTHON" -c "
import sys
sys.path.insert(0, 'src')
from kormarc_auto.analytics import generate_weekly_report
from kormarc_auto.analytics.events import iter_events

events = list(iter_events())
report = generate_weekly_report(events)
print(report)
" > "$OUTPUT" 2>&1 || echo "[WARN] weekly_report 생성 실패·data 부족"

# 슬랙 webhook 발송 (있으면)
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    PAYLOAD=$("$PYTHON" -c "
import json
with open('$OUTPUT', 'r', encoding='utf-8') as f:
    text = f.read()[:3000]  # Slack 4000 char 한도 정합
print(json.dumps({'text': text, 'username': 'kormarc-auto-funnel'}))
")
    curl -s -X POST -H "Content-Type: application/json" \
        -d "$PAYLOAD" "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 || echo "[WARN] Slack 발송 실패"
fi

echo "✓ weekly funnel = $OUTPUT"
