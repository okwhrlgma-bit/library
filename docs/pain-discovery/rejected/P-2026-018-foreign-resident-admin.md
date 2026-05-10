# P-2026-018 — 한국 외국인 거주자 행정 도우미 (NO_GO·법적 위험 자동 강제·Cycle 101)

## 페인

- audience: 한국 거주 외국인 250만+·매월 비자·세금·은행·의료
- frequency: 매월 (행정)·1년 1회 (비자 갱신)
- current_workaround: **Visa Navigator (정부 무료·다국어 일부)·행정사·변호사 (유료·자격 필요)**

## 15 요건 자동 평가

### PO 3 요건 (22/30)
| 요건 | 점수 |
|---|---|
| 1. 페인 | 8/10 |
| 2. 자동화 | 8/10 (LLM 다국어 번역) |
| 3. 수익성 | 6/10 (외국인 결제 의향 ↑·but 시장 작음) |

### 자율 12 요건 (7/12)
| 요건 | 결과 |
|---|---|
| 4. 결제권자=결제자 | ✅ |
| 5. 1인 PO 운영 | ✅ |
| 6. 정부·거대 무료 | ⚠ Visa Navigator 부분 |
| 7. founder fit | ❌ |
| 8. 반복 사용 | ⚠ 비자 1년 1회 |
| 9. 락인 | ⚠ |
| **10. 법적 위험 X** | ❌ **행정사법·변호사법 위반** |
| 11. 한국 + 글로벌 | ✅ |
| 12. 인디 검증 | ⚠ |
| 13~15 | ✅ |

## 자동 평가 (Cycle 101 룰)

```
po_score = 22/30
autonomy_score = 7/12
overall = (22/30 × 50) + (7/12 × 50) = 37 + 29 = 66

decision: NO_GO (법적 위험 = no_legal_risk = False = 자동 강제)
fail_reasons:
  - 7. founder fit X
  - 10. 법적 위험 (행정사법·변호사법)
penalties: []
```

## 폐기 이유

1. **행정사법 §3**: 출입국 대행 = 행정사 자격 (위반 시 형사 처벌)
2. **변호사법 §109**: 법무 자문 = 변호사 자격
3. **출입국관리법**: 정부 Visa Navigator 무료 (다국어 확장 중)
4. founder fit X (PO = 한국 사서·외국인 X)

## Cycle 101 룰 검증

이중 페널티 X·but **법적 위험 = no_legal_risk = False = NO_GO 자동 강제** = 정상 작동.

## 출처

- [출입국·외국인정책본부](https://www.immigration.go.kr/)
- [Visa Navigator (정부 무료)](https://www.immigration.go.kr/bbs/immigration_eng/230/454086/download.do)
- [E-7-4 비자 매뉴얼 (윤 행정사)](https://yoonhjs.com/e-visa-...)
