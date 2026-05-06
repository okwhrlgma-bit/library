# ADR 0040 — Cycle 36~42 통합 결정 (운영 통합 + V2 §3 시나리오)

- 상태: Accepted (2026-05-06·Cycle 41 7-cycle 통합)
- 일자: 2026-05-06
- 트리거: PO "진행"·1-명령 끝까지·Cycle 35 ADR 0039에서 다음 7-cycle 권장 정합

## Context

Cycle 29~35 = V2 §3 다중 에이전트 4 패턴 100% scaffolding 마무리.
Cycle 36~42 = 운영 통합 + V2 §3 시나리오 박제 (paid pilot 후 즉시 활성).

## Decision

### Cycle 36: 차단점 동적 감지 강화
- `scripts/next_blocker.py`
  * `_interview_count()` 헬퍼 신설 = 사서 인터뷰 진척 0~5 단계 자동 감지
  * SALES-1 = interviews_done < 2 → high·≥ 2 → medium 동적 severity
  * 잔여 일수 = interviews 0건 14일·1+건 7일 (학습 효과 반영)

### Cycle 37: Streamlit 매출 대시보드
- `src/kormarc_auto/ui/revenue_dashboard.py`
  * 3 col 통합 (차단점 + 예산 + Funnel)
  * `render_dashboard()` Streamlit 진입점
  * `get_dashboard_summary()` API/CLI 호출용 dict (외부 사용)
  * 실행: `streamlit run src/kormarc_auto/ui/revenue_dashboard.py`
  * silent fallback (모듈 미로드 시 caption만)

### Cycle 38: N-Vote 환불 시나리오 (V2 §3.2 + P30)
- `tests/test_v2_scenarios.py::TestRefundNVoteScenario` (4 tests)
  * 만장 50,000 환불 = 자동 처리
  * 의견 분할 = 사람 큐 (PO 직접)
  * 100만원 초과 = threshold 0.9 보수적 (사람 큐)
  * 한국어 결정 라벨 (cancel_full·refund_50000 등)

### Cycle 39: Hierarchical KORMARC 9 자료유형 (V2 §3.3)
- `tests/test_v2_scenarios.py::TestHierarchicalKormarcMigration` (3 tests)
  * 9 자료유형 = 49K 토큰 추정·3 worker 병렬
  * 174 파일 round-trip 회귀 = 448K 토큰 추정 (Opus supervisor 정당화)

### Cycle 40: Adversarial Red 시나리오 (V2 §3.4)
- `tests/test_v2_scenarios.py::TestAdversarialRedScenarios` (6 tests)
  * 일일 50회 캡 (V2 §3.4)
  * PII leak·MARC injection·인증 우회·자관 누설·8 finding_kind 분류

### Cycle 41: ADR 0040 본 문서

### Cycle 42: 마무리 (자율 재개 권장)

## Consequences

### Positive
- 차단점 동적 = PO 인터뷰 1건 진행 시 즉시 severity 하향
- 매출 대시보드 = 1 페이지 통합 5분 cadence (operations.md 정합)
- V2 §3 시나리오 13 tests = paid pilot·KOLAS3 마이그레이션·보안 강화 시 즉시 활성
- ADR 0024~0040 누적 = 17 ADR (Plan B + V2 + 외부 보고서 5건)

### Negative
- revenue_dashboard.py = Streamlit 의존 (헌법 §0 정합·기존 ui/와 동일)
- V2 §3 시나리오 = scaffolding tests (LLM 호출은 외부 cron + ANTHROPIC_API_KEY 발급 후)
- 차단점 동적 감지 = `.business-registered` 파일 생성 책임 = PO 외부 작업

### Risk Mitigation
- `revenue_dashboard.py` silent fallback = 모듈 미로드 시 caption만 (전체 실패 X)
- V2 §3 시나리오 tests = 결정론·모델 호출 X·환경 무관 회귀 보장
- 차단점 동적 = ENV 보유 여부 + 디렉토리 존재 + 날짜 다중 신호 통합

