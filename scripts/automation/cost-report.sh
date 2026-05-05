#!/usr/bin/env bash
# 비용 리포트: audit.jsonl을 읽어 일별·모델별·작업별 비용 집계.
# 사용:
#   ./scripts/cost-report.sh           # 어제 + 최근 7일 요약
#   ./scripts/cost-report.sh --days 30 # 최근 30일
#   ./scripts/cost-report.sh --today

set -euo pipefail

AUDIT_LOG="${HOME}/.claude-orchestrator/audit.jsonl"
DAYS=7
TODAY_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --days) DAYS="$2"; shift 2 ;;
    --today) TODAY_ONLY=1; shift ;;
    *) echo "알 수 없는 인자: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$AUDIT_LOG" ]]; then
  echo "audit log 없음: $AUDIT_LOG" >&2
  echo "automation/router.py를 한 번이라도 실행한 후 다시 시도하세요." >&2
  exit 1
fi

if ! command -v jq >/dev/null; then
  echo "jq 필요: sudo apt install jq" >&2
  exit 1
fi

today=$(date +%Y-%m-%d)
since=$(date -d "${DAYS} days ago" +%Y-%m-%d 2>/dev/null || date -v-"${DAYS}"d +%Y-%m-%d)

echo "=== 비용 리포트 ==="
echo "오늘: $today"
if [[ $TODAY_ONLY -eq 1 ]]; then
  echo "범위: 오늘만"
  filter_date="$today"
else
  echo "범위: $since ~ $today"
  filter_date="$since"
fi
echo ""

# 일별 합계
echo "## 일별 비용"
jq -r --arg since "$filter_date" '
  select(.timestamp >= $since) |
  "\(.timestamp[0:10])\t\(.cost_usd // 0)"
' "$AUDIT_LOG" \
| awk '{sums[$1]+=$2} END {for (d in sums) printf "  %s  $%.4f\n", d, sums[d]}' \
| sort

echo ""

# 모델별 합계
echo "## 모델별 비용 (전 기간)"
jq -r --arg since "$filter_date" '
  select(.timestamp >= $since) |
  "\(.model // "unknown")\t\(.cost_usd // 0)"
' "$AUDIT_LOG" \
| awk '{sums[$1]+=$2; counts[$1]++} END {for (m in sums) printf "  %-30s  %5d회  $%.4f\n", m, counts[m], sums[m]}' \
| sort -k 4 -nr

echo ""

# 카테고리별 합계 (router.py가 기록한 경우)
echo "## 작업 카테고리별 비용"
jq -r --arg since "$filter_date" '
  select(.timestamp >= $since) |
  "\(.category // "uncategorized")\t\(.cost_usd // 0)"
' "$AUDIT_LOG" \
| awk '{sums[$1]+=$2; counts[$1]++} END {for (c in sums) printf "  %-20s  %5d회  $%.4f\n", c, counts[c], sums[c]}' \
| sort -k 4 -nr

echo ""

# 총합
total=$(jq -r --arg since "$filter_date" '
  select(.timestamp >= $since) | .cost_usd // 0
' "$AUDIT_LOG" | awk '{s+=$1} END {printf "%.4f", s}')

echo "## 총합: \$${total}"

# 예산 대비
budget="${DAILY_BUDGET_USD:-}"
if [[ -n "$budget" ]] && [[ $TODAY_ONLY -eq 1 ]]; then
  pct=$(awk "BEGIN {printf \"%.1f\", $total / $budget * 100}")
  echo "## 예산 사용률: ${pct}% (예산 \$${budget}/일)"
  if (( $(awk "BEGIN {print ($pct > 80)}") )); then
    echo "  ⚠️  예산 80% 초과"
  fi
fi
