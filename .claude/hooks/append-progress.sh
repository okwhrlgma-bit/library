#!/usr/bin/env bash
# Cycle 17 P41 — Stop hook: 세션 종료 시 PROGRESS.md 자동 갱신.
# 외부 자동화 가이드 §2.3 정합.

set -e

REPO="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto"
cd "$REPO" 2>/dev/null || exit 0

LAST_COMMIT=$(git log -1 --pretty=%B 2>/dev/null || echo "(no commit)")
DATE=$(TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M' 2>/dev/null || date '+%Y-%m-%d %H:%M')

# 동일 헤더 중복 방지
if [ -f PROGRESS.md ]; then
    NEW_HEADER="## $DATE — $(echo "$LAST_COMMIT" | head -1 | cut -c 1-60)"
    if grep -qF "$NEW_HEADER" PROGRESS.md 2>/dev/null; then
        exit 0
    fi
fi

# Top-of-file append (최신 우선)
TMP=$(mktemp)
{
    head -5 PROGRESS.md 2>/dev/null || echo "# PROGRESS.md"
    echo ""
    echo "## $DATE — $(echo "$LAST_COMMIT" | head -1)"
    echo ""
    echo "$LAST_COMMIT" | tail -n +2
    echo ""
    echo "---"
    echo ""
    tail -n +6 PROGRESS.md 2>/dev/null || true
} > "$TMP"
mv "$TMP" PROGRESS.md

exit 0
