#!/usr/bin/env bash
# KST 시각 + 모델 + 비용 한 줄 statusline. 사서 친화 — 영문 약어 최소.
KST=$(TZ='Asia/Seoul' date '+%H:%M' 2>/dev/null || date '+%H:%M')
INPUT=$(cat 2>/dev/null || echo '{}')
MODEL=$(echo "$INPUT" | "/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe" -c "import sys, json; d=json.load(sys.stdin); print(d.get('model', {}).get('display_name', '?'))" 2>/dev/null || echo "?")
COST=$(echo "$INPUT" | "/c/Users/okwhr/OneDrive/바탕 화면/클로드 코드 활동용/kormarc-auto/.venv/Scripts/python.exe" -c "import sys, json; d=json.load(sys.stdin); c=d.get('cost', {}).get('total_cost_usd', 0); print(f'{c:.2f}')" 2>/dev/null || echo "0.00")
printf "🤖 %s | 💰 \$%s | KST %s | kormarc-auto" "$MODEL" "$COST" "$KST"
