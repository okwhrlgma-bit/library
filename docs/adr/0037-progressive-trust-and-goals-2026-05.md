# ADR 0037 — Progressive Trust + Goal Decomposer + MCP 매트릭스 + cron weekly

- 상태: Accepted (2026-05-06·Cycle 22 P44+P45+P46+P51+P52 일괄 통합)
- 일자: 2026-05-06
- 트리거: PO 명시 ("계속해서 진행 모두 승인 및 통합")·V2 §5·§6·§7·§10

## Context

PO 명시 = "모두 승인 및 통합"·자동화 인프라 잔여 V2 큐 일괄 진행.
사이클별 분할 대신 1 사이클 = 5 P (P44·P45·P46·P51·P52) 통합.

## Decision

### 1. Progressive Trust (P51·V2 §6.4)
- `src/kormarc_auto/trust/progressive.py`
  * 5 Level (Read 만 → +Edit → +Write/npm → +Bash(*) → +MCP write)
  * 30회 연속 성공 = 승격 가능 (1회 실패 = consecutive reset)
  * `record_automation_outcome()`·`can_promote()`·`suggest_next_level()`
  * 승격 = PR 자동 생성 → PO 승인 (자동 머지 X·V2 §11)
- 15 tests passing

### 2. Goal Decomposer (P52·V2 §5)
- `src/kormarc_auto/goals/decomposer.py`
  * 5계층 = Goal → Strategy → Initiative → Task → Action
  * 상위 3 = PO·하위 2 = 자동
  * `is_forbidden_action()` = 7 금지 (가격·도메인·DB·결제·이메일·env·PII)
  * `suggest_daily_actions()` = KPI 약점 기반 1~3건 (max 3)
- 12 tests passing

### 3. MCP 매트릭스 (P45·V2 §6)
- `docs/automation/MCP_MATRIX.md`
- 7 MCP 우선순위 (Stripe·Gmail·Slack·Sheets·Notion·GA4·Postgres)
- 각 MCP = PreToolUse 화이트리스트 + 캡 + 처리방침 §28의8 갱신 정합

### 4. 메타 라우터 통합 (P46·Cycle 21 차용 router.py 정합)
- automation/router.py = 8 TaskKind 분류 (claude-saas-starter 차용·Cycle 21)
- Progressive Trust state와 통합 가능 (자동화 항목별 record_automation_outcome 호출)
- 본 ADR = 통합 박제만·실 호출은 PO Anthropic API 키 발급 후

### 5. cron weekly funnel (P44·V2 §10.5)
- `scripts/automation/weekly-funnel-cron.sh`
- 매주 월요일 09:00 KST = generate_weekly_report (P34) 정합
- Slack webhook 발송 + docs/automation/reports/weekly-{date}.md 저장
- crontab 활성: `0 9 * * 1 /path/weekly-funnel-cron.sh`

### 6. 영구 invariants (V2 §11)
- Progressive Trust = 자동 승격 절대 X (PR + PO 승인만)
- Goal Decomposer = FORBIDDEN_ACTIONS 7건 자동 차단
- MCP = PreToolUse hook 게이트·처리방침 동시 갱신
- cron = 비용 캡 (월 $50 초과 = 일시 정지)

## Consequences

### Positive
- 자동화 인프라 잔여 5 P = 1 사이클 일괄 = PO 시간 절약
- Progressive Trust = 시간 흐를수록 권한 자동 확대 (안전하게)
- Goal Decomposer = 일일 cron 자동 액션 (paid pilot 후 즉시 활성)
- MCP 매트릭스 = 각 외부 시스템 진입 절차 박제
- cron weekly = PO 의사결정 5분 단축 (월요일 자동 슬랙)

### Negative
- 5 P 일괄 = ADR 0037 1건이 5 영역 책임 = 미래 분리 가능성
- Progressive Trust state = JSON 파일 30+ 누적 시 디스크 (관리 필요)
- Goal Decomposer FORBIDDEN_ACTIONS = 한국어 키워드 휴리스틱 (false positive 가능)

