#!/usr/bin/env bash
# Cycle 21 (V2 §4.2·차용) — SessionStart에서 learnings.md 최근 N개 주입.
# 다음 세션이 이전 실패 패턴 인지 가능 (3-Tier Memory Warm Tier).

REPO="/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto"
LEARNINGS="$REPO/learnings.md"

[ -f "$LEARNINGS" ] || exit 0

# 최근 헤더 (## YYYY-MM-DD) 5개 + 본문 추출
echo ""
echo "=== learnings.md 최근 5개 항목 (V2 §4.2 SessionStart 자동 주입) ==="
"/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe" -c "
from pathlib import Path
text = Path(r'$LEARNINGS').read_text(encoding='utf-8')
lines = text.split('\n')
out = []
header_count = 0
for line in lines:
    if line.startswith('## '):
        header_count += 1
        if header_count > 5:
            break
    if header_count >= 1 and header_count <= 5:
        out.append(line)
print('\n'.join(out[:200]))  # 200줄 cap
" 2>/dev/null || echo "(learnings 주입 skip)"

exit 0
