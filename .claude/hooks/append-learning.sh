#!/usr/bin/env bash
# Cycle 21 (V2 §4.2·차용) — Stop hook에서 실패 학습 자동 적재.
# Cycle 9 PAVR + Cycle 17 PROGRESS hook과 정합.

REPO="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto"
cd "$REPO" 2>/dev/null || exit 0

# 직전 세션 exit code (있으면)
LAST_EXIT_FILE=".claude/last_exit_code"
[ -f "$LAST_EXIT_FILE" ] || exit 0

LAST_EXIT=$(cat "$LAST_EXIT_FILE" 2>/dev/null || echo 0)
[ "$LAST_EXIT" = "0" ] && exit 0

# 실패 = learnings.md 자동 적재 (top-of-file·SessionStart 우선 노출)
DATE=$(TZ='Asia/Seoul' date '+%Y-%m-%d')
TASK=$(cat .claude/last_task.txt 2>/dev/null || echo "(unknown)")
ERROR=$(cat .claude/last_error.txt 2>/dev/null | head -3 || echo "(no error log)")

ENTRY="
## ${DATE} — 실패 패턴 (자동·append-learning hook)

**작업**: ${TASK}
**증상**: ${ERROR}
**원인**: <자동 분석 placeholder·다음 세션에서 채움>
**예방**: <다음 작업 전 체크할 것>
**관련**: hook·skill·CLAUDE.md 규칙
"

# 헤더 5줄 보존 + 신규 entry top-of-content append
TMP=$(mktemp)
{
    head -5 learnings.md 2>/dev/null
    echo "$ENTRY"
    tail -n +6 learnings.md 2>/dev/null
} > "$TMP"
mv "$TMP" learnings.md

exit 0
