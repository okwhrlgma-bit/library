# P-2026-017 — 직장인 영어 단어 학습 자동 (NO_GO·거대 사업자 포화)

## 페인

- audience: 한국 직장인 영어 학습자 1,000만+·매일 사용
- frequency: 매일
- current_workaround: **Duolingo (글로벌 $9B)·Anki (무료·31,000원)·말해보카·산타토익·캐피톨**

## 15 요건 자동 평가 (ADR 0065)

### PO 3 요건 (24/30)
| 요건 | 점수 |
|---|---|
| 1. 페인 | 8/10 |
| 2. 자동화 | 9/10 (LLM 단어·예문·발음) |
| 3. 수익성 | 7/10 (시장 큼·but 거대 점유) |

### 자율 12 요건 (8/12)
| 요건 | 결과 |
|---|---|
| 4. 결제권자=결제자 | ✅ 본인 |
| 5. 1인 PO 운영 | ✅ |
| 6. 정부·거대 무료 X | ❌ **Duolingo·Anki·말해보카 거대 점유** |
| 7. founder fit | ❌ PO = 사서·영어 전문 X |
| 8. 반복 사용 | ✅ 매일 |
| 9. 락인 | ⚠ |
| 10. 법적 위험 X | ✅ |
| 11. 한국 + 글로벌 | ✅ |
| 12. 인디 검증 | ❌ **Duolingo $9B·거대 SaaS 정면** |
| 13. ADR 0052 정합 | ✅ |
| 14. 헌법 §14 | ✅ |
| 15. MIT | ✅ |

## 자동 평가 결과

```
po_score = 24/30
autonomy_score = 8/12
overall = 40 + 33 = 73

decision: MAYBE
fail_reasons:
  - 6: Duolingo·Anki·말해보카 거대 점유
  - 7: founder fit X
  - 9: 락인 약함
  - 12: 인디 검증 X (Duolingo $9B 반례)
```

## 폐기 정직 결정 = NO_GO (MAYBE → 보수적 NO_GO)

이유:
1. **Duolingo $9B·Anki 26년 무료** = 인디 1인 PO X
2. 한국 사업자 = 산타토익 (시리즈 B 받음)·말해보카 (시리즈 B)·캐피톨 = 거대 사업자
3. founder fit X (PO = 사서·영어 학습 도메인 외)
4. 1인 PO 신규 진입 = 마케팅 자금 없이 = 사실상 불가능

## 출처

- [Anki 나무위키](https://namu.wiki/w/Anki)
- [디지털 영어 학습 시장 (Business Research Insights)](https://www.businessresearchinsights.com/market-reports/digital-english-language-learning-market-101452)
- [K-에듀테크 (포브스)](https://www.forbeskorea.co.kr/news/articleView.html?idxno=401704)
