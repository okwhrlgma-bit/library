# ADR 0034 — Hooks 강화 (P42) + LLM GEO 인용 모니터링 (P40)

- 상태: Accepted (2026-05-06·Cycle 18A + 18B 통합 + V2 흡수)
- 일자: 2026-05-06
- 트리거: 외부 매출 보고서 P40·P42 + 외부 자동화 V2 가이드 흡수

## Context

### A. Hook 강화 = 시크릿·포맷 결정론 (P42)
- 외부 V1 가이드 §3.2 패턴 #2 (PostToolUse / Edit 자동 ruff) + #3 (PreToolUse / Write 시크릿 차단)
- 외부 V2 가이드 §9 Defense in Depth = 6 레이어 중 #3 PreToolUse hook 결정론

### B. LLM GEO + AI 인용 모니터링 (P40)
- 외부 매출 보고서 §5 = 76.1% AI Overviews 인용 = 구글 Top 10 정합
- 첫 단락 40-60단어 정의문 + 200단어당 1 통계 = AI 인용 친화
- 표준 쿼리 10건 베이스라인 = 주 1회 측정·경쟁사 비교

## Decision

### 1. `.claude/hooks/scan-secrets.sh` (P42·V2 §9 정합)
- PreToolUse / Write·Edit 시크릿 정규식 차단
- sk-* (Anthropic/OpenAI) / sk_live_* (Stripe) / ANTHROPIC_API_KEY 평문 / JWT (eyJ...)
- 차단 시 permissionDecision deny + 사유 메시지

### 2. `.claude/hooks/post-format.sh` (P42)
- PostToolUse / Edit·Write 자동 ruff format + check --fix
- kormarc-auto 외부 = skip (안전)
- silent fail (편집 자체 보존·async)

### 3. `src/kormarc_auto/geo/answer_first.py` (P40)
- `measure_answer_first()` = 첫 단락 40-60단어 + 정의문 패턴 검증
- `measure_fact_density()` = 200단어당 1+ 통계 (연도·D-day·% 등 8 패턴)

### 4. `src/kormarc_auto/geo/citation_monitor.py` (P40)
- `STANDARD_QUERIES` 10개 (KORMARC·KOLAS III·DLS·880·가격 등)
- `parse_citation_response()` = LLM 응답 → 우리 SaaS·5 경쟁사 인용 추출
- 4 카테고리 인용 라벨 (🟢 우리만 / 🟡 우리+경쟁 / 🔴 경쟁만 / ⚪ 없음)
- `aggregate_results()` 베이스라인 집계
- 17 tests passing

### 5. STOP 조건 (외부 V2 §9 + 매출 보고서 P40)
- LLM 모니터링 비용 = 월 $50 초과 = 일시 중단
- 경쟁사 비방 콘텐츠 자동 생성 = STOP
- 시크릿 정규식 차단 통과 후에도 사람 검토 필수 (이중 게이트)

## Consequences

### Positive
- PreToolUse hook = sk-*·sk_live_*·JWT 평문 commit 차단
- PostToolUse 자동 ruff = 매 편집 후 포맷 일관성
- AI Overviews 인용 친화 콘텐츠 측정 자동
- 베이스라인 측정 = 4주마다 비교 리포트 가능

### Negative
- 시크릿 정규식 = false positive 가능 (placeholder도 차단·수동 우회 필요)
- citation_monitor = LLM API 호출 자체는 외부 cron (별도 구현·V2 비용 캡 정합)
- 첫 단락 패턴 = 한국어/영문 혼합 텍스트에서 정확도 낮음

### Risk Mitigation
- scan-secrets.sh = silent fail X·deny 명시 (V2 §9)
- post-format.sh = silent fail (편집 보존·async)
- citation_monitor = parse_citation_response만 in-module·LLM 호출은 외부 cron
- 비용 캡 = monitoring/scripts에 별도 구현 (Cycle 19+)

## V2 가이드 흡수 (메모리 영속화)

V2 핵심 7 패턴 (Cycle 19+ 구현 권장):
- P46 메타 라우터 (Haiku 분류 → Sonnet/Opus 자동)
- P47 PAVR 슬래시 (Plan→Act→Verify→Reflect·worktree)
- P48 learnings.md + Failure Replay
- P49 budget-guard.sh (SessionStart 일일 예산)
- P50 refine-claudemd skill (PR만·자동 머지 X)
- P51 Progressive Trust (Level 1~5·30회 성공 → 확대)
- P52 일일 자율 루프 cron (Goal Decomposer·paid pilot 후)

V2 안전 8 원칙 박제 (AUTONOMOUS_BACKLOG.md):
1. 결정론 = 모델 외부
2. unsafe = 사람 큐
3. 자기 수정 = PR만
4. 모든 실행 audit
5. 모델 = 인턴
6. Progressive Trust
7. 비용 = 침묵의 살인자
8. 비전 = 사람·일일 = 모델

## Alternatives Considered

### Alt 1: scan-secrets에 base64·hex 모든 패턴 추가
- Reject: false positive 폭발·핵심 4 패턴 (sk-*·sk_live_*·ANTHROPIC·JWT)만 강제

### Alt 2: post-format = 동기 실행
- Reject: 편집 흐름 차단 위험·async + silent fail로 대체

### Alt 3: citation_monitor = LLM API 직접 호출 in-module
- Reject: 비용 캡 어려움·외부 cron으로 분리·V2 §9 정합

## References

- 외부 매출 성장 보고서 (2026-05-05) P40·P42
- 외부 자동화 V1 가이드 §3.2 패턴 5선
- 외부 자동화 V2 가이드 §9 Defense in Depth + §11 체크리스트
- Cycle 17 P41 Stop hook (정합)
- ADR 0026~0033 (전체 정책 정합)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 18A+B + V2 흡수
