#!/usr/bin/env bash
# Cycle 46 (P37 + V3) — KOLAS III D-day 자동 갱신 cron.
#
# 매일 06:00 KST cron 실행 = countdown 갱신·urgency_window 변경 시 Slack 알림.
# 외부 의존: Cycle 12 P37 migration/countdown.py (D-240 골든윈도우).
#
# 사용 (cron):
#   0 21 * * * /path/to/kolas3-daily-update.sh   # UTC 21:00 = KST 06:00
#
# 산출:
#   docs/sales/kolas3-countdown-current.json   # D-day·urgency 현재 값
#   Slack 알림 (urgency_window 전환 시·골든→중요·중요→만료)

set -euo pipefail

REPO="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto"
cd "$REPO" 2>/dev/null || exit 0

PYTHON="$REPO/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python3
[ -x "$(command -v "$PYTHON" 2>/dev/null)" ] || PYTHON=python

CURRENT_FILE="docs/sales/kolas3-countdown-current.json"
PREVIOUS_FILE="docs/sales/kolas3-countdown-previous.json"

# 이전 값 백업
[ -f "$CURRENT_FILE" ] && cp "$CURRENT_FILE" "$PREVIOUS_FILE"

# 현재 D-day 계산
"$PYTHON" -c "
import json, sys
sys.path.insert(0, 'src')
from kormarc_auto.migration.countdown import (
    KOLAS3_END_DATE, days_until_kolas3_end, timeline_actions_for_remaining_days,
    lost_data_categories
)
days = days_until_kolas3_end()
urgency = 'golden' if days > 90 else 'critical' if days > 0 else 'expired'
out = {
    'kolas3_end_kst': KOLAS3_END_DATE.isoformat(),
    'days_remaining': days,
    'urgency_window': urgency,
    'official_source': 'books.nl.go.kr (국립중앙도서관 KOLAS III 표준형 기술 지원 종료 공지)',
    'public_libraries_count_2024': 1296,
    'knu_unused_small_libraries': 5100,
    'lost_data_categories': lost_data_categories(),
    'timeline_actions': timeline_actions_for_remaining_days(days),
}
with open('$CURRENT_FILE', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f'D-{days} ({urgency})')
" || exit 0

# urgency_window 전환 감지 = Slack 알림
if [ -f "$PREVIOUS_FILE" ] && command -v jq >/dev/null 2>&1; then
  prev_urgency=$(jq -r '.urgency_window // "unknown"' < "$PREVIOUS_FILE" 2>/dev/null || echo "unknown")
  curr_urgency=$(jq -r '.urgency_window // "unknown"' < "$CURRENT_FILE" 2>/dev/null || echo "unknown")
  curr_days=$(jq -r '.days_remaining // 0' < "$CURRENT_FILE" 2>/dev/null || echo "0")

  if [ "$prev_urgency" != "$curr_urgency" ] && [ -n "${SLACK_WEBHOOK:-}" ]; then
    msg="🚨 KOLAS III urgency_window 전환: $prev_urgency → $curr_urgency (D-$curr_days)"
    curl -s -X POST -H 'Content-Type: application/json' \
      -d "{\"text\":\"$msg\"}" "$SLACK_WEBHOOK" 2>/dev/null || true
  fi
fi

echo "✓ KOLAS III countdown 갱신 완료: $CURRENT_FILE"
