# Operations Handbook (Cycle 27·운영 핸드북·Cycle 58 V3 통합)

> Plan B 무중단 자율 + V2 L4 자율성 + V3 외부 256 출처·1인 SaaS 운영 단일 진실원.
> **상세 사고 응답**: `docs/RUNBOOK.md` (Cycle 44·Tonight's command·Morning check·Incident response).

## 매일 (PO 외부 작업·5분)

```bash
make blocker       # 매출 차단점 자동 감지
make cost          # 일일 USD 비용 확인
make kolas3        # KOLAS III D-day 갱신 (cron 자동·수동 트리거)
```

## 매주 월요일 (5분)

```bash
make funnel        # 주간 funnel 리포트 (P34)
make weekly        # V3 Block 4 주간 리포트 (Cycle 47·1주 audit 데이터 후)
git log --oneline -20  # 지난 주 commit 검토
```

## 매월 1회 (router_patcher·V3 Block 5)

```bash
python automation/router_patcher.py --dry-run   # 30일 audit 권고
python automation/router_patcher.py --apply     # PR 브랜치 생성·자동 머지 X
```

활성: 2026-06-06+ (audit.jsonl 30일 누적 후·MIN_SAMPLES=20).

## V3 야간 무중단 자율 (Phase 2·사업자 등록 + API 키 후)

```bash
# Tonight's command (RUNBOOK §0)
./automation/po_loop_with_cost_guard.sh \
  --hard 20 --soft 5 --per-iter 2 \
  "다음 매출 차단점 1건 자동 진행"

# 정지 (3 방법)
touch /tmp/po-stop                 # po_loop 다음 사이클부터
# Ctrl+C                           # 트랩 → STOP 파일 자동
# 채팅: "STOP" / "PAUSE"            # 즉시
```

## V3 사고 응답 (RUNBOOK §3 정합)

| 영역 | 명령 | 시점 |
|---|---|---|
| 비용 폭주 | `make stop` + `cat /tmp/claude-budget.json` | 즉시 |
| 자관 round-trip 회귀 | `python scripts/regression_check.py --strict` | 1pp 초과 시 |
| GitHub Actions 실패 | `gh run list --limit 5` + `gh run view <id> --log-failed` | 매주 |
| 인증 깨짐 | `unset ANTHROPIC_API_KEY` 후 `claude /login` | 401 시 |
| 자관 누설 의심 | `git diff HEAD~5..HEAD \| grep -iE 'okwhr[^-]\|박지수'` | 발견 시 |

## 매월 (15분)

- learnings.md 최근 30일 패턴 검토
- decisions.md 누적 결정 검토
- `/refine-claudemd` 슬래시 (자동 PR·자동 머지 X)

## 매 commit (자동·hook)

- PreToolUse / Bash = validate-bash.sh (위험 패턴 차단)
- PreToolUse / Write·Edit = scan-secrets.sh (시크릿 차단)
- PostToolUse / Edit·Write = post-format.sh (자동 ruff)
- Stop = append-progress.sh (PROGRESS.md) + binary_assertions
- SessionStart = inject-recent-learnings.sh + budget-guard.sh
- PreCompact = backup-transcript.sh

## CI (자동·GitHub Actions)

- ci.yml = ruff·pytest·binary_assertions·자관 회귀
- regression-check.yml = 자관 baseline 회귀 (매주 월·main push)
- test-hooks.yml = hook 회귀 (PR·main push)
- nightly-autonomy.yml = 야간 자율 (사업자 등록 후)
- security-audit.yml = 의존성 보안 스캔 (주간)

## 응급 (V2 §11)

```bash
make stop          # 🚨 모든 자율 프로세스 즉시 정지
make rollback      # 최근 1 commit revert
bash scripts/automation/rollback.sh --commits 5   # 5 commit revert
```

자세한 시나리오 = `docs/automation/ROLLBACK_PLAYBOOK.md`.

## 운영 게이트 (Plan B §0·자동 머지 차단 6 게이트)

매 commit 직전 `make gates`:
1. ruff check . = 0 errors
2. ruff format --check = 0 차이
3. pytest -q = 전수 통과
4. binary_assertions 39/39
5. 자관 회귀 ≤ 1pp (`scripts/regression_check.py --strict`)
6. 헌법 §1~§12 위반 0건 (수동 검토)

## 영구 invariants (변경 = ADR 필수)

1. **헌법 위반 0건** (raw 확률·100% 자동·본문 LLM 송신·사서 검토 우회)
2. **자관 데이터 git 누설 0건** (D:\ commit 시도 = 자율 정지·PIPA 사고 차단)
3. **결정론** (temperature=0·top_p=1·모델 pinning·ADR 0028)
4. **AI 출처 표시** (KORMARC 588 + audit log + UI ghost text·ADR 0029)
5. **카테고리형 신뢰** (확실/검토 필요/불확실·raw % UI X·ADR 0030)
6. **KWCAG 2.2 Level AA** (모든 UI·ADR 0032)
7. **KOLAS3 종료일 = 2026-12-31** (1초 변경 = STOP·fact_checker 게이트)

## 세션 종료 (PO·매일)

- 17:30 shutdown ritual (Newport·외부 901 보고서 정합)
- 일요일 = laptop off
- 프로젝트 외 인간과 2시간 이상 대화·1회/주

## 위기 신호 (외부 901 보고서·즉시 7일 휴식)

다음 3건 이상 시 = 7일 프로젝트 정지:
- 인섬니아 ≥ 3일/주·2주 연속
- Sunday-night dread 안 가심
- "프로젝트 실패 = 나 = 무가치" 사고
- 신체 증상 (GI·두통·시야 흐림·재발 감염)
- 비-프로젝트 인간 2시간+ 대화 ≥ 10일 부재
- 프로젝트 향한 분노 (Cait Donovan 가장 신뢰 예측)
- "프로젝트 내일 끝나면?" 질문에 panic

대응: 1577-0199 (24h)·1393 자살예방·청년 마음건강 (`youth.seoul.go.kr`).

## 정합 메모리

- `~/.claude/projects/.../memory/feedback_one_shot_completion_2026_05_06.md` ⭐⭐⭐⭐⭐
- `~/.claude/projects/.../memory/project_solo_founder_diagnosis_2026_05_03.md`
- `~/.claude/projects/.../memory/project_claude_code_automation_v2_2026_05_06.md`
