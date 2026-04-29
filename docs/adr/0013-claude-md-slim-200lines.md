# ADR-0013: CLAUDE.md slim 200줄 이하 유지

## Status
Accepted (2026-04-30)

## Context

CLAUDE.md는 Claude Code 매 세션 자동 로드되는 헌법 파일. 우리 프로젝트는 v0.4.37 시점 323줄이었음.

Anthropic 공식 베스트 프랙티스 + HumanLayer 분석 (Part 6 종합 가이드 §3) 핵심:

> "각 줄마다 '이걸 지우면 Claude가 실수할까?' 자문하라.
> 200줄 초과 시 Claude가 instruction 균등 무시 시작.
> 시스템 프롬프트엔 이미 ~50개 instruction 존재."

문제:
- 323줄 = instruction 무시 위험 (200줄 권장 60% 초과)
- §11 변경 이력 17줄 = CHANGELOG_NIGHT.md 중복
- §12 수익 모델 50줄 = docs/sales/INDEX.md·pricing.md 중복
- §13 모바일 운영 18줄 = docs/mobile-tunnel.md 중복
- §9 슬래시·§10 모듈 인덱스·§8 참조 문서 = docs/index.md 중복

기존 헌법 정합성 (KORMARC 도메인·평가축 §0/§12·자율성 4단·종료 규약·5대 멈춤 패턴)은 유지 필수.

대안:
1. (A) 그대로 유지 — 단순성 ↑·instruction 무시 위험 ↑ ❌
2. (B) 본 결정: 단계적 slim (5 step·중복 제거·docs/ 포인터만 유지)
3. (C) 처음부터 재작성 — 큰 위험·기존 §0~§7 헌법 손실 가능 ❌

## Decision

**CLAUDE.md를 단계적으로 200줄 이하로 slim**한다 (B).

각 §별 docs/ 위치:

| § | 이전 | 이후 |
|---|---|---|
| §11 변경 이력 | 17줄 | "CHANGELOG_NIGHT.md 참조" 1줄 |
| §13 모바일 운영 | 18줄 | "docs/mobile-tunnel.md 참조" 1줄 |
| §12 수익 모델 | 50줄 | 평가 기준 핵심 + "docs/sales/INDEX.md 참조" 5줄 |
| §9·§10 슬래시·모듈 인덱스 | 35줄 | "docs/index.md 참조" 1줄 |
| §8 참조 문서 | 8줄 | "docs/index.md 참조" 1줄 |

Step 1~5 commit 시리즈 (4-30):
- Step 1 (9d08904): §11 archive (323→307줄)
- Step 2 (a0fe201): §13 (308→290줄)
- Step 3 (ebcd5f6): §12 (290→245줄)
- Step 4 (35f88ef): §9·§10 (245→205줄)
- Step 5 (05c5549): §8 (213→206줄)

최종: **206줄** (목표 200줄 ≤ 6줄 차이·사실상 달성).

## Consequences

### 쉬워지는 것

- Claude가 매 세션 핵심 헌법만 읽음 (instruction 무시 회피)
- 컨텍스트 효율 ↑ (한국어 토큰 절약·세션 길어도 헌법 정합)
- 변경 시 단일 진실 (docs/ 1곳만 수정·CLAUDE.md 영향 X)

### 어려워지는 것

- 새 사람이 CLAUDE.md만 보고 전체 파악 X (docs/ 추적 필요)
- 회피: README.md + docs/index.md가 진입점

### 트레이드오프

- 단순성 (1 파일) ↔ 컨텍스트 효율 (200줄)
- 우리 선택: 컨텍스트 효율 (Anthropic 공식·5중 자동화 정합)

### 후속

- 향후 새 §·새 모듈 추가 시 본 ADR 참조 (CLAUDE.md 유혹 회피)
- 200줄 권장은 hard limit 아님 — 320줄+ 회피만으로 충분
- Part 6 격차 4건 중 1번 완료

## Sources

- `docs/research/part6-claude-code-comprehensive-guide-2026.md` §3
- Anthropic 공식 베스트 프랙티스 (claude.com/docs)
- HumanLayer CLAUDE.md 분석
- 우리 commit 시리즈 9d08904·a0fe201·ebcd5f6·35f88ef·05c5549
