# RUNBOOK — kormarc-auto 운영 핸드북

> Cycle 44 (V3 Block 7 정합·외부 256 출처) — 야간 무중단 자율 + 사고 응답 단일 진실원.
> 매일 운영자(PO)가 첫 5분에 보는 곳·고장 시 첫 30분에 보는 곳.

---

## 0. Tonight's Command (오늘 밤 한 줄)

### Phase 1 (현재·OAuth + 로컬)

```bash
./automation/po_loop.sh "다음 매출 차단점 1건 자동 진행"
```

### Phase 2 (사업자 등록 + Anthropic API 키 발급 후·Docker)

```bash
./automation/po_loop_with_cost_guard.sh \
  --hard 20 --soft 5 --per-iter 2 \
  "다음 매출 차단점 1건 자동 진행"
```

### 정지 (3 방법·아무거나)

```bash
touch /tmp/po-stop                 # 다음 사이클부터 정지
# 또는 Ctrl+C (트랩 → STOP 파일 자동 생성)
# 또는 채팅 입력: STOP / PAUSE
```

---

## 1. Morning Check (매일 아침 5분)

```bash
make blocker          # 매출 차단점 자동 감지 (next_blocker.py)
make cost             # 일일 USD 비용 + 14일 누적
git log --oneline -10 # 어젯밤 commit 누적
cat PROGRESS.md | head -30  # 사이클 진척
```

핵심 확인 (5건):
1. **`make blocker`** = critical/high 차단점 변화·신규?
2. **`make cost`** = 어제 비용 누적·USD < 일일 캡?
3. **GitHub actions** = regression-check.yml 통과?
4. **자관 round-trip** = baseline 100% 유지?
5. **Slack/Cron 알림** = 비용 캡·anomaly 발생?

---

## 2. Weekly Routine (월요일 30분)

```bash
# 1. 주간 리포트 (1주 audit 데이터 후·Cycle 47 Block 4 활성)
make weekly

# 2. learnings 리뷰 + 헌법 후보 검토
cat learnings.md | head -100

# 3. router 자동 업데이트 (1개월+ 데이터 후·Cycle 46 활성)
# python3 automation/update_router.py --dry-run

# 4. ADR 누적 검토
ls -t docs/adr/ | head -5

# 5. 다음 주 사이클 큐 재정렬 (AUTONOMOUS_BACKLOG.md)
```

**임계 위반 시 액션** (V3 §4.2 13 메트릭 정합):
- M01 성공률 < 70% → router unsafe 추가
- M03 평균 반복 > 15 → PROMPT 분해
- M04 cycle당 > $3 → Haiku 비중 ↑
- M09 ctx > 15% 포화 → subagent 분리
- M13 야간 ROI× < 1.0 → **야간 운영 일시 중단**

---

## 3. Incident Response (사고 시 첫 30분)

### 3.1 비용 폭주 (Slack 80% 알림 또는 hard cap)

```bash
# 1. 즉시 차단 (모든 Claude Code 세션 정지)
./scripts/automation/emergency-stop.sh

# 2. 마지막 1시간 비용 분석
make cost

# 3. /tmp/claude-budget.json 확인
cat /tmp/claude-budget.json | jq .

# 4. 패턴 진단 (V3 §3.6 사례)
# - 무한 루프? → --max-turns 누락 확인
# - 동일 명령 반복? → tool error 무시 패턴
# - context rebuild loop? → MCP 도구 너무 많음
```

### 3.2 자관 round-trip 회귀 (1pp 초과)

```bash
# 1. 즉시 회귀 베이스라인 비교
python scripts/regression_check.py --strict

# 2. 차이 분석
diff docs/eval/results/2026-05-04/regression_baseline.json \
     docs/eval/results/$(date +%Y-%m-%d)/per-record.json

# 3. 직전 commit revert
git log --oneline -5
git revert <SHA>
git push
```

### 3.3 자관 데이터 누설 시도 차단

```bash
# 1. .gitignore + .claudeignore 확인
grep -E "^D:|자관|PILOT" .gitignore .claudeignore

# 2. 최근 커밋 leak 검증
git diff HEAD~5..HEAD | grep -iE "okwhr[^-]|박지수|김기수|박세진|신은미|조기흠|내건숲|은평구공공" \
  | grep -vE "사서 [A-E]|anonymize|forbidden"

# 3. 의심 시 즉시 force-pull X·git history 검토 후 PO 통보
```

### 3.4 GitHub Actions 실패

```bash
# 1. 최신 실행 확인
gh run list --limit 5

# 2. 실패 로그
gh run view <run-id> --log-failed

# 3. regression-check.yml = D:\ 미접근 = expected SKIPPED
# test-hooks.yml = hook 회귀 = critical
```

