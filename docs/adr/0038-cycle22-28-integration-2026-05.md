# ADR 0038 — Cycle 22~28 통합 결정 박제 (V2 마무리·운영 핸드북)

- 상태: Accepted (2026-05-06·Cycle 28 META_REVIEW 정합)
- 일자: 2026-05-06

## Context

PO 명시 = "계속해서 진행 모두 승인 및 통합"·"무한 진행"·"진행 적용".
Cycle 22~28 = V2 자율 인프라 마무리 + 운영 핸드북 박제.
1-명령 1-완료 정책 메모리 영속화 (`feedback_one_shot_completion_2026_05_06.md`).

## Decision

### 7-Cycle 통합 산출 (Cycle 22~28)

1. V2 §1·§3·§5·§6·§7·§10 마스터 코드 100% 적용
2. claude-saas-starter v1+v2 = 차용 매트릭스 작성 후 폴더 삭제
3. 자관 회귀 자동 비교 (`scripts/regression_check.py` + GitHub Actions)
4. 매출 차단점 자동 감지 (`scripts/next_blocker.py` + `/blockers` endpoint + Streamlit 카드)
5. 외부 작업 단일 진실원 (`docs/external-dependencies-matrix-2026-05.md`)
6. Makefile 단축 명령 (gates·blocker·funnel·demo·serve·audit·cost·stop·rollback·pavr·ci)
7. 운영 핸드북 (`agent_docs/operations.md`) + `.claudeignore` (V2 §11)
8. META_REVIEW.md 7-cycle 자동 회고 (V2 §6.1 자기 수정)

### 영구 invariants 7건 박제

1. 헌법 위반 0건
2. 자관 데이터 git 누설 0건
3. 결정론 (temperature=0·top_p=1·모델 pinning·ADR 0028)
4. AI 출처 표시 (588 + audit + ghost text·ADR 0029)
5. 카테고리형 신뢰 (확실/검토/불확실·raw % UI X·ADR 0030)
6. KWCAG 2.2 Level AA (ADR 0032)
7. KOLAS3 종료일 = 2026-12-31 (1초 변경 = STOP)

### V2 §6.1 자기 수정 트리거 점검

- 반복 3회+ 패턴 2건 식별:
  * 외부 보고서 흡수 = memory + P 큐 + ADR 박제
  * starter 차용 = 매트릭스 + 즉시 폴더 삭제
- 헌법 §13·§14 후보 = `/refine-claudemd` 슬래시 호출 시 검토 권장 (PR만·자동 머지 X)

### Plan B P29~P52 22/24 완료 매트릭스

- ✅ 22 (P29·P31·P32·P33·P34·P35·P36·P37·P38·P40·P41·P42·P43·P44·P45·P46·P47·P48·P49·P50·P51·P52)
- ⏳ P30 PortOne (사업자 등록 후·외부 의존)
- 🟡 P39 사서어 매핑 (SALES-1 인터뷰 후·외부 의존)

## Consequences

### Positive
- V2 자율 인프라 = 코드·문서 측면 완비 (외부 의존 해소만 남음)
- PO 5분 cadence (`make blocker`·`make cost`·`make funnel`) 운영 가능
- 자관 baseline 자동 게이트 = 매 push 영구 invariant 보호
- 차단점 자동 감지 = PO 의사결정 시간 ↓·매출 가능 시점 명확

### Negative
- META_REVIEW = 7-cycle마다 수동 작성 권장 (자동 cron 미설정·V2 §11 자동 머지 X 정합)
- TaskList 130+ 누적 = 다음 사이클 archive 권장 (Cycle 31 후보)
- 외부 의존 해소 X = 본질적 매출 차단점 잔존 (PO PROD-1·2·3·5·6 + SALES-1 의존)

### Risk Mitigation
- Plan B §0 자동 머지 6 게이트 = `make gates` 통합 entry
- `.claudeignore` = 컨텍스트 비용 폭주 차단 (V2 §11)
- META_REVIEW = 매 7 사이클·PO 검토 권장 (자동 머지 X)
- next_blocker = 매 turn 시작 = `make blocker` 자동 우선순위

## Alternatives Considered

### Alt 1: 외부 의존 해소 전 본질적 진행 중단
- Reject: PO "무한 진행" 명시·인프라 완비 = 외부 해소 시 즉시 활성

### Alt 2: V2 §3.2 N-Vote Consensus 즉시 구현
- Reject: 비용 = 동일 작업 N회 호출·paid pilot 후 검토

### Alt 3: META_REVIEW 자동 cron 생성
- Reject: V2 §6.1 = 자동 머지 X·자기 수정은 사람 검토 필수

## V2 정합 매트릭스 (Cycle 22~28 마무리)

| V2 § | 적용 ADR | 사이클 |
|---|---|---|
| §1 메타 라우터 | 0037 | 22 |
| §2 PAVR 루프 | 0036 | 20A |
| §3.1 Proposer-Critic | (Cycle 21 차용 박제) | 21 |
| §4 3-Tier Memory | 0036 | 20B |
| §5 Goal Decomposer | 0037 | 22 |
| §6.1 자기 수정 | 본 ADR 0038·META_REVIEW | 28 |
| §6.4 Progressive Trust | 0037 | 22 |
| §7 Multi-SaaS | (Cycle 21 차용·본 프로젝트 단일) | 21 |
| §8 옵저버빌리티 | 0035 (budget regression) | 19A |
| §9 Defense in Depth | 0034 (scan-secrets·validate-bash) | 18A·21 |
| §10 마스터 코드 | 0037 (5 hooks·scripts) | 21 |
| §11 안전 체크리스트 | 본 ADR 0038·invariants 7건 | 27·28 |

## References

- 외부 자동화 V2 §6.1 자기 수정 PR
- ADR 0024~0037 누적
- META_REVIEW.md (본 사이클 산출)
- 외부 901 출처 (솔로 PO 진단·매 사이클 정합 검증)
- 메모리: `feedback_one_shot_completion_2026_05_06.md`

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 28 통합 결정
