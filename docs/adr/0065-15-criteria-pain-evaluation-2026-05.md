# ADR 0065 — 15 요건 페인 평가 매트릭스 (PO 명령 2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠 (3 요건) + Claude 자율 (12 요건)
- 일자: 2026-05-08

## PO 명령

> "내 생각에 3가지 요건이 있어야하는거같아 페인 혹은 귀찮은 포인트, 자동화 및 신경 끌수 있는지, 사람들이 결제로 이어지거나 지속해서 돈을 벌수 있는등 수익성이 있는지·그외의 우리의 목표를 위한 요소가 뭐뭐 있을려나?"

## PO 3 요건 (검증·정확)

1. **페인·귀찮은 포인트** (0~10)
2. **자동화·신경 끌 수 있는지** (set-and-forget·0~10)
3. **수익성** (결제·지속 매출·0~10)

## Claude 자율 12 요건 (누적 학습 정합)

| # | 요건 | 출처 |
|---|---|---|
| 4 | 결제권자 = 결제자 | ADR 0050·외부 901 |
| 5 | 1인 PO 운영 가능 | 외부 901·domain expert curse |
| 6 | 정부·거대 무료 잠식 X | P-007·P-014 NO_GO 패턴 |
| 7 | founder fit (PO = 사용자) | Cycle 69 |
| 8 | 반복 사용 (1회성 X) | Cycle 84 |
| 9 | 락인 메커니즘 | Marc Lou cross-link |
| 10 | 법적 위험 X | I-002·#31 면책 |
| 11 | 한국 + 글로벌 | Sandi Metz AHA |
| 12 | 인디 검증 1+ | Pieter·Tony·Marc·Habit Pixel |
| 13 | ADR 0052 정합 | 코딩 외 X |
| 14 | 데이터 사용자 컴퓨터 | 헌법 §14 |
| 15 | MIT/Apache 가능 | 오픈 신뢰 |

## 자동 평가 (코드)

`scripts/evaluate_pain_15.py` 신규·결정적·LLM 호출 0.

```python
po_score = pain + automation + revenue  # 30 max
autonomy_score = sum(12 booleans)  # 12 max
overall = (po/30 × 50) + (autonomy/12 × 50)

GO    if overall >= 75 and no_legal_risk
MAYBE if overall >= 60
NO_GO otherwise
```

## 검증 (#31 freelancer-tax-helper)

- PO score: 26/30 (페인 9·자동화 8·수익 9)
- 자율 score: 10/12 (founder fit X·한국만)
- **overall 85·GO ✅**·fail_reasons []

## 적용

매 신규 앱 = 15 요건 평가 의무 (ADR 0055·0058 보강)·`evaluate_pain_15.py --demo` 호출.

## 메모리

- `feedback_15_criteria_pain_eval.md` ⭐⭐⭐⭐ (다음 cycle)
- CLAUDE.md §8K 추가 (다음 cycle)
- `scripts/evaluate_pain_15.py` (코드 페어·ADR 0061 정합)

## Cycle 100 룰 보강 (2026-05-09)

자율 평가 한계 발견 (Cycle 99·P-017 영어 학습) = 자동 룰 보강.

### 신규 페널티 (보수 보정·-10 each)

| 페널티 | 트리거 | 사례 |
|---|---|---|
| `giant_competitor_billion` | 시가총액 $1B+ 거대 사업자 정면 | Duolingo $9B·Stripe·Notion |
| `government_free_dominant` | 정부 무료 도구 직접 잠식 | HUG 안심전세·홈택스 손택스 |

### 검증 결과

| 페인 | 이전 | 페널티 적용 후 |
|---|---:|---|
| #31 freelancer-tax | 85 (GO) | 85 (변동 X·페널티 0) |
| #1 kormarc-auto | 72 (MAYBE) | 72 (변동 X) |
| **P-017 영어 학습** | 73 (MAYBE) | **63 (MAYBE)·-10 ✅** |

→ 페널티 적용 = MAYBE 영역 보수 보정·but **두 페널티 동시 = -20 = NO_GO 자동 강제** (다음 cycle 보강 후보).

### 적용 정책

매 신규 평가 = `giant_competitor_billion` + `government_free_dominant` 자동 점검 의무·MAYBE 보수 보정.

## Cycle 108 룰 v5 보강 (2026-05-09)

P-021 자영업 정산·P-017 영어 학습 = MAYBE 자동·but 정직 NO_GO 패턴 발견.

### 신규 자동 룰

```python
# v5: founder fit X AND indie_benchmark X = NO_GO 강제
if not eval.founder_fit and not eval.indie_benchmark:
    decision = "NO_GO"
    penalties.append("founder fit X + 인디 검증 X = NO_GO 강제 (보수)")
```

### 검증 결과 (v5 적용)

| 페인 | v4 | v5 |
|---|---|---|
| #31 freelancer-tax (founder X·indie ✅) | GO 85 | **GO 유지** ✅ |
| #1 kormarc-auto (founder ✅·indie X) | MAYBE 72 | **MAYBE 유지** ✅ |
| P-017 영어 학습 (founder X·indie X) | MAYBE 63 | **NO_GO 자동** ✨ |
| 완벽 평가 (founder ✅·indie ✅) | GO 90 | GO 90 ✅ |

→ **자동 NO_GO 강제 = 보수 보정 자동화 성공·정직 정합**.

## 자동 NO_GO 강제 룰 종합 (3건)

1. giant + government 페널티 동시 → NO_GO
2. no_legal_risk = False → NO_GO
3. **founder_fit X + indie_benchmark X → NO_GO (v5·이번)**

→ 위 3건 = **자동 보수 보정**·MAYBE 영역 = 정직 NO_GO 자동.

## tests 회귀 (Cycle 108)

`tests/test_evaluate_pain_15.py` 16건 passing (v5 신규 3건 + 회귀 갱신 1건).
