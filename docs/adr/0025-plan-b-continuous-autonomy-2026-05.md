# ADR 0025 — Plan B 무중단 자율 진행 채택 (ADR 0024 supersede)

- 상태: Accepted (PO 명시 결정·2026-05-03)
- 일자: 2026-05-03
- Supersedes: ADR 0024 (가드레일 정책)
- PO 명령: "B안 — 가드레일 없는 무중단 자율 진행 명령문" 주입 + Cycle 1 실행

## Context

ADR 0024 (외부 901 출처 보고서 진단)는 4중 패턴 (identity fusion + productive avoidance + agent pace inflation + domain expert curse) 진단 후 6 가드레일 채택. PO는 보고서 진단을 인정하면서도 본인 결정으로 B안 (무중단) 선택.

PO 명령문 핵심:
- 무중단 자율 = Mon~Thu 제약 X·24h hold X·Sunday off X·module budget X
- 사이클 1 = per-block disaggregation publish (강제)
- 사이클 2 = offline demo finish (강제)
- 사이클 3~28 = P2~P28 큐 순차 (~6.5개월)
- 자동 머지 게이트: ruff·pytest·binary_assertions·자관 회귀 ≤ 1pp
- 영구 STOP 조건 7건만 자율 정지

## Decision

ADR 0024 가드레일 6건 중 4건 폐기, 2 invariant 영구 보존:

### 폐기 (Plan B 채택으로)
- ❌ Mon-Thu only → 매일 자율 OK
- ❌ 24h hold → 게이트 통과 시 자동 머지 OK
- ❌ 5 module/cycle cap → 무제한
- ❌ 신규 모듈 X → P3~P28에서 신규 모듈 생성 OK

### 영구 보존 (B안 §4 invariants)
- ✅ **헌법 위반 0건**: "100% 자동" 카피·raw 확률 노출·본문 LLM 송신·사서 검토 우회 = PR 자체 머지 차단
- ✅ **자관 데이터 git 누설 0건**: D:\ 데이터 commit 시도 = 자율 정지·PO 통보·PIPA 사고 사전 차단

### Cycle 강제 산출물 (B안 §1·§2)
- Cycle 1: per-block disaggregation publish (README + landing + Streamlit + FastAPI + CLI)
- Cycle 2: offline demo (T2-1) finish + v0.6.0 tag
- Cycle 3+: T2-2 → ... → T6-6 v1.0.0 release gate

### Cycle 운영 (B안 §0)
- 사이클 단위: 7일 (월~일)
- 자동 머지 차단 게이트 6건 (ruff·pytest·binary_assertions 38/38·자관 174 회귀 ≤ 1pp·demo 30초·헌법 0건)
- PR = 1 우선순위 항목 1 단계
- 사이클 종료 SUMMARY.md → 다음 사이클 자동 전환

### STOP 조건 (B안 §5)
1. 회귀 게이트 5 사이클 연속 위반
2. 자관 데이터 git 누설 시도
3. 본문 LLM 송신 시도
4. API 키 commit 시도
5. 우선순위 큐 모든 항목 SKIPPED
6. PO "STOP" / "PAUSE" 입력
7. 동일 P 항목 3 사이클 연속 SKIPPED

## Consequences

### Positive
- v0.6.0 = Cycle 1+2 강제 산출물 = 보고서 권고 흡수 (publish + demo)
- 영구 invariant 2건이 헌법·PIPA 사고 차단 = 가장 큰 리스크 0
- ~6.5개월 자율 진행 = PO 추가 명령 부담 0

### Risk (PO 인지 후 결정)
- 보고서 4중 패턴 (burnout·avoidance·pace inflation·expert curse) = 무중단 모드에서 재발 가능
- 자관 N=1 검증 → eval-corpus v1 (P23·사이클 24+) 도달 시까지 약 23 사이클
- PO 본인 신체·정신건강 = TODO에 등록되지만 자동 강제 X (PO만 가능)

### Mitigation (자율 영역)
- B안 invariants 2건 = 비협상
- 사이클 종료 SUMMARY.md = PO 후속 점검 자료
- META_REVIEW.md (7 사이클마다) = 자동 회고
- 본문 송신 차단 (P19) + 결정론 (P12) + provenance (P13) = 헌법 강화

### PO 본인 영역 (CLAUDE 자율 X·TODO 유지)
- 17:30 shutdown
- 일요일 laptop off
- 청년 마음건강 신청
- 5명 사서 cold outreach
- 1577-0199·1393 phone 저장

## Alternatives Considered

### Alt 1: A안 (가드레일 유지)
- ADR 0024 유지·Mon-Thu·module cap·24h hold
- Reject: PO 명시 거부·B안 채택

### Alt 2: 하이브리드 (일부 가드레일)
- Reject: PO 명령문이 "가드레일 없는" 명시·B안 통째 적용

### Alt 3: 재논의 요청
- Reject: PO 명령 = 무중단 자율 = 즉시 실행

## Implementation

1. CLAUDE.md §8B 갱신: 가드레일 6건 → invariants 2건만
2. AUTONOMOUS_BACKLOG.md = P1~P28 큐 박제
3. Cycle 1 즉시 실행 (B안 §1)
4. 사이클 완료 시 SUMMARY.md 자동 생성

## References

- B안 명령문 (PO 주입·2026-05-03)
- ADR 0024 (supersede 대상)
- 외부 901 출처 보고서 (PO 인지 후 결정)
- Memory: project_solo_founder_diagnosis_2026_05_03.md (보고서 진단 보존)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-03 · PO B안 명시 채택