### 3.5 Claude Code 인증 깨짐

상세: `docs/automation/HEADLESS_AUTH.md` §"5 디버깅 케이스".

```bash
# 1. /status 활성 인증 확인 (Claude Code 안)
# 2. ANTHROPIC_API_KEY env 확인 (OAuth 무시 함정)
unset ANTHROPIC_API_KEY  # OAuth로 돌아가려면

# 3. setup-token 1년 토큰 재발급 (Max 구독 헤드리스 시)
claude setup-token
```

---

## 4. Slack 신호 가이드 (cost_supervisor 알림)

| 이모지 | 의미 | PO 액션 |
|---|---|---|
| 🚀 | 시작 | 관찰만 |
| 🏁 | iter 완료 | 관찰 |
| ⚠️ SOFT | soft cap 도달 (예: $5) | 관찰·계속 가능 |
| 🚨 80% | 80% 도달 (예: $16/$20) | 30분 내 마무리 권장 |
| ⛔ HARD CAP | 강제 종료 (SIGTERM) | 즉시 비용 분석 |
| ⚠️ per-iter | 단일 iter 폭주 | 명세 모호 또는 도구 폭주 |
| ✅ end | 정상 종료 | 관찰 |

---

## 5. 주요 Make 명령

```bash
make help        # 사용 가능 명령 출력
make test        # pytest -q
make gates       # ruff + pytest + assertions + regression + demo
make blocker     # 매출 차단점 자동 감지
make cost        # 일일 비용 + 14일 누적
make funnel      # 주간 funnel 리포트 (P34)
make demo        # 30초 offline demo (zero API)
make regression  # 자관 round-trip baseline 비교
make audit       # audit-query.sh (ccusage 호환)
make stop        # emergency-stop.sh
make rollback    # rollback.sh (마지막 commit 복원)
make pavr ARGS="<task>"  # /pavr 슬래시 명령
```

---

## 6. 외부 의존 차단점 (PO 외부 작업)

`docs/external-dependencies-matrix-2026-05.md` 단일 진실원.

### 즉시 가능 (PO 30분~3일)
- **PO-PROD-1** 일반과세자 홈택스 등록 → P30 PortOne 라이브 활성
- **PO-PROD-5** NL_CERT_KEY 발급 → 정확도
- **PO-PROD-6** ANTHROPIC_API_KEY 발급 → AI 기능
- **SALES-1** 사서 5명 인터뷰 → wedge 확정

### Phase 2 (사업자 등록 후)
- **night workspace** Console 신설·spend cap $50/월
- **PortOne v2 라이브 모드** 활성
- **사업자통장** 카뱅/토스 + 시중은행 1

---

## 7. 핵심 invariants (위반 = 즉시 STOP)

1. 헌법 위반 0건 (raw 확률·100% 자동·본문 LLM 송신·사서 검토 우회)
2. 자관 데이터 git 누설 0건 (D:\ commit 시도 = 자율 정지)
3. 결정론 (ADR 0028·temperature=0)
4. AI 출처 표시 (ADR 0029·KORMARC 588 + audit log + UI ghost text)
5. 카테고리형 신뢰 (ADR 0030·raw % 금지)
6. KWCAG 2.2 (ADR 0032·Level AA)
7. KOLAS3 종료일 = 2026-12-31 (1초 변경 = STOP·ADR 0026)
8. 야간 자율 = cost_supervisor.py 래핑 의무 (ADR 0041·Phase 2+)
9. budget-cap-precheck.sh exit 2 = 절대 우회 금지 (ADR 0041)
10. audit.jsonl append-only = 직접 편집·삭제 금지 (ADR 0041)

---

## 8. 참조

- `STATUS.md` — 단일 진실원 (Cycle 7+)
- `META_REVIEW.md` — 7-cycle 회고
- `learnings.md` — 사실 누적 + 헌법 후보
- `decisions.md` — V2 §4.4 의사결정 로그
- `PROGRESS.md` — Stop hook 자동 갱신
- `docs/automation/INDEX.md` — 자동화 6 영역 색인
- `docs/automation/HEADLESS_AUTH.md` — V3 Block 1
- `docs/automation/MCP_MATRIX.md` — Cycle 22 P45
- `docs/external-dependencies-matrix-2026-05.md` — PO 외부 작업
- `agent_docs/operations.md` — Cycle 27 운영 핸드북
- `AUTONOMOUS_BACKLOG.md` — 자율 큐 P29~P52

---

## 9. 변경 이력

- v1 (2026-05-06·Cycle 44) — V3 Block 7 정합·초기 발행
