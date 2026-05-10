# ADR 0061 — 박제·코드 균형 의무 (자기 진단 결과·2026-05-08)

- 상태: Accepted (자율·자기 진단 정합)
- 일자: 2026-05-08
- 관계: ADR 0059 (적합성 판단) 보강·외부 901 진단 정합

## 배경

자기 진단 (Cycle 89·`docs/self-assessment/2026-05-08-cycle-89-po-commands-review.md`):
- 5 cycle 누적 = 박제 매우 강함 (ADR 11건·메모리 4건·docs 30+)
- 코드 = 5 앱 (1,407 tests)·균형 OK
- **but 실 검증 0건·사용자 0명·매출 ₩0**
- 외부 901 진단 재발 위험 ("productive avoidance"·"identity fusion")

## 결정

**매 cycle = 박제·코드 균형 의무.**

### 균형 룰

```
1 cycle 작업 분배:
- 박제 (ADR·docs·메모리·INDEX) = 30~50%
- 코드 (src·tests·smoke test·UI) = 50~70%
- 페인 발굴 (WebSearch·평가) = 0~20%

박제 > 50% 비율 = 다음 cycle 코드 우선 의무
박제 = 0% = OK (코드 깊이 cycle)
코드 = 0% = ⚠ (다음 cycle 보강 의무)
```

### 신규 박제 게이트 (ADR·메모리)

매 신규 ADR 박제 = 다음 모두 통과:
1. ADR 0059 7 차원 통과
2. ADR 0060 10 규칙 정합
3. **수익화 직접 기여 1줄 명시**
4. **동일 cycle 코드 1+ 동시 진행** (박제만 X·코드 페어 의무)

→ 4 통과 X = 박제 보류·코드만 진행.

### 박제 동결 트리거

- 5 cycle 연속 박제 > 코드 = 즉시 박제 1 cycle 동결 (코드만)
- ADR 신규 = 1 cycle = 1+건 X (집중 분산 방지)

## 자기 진단 결과 적용

### Cycle 89 = 박제 비율 ≈ 70% (코드 30%)
- 박제: ADR 5건·docs 10+·메모리 2건·CLAUDE 4 항
- 코드: #32 Streamlit UI + #31 Streamlit UI + _shared/payments·legal templates

→ 박제 > 50% = **다음 cycle (90) = 코드 우선·박제 동결**.

### Cycle 90 권장 (자율 결정)
- ✅ 코드 (필수): _shared/auth + _shared/email + #32 smoke test 5건 + kormarc-auto 페인 게이트 평가
- ❌ 박제 동결: 신규 ADR X·신규 메모리 X·docs/ 추가 = 코드 페어 시만

## 수익화 기여

| 항목 | 이유 |
|---|---|
| 박제 인플레이션 차단 | 의사결정 비용 ↓·실행 가속 |
| 코드 우선 회복 | 실 검증 가속·매출 가속 |
| 외부 901 재발 회피 | productive avoidance 차단 |

## 박제

- 본 ADR = 박제 + 코드 페어 의무 (matrix·코드 측면 = 적용 자체)
- CLAUDE.md §8L (다음 cycle 추가)
- INDEX 갱신 = ADR 0061

## 메타 적합성

본 ADR = 자가 ADR 0059 7 차원 검증:
1. 헌법: ✅
2. ADR 정합: ✅ (0052·0053·0055·0056·0058·0059·0060)
3. PO 명령: ✅ ("진지하게 고려"·자기 진단)
4. 수익화 ROI: ✅ (인플레이션 차단)
5. 1인 PO 운영: ✅ (단순 룰)
6. 벤치마크: ✅ (외부 901 진단·"productive avoidance" 회피)
7. 부작용: ✅ (없음)

→ 7 차원 통과·Accepted.
