# ADR 0041 — V3 Block 1+2+3 통합 (Headless Auth + Cost Cap + Audit)

- 상태: Accepted (2026-05-06·Cycle 43 통합)
- 일자: 2026-05-06
- 트리거: PO V3 마스터 가이드 (외부 256 출처) "정리해서 연구해줘" + 무한 진행

## Context

V1 (Cycle 17·자동화 4 레이어) + V2 (Cycle 32~35·메타 오케스트레이션) 후
V3 = 야간 무중단 자율 운영 3 빈자리만 깊게.

V3 자체 §6 결론: "오늘 Block 1·2·3만 깔아라 → 1주 후 Block 4 → 30일 후 Block 5" 정합.

## Decision

### Block 1 — Headless Auth (V3 §2)
- `docs/automation/HEADLESS_AUTH.md` 신설 (condensed·Windows PO 환경 정합)
- 인증 우선순위 박제·5 디버깅 케이스·workspace 분리 가이드
- Phase 1 (현재) = OAuth 유지·Phase 2+ = night workspace + API 키

### Block 2 — Cost Cap 3-Layer (V3 §3.7)
- `automation/cost_supervisor.py` 신설 (단일 세션 watchdog·기존 `automation/supervisor.py` 멀티 프로젝트와 분리)
- `.claude/hooks/budget-cap-precheck.sh` 신설 (PreToolUse Layer 2)
- 기존 `src/kormarc_auto/budget/tracker.py` (Cycle 19A) = 일일 USD 누적 (별도 트랙·Layer 3 정합)
- 모델 가격 PRICING dict 박제 (Sonnet 4.6 $3/$15·Haiku 4.5 $1/$5·Opus 4.7 $5/$25)
- atomic state write·jq 부재 시 silent passthrough

### Block 3 — Audit Log Schema (V3 §3.2)
- `.claude/hooks/audit-log.sh` 신설 (PostToolUse·tool_call 단위)
- 기존 `src/kormarc_auto/audit/store.py` (Cycle 9) = KORMARC 레코드 단위 (별도 트랙)
- 본 hook = Claude Code 세션 도구 호출 단위·V3 weekly_report 입력 자산

## Alternatives

1. **`--max-budget-usd` 단독 의존** — 거부. V3 §3.4 = 공식 cli-reference 미등재·검증 부족·단독 금지
2. **Anthropic Admin Usage API 폴링** — 거부. V3 §3.8 = 5분 지연·하드 스톱 부적합 (사후 정산만)
3. **기존 supervisor.py에 cost guard 통합** — 거부. 멀티 프로젝트 큐 디스패치와 책임 혼합·SRP 위반
4. **Block 4 (weekly_report) 동시 적용** — 미룸. V3 §6 = "1주 데이터 쌓인 후" 권고 정합
5. **Block 5 (Haiku 분류기) 동시 적용** — 미룸. V3 §6 = "30일 후 데이터로 임계 재조정"
6. **Block 6 (cross-project sync)** — 미룸. 두 번째 SaaS 시작 시점에만 의미

## Consequences

### Positive
- 야간 무중단 자율 시 비용 폭주 차단 게이트 = 3 계층 박제 (사고 1건 손실 << 30분 작업)
- audit.jsonl 스키마 = 7일 후 weekly_report 즉시 가동 가능
- 인증 분리 가이드 = Phase 2 (사업자 등록 후 API 키 발급) 즉시 활성

### Negative
- cost_supervisor.py = stream-json subprocess 호출 시에만 작동 (Claude Code 자체 호출은 이 wrapper 안에서만 보호)
- jq 의존 (Windows = git-bash 기본 포함·외부 환경 = silent fallback)
- atomic write = 분산 환경 (NFS) 정합성 보장 X (PO 1인 운영 = 무관)

### Neutral
- ADR 0035 (Cycle 19A budget tracker) 와 분리·중첩 보호
- supervisor.py (Cycle 21·멀티 프로젝트) 보존·cost_supervisor.py 별도 파일

## Related ADRs

- ADR 0035 budget tracker (Cycle 19A) — 일일 USD 누적·Layer 3 정합
- ADR 0029 audit log + AI disclaimer (Cycle 9) — KORMARC 레코드 단위 (별도 트랙)
- ADR 0028 결정론 (Cycle 8) — 비용 일관성 정합
- ADR 0036 PAVR + Failure Replay (Cycle 20) — 사이클 재시도 비용 가시화

## V3 정합 매트릭스

| V3 영역 | 적용 | 모듈 |
|---|---|---|
| Block 1 (Auth) | ✅ doc | docs/automation/HEADLESS_AUTH.md |
| Block 2 (Cost Cap Layer 1 watchdog) | ✅ | automation/cost_supervisor.py |
| Block 2 (Cost Cap Layer 2 PreToolUse) | ✅ | .claude/hooks/budget-cap-precheck.sh |
| Block 2 (Cost Cap Layer 3 Stop) | 🟡 | append-progress.sh + budget tracker (간접) |
| Block 3 (audit.jsonl) | ✅ | .claude/hooks/audit-log.sh |
| Block 4 (weekly_report) | ⏳ | 1주 후 활성 |
| Block 5 (Haiku 분류기) | ⏳ | 30일 후 활성 |
| Block 6 (cross-project) | ⏳ | 두 번째 SaaS 시작 시 |
| Block 7 (verify-overnight-stack) | ⏳ | Phase 2 (Docker) 시 |

## V3 자체 권고 (skeptical review §6) 정합

V3 §6 = "Block 4~7 = 1주~30일 후 데이터로 임계 재조정" 정합:
- ✅ 한계효용 매우 높음 (즉시 필요): Block 1 + Block 2 supervisor (오늘)
- 🟡 한계효용 중간 (1주 후): Block 2 hooks (이번 적용·중첩 안전망) + Block 3 (스키마만 박제)
- ⏳ 한계효용 낮음 (1개월+): Block 4 weekly·Block 5 router·Block 6 cross-project

## 영구 invariants 추가

8. 야간 자율 = cost_supervisor.py 래핑 의무 (PO Phase 2+ 환경)
9. budget-cap-precheck.sh exit 2 = 절대 우회 금지
10. audit.jsonl append-only = 직접 편집·삭제 금지

## 다음 7-cycle 권장 (Cycle 44~50)

| Cycle | 영역 | 우선순위 |
|---|---|---|
| 44 | V3 Block 4 weekly_report (1주 audit 데이터 후) | 사이클 50 후 |
| 45 | po_loop.sh + cost_supervisor 통합 검증 (Phase 2 사업자 후) | PO 외부 |
| 46 | Block 5 router_patcher AST + Haiku 분류기 (1개월 후) | 데이터 의존 |
| 47 | docs/RUNBOOK.md (V3 Block 7 정합·운영 핸드북 보강) | 즉시 가능 |
| 48 | KOLAS3 D-day 자동 갱신 cron + countdown UI | 즉시 가능 |
| 49 | META_REVIEW Cycle 36~49 + ADR 0042 | 7-cycle 마무리 |
| 50 | (예비·외부 의존 해소 시 P30 PortOne 전환) | PO 외부 |
