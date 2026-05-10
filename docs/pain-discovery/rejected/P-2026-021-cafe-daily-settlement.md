# P-2026-021 — 한국 작은 카페·식당 1인 사장 일일 마감 정산 (NO_GO)

## 페인

- audience: 한국 자영업 카페·식당 60만+
- frequency: 매일 (마감)
- current_workaround: **카카오뱅크·토스 가계부 (무료)·POS 시스템·세무사 SaaS·엑셀**

## 15 요건 자동 평가

### PO 3 요건 (20/30)
| 요건 | 점수 |
|---|---|
| 1. 페인 | 7/10 |
| 2. 자동화 | 6/10 (POS·카드사 통합 복잡) |
| 3. 수익성 | 7/10 (자영업 결제 가능) |

### 자율 12 요건 (7/12)
| 요건 | 결과 |
|---|---|
| 4. 결제권자=결제자 | ✅ |
| 5. 1인 PO 운영 | ⚠ POS·카드사 API 통합 어려움 |
| 6. 정부·거대 무료 X | ⚠ 카카오뱅크·토스 가계부 무료 |
| 7. founder fit | ❌ PO = 사서·자영업 X |
| 8. 반복 사용 | ✅ 매일 |
| 9. 락인 | ✅ 매출 history |
| 10. 법적 위험 X | ✅ |
| 11. 한국 + 글로벌 | ❌ 한국만 |
| 12. 인디 검증 | ❌ (검증 X·sales niche) |
| 13. ADR 0052 정합 | ✅ |
| 14. 헌법 §14 | ✅ |
| 15. MIT | ✅ |

## 자동 평가 결과

```
po_score = 20/30
autonomy_score = 7/12
overall = (20/30 × 50) + (7/12 × 50) = 33 + 29 = 62

decision: MAYBE (>= 60·< 75)·but 보수 NO_GO 권장
fail_reasons:
  - 5: 1인 PO POS 통합 어려움
  - 6: 카카오·토스 가계부 무료
  - 7: founder fit X
  - 11: 글로벌 X
  - 12: 인디 검증 X
```

## 정직 진단 = 보수 NO_GO

자동 평가 = MAYBE 62·but 정직:
1. **POS·카드사·식자재 통합** = API 복잡·1인 PO 부담 ↑
2. **카카오뱅크·토스 가계부** = 무료·일반 자영업자 충분
3. **founder fit X** = PO = 자영업 운영 경험 X
4. **인디 검증 X** = 자영업 sales SaaS niche·1인 사례 발견 X

## 영구 폐기 (MAYBE → NO_GO 보수 보정)

ADR 0065 자동 룰 = MAYBE·but 사람 판단 = NO_GO (외부 901 진단 정합·domain expert curse 회피).

→ 다음 후보 = founder fit 강한 영역·or 단일 기능 단순 niche.

## 출처

- [2026 카페 창업 트렌드 (ESGeconomy)](https://www.esgeconomy.com/news/articleView.html?idxno=14145)
- [중소기업 세무회계 TOP10 (Jounboo)](https://www.jounboo.com/blog/top-10-accounting-solutions-for-small-businesses-pros-and-cons-comparison-2024)
- [마이크로 SaaS 롤업 (진양 인수창업)](https://www.jianyang.co.kr/p/ai-saas)
