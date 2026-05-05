#!/usr/bin/env bash
# scripts/audit-query.sh
# audit.jsonl 조회. 사용: ./scripts/audit-query.sh [--days 7] [--cost] [--project NAME]
set -uo pipefail

DAYS=7
SHOW_COST=false
PROJECT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --days) DAYS="$2"; shift 2 ;;
    --cost) SHOW_COST=true; shift ;;
    --project) PROJECT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

AUDIT="${HOME}/.claude/audit.jsonl"
[ -f "$AUDIT" ] || { echo "audit log 없음: $AUDIT"; exit 0; }

# Linux/Mac 모두 호환
if date -d "1 day ago" >/dev/null 2>&1; then
  CUTOFF=$(date -u -d "${DAYS} days ago" +%Y-%m-%dT%H:%M:%SZ)
else
  CUTOFF=$(date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ)
fi

if $SHOW_COST; then
  echo "💰 최근 ${DAYS}일 비용 합계 (USD):"
  jq -r --arg cutoff "$CUTOFF" --arg project "$PROJECT" '
    select(.ts >= $cutoff) |
    select($project == "" or (.cwd // "" | contains($project))) |
    .cost // 0
  ' "$AUDIT" | awk '{ s += $1 } END { printf "  $%.4f\n", s }'
  echo ""
  echo "📅 일별:"
  jq -r --arg cutoff "$CUTOFF" --arg project "$PROJECT" '
    select(.ts >= $cutoff) |
    select($project == "" or (.cwd // "" | contains($project))) |
    [.ts[:10], (.cost // 0 | tostring)] | @tsv
  ' "$AUDIT" | awk '{ d[$1] += $2 } END { for (k in d) printf "  %s  $%.4f\n", k, d[k] }' | sort
else
  echo "📋 최근 ${DAYS}일 audit 로그:"
  jq -r --arg cutoff "$CUTOFF" --arg project "$PROJECT" '
    select(.ts >= $cutoff) |
    select($project == "" or (.cwd // "" | contains($project))) |
    "\(.ts)  $\(.cost // 0)  \(.cwd // "?")"
  ' "$AUDIT" | tail -50
fi
