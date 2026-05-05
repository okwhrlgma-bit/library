#!/usr/bin/env bash
# scripts/emergency-stop.sh
# 🚨 자율 시스템이 폭주하거나 문제 생겼을 때 즉시 정지.
# 한 줄로 외워두세요: ./scripts/emergency-stop.sh

set -u

echo "🚨 EMERGENCY STOP 시작..."
echo ""

# 1. 모든 claude 프로세스 종료
echo "1/5: claude 프로세스 종료 중..."
pkill -9 -f "claude" 2>/dev/null && echo "  ✓ claude 프로세스 종료" || echo "  - 실행 중인 claude 없음"
pkill -9 -f "claude-code" 2>/dev/null || true

# 2. Python 자동화 프로세스 종료
echo "2/5: 자동화 스크립트 종료 중..."
pkill -9 -f "automation/router.py" 2>/dev/null || true
pkill -9 -f "automation/supervisor.py" 2>/dev/null || true
pkill -9 -f "automation/proposer_critic.py" 2>/dev/null || true
echo "  ✓ 자동화 스크립트 종료"

# 3. cron 잡 비활성화 (백업 후)
echo "3/5: cron 잡 비활성화 중..."
CRONTAB_BACKUP="${HOME}/.claude/crontab-backup-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p "${HOME}/.claude"
crontab -l > "$CRONTAB_BACKUP" 2>/dev/null && {
  echo "" | crontab -
  echo "  ✓ cron 비활성화 (백업: $CRONTAB_BACKUP)"
  echo "  복구: crontab $CRONTAB_BACKUP"
} || echo "  - cron 없음"

# 4. 진행 중인 git 작업 알림
echo "4/5: 진행 중인 git 작업 확인..."
if [ -d .git ]; then
  CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "?")
  UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  if [ "$UNCOMMITTED" != "0" ]; then
    echo "  ⚠️  현재 브랜치: $CURRENT_BRANCH, 커밋 안 된 변경 $UNCOMMITTED 개"
    echo "  필요 시: git stash 또는 docs/ROLLBACK_PLAYBOOK.md 참고"
  else
    echo "  ✓ 커밋되지 않은 변경 없음 (브랜치: $CURRENT_BRANCH)"
  fi
fi

# 5. 사고 알림 (선택)
echo "5/5: 사고 알림..."
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . .env
  set +a
fi

if [ -n "${EMERGENCY_CONTACT_WEBHOOK:-}" ]; then
  curl -s -X POST "$EMERGENCY_CONTACT_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"🚨 emergency-stop.sh 발동 — $(hostname) at $(date)\"}" \
    >/dev/null 2>&1 && echo "  ✓ 웹훅 알림 전송" || echo "  ✗ 웹훅 전송 실패"
else
  echo "  - EMERGENCY_CONTACT_WEBHOOK 미설정 (.env)"
fi

echo ""
echo "✅ Emergency stop 완료."
echo ""
echo "다음 단계:"
echo "  1. docs/ROLLBACK_PLAYBOOK.md 읽기"
echo "  2. 무엇이 잘못됐는지 학습: git log -10, audit 조회"
echo "  3. 원인 분석 후 learnings.md에 기록"
echo "  4. cron 복구: crontab $CRONTAB_BACKUP"
