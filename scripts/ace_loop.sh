#!/bin/bash
# ACE (Agentic Context Engine) 자율 학습 루프
# 검증 사례: Python→TypeScript 14,000줄 / 119 commit / 빌드 에러 없이 자율 완료
# 출처: kayba-ai/agentic-context-engine + Anthropic 멀티 에이전트 패턴
# 적용: kormarc-auto AUTONOMOUS_BACKLOG 우선순위 -2.5/-2/-1.5/-1/0/0-2/0-3 자율 진행

set -e

# 설정
MAX_ITERATIONS=${MAX_ITERATIONS:-30}
COMPLETION_MARKER="<<<TASK_COMPLETE>>>"
TRACE_DIR=".claude/ace-traces"
LEARNINGS_FILE="learnings.md"
TASK_FILE=${1:-"AUTONOMOUS_BACKLOG.md"}

mkdir -p "$TRACE_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TRACE_FILE="$TRACE_DIR/trace-$TIMESTAMP.json"
LEARNING_PATCH="$TRACE_DIR/learning-$TIMESTAMP.md"

echo "=== ACE 자율 학습 루프 시작 ==="
echo "Max iterations: $MAX_ITERATIONS"
echo "Task file: $TASK_FILE"
echo "Trace: $TRACE_FILE"
echo ""

ITERATION=0

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
  ITERATION=$((ITERATION + 1))
  echo "--- Iteration $ITERATION/$MAX_ITERATIONS ---"

  # ===== Phase 1: Run (실행) =====
  # AUTONOMOUS_BACKLOG에서 다음 우선순위 작업 1건 진행
  claude -p "$(cat <<EOF
$TASK_FILE 의 가장 높은 우선순위 작업 1건 진행:

1. 우선순위 -2.5/-2/-1.5/-1/0/0-2/0-3/Part29~34 순으로 첫 미완료 [ ] 항목 1건만 선택
2. 해당 작업 완료
3. 이중 게이트 검증:
   - pytest -q 통과
   - python scripts/binary_assertions.py --strict 통과
4. 자관 익명화 정책 정합 (compliance-officer 호출)
5. 평가축 §0/§12 양수 명시
6. commit 메시지 생성 (Conventional Commits)
7. AUTONOMOUS_BACKLOG.md에서 [ ] → [x] 업데이트
8. 응답 마지막 줄에 $COMPLETION_MARKER 출력

만약 다음 상황 발생 시 SKIPPED.md에 기록 후 다음 작업으로:
- 같은 테스트 3회 실패
- 자가 디버그 30회 초과
- 외부 의존성 추가 필요 (자율 commit 차단점)
- L4 작업 (PO 수동 필요)

마지막 줄에 [ITERATION_RESULT: completed/skipped/blocked] 출력
EOF
)" \
    --permission-mode auto \
    --max-turns 50 \
    --output-format stream-json \
    --allowedTools "Read,Write,Edit,Glob,Grep,Bash(pytest*),Bash(python scripts/*),Bash(git add*),Bash(git commit*),Bash(git status),Bash(ruff*)" \
    > "$TRACE_FILE.iter$ITERATION" 2>&1

  # ===== Phase 2: Reflect (분석) =====
  # 트레이스에서 결과·실패 패턴 추출
  if grep -q "$COMPLETION_MARKER" "$TRACE_FILE.iter$ITERATION"; then
    RESULT=$(grep -oE "ITERATION_RESULT: \w+" "$TRACE_FILE.iter$ITERATION" | tail -1)
    echo "Iteration $ITERATION: $RESULT"
  else
    echo "Iteration $ITERATION: NO_MARKER (강제 종료 또는 실패)"
    RESULT="ITERATION_RESULT: failed"
  fi

  # ===== Phase 3: Learn (학습) =====
  # 별도 reflector 모델이 트레이스 분석 → learnings.md 갱신
  if [ "$RESULT" = "ITERATION_RESULT: failed" ] || [ $((ITERATION % 5)) -eq 0 ]; then
    echo "  → Reflector 호출 (학습 패턴 추출)"

    claude -p "$(cat <<EOF
다음 실행 트레이스를 분석하여 실패·성공 패턴을 추출하라:

trace 마지막 200줄:
$(tail -200 "$TRACE_FILE.iter$ITERATION")

다음 형식으로 $LEARNING_PATCH 에 추가하라:

## $(date +%Y-%m-%d) Iteration $ITERATION 학습

### 성공 패턴 (재사용 가능)
- ...

### 실패 패턴 (회피)
- ...

### CLAUDE.md 갱신 후보 (트리거-행동 형식)
- ...

응답 마지막에 [REFLECT_DONE] 출력.
EOF
)" \
      --permission-mode auto \
      --max-turns 5 \
      --allowedTools "Read,Write,Edit"

    # learnings.md에 패치 병합 (수동 검토 후 PO가 적용)
    if [ -f "$LEARNING_PATCH" ]; then
      cat "$LEARNING_PATCH" >> "$LEARNINGS_FILE.pending"
      echo "  → 학습 패치 → $LEARNINGS_FILE.pending (PO 검토 후 병합)"
    fi
  fi

  # ===== Phase 4: Loop 또는 종료 =====

  # 효율 가드 5종 체크
  if [ -f "scripts/efficiency_guards.py" ]; then
    GUARD_RESULT=$(python scripts/efficiency_guards.py 2>/dev/null || echo "OK")
    if [ "$GUARD_RESULT" != "OK" ]; then
      echo "효율 가드 발동: $GUARD_RESULT"
      git add -A && git commit -m "WIP: ACE loop halted at iteration $ITERATION (gate: $GUARD_RESULT)" || true
      break
    fi
  fi

  # 비가역 액션 감지 시 즉시 중단
  if grep -qE "git push.*--force|rm -rf|DROP TABLE" "$TRACE_FILE.iter$ITERATION"; then
    echo "비가역 액션 감지 — ACE 루프 즉시 중단"
    break
  fi

  # AUTONOMOUS_BACKLOG에 미완료 항목 없으면 종료
  PENDING=$(grep -c "^\- \[ \]" "$TASK_FILE" || echo "0")
  if [ "$PENDING" = "0" ]; then
    echo "모든 우선순위 작업 완료 (PENDING=0)"
    break
  fi

  echo "  → 남은 작업: $PENDING 건"
  sleep 2  # API rate limit 회피
done

echo ""
echo "=== ACE 루프 종료 ==="
echo "총 iteration: $ITERATION"
echo "Trace: $TRACE_FILE.iter*"
echo "학습 패치: $LEARNINGS_FILE.pending (PO 검토)"
echo ""

# 종합 보고
git log --oneline -$ITERATION 2>/dev/null | head -$ITERATION
