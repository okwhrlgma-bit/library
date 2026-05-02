#!/bin/bash
# Self-Healing Agent 4단계 hook (Detect → Diagnose → Heal → Verify)
# 검증 사례: 64% autonomy rate (14건 중 9건 자율 해결)
# 출처: ClaudeWatch (PolarOrchid) + Self-healing AI Agents Production Patterns
# 적용: PostToolUseFailure hook으로 등록

set -e

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // {}')
ERROR=$(echo "$INPUT" | jq -r '.error // ""')

# ===== Phase 1: Detect (탐지) =====
# 실패한 도구 호출 패턴 분류
ERROR_TYPE="unknown"
case "$ERROR" in
  *"Permission denied"*) ERROR_TYPE="permission" ;;
  *"ModuleNotFoundError"*|*"ImportError"*) ERROR_TYPE="missing_dependency" ;;
  *"TimeoutError"*|*"timed out"*) ERROR_TYPE="timeout" ;;
  *"ConnectionError"*|*"NetworkError"*) ERROR_TYPE="network" ;;
  *"FAILED"*|*"AssertionError"*) ERROR_TYPE="test_fail" ;;
  *"SyntaxError"*) ERROR_TYPE="syntax" ;;
  *"FileNotFoundError"*) ERROR_TYPE="file_not_found" ;;
  *) ERROR_TYPE="unknown" ;;
esac

echo "Self-Healing: Detect — error_type=$ERROR_TYPE, tool=$TOOL_NAME" >&2

# ===== Phase 2: Diagnose (진단) =====
# 자동 복구 가능 여부 판단
RECOVERABLE="false"
RECOVERY_STRATEGY=""

case "$ERROR_TYPE" in
  permission)
    # 권한 거부 = 비가역 게이트 통과 못함 → 복구 X (인간 승인 필요)
    RECOVERABLE="false"
    RECOVERY_STRATEGY="human_escalation"
    ;;
  missing_dependency)
    # 의존성 부재 = 효율 가드 §2 (24h 내 5개+ 추가 시 가드)
    # PO 결정 영역
    RECOVERABLE="false"
    RECOVERY_STRATEGY="po_decision_required"
    ;;
  timeout|network)
    # 외부 API 타임아웃·네트워크 = 자동 재시도 가능
    RECOVERABLE="true"
    RECOVERY_STRATEGY="exponential_backoff"
    ;;
  test_fail)
    # 테스트 실패 = LLM 자가 분석 가능
    RECOVERABLE="true"
    RECOVERY_STRATEGY="llm_self_repair"
    ;;
  syntax)
    # 문법 오류 = LLM 자가 수정 가능
    RECOVERABLE="true"
    RECOVERY_STRATEGY="llm_self_repair"
    ;;
  file_not_found)
    # 파일 부재 = 경로 확인 후 재시도
    RECOVERABLE="true"
    RECOVERY_STRATEGY="path_verification"
    ;;
  *)
    RECOVERABLE="false"
    RECOVERY_STRATEGY="human_escalation"
    ;;
esac

echo "Self-Healing: Diagnose — recoverable=$RECOVERABLE, strategy=$RECOVERY_STRATEGY" >&2

# ===== Phase 3: Heal (복구) =====
# 자동 복구 시도
if [ "$RECOVERABLE" = "true" ]; then
  case "$RECOVERY_STRATEGY" in
    exponential_backoff)
      # 1s·2s·4s·8s·16s + jitter (최대 ~31초)
      ATTEMPT_COUNT=$(echo "$INPUT" | jq -r '.recovery_attempt_count // 0')
      if [ "$ATTEMPT_COUNT" -lt 5 ]; then
        DELAY=$((2 ** ATTEMPT_COUNT))
        JITTER=$((RANDOM % 1000))  # 0~999ms
        echo "Self-Healing: Heal — backoff ${DELAY}s + ${JITTER}ms (attempt $((ATTEMPT_COUNT+1))/5)" >&2
        sleep $DELAY
        sleep 0.$JITTER 2>/dev/null || true
        # exit 0 = 재시도 권장 (Claude Code가 자동 재시도)
        exit 0
      else
        echo "Self-Healing: Heal — backoff 5회 초과, ESCALATE" >&2
        RECOVERY_STRATEGY="human_escalation"
      fi
      ;;
    llm_self_repair)
      # LLM이 다음 턴에서 자가 수정 (Claude Code 본체 처리)
      echo "Self-Healing: Heal — LLM 자가 수정 (다음 턴)" >&2
      exit 0
      ;;
    path_verification)
      # 작업 디렉토리 확인 후 재시도
      pwd >&2
      ls -la 2>&1 | head -10 >&2
      exit 0
      ;;
  esac
fi

# ===== Phase 4: Verify + Escalate =====
if [ "$RECOVERY_STRATEGY" = "human_escalation" ] || [ "$RECOVERY_STRATEGY" = "po_decision_required" ]; then
  echo "Self-Healing: Verify FAILED — human escalation 필요" >&2

  # 에스컬레이션 로그 (Telegram·카카오톡 통합 시 활용)
  ESCALATION_LOG=".claude/escalation-log.jsonl"
  jq -n \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg tool "$TOOL_NAME" \
    --arg error_type "$ERROR_TYPE" \
    --arg strategy "$RECOVERY_STRATEGY" \
    --arg error "$ERROR" \
    '{ts: $ts, tool: $tool, error_type: $error_type, strategy: $strategy, error: $error}' \
    >> "$ESCALATION_LOG" 2>/dev/null || true

  # PO 알림 트리거 (카카오 알림톡 통합 시)
  if [ -f "scripts/notify_po.py" ]; then
    python scripts/notify_po.py "Self-healing escalation: $ERROR_TYPE" 2>/dev/null || true
  fi

  # exit 1 = Claude Code에 실패 보고 (재시도 X)
  exit 1
fi

# 기본: Verify OK
exit 0
