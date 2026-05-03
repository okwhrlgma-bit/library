# ADR-0014: 5중 자동화 (Cloud routine 3 + GitHub Actions 2)

## Status
Accepted (2026-04-30)

## Context

PO 1인 운영. 매출 직결 작업 (영업 자료·코드 품질·자관 PILOT 진행) 24/7 진행 필요. 사용자 외출·잠 사이에도 자동 commit 누적 = 캐시카우 도달 시점 앞당김.

옵션:
1. (A) 로컬 cron — 사용자 PC 켜져 있어야 동작 ❌
2. (B) GitHub Actions만 — 6h 한도·anthropics/claude-code-action API 키 별도 ❌
3. (C) Cloud routine만 — Anthropic 인프라·OAuth·하지만 빠진 영역 (push 시 자동 검증) ⚠️
4. (D) **Cloud routine + GitHub Actions 결합** ★

Anthropic Cloud routine (2026-04-14 출시) 한도:
- Pro: 일 5건·Max 15건·Team/Enterprise 25건 (구독 한도와 별개)
- 5시간 윈도우·주간 한도 (Pro 40~80h Sonnet)

GitHub Actions 한도:
- 무료 월 2,000분 (linux runner·private OK)

## Decision

**5중 자동화 구조**를 채택 (D).

| Layer | 도구 | 빈도 | 첫 fire | 용도 |
|---|---|---|---|---|
| 1 | Cloud routine 1h sync | 매시간 | 4-30 03:00 KST | 매출 직결 commit (AUTONOMOUS_BACKLOG 위→아래) |
| 2 | Cloud routine 주간 (월 09 KST) | 주 1회 | 5-4 09:00 | 영업 funnel·PILOT 분석·주간 계획 |
| 3 | Cloud routine 월간 (1일 09 KST) | 월 1회 | 5-1 09:00 | 매출 환산·계절 정합·월간 보고서 |
| 4 | GitHub Actions ci.yml | 매 push | 즉시 | pytest·ruff·M/A/O 검증 |
| 5 | GitHub Actions autonomous-6h.yml | 6시간 | API 키 등록 후 | 백업 자동 (claude-code-action) |

Routine 등록 시점:
- `trig_01THW9GZG6G4sorCtwgJaR77` (1h)
- `trig_01Yb5Ze4eAwn4Z6srKDDu2Ma` (주간)
- `trig_01JGajzBSdRhMnS8KQPz5H8q` (월간)

GitHub repo: PRIVATE (https://github.com/kormarc-auto/library) — Cloud routine OAuth 인증으로 작동.

## Consequences

### 쉬워지는 것

- 사용자 외출·잠 사이 24/7 자동 commit
- 1년 5,000+ commit 자동 누적 예상
- Cloud routine 장애 시 GitHub Actions 백업
- 매 push 회귀 즉시 검출

### 어려워지는 것

- Routine 일일 한도 (Pro 5건) → 1h routine 24/일 fire 시 일부 누락
- 모니터링: PO 매주 1회 5분 점검 (`docs/cloud-routine-monitoring-guide.md`)
- 평가축 음수 commit 회피 위해 BACKLOG·평가축 명문화 필수

### 트레이드오프

- 복잡도 (5 layer 관리) ↔ PO 시간 0
- 우리 선택: PO 시간 0 (1인 운영·캐시카우 가속)

### 후속

- Pro → Max 5x 업그레이드 검토 (주간 한도 ↑)
- Routine 일 한도 도달 시 GitHub Actions 6h가 백업
- ADR 0010 (night-autonomous-setup) 후속·확장

## Sources

- `docs/research/part6-claude-code-comprehensive-guide-2026.md` §1·§2
- `docs/cloud-routine-monitoring-guide.md` (PO 매주 점검)
- `AUTONOMOUS_BACKLOG.md` (cloud routine 자율 큐)
- claude.ai/code/routines (관리 UI)
