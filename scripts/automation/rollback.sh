#!/usr/bin/env bash
# scripts/rollback.sh
# 가장 최근 자동 PR/커밋을 안전하게 되돌린다.
# 사용: ./scripts/rollback.sh [--commits N] [--branch <name>] [--dry-run]
set -euo pipefail

COMMITS=1
DRY=false
BRANCH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --commits) COMMITS="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --dry-run) DRY=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [ -n "$BRANCH" ]; then
  echo "🔍 브랜치 '$BRANCH' 삭제/되돌림"
  if $DRY; then
    echo "  (dry-run) git branch -D $BRANCH"
    git push origin --delete "$BRANCH" --dry-run 2>&1 || true
  else
    git branch -D "$BRANCH" 2>/dev/null || echo "  로컬 브랜치 없음"
    git push origin --delete "$BRANCH" 2>/dev/null || echo "  원격 브랜치 없음"
  fi
  exit 0
fi

# 마지막 N개 커밋 revert
echo "🔍 마지막 $COMMITS 개 커밋:"
git log -n "$COMMITS" --oneline

echo ""
read -r -p "이 커밋들을 revert할까요? (yes 입력): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "취소됨."
  exit 1
fi

# 안전을 위해 새 브랜치에서 revert
SAFE_BRANCH="rollback/$(date +%Y%m%d-%H%M%S)"

if $DRY; then
  echo "(dry-run) git checkout -b $SAFE_BRANCH"
  echo "(dry-run) git revert --no-edit HEAD~${COMMITS}..HEAD"
else
  git checkout -b "$SAFE_BRANCH"
  git revert --no-edit "HEAD~${COMMITS}..HEAD"
  echo ""
  echo "✅ Revert 완료. 브랜치: $SAFE_BRANCH"
  echo ""
  echo "다음 단계:"
  echo "  1. 변경 확인: git diff main"
  echo "  2. 푸시: git push origin $SAFE_BRANCH"
  echo "  3. PR 생성하거나 main에 머지"
  echo "  4. learnings.md에 무엇이 잘못됐는지 기록"
fi
