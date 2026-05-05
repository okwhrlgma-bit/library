#!/usr/bin/env bash
# Cycle 21 (V2 §10.3·P49 정합·차용) — SessionStart 일일 예산 차단.
# Cycle 19A budget tracker (Python) 와 통합·SessionStart hook으로 노출.

PYTHON="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON=python

REPO="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto"
cd "$REPO" 2>/dev/null || exit 0

STATUS=$("$PYTHON" -c "
import sys
sys.path.insert(0, 'src')
try:
    from kormarc_auto.budget import BudgetTracker
    t = BudgetTracker()
    msg = t.status_message()
    if t.should_block_session():
        print(f'BLOCK::{msg}')
    else:
        print(f'OK::{msg}')
except Exception as e:
    print(f'OK::budget-guard skip: {type(e).__name__}')
" 2>/dev/null || echo "OK::budget-guard error")

if [[ "$STATUS" == BLOCK::* ]]; then
    echo "${STATUS#BLOCK::}" >&2
    echo "(SessionStart 차단·\$KORMARC_DAILY_USD_BUDGET 조정 또는 다음날 재시도)" >&2
    exit 2
fi

# 정상 = 상태만 stdout
echo "${STATUS#OK::}"
exit 0
