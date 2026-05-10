# P-2026-015 — 한국 인디 게임 1인 개발자 마케팅 (NO_GO·15 요건 첫 적용)

## 페인

- audience: 한국 인디 게임 개발자 1만+·STOVE Indie + Steam
- frequency: 게임 1~2년에 1개 (낮음·1회성)
- current_workaround: STOVE Indie 무료 등록·창작자 센터·트위터·디스코드

## 15 요건 평가 (ADR 0065·자동)

### PO 3 요건 (17/30)

| 요건 | 점수 |
|---|---|
| 1. 페인 (스크린샷 7장·홍보 시간 多) | 7/10 |
| 2. 자동화 (스크린샷 가능·트위터 자동 약관 X) | 5/10 |
| 3. 수익성 (1회성·인디 ₩9,900) | 5/10 |

### 자율 12 요건 (7/12)

| 요건 | 결과 |
|---|---|
| 4. 결제권자=결제자 | ✅ 인디 본인 |
| 5. 1인 PO 운영 | ✅ |
| 6. 정부·거대 무료 잠식 X | ⚠ STOVE 무료 등록 |
| 7. founder fit | ❌ PO = 인디 게임 X |
| 8. 반복 사용 | ❌ 1~2년 1게임 = 1회성 |
| 9. 락인 | ❌ 약함 |
| 10. 법적 위험 X | ⚠ 트위터 자동 약관 위반 |
| 11. 한국 + 글로벌 | ✅ |
| 12. 인디 검증 | ⚠ 글로벌 Steam 마케팅 SaaS 다수 |
| 13. ADR 0052 정합 | ❌ STOVE·Steam 외부 가입 |
| 14. 헌법 §14 | ✅ |
| 15. MIT | ✅ |

## 자동 평가 결과

```
po_score = 17/30
autonomy_score = 7/12
overall = (17/30 × 50) + (7/12 × 50) = 28 + 29 = 57
fail_reasons:
  - 8. 반복 사용 X (1회성)
  - 7. founder fit X
  - 9. 락인 X
  - 13. ADR 0052 외부 가입

→ NO_GO (overall < 60)
```

## 폐기 이유

1. **1회성 = 캐시카우 X** (반복 사용 X·1~2년 1게임)
2. **founder fit X** (PO = 사서·게임 개발 X)
3. **글로벌 거대 SaaS** = Steam 마케팅 도구 다수
4. **트위터 자동 = 약관 위반** = 법적 위험

## 출처

- [STOVE Indie 창작자 센터](http://forcreators.stoveindie.com/)
- [스팀 출시 강좌 (인디 갤러리)](https://gall.dcinside.com/mgallery/board/view/?id=game_dev&no=56289)
- [인디 게임 사업자 등록](http://forcreators.stoveindie.com/post/?bmode=view&idx=84443359)

## 15 요건 게이트 첫 적용 결과

- Cycle 95 ADR 0065 신설
- Cycle 96 첫 적용 = NO_GO 정확 분류
- 정직 = 자율 12 요건 = 8·9·13 fail = 핵심 차단
</thinking>
