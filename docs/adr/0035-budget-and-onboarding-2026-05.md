# ADR 0035 — Budget Tracker (P49) + 5분 온보딩 위저드 (P32)

- 상태: Accepted (2026-05-06·Cycle 19A + 19B 통합)
- 일자: 2026-05-06
- 트리거: V2 §10.3 (budget-guard.sh) + 외부 매출 보고서 P32

## Context

### A. 비용 폭주 = 1인 SaaS 침묵의 살인자 (V2 §11)
- V2 8 원칙 #7 = 비용 = 침묵의 살인자
- 일일 토큰 폭주 감지 부재 = 며칠 후 알림 받음
- 모델/코드/CLAUDE.md 변경 시 회귀 진단 필수

### B. Activation 정의 부재 = 전환율 측정 불가 (P32)
- Lenny Rachitsky 2024 = activation 정의 시 2.5x 전환
- 5분 위저드 미완 = 첫 단계 통과 X = funnel 단절
- 14일 trial 전환 트리거 부재 = 자동 freemium 회수 어려움

## Decision

### 1. `src/kormarc_auto/budget/` (P49·V2 §10.3)
- `tracker.py`
  * UsageRecord (timestamp·task_kind·model·input/output 토큰·cost_usd·duration)
  * append_record JSONL append (~/.kormarc-auto/budget/{YYYY-MM}/usage.jsonl)
  * BudgetTracker(daily_usd_budget=$20)
    - state() = normal / warning(70%) / near_limit(90%) / exceeded(100%)
    - should_block_session() = SessionStart hook
    - usage_today()·usage_last_7_days()·remaining_budget_usd()
  * ENV override (KORMARC_DAILY_USD_BUDGET·KORMARC_BUDGET_DIR)
- `regression.py`
  * detect_token_regression(baseline·recent) → severity (normal/watch/alert/critical)
  * pct_change ≤ 10% normal·≤ 30% watch·≤ 80% alert·> 80% critical
  * V2 §8.3 4 후보 원인 자동 (모델·코드·CLAUDE.md·루프)
- 18 tests passing

### 2. `src/kormarc_auto/onboarding/` (P32·외부 매출 보고서)
- `wizard.py`
  * WIZARD_STEPS 6 (library_code·classification·hanja_880·output_format·first_isbn·complete)
  * OnboardingState dataclass
  * advance_step() = 단계별 검증 (자관코드·KDC6/DDC/custom·DLS/KOLAS/ALPAS·ISBN-13)
  * progress_percentage(state)
- `activation.py`
  * ACTIVATION_THRESHOLD_RECORDS = 100 + reports = 1
  * check_activation() → ActivationStatus (4 churn levels: safe·watch·at_risk·lost)
  * is_at_risk_of_churn()
  * trial_end_trigger() = D-7/D-3/D-0 (Founding Member 50% 강조)
- 22 tests passing

### 3. STOP 조건 (V2 §11)
- 일일 USD 90% 도달 = SessionStart hook 자동 차단
- 토큰 회귀 critical (+80%) = 사람 검토 + 자율 사이클 일시 중단
- 14일 trial 종료 ≠ 30일로 변경 시 STOP (외부 보고서 P32: 30일 = 3.6% vs 14일 = 7.1%)

### 4. AUTONOMOUS_BACKLOG.md 갱신
- P49 ✅ (Cycle 19A)
- P32 ✅ (Cycle 19B·온보딩+activation)
- 다음 사이클 권장 = P30 PortOne sandbox (사업자 등록 후) 또는 P46 메타 라우터 (V2)

## Consequences

### Positive
- 비용 폭주 자동 차단 (90% 도달 = 세션 차단)
- activation 정의 박제 = funnel 측정 정확
- 14일 trial 자동 freemium 전환 = 옵트인 8-15% 목표 달성 가능
- 회귀 진단 = 모델 자동 업데이트 영향 추적 가능

### Negative
- $20 default = 너무 낮을 수 있음 (운영 중 ENV override)
- activation = 100건 임계 = 첫 trial에서 도달 어려움 (작은도서관 평균 30-40권/월)
  → 14일 trial = 100건 도달 불가능·Cycle 20+에서 임계 재조정 검토
- 회귀 진단 = baseline 데이터 부족 시 false positive

### Risk Mitigation
- BudgetTracker.should_block_session = SessionStart hook 검증 (V2 §10.3)
- 회귀 진단 = empty data 시 normal 반환 (false positive 차단)
- activation 임계 = ENV override 가능 (운영 중 조정·ADR 필수)
- onboarding wizard = 멱등 (재호출 안전·complete 단계 stable)

## Alternatives Considered

### Alt 1: 일일 USD 예산 = $50 (외부 보고서 권장 LLM 모니터)
- Reject: $20이 1인 SaaS 합리적 (P40 LLM 모니터링 별도 캡)·운영 중 ENV override

### Alt 2: activation = ISBN 50건 (낮춤)
- Reject: Lenny 2.5x 효과 = 의미 있는 임계·100건 = 1주 사용자 적정

### Alt 3: 7단계 위저드 (더 세밀)
- Reject: 5분 한도·5단계 = ProfitWell 7.1% 전환 정합

### Alt 4: SQLite (JSONL 대신)
- Reject: append-only JSONL = audit_log·analytics와 정합·복잡도 X

## References

- V2 자동화 가이드 §8.3·§10.3·§11 비용 체크리스트
- 외부 매출 보고서 (2026-05-05) P32·P49
- ADR 0029 audit log JSONL (정합)
- ADR 0031 funnel analytics (정합·analytics와 budget 분리)
- ADR 0034 hooks + GEO (SessionStart hook 개념 정합)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 19A+B 병행
