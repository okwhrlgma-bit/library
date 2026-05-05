# ADR 0039 — Cycle 29~35 통합 결정 (Multi-Agent + 운영 청결)

- 상태: Accepted (2026-05-06·Cycle 35 7-cycle 통합)
- 일자: 2026-05-06
- 트리거: PO "진행"·1-명령 1-완료 정합·V2 §3 다중 에이전트 마무리

## Context

Cycle 22~28 = V2 자율 인프라 마무리 (META_REVIEW Cycle 28).
Cycle 29~35 = 운영 청결 + V2 §3.2~§3.4 다중 에이전트 100% 적용.

## Decision

### Cycle 29~31: 운영 청결 + 글로벌
- README.en.md 갱신 (v0.7.0 + 1047 tests + 22/24 Plan B 반영)
- docs/automation/INDEX.md (6 핵심 문서 단일 진입점·운영 cadence·V2 §11 정합)
- docs/archive/TASK_LIST_2026_05_06.md (Cycle 1~28 task ID 매트릭스 보존·신규 ID 132+ 시작점)

### Cycle 32~33: V2 §3.2 N-Vote + §3.4 Adversarial
- `src/kormarc_auto/consensus/n_vote.py`
  * Vote dataclass·aggregate_votes·is_consensus_reached
  * DEFAULT_AGREEMENT_THRESHOLD = 0.6 (결제 = 0.8 권장)
  * 임계 미달 = winning_decision=None = 사람 큐
- `src/kormarc_auto/consensus/adversarial.py`
  * AdversarialFinding (8 kind)·classify_finding
  * ADVERSARIAL_DAILY_CAP = 50 (V2 §3.4 비용 캡)
- 22 tests passing

### Cycle 34: V2 §3.3 Hierarchical
- `src/kormarc_auto/consensus/hierarchical.py`
  * HierarchicalPlan (supervisor=Opus·worker=Sonnet·reviewer=Sonnet)
  * WorkUnit (unit_id·description·status·assigned_to)
  * decompose_into_units(file_count) = 파일 수 기반 분해
  * assign_to_workers = round-robin 할당
  * 200 컴포넌트 = 413K 토큰 추정 (KORMARC 9 자료유형 시나리오)
- 14 tests passing

### Cycle 35: ADR 0039 본 문서 + META_REVIEW 갱신 권장

## Consequences

### Positive
- V2 §3 다중 에이전트 4 패턴 = 100% 적용 (Proposer-Critic·N-Vote·Hierarchical·Adversarial)
- 결제·삭제·DB 등 unsafe 작업 = 자동 사람 큐 (N-Vote 임계 미달)
- 큰 마이그레이션 (200 컴포넌트) = 자동 분해·병렬 실행 가능
- README.en + INDEX = 글로벌 + 한국 도서관 community 동시 진입

### Negative
- consensus 모듈 = scaffolding only (LLM 호출은 Anthropic 키 발급 후 외부)
- TaskList archive = 130+ 누적 정리·향후 task ID 132+ 시작 (재발 방지 = 매 META_REVIEW 갱신)
- Hierarchical = supervisor (Opus) 비용 = 200 컴포넌트 시나리오 비용 cap 검토 필요

### Risk Mitigation
- N-Vote 사람 큐 = 자동 fallback·결제 사고 차단 (V2 §3.2)
- Adversarial 일일 50회 캡 = 비용 폭주 차단 (V2 §3.4)
- Hierarchical 토큰 추정 = decompose_into_units에서 사전 계산·budget tracker 통합 가능

## V2 §3 다중 에이전트 4 패턴 매트릭스 (Cycle 35 마무리)

| § | 패턴 | 모듈 | 적용 시점 |
|---|---|---|---|
| §3.1 | Proposer-Critic | automation/proposer_critic.py (Cycle 21 차용) | 즉시 가능 |
| §3.2 | N-Vote Consensus | src/kormarc_auto/consensus/n_vote.py | 결제·삭제 unsafe 작업 |
| §3.3 | Hierarchical | src/kormarc_auto/consensus/hierarchical.py | 큰 마이그레이션 (50+ 파일) |
| §3.4 | Adversarial Pair | src/kormarc_auto/consensus/adversarial.py | 보안 강화 (paid pilot 후) |

## Plan B P29~P52 + V2 적용 = 24/24 (V2 §3 마무리로 완전)

- ✅ 22/24 Plan B P29~P52
- ⏳ P30 PortOne (PO 사업자 등록 후)
- ⏳ P39 사서어 매핑 (KLA 5/31 인터뷰 후)
- ✅ V2 §1·§3·§5·§6·§7·§10·§11 = 100% scaffolding

## 다음 7-cycle 권장 (Cycle 36~42)

외부 의존 해소 전 자율 가능:
- Cycle 36 = `make blocker` 동적 갱신 (사업자 등록 감지)
- Cycle 37 = Streamlit 매출 대시보드 (funnel + budget + blockers 통합)
- Cycle 38 = N-Vote scaffolding + 환불 시나리오 통합 (P30 결합)
- Cycle 39 = Hierarchical + KORMARC 9 자료유형 builder 통합 시뮬
- Cycle 40 = Adversarial Red 시나리오 박제 (PII·자관·KORMARC injection)
- Cycle 41~42 = META_REVIEW Cycle 28~42 + ADR 0040 통합

외부 의존 해소 시:
- Cycle 36+ = P30 PortOne v2 라이브 통합 (사업자 등록 후)
- Cycle 37+ = SALES-1 인터뷰 데이터 → P39 사서어 매핑

## 영구 invariants 7건 + V2 §3 정합 (변경 = ADR 필수)

1. 헌법 위반 0건
2. 자관 데이터 git 누설 0건
3. 결정론 (ADR 0028)
4. AI 출처 표시 (ADR 0029)
5. 카테고리형 신뢰 (ADR 0030)
6. KWCAG 2.2 (ADR 0032)
7. KOLAS3 종료일 = 2026-12-31 (1초 변경 = STOP)

## Alternatives Considered

### Alt 1: Cycle 32~35 = N-Vote만 (Adversarial·Hierarchical 제외)
- Reject: V2 §3 다중 에이전트 4 패턴 = 일괄 적용·재발명 X·Cycle 36+ 효율

### Alt 2: 외부 cron + LLM 호출 즉시 통합
- Reject: ANTHROPIC_API_KEY 미발급·비용 캡 부재·scaffolding 우선

### Alt 3: TaskList archive 미정리
- Reject: 130+ 누적 = task 검색 어려움·운영 청결 악화 (V2 §11 정합)

## References

- 외부 자동화 V2 §3 (Multi-Agent 4 패턴) + §11 안전 체크리스트
- Anthropic 내부 사례: 200 컴포넌트 React 마이그레이션 며칠 → 몇 시간
- ADR 0024~0038 누적
- META_REVIEW.md Cycle 22~28 (Cycle 28)
- 메모리: feedback_one_shot_completion_2026_05_06.md

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 35 7-cycle 통합