### Risk Mitigation
- can_promote = 5 Level 상한·자동 승격 X·PR 생성만
- FORBIDDEN_ACTIONS 매칭 시 = is_forbidden=True + 안전 표시
- MCP 매트릭스 = 활성 전 6 단계 체크리스트 (PreToolUse·캡·audit·처리방침·PIPC·PR)
- cron = 비용 캡 ENV (KORMARC_DAILY_USD_BUDGET 정합·Cycle 19A)

## V2 정합 매트릭스 (Cycle 22 마무리)

| V2 § | 본 ADR 적용 |
|---|---|
| §1 메타 라우터 | ✅ Cycle 21 차용 router.py·Cycle 22 통합 박제 |
| §3.1 Proposer-Critic | ✅ Cycle 21 차용 proposer_critic.py |
| §5 Goal Decomposer | ✅ src/kormarc_auto/goals/decomposer.py (P52) |
| §6.4 Progressive Trust | ✅ src/kormarc_auto/trust/progressive.py (P51) |
| §6 MCP | ✅ docs/automation/MCP_MATRIX.md (P45) |
| §7 Multi-SaaS supervisor | ✅ Cycle 21 차용 supervisor.py |
| §10 마스터 코드 | ✅ Cycle 21 차용 5 hooks + 5 scripts |
| §10.5 cron weekly | ✅ scripts/automation/weekly-funnel-cron.sh (P44) |
| §11 안전 체크리스트 | ✅ FORBIDDEN_ACTIONS·자동 머지 X·캡 |

## Plan B 큐 (P29~P52) 완료 매트릭스

| P | 영역 | 상태 |
|---|---|---|
| P29 | 처리방침 §28의8 + AI disclaimer | ✅ Cycle 10B |
| P30 | PortOne v2 sandbox | ⏳ 사업자 등록 후 |
| P31 | 4 플랜 가격 페이지 | ✅ Cycle 11 |
| P32 | 5분 위저드 + activation | ✅ Cycle 19B |
| P33 | 한도 알림 + CTA | ✅ Cycle 13B |
| P34 | Funnel Plausible | ✅ Cycle 14B |
| P35 | 네이버 SEO + JSON-LD | ✅ Cycle 15B |
| P36 | 블로그 파이프라인 | ✅ Cycle 16A |
| P37 | KOLAS III 카운트다운 | ✅ Cycle 12 |
| P38 | 자치구 묶음 영업 | ✅ Cycle 16B |
| P39 | 사서어 매핑 | 🟡 부분 (Cycle 10A field_status·KLA 5/31 후) |
| P40 | LLM GEO 인용 측정 | ✅ Cycle 18B |
| P41 | Stop hook PROGRESS | ✅ Cycle 17 |
| P42 | hooks 강화 | ✅ Cycle 18A·21 |
| P43 | 슬래시 /deploy | ✅ Cycle 21 (사업자 후 활성) |
| P44 | cron weekly funnel | ✅ Cycle 22 (이번) |
| P45 | MCP 매트릭스 | ✅ Cycle 22 (이번·박제만) |
| P46 | 메타 라우터 | ✅ Cycle 21 차용·Cycle 22 통합 |
| P47 | PAVR 슬래시 | ✅ Cycle 20A |
| P48 | learnings + Replay | ✅ Cycle 20B |
| P49 | budget-guard | ✅ Cycle 19A·21 |
| P50 | refine-claudemd | ✅ Cycle 21 |
| P51 | Progressive Trust | ✅ Cycle 22 (이번) |
| P52 | Goal Decomposer | ✅ Cycle 22 (이번) |

**24 P 중 22 완료·2 미완 (P30 사업자 후·P39 KLA 5/31 후·둘 다 외부 의존)**.

## References

- 외부 자동화 V2 §1·§3·§5·§6·§7·§10·§11
- 외부 매출 보고서 (2026-05-05) P29~P40
- ADR 0024~0036 (전체 정책)
- claude-saas-starter (Cycle 21 차용·삭제 완료)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 22 일괄 통합 마무리
