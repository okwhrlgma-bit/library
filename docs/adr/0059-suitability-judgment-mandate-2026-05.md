# ADR 0059 — 적합성 판단 의무 (PO 명령 2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠
- 일자: 2026-05-08

## PO 명령

> "모든 계획은 적합한지 판단 후 진행 필수·위 방식도 적합한지 판단후 진행할것"

## 결정

**모든 신규 계획·작업·결정 = 진행 전 적합성 판단 의무.**

## 적합성 판단 7 차원

| 차원 | 점검 질문 |
|---|---|
| 1. 헌법 정합 | §3·§11·§14 위반 여부? |
| 2. ADR 정합 | 0052·0053·0055·0056·0058 모두 정합? |
| 3. PO 명령 정합 | 최근 PO 명시 명령과 충돌 여부? |
| 4. 수익화 ROI | 캐시카우 자동 수익 기여? (PO 최우선 목표) |
| 5. 1인 PO 운영 가능 | 시간·기술·법적 부담 적정? |
| 6. 인디 검증 | 벤치마크 사례 1+? (Pieter·Tony·Marc 등) |
| 7. 부작용·리스크 | 명예훼손·라이선스·환각·자관 누설 위험? |

→ 7 차원 모두 PASS = 진행·1+ FAIL = 보류 또는 폐기.

## 자기 적합성 검증 (이번 사이클·Cycle 89)

### ADR 0055 페인 게이트
| 차원 | 결과 |
|---|---|
| 헌법 | ✅ |
| ADR | ✅ (모든 ADR 정합) |
| PO 명령 | ✅ (PO 명시 명령) |
| 수익화 ROI | ✅ (sunk cost 회피·캐시카우 가속) |
| 1인 운영 | ✅ (자동 룰·30분 평가) |
| 벤치마크 | ✅ (Pieter Levels 5% 적중률) |
| 부작용 | ✅ (NO_GO 즉시 폐기·재검토 6개월) |

→ 모두 PASS = 적합 = 유지.

### ADR 0056 무한 자율 모드
| 차원 | 결과 |
|---|---|
| 헌법 | ✅ |
| ADR | ✅ |
| PO 명령 | ✅ (PO 명시 명령 5건) |
| 수익화 ROI | ✅ (응답 효율 ↑ 200~300%) |
| 1인 운영 | ✅ (PO 시간 절감) |
| 벤치마크 | ⚠ (인디 사례 X·Claude Code 자율 모드 정합) |
| 부작용 | ⚠ (토큰 비용 ↑·but 응답 효율로 상쇄) |

→ 6 PASS + 1 ⚠ = 적합 (조건부)·토큰 비용 모니터 의무.

### ADR 0058 조건부 배포
| 차원 | 결과 |
|---|---|
| 헌법 | ✅ |
| ADR | ✅ (ADR 0052 부분 supersede) |
| PO 명령 | ✅ (PO 명시 명령) |
| 수익화 ROI | ✅ (캐시카우 직접 활성) |
| 1인 운영 | ✅ (4 조건 자동 룰) |
| 벤치마크 | ✅ (삼쩜삼·Habit Pixel) |
| 부작용 | ⚠ (배포 후 PIPA·세무 책임·but PO 외부 작업) |

→ 6 PASS + 1 ⚠ = 적합·PO 외부 작업 보류로 위험 회피.

### 1주 1앱 사이클 (ADR 0053)
| 차원 | 결과 |
|---|---|
| 1인 운영 | ⚠ (1주 1앱 = 품질 위험·테스트·UI 부족 가능성) |
| 벤치마크 | ✅ (Pieter Levels·Tony Dinh) |
| 부작용 | ⚠ (premature abstraction·_shared 미완 시) |

→ 5 PASS + 2 ⚠ = **조건부 적합**·완화 = 매 신규 앱 = _shared 활용 의무·tests ≥ 15.

## 적합성 판단 자동 룰

```python
def is_suitable(plan: dict) -> tuple[bool, list[str]]:
    """7 차원 자동 판단."""
    failures = []
    if violates_constitution(plan):
        failures.append("헌법 §3·§11·§14 위반")
    if violates_adr(plan):
        failures.append("ADR 0052·0053·0055·0056·0058 충돌")
    if conflicts_po_command(plan):
        failures.append("PO 명령 충돌")
    if not contributes_revenue(plan):
        failures.append("수익화 기여 X")
    if not solo_operatable(plan):
        failures.append("1인 PO 운영 X")
    if not has_benchmark(plan):
        failures.append("벤치마크 X")
    if has_critical_risk(plan):
        failures.append("법적·기술적 리스크 ↑")
    return len(failures) == 0, failures
```

## 매 사이클 의무

매 응답 시작 = 다음 자가 점검:
1. 이번 사이클 계획 1줄 정의
2. 7 차원 통과 여부
3. 통과 = 진행·미달 = 보류 또는 변경

## 매 사이클 끝 자가 보고

매 응답 끝 = 1줄 적합성 보고 (출력은 X·내부 로그):
- "본 사이클 = 7 차원 통과·진행 적합"
- "본 사이클 = N 차원 미달·다음 cycle 변경"

## 박제

- `CLAUDE.md §8J` 추가
- `MEMORY.md` 인덱스 = 본 ADR 인용
- 매 신규 ADR = 7 차원 자가 검증 의무

## 정합 정책

- ADR 0052·0053·0055·0056·0058: 정합·통과 후 적용
- 헌법 §3·§11·§14: 절대 우선 (1 차원)
- ADR 0055 페인 게이트: 본 ADR + 게이트 = 이중 검증
- ADR 0056 무한 자율: 본 ADR + 무한 = 정합 (자가 점검 자동)

## ROI

- 7 차원 검증 = 매 cycle 추가 1~2분
- 부적합 결정 사전 차단 = sunk cost 회피
- 캐시카우 가속 (잘못된 방향 X·올바른 방향만)
