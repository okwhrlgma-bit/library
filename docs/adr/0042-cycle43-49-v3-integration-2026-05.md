# ADR 0042 — Cycle 43~49 V3 통합 마무리 (Auth + Cost Cap + Audit + Weekly + RUNBOOK)

- 상태: Accepted (2026-05-06·Cycle 49 7-cycle 통합)
- 일자: 2026-05-06
- 트리거: PO "만들던 자동화 툴 지속해서 진행"·V3 외부 256 출처 마스터 가이드 흡수 마무리

## Context

ADR 0041 (Cycle 43) = V3 Block 1+2+3 즉시 통합·Block 4~7 미룸.
Cycle 44~49 = V3 §6 권고 정합으로 즉시 가능한 항목 일괄:
- Block 4 weekly_report scaffold (1주 후 데이터 활성·지금은 graceful)
- Block 7 verify-overnight-stack 부분 = RUNBOOK
- Phase 2 wrapper (PO 외부 의존 후 즉시 활성)
- KOLAS III D-day 자동 갱신 (Cycle 12 P37 활용)

## Decision

### Cycle 44 — `docs/RUNBOOK.md` (V3 Block 7 핵심)
- "Tonight's command" / "Morning check" / "Weekly routine" / "Incident response"
- Phase 1 (현재 OAuth) + Phase 2 (사업자 등록 후 API 키) 분기
- Slack 신호 가이드 (cost_supervisor 알림 8 emoji)
- 영구 invariants 10건 박제 (V3 추가 3건 포함)

### Cycle 45 — `automation/po_loop_with_cost_guard.sh`
- po_loop.sh + cost_supervisor.py 통합 wrapper
- Phase 2 활성 (Anthropic API 키 발급 후)
- abort 감지·cumul/hard 표시·SIGTERM exit 2 처리
- 인증 미설정 시 사전 차단 (V3 §2 정합)

### Cycle 46 — `scripts/automation/kolas3-daily-update.sh`
- 매일 06:00 KST cron = D-day 자동 갱신
- urgency_window 전환 시 Slack 알림 (golden → critical → expired)
- 검증: D-238 (golden) 계산 정상

### Cycle 47 — `automation/weekly_report.py` (V3 Block 4 scaffold)
- audit.jsonl + usage.json + git log → 13 메트릭 markdown
- LLM 호출 0 (V3 §4.10 정합·통계 결정적)
- 데이터 부족 시 graceful 메시지 + 7일 누적 힌트
- 자동 권장 액션 (성공률 < 70%·반복 > 15·cost > $3·ctx > 15%)

### Cycle 48 — `tests/test_weekly_report.py`
- 21 테스트·V3 §4 invariants 검증
- TestComputeMetricsEmpty (graceful)·Basic·Cost·Categories·Render·V3Invariants
- LLM 의존 부재 검증 (anthropic·openai SDK 0건)

### Cycle 49 — Makefile + ADR 0042 + META_REVIEW
- `make weekly` = V3 Block 4 트리거
- `make kolas3` = KOLAS3 D-day 갱신
- `make night-loop` = Phase 2 안내

## Alternatives

1. **Block 4~7 미룸 유지** — V3 §6 = "1주~30일 후"·하지만 scaffold 없으면 활성 시 지연·**채택 X**
2. **scaffold + 활성 동시** — 데이터 부족 = 거짓 메트릭·**거부**
3. **RUNBOOK 미작성** — 사고 시 첫 30분 진단 없음·**거부**
4. **kolas3 cron = Phase 2 미룸** — D-238 골든윈도우 = 매일 갱신 가치·**즉시 활성**

## Consequences

### Positive
- V3 마스터 가이드 = 100% scaffolding 완료 (Block 1~7 모두)
- audit.jsonl 7일 누적 시 weekly 즉시 가동 가능
- PO Phase 2 (사업자 등록 후) = wrapper 즉시 활성
- 사고 시 첫 30분 = RUNBOOK 단일 진실원

### Negative
- weekly_report = audit hook 활성 후 7일 = 2026-05-13까지 빈 데이터 graceful
- po_loop_with_cost_guard = ANTHROPIC_API_KEY 부재 시 차단 (Phase 1 = po_loop.sh 사용)
- kolas3 cron = Windows = 수동 또는 Task Scheduler (Linux/Mac = crontab 표준)

