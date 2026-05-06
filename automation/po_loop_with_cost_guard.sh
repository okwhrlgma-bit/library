#!/usr/bin/env bash
# Cycle 45 (V3 Block 2 + po_loop 통합) — 비용 가드 wrapper.
#
# po_loop.sh + cost_supervisor.py 통합 = 무중단 자율 + 3-Layer 비용 보호.
# Phase 2 활성 (사업자 등록 + Anthropic API 키 발급 후).
#
# 사용:
#   ./automation/po_loop_with_cost_guard.sh "다음 매출 차단점 1건 자동 진행"
#   ./automation/po_loop_with_cost_guard.sh --hard 30 --soft 8 --per-iter 3 "P30 PortOne sandbox"
#
# 정지: touch /tmp/po-stop  또는  Ctrl+C
#
# Exit codes:
#   0   = 모든 사이클 완료 (COMPLETED)
#   1   = 인자 오류
#   2   = hard cap 도달 (cost_supervisor SIGTERM)
#   130 = SIGINT (Ctrl+C)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 기본값 (V3 §3 권장·1인 SaaS Phase 2)
HARD_CAP="${PO_HARD_CAP:-20.00}"
SOFT_CAP="${PO_SOFT_CAP:-5.00}"
PER_ITER_CAP="${PO_PER_ITER_CAP:-2.00}"
MAX_TURNS="${PO_MAX_TURNS:-40}"
MAX_CYCLES="${PO_MAX_CYCLES:-100}"
INTERVAL_SECONDS="${PO_INTERVAL:-30}"
STOP_FILE="${PO_STOP_FILE:-/tmp/po-stop}"
STATE_FILE="${CLAUDE_BUDGET_STATE:-/tmp/claude-budget.json}"
LOG_DIR="${HOME}/.claude-orchestrator"
LOG_FILE="${LOG_DIR}/po-loop-cost-guard.log"
mkdir -p "$LOG_DIR"

PROMPT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hard) HARD_CAP="$2"; shift 2 ;;
    --soft) SOFT_CAP="$2"; shift 2 ;;
    --per-iter) PER_ITER_CAP="$2"; shift 2 ;;
    --max-turns) MAX_TURNS="$2"; shift 2 ;;
    --max-cycles) MAX_CYCLES="$2"; shift 2 ;;
    --interval) INTERVAL_SECONDS="$2"; shift 2 ;;
    *) PROMPT="$1"; shift ;;
  esac
done

[[ -z "$PROMPT" ]] && {
  echo "사용: $0 [--hard N] [--soft N] [--per-iter N] [--max-turns N] '명령'"
  exit 1
}

command -v claude >/dev/null || {
  echo "claude CLI 필요·docs/automation/HEADLESS_AUTH.md 참조"
  exit 1
}
command -v python3 >/dev/null || {
  echo "python3 필요 (cost_supervisor.py)"
  exit 1
}

[[ -f "$STOP_FILE" ]] && {
  echo "기존 stop 파일 먼저 삭제: rm $STOP_FILE"
  exit 1
}

# Phase 2 인증 검증 (V3 §2 정합)
if [[ -z "${ANTHROPIC_API_KEY:-}" ]] && [[ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
  echo "⚠ 인증 미설정: ANTHROPIC_API_KEY 또는 CLAUDE_CODE_OAUTH_TOKEN 필요"
  echo "→ docs/automation/HEADLESS_AUTH.md 참조"
  exit 1
fi

# State file 초기화
rm -f "$STATE_FILE"
echo '{"cumulative":0,"iteration":0,"abort":false}' > "$STATE_FILE"

cycle=0
trap 'echo ""; echo "Ctrl+C — 다음 사이클부터 정지"; touch "$STOP_FILE"' INT TERM

echo "=== PO Loop with Cost Guard 시작 ==="
echo "  명령: $PROMPT"
echo "  비용 캡: soft=\$$SOFT_CAP / hard=\$$HARD_CAP / per-iter=\$$PER_ITER_CAP"
echo "  최대: $MAX_CYCLES 사이클·${INTERVAL_SECONDS}초 간격·turn $MAX_TURNS"
echo "  정지: touch $STOP_FILE"
echo "  로그: $LOG_FILE"
echo "  state: $STATE_FILE"

while [[ $cycle -lt $MAX_CYCLES ]]; do
  if [[ -f "$STOP_FILE" ]]; then
    echo "[$(date +%H:%M:%S)] STOP 감지 — 종료"
    rm -f "$STOP_FILE"
    break
  fi

  # cost_supervisor state = abort=true 면 hard cap 도달
  if command -v jq >/dev/null 2>&1; then
    abort=$(jq -r '.abort // false' < "$STATE_FILE" 2>/dev/null || echo "false")
    cumul=$(jq -r '.cumulative // 0' < "$STATE_FILE" 2>/dev/null || echo "0")
    if [[ "$abort" == "true" ]]; then
      echo "[$(date +%H:%M:%S)] cost_supervisor abort=true (cumul=\$$cumul) — 종료"
      break
    fi
  fi

  cycle=$((cycle + 1))
  echo "[$(date +%H:%M:%S)] === 사이클 $cycle/$MAX_CYCLES (누적 \$${cumul:-0}/\$$HARD_CAP) ==="

  cycle_prompt="[사이클 $cycle/$MAX_CYCLES] $PROMPT

이전 사이클 결과를 PROGRESS.md에서 확인하고 다음 단계만 진행하세요.
이번 사이클이 끝나면 응답을 종료. 다음 사이클은 외부 루프가 시작합니다.
완료된 작업이 더 없으면 'COMPLETED'라고만 출력하세요."

  # cost_supervisor + claude --output-format stream-json 통합
  output=$(python3 automation/cost_supervisor.py \
    --soft "$SOFT_CAP" --hard "$HARD_CAP" --per-iter "$PER_ITER_CAP" \
    --state-file "$STATE_FILE" \
    --slack-webhook "${SLACK_WEBHOOK:-}" \
    -- claude -p "$cycle_prompt" \
    --output-format stream-json --verbose --include-partial-messages \
    --max-turns "$MAX_TURNS" --dangerously-skip-permissions 2>&1) || rc=$?
  rc=${rc:-0}

  echo "$output" | tee -a "$LOG_FILE"

  if [[ "$rc" == "2" ]]; then
    echo "[$(date +%H:%M:%S)] ⛔ cost_supervisor hard cap 종료"
    break
  fi

  if echo "$output" | grep -q "^COMPLETED$"; then
    echo "[$(date +%H:%M:%S)] COMPLETED — 모든 작업 끝"
    break
  fi

  if [[ $cycle -lt $MAX_CYCLES ]]; then
    for ((i=0; i<INTERVAL_SECONDS; i++)); do
      [[ -f "$STOP_FILE" ]] && break 2
      sleep 1
    done
  fi
done

echo "=== PO Loop with Cost Guard 종료 ($cycle 사이클) ==="
if command -v jq >/dev/null 2>&1; then
  final_cumul=$(jq -r '.cumulative // 0' < "$STATE_FILE" 2>/dev/null || echo "0")
  echo "    누적 비용: \$$final_cumul / \$$HARD_CAP"
fi
