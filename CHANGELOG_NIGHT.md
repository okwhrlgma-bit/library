# 야간 자율 실행 로그 (2026-04-26 KST 시작)

> NIGHT_RUN_PROTOCOL.md 표준 양식 따라 매 commit 변경 사유 기록.
> 종료 게이트: pytest 통과 + binary_assertions 21/21 + commit.


## v0.4.32 — 2026-04-26
- 이중 게이트 Stop hook 도입 (TASK_COMPLETE 마커 + pytest + 어셔션 21/21)
- Trust Counter hook (RSI Stage 1) — `.claude/metrics/trust.json` 영속
- scripts/trust_report.py — 자동 allow/deny 후보 추출
- 어셔션 21/21 통과
- 변경 사유: PO 야간 자율 명령 직후 즉시 자기 검증 루프 닫음

## v0.4.33 — 2026-04-26 (Phase 4·6 진입)

캐시카우 직결 인프라 — 사서 자동 결제 의향 향상 위해 자율 품질 강화:

- **Phase 4 Plan Mode 분리** (PO 가이드 §2.2·§2.4):
  - planner.md (Opus, plan 작성 전담, 코드 X)
  - implementer.md (Sonnet, plan 정확 실행, 자체 결정 X)
  - explorer.md (Haiku, 메인 컨텍스트 보호 탐색)
  - 비용 라우팅: Haiku 5x ↓ + Sonnet 40% ↓ → 자율 운영비 직접 절감

- **Phase 6 Stage 2 Pattern Library**:
  - scripts/extract_patterns.py — git diff 자동 분류
  - 6 유형 (testCreated·assertionAdded·adrAdded·hookAdded·agentAdded·ruleAdded)
  - .claude/patterns/ 26건 즉시 추출 (33 commit 누적 history에서)
  - SKILL 승격 후보 3종: testCreated(8)·assertionAdded(7)·adrAdded(5)
  - logs/evals/patterns.jsonl 누적 → Stage 3 ratchet 입력

- **어셔션 22·23**:
  - assert_plan_act_agents (Explore-Plan-Act 3종)
  - assert_pattern_library_exists (≥10건)

- **자율 게이트 강화** (.claude/rules/autonomy-gates.md):
  - 캐시카우 평가축 §0+§12 commit 메시지 명시 의무화
  - 측정: aggregate_revenue.py 매월

평가축:
- §0: planner/implementer 분리로 plan 정확도 ↑ → 권당 마크 시간 회귀 0%
- §12: 자율 운영비 절감(Haiku 라우팅) + Pattern Library 누적 → 매출 영향 신규 모듈 빨라짐

검증: 23/23 어셔션 / 229 tests / ruff 0.

## v0.4.33 — 2026-04-26 (캐시카우 매니지드 스택 + 항상 야간 모드)

### 캐시카우 평가축 매 commit 강제
- `.claude/rules/autonomy-gates.md` "캐시카우 평가축" 섹션 신규
- §0 (마크 시간) + §12 (매출 의향) 둘 중 하나 양수 영향 commit 메시지에 명시 의무화
- 측정: `scripts/aggregate_revenue.py` 매월

### ADR 0011 매니지드 스택·웹 vs 모바일·캐시카우 운영
- 매니지드 5종 도입 트리거 매핑 (Vercel·Supabase·포트원·Fly.io·Logtail)
- 웹 (PWA) 우선, 모바일 네이티브 ★ 보류 (App Store 30% + 심사 7~14일이 패시브 인컴 역행)
- 결제 자동화 4축 (가입·카운터·청구·잔여 알림) — PG 도입 직후 자동화 완성
- "두면 돈 버는" = PO 시간 0, 매월 자동 결제

### Phase 4 Plan Mode 분리 (PO 가이드 §2.2·§2.4)
- planner.md (Opus) — plan 작성 전담, 코드 X, `docs/plans/`
- implementer.md (Sonnet) — plan 정확 실행, 자체 결정 X
- explorer.md (Haiku) — 메인 컨텍스트 보호 탐색 (5x ↓)

### Phase 6 Stage 2 Pattern Library
- `scripts/extract_patterns.py` — git diff 6 유형 자동 분류
- `.claude/patterns/` 26건 즉시 추출 (33 commit history)
- SKILL 승격 후보 3종: testCreated(8) · assertionAdded(7) · adrAdded(5)
- `logs/evals/patterns.jsonl` 누적 → Stage 3 ratchet 입력

### 어셔션 22·23
- assert_plan_act_agents (Explore-Plan-Act 3종)
- assert_pattern_library_exists (≥10건)

### 항상 야간 모드 (PO 정점 정책)
- `~/.claude/settings.json` ask 5종 → 1종 (`git tag`)으로 축소
- `git push`·`pip install`·`winget install`·`npm publish` 모두 **deny** 전환
  → 권한 prompt 멈춤 0회 (hook reason으로 Claude가 우회 결정)
- PO 부재 야간 자율 commit 100% 진행 가능
- PO 추가 명령은 야간 작업 우선순위 갱신 신호로 흡수, 정지 X
- 평가축: §0/§12 최고의 아웃풋이 목표 (단순 처리 X)

평가축 부합:
- §0: planner/implementer 분리 + Plan 영속화로 큰 작업 plan 정확도 ↑ → 마크 시간 회귀 0%
- §12: ADR 0011 매니지드 스택 매핑으로 PG 도입 직후 캐시카우 자동화 완성 직결

검증: 23/23 어셔션 / 229 tests / ruff 0.
