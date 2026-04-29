# ADR-0018: 8 Agent 동시 병렬 launch 패턴

## Status
Accepted (2026-04-30)

## Context

PO 4-30 명령 "부족한 부분 자율 조사 + 더 깊고 넓게" → 동시 4개 Agent (Part 7·8·9·10) → 추가 4개 Agent (Part 11·12·13·14). 총 8개.

순차 실행 시 약 8 × 5~15분 = 40~120분. 동시 실행 시 약 5~15분 (max).

## Decision

**8 Agent 동시 병렬 launch (background)** 채택.

각 Agent:
- general-purpose subagent (외부 웹 조사·WebFetch·WebSearch)
- 독립 컨텍스트 (200K window)
- 결과 파일 docs/research/part{N}-...md 작성
- 200자 요약 보고

## Consequences

### 쉬워지는 것

- 시간 1/8 (40~120분 → 5~15분)
- 메인 컨텍스트 보존 (각 Agent 자체 200K)
- 4건 정상 완료 시 즉시 매뉴얼 4개 (Part 7·8·9·10·22K+9K+14K+0.5K=46K자)

### 어려워지는 것

- ★ Token 한도 도달 (KST 07:40 회복 알림) — 4건 fail
- 회피: ADR-0017 (메인 직접 작성 대체 패턴)
- 동시 launch 시 같은 외부 API rate limit 충돌 가능
- 회피: WebFetch·WebSearch 분산 (각 Agent 다른 도메인)

### 트레이드오프

- 시간 (병렬·1/8) ↔ Token 한도 (8 × 100K = 800K 동시)
- 우리 선택: 병렬 (5월 PILOT·KLA 마감 임박)
- Token 한도 도달 시 ADR-0017 직접 대체 패턴

### 후속

- 향후 Agent 동시 launch 시 4건 이하 권장 (token 한도 회피)
- KST 07:40 회복 후 재실행 또는 직접 대체 미리 결정
- cloud routine (1h fire) = 매시간 1건씩 처리 = token 분산

## Sources

- 4-30 8 Agent launch 시리즈 (Part 7~14)
- ADR-0017 (token 한도 회피·메인 직접 대체)
- claude.ai/code/routines (1h cloud routine)
- Part 6 §10 (컨텍스트 관리)
