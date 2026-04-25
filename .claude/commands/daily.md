---
description: 매일 시작 — 현황 점검 + 오늘 우선순위 3가지
---

## Step 1 — 환경·git 상태

```powershell
git status
git log --oneline -5
git branch --show-current
.\.venv\Scripts\Activate.ps1
kormarc-auto info
```

## Step 2 — 빠른 헬스 체크

```powershell
ruff check src tests
pytest -v --tb=line
```

실패 있으면 즉시 우선 수정 (Level 2).

## Step 3 — 오늘의 3가지 제안

`docs/spec.md` "다음 세션 작업 큐"를 보고 다음 형식으로 3가지 제안:

```
# 오늘의 시작 — YYYY-MM-DD

## 📊 현황
- Git: clean / N개 미커밋
- 테스트: N개 통과 / 0개 실패
- 환경변수: ✓ NL_CERT_KEY / ✓ ALADIN_TTB_KEY / ...

## 🎯 오늘의 3가지 제안

**1. [가장 중요한 것]** (약 N분)
- 왜: [어떤 결과 지표에 기여]
- 어떻게: [첫 명령]

**2. [두 번째]** (약 N분)
**3. [세 번째]** (약 N분)
```

PO는 1/2/3 중 선택만. 결정 부담 PO → Claude로 이전.