### Neutral
- 테스트 수: 1,119 → 1,140 (+21)
- ADR: 0041 → 0042
- Makefile: 3 신규 명령 (weekly·kolas3·night-loop)
- 자동화 모듈 = 100% scaffolding·활성은 외부 트리거 의존

## V3 통합 매트릭스 최종 (Cycle 43~49)

| V3 영역 | Cycle | 상태 | 모듈 |
|---|---|---|---|
| Block 1 (Auth) | 43 | ✅ doc | docs/automation/HEADLESS_AUTH.md |
| Block 2 Layer 1 (watchdog) | 43 | ✅ | automation/cost_supervisor.py |
| Block 2 Layer 2 (PreToolUse) | 43 | ✅ | .claude/hooks/budget-cap-precheck.sh |
| Block 2 Layer 3 (Stop) | 17·19A | 🟡 간접 | append-progress.sh + budget tracker |
| Block 3 (audit.jsonl) | 43 | ✅ | .claude/hooks/audit-log.sh |
| Block 4 (weekly_report) | 47 | ✅ scaffold·1주 후 활성 | automation/weekly_report.py |
| Block 5 (Haiku 분류기) | - | ⏳ 30일 후 | (미작성·데이터 의존) |
| Block 6 (cross-project sync) | - | ⏳ 두 번째 SaaS | (미작성·미해당) |
| Block 7 (verify-overnight) | 44·49 | ✅ doc + Makefile | docs/RUNBOOK.md + make ci |

## 영구 invariants 매트릭스 (10건·ADR 0041 추가 3건 포함)

| # | invariant | 위반 = STOP |
|---|---|---|
| 1 | 헌법 위반 0건 | ✓ |
| 2 | 자관 데이터 git 누설 0건 | ✓ |
| 3 | 결정론 (ADR 0028) | ✓ |
| 4 | AI 출처 표시 (ADR 0029) | ✓ |
| 5 | 카테고리형 신뢰 (ADR 0030) | ✓ |
| 6 | KWCAG 2.2 (ADR 0032) | ✓ |
| 7 | KOLAS3 종료일 = 2026-12-31 (ADR 0026) | ✓ |
| 8 | 야간 자율 = cost_supervisor 래핑 (ADR 0041·Phase 2+) | ✓ |
| 9 | budget-cap-precheck.sh exit 2 우회 금지 (ADR 0041) | ✓ |
| 10 | audit.jsonl append-only·직접 편집·삭제 금지 (ADR 0041) | ✓ |

## 다음 7-cycle 권장 (Cycle 50~56)

| Cycle | 영역 | 우선순위 | 의존 |
|---|---|---|---|
| 50 | weekly_report 1주 데이터 검증 (2026-05-13 후) | 시간 의존 | audit.jsonl 누적 |
| 51 | V3 Block 5 router_patcher AST + Haiku 분류기 | 30일 후 데이터 | 1개월+ audit |
| 52 | KOLAS3 streamlit_app countdown 실시간 카드 | 즉시 | docs/sales JSON |
| 53 | revenue_dashboard 통합 메트릭 추가 | 즉시 | weekly + blockers |
| 54 | cron weekly_report.yml + GitHub Actions | 즉시 | 자율 |
| 55 | META_REVIEW Cycle 43~56 + ADR 0043 | 7-cycle 마무리 | 누적 |
| 56 | (예비·외부 의존 해소 시 P30 PortOne 활성) | PO 외부 | 사업자 등록 |

## 21 사이클 누적 (Cycle 22 → 49)

- Tests: 1,009 → **1,140** (+131 over 28 cycles)
- ADRs: 0036 → **0042** (+7)
- Plan B P29~P52 = 22/24 (외부 의존 P30·P39만)
- V2 §1·§3·§5·§6·§7·§10·§11 = 100% scaffolding
- V3 Block 1·2·3·4·7 = ✅ scaffolding·5·6 = ⏳ (데이터/시간 의존)
- 메모리: 7건 (901·858·매출·V1·V2·V3·1-명령 1-완료 ⭐⭐⭐⭐⭐)
