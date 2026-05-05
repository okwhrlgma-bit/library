---
name: pavr
description: PAVR 자율 루프 (Plan→Act→Verify→Reflect)·worktree 격리·결정론 검증·learnings 자동 갱신
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, TodoWrite
---

# PAVR — 자율 안전 작업 루프 (V2 §2 정합)

너는 PAVR 자율 에이전트다. 다음 작업을 4단계로 실행하라.

작업: $ARGUMENTS

---

## 1. PLAN (명세 먼저)

1. 작업을 테스트 가능한 수용 기준 3~7개로 분해해 `docs/pavr/$(date +%Y%m%d-%H%M%S).md`에 저장.
2. 영향 받을 파일 목록 + 위험도 분석.
3. 롤백 절차 명시 (`git revert <SHA>` 또는 `git checkout main && git branch -D <branch>`).
4. 검증 단계에서 실행할 결정론 셸 명령 목록 (모델이 우회 못 하도록).

**출력**: plan markdown 파일 경로 + 수용 기준 핵심 1줄 보고.

---

## 2. ACT (격리 실행)

1. `git checkout -b pavr/$(date +%Y%m%d-%H%M%S)` 또는 worktree 분기.
2. 수용 기준 충족할 **최소** 변경만.
3. 신규 기능 = 신규 테스트 동시 추가 (헌법 §2 정합).
4. 자관 데이터 (D:\, .mrc 원본) 수정 금지 (영구 invariant).
5. 시크릿 평문 commit 금지 (.claude/hooks/scan-secrets.sh 자동 차단).

---

## 3. VERIFY (결정론·모델 외부)

다음 셸 명령을 순서대로 실행하고 모두 0번 종료여야 함:

```bash
ruff check .
ruff format --check .
python -m pytest -q
python scripts/binary_assertions.py --strict
```

**+ 자관 회귀 ≤ 1pp 확인** (외부 보고서 게이트):
```bash
python scripts/eval_per_record_roundtrip.py --sample 50
# 결과 비교: docs/eval/results/2026-05-04/regression_baseline.json (round-trip 100%)
```

**+ leak 게이트** (PII·자관 식별자):
```bash
git diff --cached | grep -iE "okwhr[^-]|박지수|김기수|박세진|신은미|조기흠|내를건너서|내건숲|은평구공공" \
  | grep -vE "사서 [A-E]|anonymize_pii|forbidden|fact_checker|placeholder" \
  || echo "leak OK"
```

하나라도 실패 시 → 즉시 4단계 (Reflect).

---

## 4. REFLECT (성공 + 실패 모두 학습)

### 성공 시
- `PROGRESS.md` (Stop hook이 자동 갱신·중복 방지)
- 수용 기준 모두 충족 = commit + push (Conventional Commits)
- learnings.md = 시간 낭비한 부분 1줄 (있으면)

### 실패 시
- `learnings.md`에 추가 (top-of-file·자동 SessionStart 주입):
  ```markdown
  ## YYYY-MM-DD — 실패 패턴: <짧은 제목>
  **작업**: <PAVR 작업 요약>
  **증상**: <실패 게이트 + 에러 첫 줄>
  **원인**: <자동 진단 또는 사람 검토>
  **예방**: <다음 PAVR 전 체크할 것>
  ```
- 브랜치 폐기 (`git checkout main && git branch -D pavr/...`)
- 재시도 ≤ 3회·초과 시 사람 큐 (PR 생성 또는 메시지)

---

## STOP 조건 (V2 §11)

다음 시 즉시 중단·사람 호출:
- 결정론 verify 5회 연속 실패
- 자관 데이터 git 누설 시도
- 본문 LLM 송신 시도
- API 키 평문 commit 시도
- 사람 명시 STOP 입력

---

## 보고 형식

각 단계 끝에 한 줄 보고:
```
[PLAN]   docs/pavr/20260506-...md·수용 기준 5건
[ACT]    pavr/20260506-... 브랜치·3 파일 변경
[VERIFY] 5/5 게이트 통과 (ruff·pytest·assertions·자관 회귀·leak)
[REFLECT] 성공·PROGRESS 자동 갱신 (Stop hook)
```

---

## 정합 ADR

- ADR 0028 결정론 (temperature=0·top_p=1 = verify 정합)
- ADR 0029 audit log (REFLECT 단계 정합)
- ADR 0034 hooks (scan-secrets·post-format = ACT 안전망)
- ADR 0035 budget (VERIFY 비용 회귀 부분 정합)
- 외부 자동화 V2 §2 PAVR 루프
