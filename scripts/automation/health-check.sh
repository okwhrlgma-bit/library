#!/usr/bin/env bash
# scripts/health-check.sh
# 셋업 전체가 정상인지 검증. 사용: make health
set -uo pipefail

PASS=0
FAIL=0
WARN=0

check() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "  ✅ $name"
    PASS=$((PASS+1))
  else
    echo "  ❌ $name"
    FAIL=$((FAIL+1))
  fi
}

warn() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "  ✅ $name"
    PASS=$((PASS+1))
  else
    echo "  ⚠️  $name (선택)"
    WARN=$((WARN+1))
  fi
}

echo "🔍 Health Check"
echo ""

echo "[필수 도구]"
check "git" "command -v git"
check "jq" "command -v jq"
check "node" "command -v node"
check "npm" "command -v npm"
check "claude (Claude Code CLI)" "command -v claude"

echo ""
echo "[필수 파일]"
check "CLAUDE.md" "test -f CLAUDE.md"
check "PROGRESS.md" "test -f PROGRESS.md"
check "learnings.md" "test -f learnings.md"
check "decisions.md" "test -f decisions.md"
check "goals/current.md" "test -f goals/current.md"
check ".gitignore" "test -f .gitignore"
check ".claudeignore" "test -f .claudeignore"
check ".env" "test -f .env"
check ".claude/settings.json" "test -f .claude/settings.json"

echo ""
echo "[Hook 실행 권한]"
for hook in scripts/hooks/*.sh; do
  check "$(basename "$hook") executable" "test -x $hook"
done
check "emergency-stop.sh executable" "test -x scripts/emergency-stop.sh"
check "rollback.sh executable" "test -x scripts/rollback.sh"

echo ""
echo "[Hook 동작 검증]"
# validate-bash가 위험 명령을 실제 차단하는지
RESULT=$(echo '{"tool_input":{"command":"sudo rm -rf /"}}' | ./scripts/hooks/validate-bash.sh 2>&1)
RC=$?
if [ "$RC" = "2" ]; then
  echo "  ✅ validate-bash가 sudo rm -rf 차단"
  PASS=$((PASS+1))
else
  echo "  ❌ validate-bash가 위험 명령을 차단 못함! (rc=$RC)"
  FAIL=$((FAIL+1))
fi

# scan-secrets가 가짜 API 키를 차단하는지
RESULT=$(echo '{"tool_input":{"content":"const key=\"sk-ant-fake1234567890abcdefghij\""}}' | ./scripts/hooks/scan-secrets.sh 2>&1)
RC=$?
if [ "$RC" = "2" ]; then
  echo "  ✅ scan-secrets가 Anthropic 키 패턴 차단"
  PASS=$((PASS+1))
else
  echo "  ❌ scan-secrets가 시크릿을 차단 못함! (rc=$RC)"
  FAIL=$((FAIL+1))
fi

echo ""
echo "[환경변수]"
if [ -f .env ]; then
  set -a; . .env; set +a
fi
check "ANTHROPIC_API_KEY 설정됨" "test -n \"${ANTHROPIC_API_KEY:-}\""
warn "DAILY_BUDGET_USD 설정됨" "test -n \"${DAILY_BUDGET_USD:-}\""
warn "EMERGENCY_CONTACT_WEBHOOK 설정됨" "test -n \"${EMERGENCY_CONTACT_WEBHOOK:-}\""

echo ""
echo "[선택 도구]"
warn "prettier" "command -v prettier"
warn "ruff (Python)" "command -v ruff"
warn "gh (GitHub CLI)" "command -v gh"
warn "Python claude-agent-sdk" "python -c 'import claude_agent_sdk' 2>/dev/null"

echo ""
echo "================================"
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  WARN: $WARN (선택)"
echo "================================"

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "❌ 실패 항목이 있습니다. 위 ❌ 항목을 고치세요."
  exit 1
fi

echo ""
echo "✅ 셋업 정상."
exit 0
