# ADR-0016: signup endpoint 페르소나 자동 분류

## Status
Accepted (2026-04-30)

## Context

신규 가입 시 사서가 4 페르소나 (macro·acquisition·general·video) 중 어디에 속하는지 자동 판단 → 영업 funnel by_persona 자동 매핑·페르소나별 결제 전환률 분석 가능.

수동 분류 대안:
- (A) 가입 폼에 "페르소나 선택" 드롭다운 — UX 부담 (사서가 페르소나 모름)
- (B) PO 수동 분류 — 200관+ 시 시간 소요
- (C) 자동 분류 — 도서관명·이메일 도메인 패턴

## Decision

도서관명·이메일 도메인 패턴 기반 자동 분류 (C).

규칙 (`src/kormarc_auto/server/signup.py:detect_persona`):

| 패턴 | 분류 | 근거 |
|---|---|---|
| 도서관명 "영상"·"방송" | video | 자관 김신학·우리 영역 X |
| 도서관명 "대학"·"university" or 이메일 ".ac.kr"·".edu" | acquisition | 학위논문·전자책 |
| 도서관명 "전문"·"법무"·"의학"·"병원"·"연구원" | acquisition | 분야 시소러스 |
| 도서관명 "작은"·"마을"·"동네" | general | 1인 사서 작은도서관 |
| 도서관명 "학교"·"초등"·"중학교"·"고등학교" | general | 자원봉사 86% |
| 이메일 ".go.kr" or "공공" | general | 정부·공공 |
| (default) | unknown | PO 수동 분류 |

매크로 (조기흠 페르소나)는 도서관명·이메일로 자동 판단 어려움 → unknown 후 PO 수동 또는 PILOT 시연 시 분류.

## Consequences

### 쉬워지는 것

- 신규 가입 즉시 페르소나 판정 → 환영 메시지·영업 funnel 자동
- aggregate_interviews.by_persona 정합 (signup persona 키 활용)
- /admin/stats by_persona funnel 정합

### 어려워지는 것

- "매크로 사서"는 외형 판단 X → unknown
- 회피: PILOT 시연 후 pilot_collect.py로 명시 분류

### 트레이드오프

- 정확도 (수동) ↔ 자동 (cold start UX)
- 우리 선택: 자동 (영업 funnel 즉시 매핑·캐시카우 직결)

### 후속

- BACKLOG 1순위 /signup persona 완료
- 7 tests로 회귀 차단 (test_signup_persona_detection.py)
- aggregate_interviews + sales_funnel.funnel_by_persona 정합

## Sources

- 54376d0: detect_persona + 7 tests
- `docs/saseo-personas-2026-04-28.md` (4 페르소나 정밀)
- `scripts/pilot_collect.py` (PILOT 시 명시 분류)
- `scripts/sales_funnel.py:funnel_by_persona`
