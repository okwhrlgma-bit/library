# ADR 0067: Programmatic SEO + 시기상조 박제 정합 (2026-05-09·Cycle 213)

## 상태

Accepted (PO 영구 명령 정합·2026-05-09·Cycle 200 메모리 박제)

## 배경

- 외부 AI 보고서 (2026-05-09·40+ URL) = 자가 치유·Programmatic SEO·SOC2·RFP 자동화·매각 실사 등 10대 영역
- PO 명령: "외부 URL 정보 내재화 + 시기상조도 박제·향후 자료 재탐색 X"
- 현재 시점 (Cycle 212·매출 ₩0 115 cycle) = 자동화 + B2B + 세무 100% 완성
- 시기상조 박제 X 시 = 향후 매출 도달 시 자료 재탐색·자원 소모

## 결정

### 1. Programmatic SEO 시드 = _shared/seo 모듈 (Cycle 207~211 적용)

```
Phase 1 (현재): 메타데이터·키워드 매트릭스 helper 8건
Phase 2 (트래픽 ≥1K MAU): 정적 사이트 (Hugo·Astro) 신규
Phase 3 (매출 ₩1M+): 수천 페이지 자동 생성 + 구글 인덱싱
```

### 2. 시기상조 박제 의무 (정합도 ≥70% 시)

```
- _meta/06~16 = 16 박제 (Cycle 196~205 누적)
- 향후 PO 결정 시 = 즉시 활성 가능 (자료 재탐색 X)
- 트리거 매트릭스 = _meta/15 (매출·트래픽 임계값)
```

### 3. PO 1줄 명령 패턴 = 시기상조 즉시 활성

```
"_meta/09 SEO 시작" → Cycle N = SEO 메타데이터 + _shared/seo 모듈
"_meta/11 Sentry 도입" → Cycle N = sentry_sdk + observability 모듈
"_meta/12 Lightsail 이전" → Cycle N = Dockerfile + nginx
"_meta/13 SOC2 시작" → Cycle N = audit log 9개월 자동
"_meta/14 RFP 응답" → Cycle N = 고객 RFP markdown → PDF
```

## 근거

### 외부 보고서 정합 검증

| 영역 | 출처 | 정합도 |
|---|---|---:|
| Programmatic SEO | Founderpath (24 templates·50K leads) | 80% |
| 자가 치유 (Sentry) | Sentry Seer + Claude Agents | 70% |
| AWS Lightsail | AWS·KISA·PIPA 정합 | 90% |
| SOC2 | ethyca·secureleap·optro·scytale | 81% |
| RFP 자동화 | heyiris·tribble·iternal·arphie | 90% (BYOK) |
| 매각 실사 | Acquire.com (4~5x ARR) | 85% |

### 우리 시점 정직

- 매출 ₩0 = 115 cycle = 핵심 차단점
- 시기상조 박제 = 향후 효율 ↑ (자료 X·자원 X)
- Programmatic SEO 시드 = Phase 2 즉시 활성 가능

## 결과 (긍정)

- _shared/seo 8 helper = Phase 2 즉시 활성
- _meta 16 박제 = 향후 PO 결정 시 1줄 명령
- 자료 재탐색 = 0 (영구 메모리 정합)

## 부작용 (정직)

- 시기상조 박제 = 박제 비중 ↑ (ADR 0061 균형 일시 위반·Cycle 198~206)
  → Cycle 207~212 = 코드 비중 ↑ 회복 ✅
- 박제만 누적·실 활용 = PO 결정 후만

## 정합 정책

- ADR 0058 (조건부 배포): Phase 별 활성 조건 정합
- ADR 0061 (박제·코드 균형): 5 cycle 누적 시 균형 의무
- ADR 0064 (Blanket auth): 자료 fetch + 박제 자율
- ADR 0066 (5 사용처 packages/): 5번째 사용처 도달 시 승격
- feedback_research_internalization (PO 영구·Cycle 200 메모리)

## 메타

- 작성: 2026-05-09 Cycle 213
- 적용: 즉시·향후 모든 외부 보고서 fetch 시
- 다음 외부 보고서 수신 시 = 본 ADR 정합 자동 적용