## V2 §3 다중 에이전트 + Plan B + 외부 보고서 매트릭스

| 영역 | 진행 |
|---|---|
| Plan B P29~P52 | 22/24 (P30 사업자 후·P39 인터뷰 후) |
| V2 §1 메타 라우터 | ✅ Cycle 21 차용 |
| V2 §3.1 Proposer-Critic | ✅ Cycle 21 차용 |
| V2 §3.2 N-Vote | ✅ Cycle 32 + 시나리오 4 tests |
| V2 §3.3 Hierarchical | ✅ Cycle 34 + 시나리오 3 tests |
| V2 §3.4 Adversarial | ✅ Cycle 33 + 시나리오 6 tests |
| V2 §4 3-Tier Memory | ✅ Cycle 20B (Replay) + Cycle 21 (learnings hook) |
| V2 §5 Goal Decomposer | ✅ Cycle 22 |
| V2 §6.1 자기 수정 | ✅ Cycle 21 (refine-claudemd) |
| V2 §6.4 Progressive Trust | ✅ Cycle 22 |
| V2 §7 Multi-SaaS | ✅ Cycle 21 supervisor 차용 |
| V2 §8 옵저버빌리티 | ✅ Cycle 19A budget regression |
| V2 §9 Defense in Depth | ✅ Cycle 18A·21 hooks |
| V2 §10 마스터 코드 | ✅ Cycle 21 차용 |
| V2 §11 안전 체크리스트 | ✅ Cycle 27 operations.md |
| 외부 901 출처 (PO 정신건강) | ✅ memory + Cycle 24 외부 매트릭스 |
| 외부 858 출처 (한국 SaaS) | ✅ memory + ADR 0026 + P29~P40 |
| 외부 매출 보고서 | ✅ memory + P29~P52 |
| 1-명령 1-완료 정책 | ✅ memory ⭐⭐⭐⭐⭐ + CLAUDE.md §자율 작업 가이드 |

## Plan B + V2 100% 적용·외부 의존 2건만 잔존

- ⏳ P30 PortOne 라이브 (PO 사업자 등록·D+14)
- ⏳ P39 사서어 매핑 데이터 (SALES-1 인터뷰 5명·14일)

## 다음 7-cycle 권장 (Cycle 43~49)

외부 의존 해소 전:
- Cycle 43 = README.md (한국어) Cycle 28~42 누적 반영
- Cycle 44 = pyproject.toml v0.7.1 (1083+ tests·V2 §3 100%)
- Cycle 45 = `make blocker` 출력 → PROGRESS.md 자동 append
- Cycle 46 = consensus 모듈 통합 docstring 갱신
- Cycle 47 = test-hooks workflow에 consensus tests 포함
- Cycle 48 = META_REVIEW Cycle 28~49 갱신
- Cycle 49 = ADR 0041

외부 의존 해소 시:
- Cycle 43+ = P30 PortOne v2 라이브 통합
- Cycle 44+ = SALES-1 인터뷰 → P39 사서어 매핑

## Alternatives Considered

### Alt 1: Cycle 36 차단점 단일 정적 유지
- Reject: 인터뷰 진척 = 동적 severity = PO 의사결정 시간 ↓

### Alt 2: revenue_dashboard = FastAPI endpoint만
- Reject: Streamlit = 사서 친화 UI·기존 ui/ 일관성

### Alt 3: V2 §3 시나리오 = scaffolding 없이 LLM 호출
- Reject: ANTHROPIC_API_KEY 미발급·비용 캡 부재·PO 외부 작업 후

## References

- 외부 V2 §3 (Multi-Agent 4 패턴) + §11 안전 체크리스트
- ADR 0024~0039 누적
- META_REVIEW.md (Cycle 28 작성·Cycle 42+ 갱신 권장)
- 메모리: feedback_one_shot_completion_2026_05_06.md (PO 정책)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 41 통합
