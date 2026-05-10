# P-2026-009 — 1인 출판사 ISBN + 서지 + 등록 도우미 (MAYBE·다음 cycle)

## 페인

- 1인 출판사 등록 (출판사명 중복·면세업 정합)·ISBN 신청 (NL Korea seoji)·KORMARC 서지·도서관 납본
- audience: 한국 1인 출판사 ~1만+ + 자비 출판 ~5만+ (합 SAM 6만)
- frequency: 책 1권당 1회·자비 출판 = 평생 1~3권
- current_workaround: 작가와·북퍼브·북플레이트 (통합 플랫폼·but 비싸고 패키지)

## 시장성

| 항목 | 점수 |
|---|---|
| 시장 (SAM 6만) | +15 |
| 경쟁 = 통합 플랫폼 3개 (단일 niche 부족) | +15 |
| 인디 검증 | +5 |
| 빈도 (낮음) | +0 |
| 결제 의향 (자비 출판자 = 강함) | +10 |
| 한국 niche·founder fit | +10 |
| **합계: 55/100** (경계선) | |

## 캐시카우

| 항목 | 점수 |
|---|---|
| ARPU ₩9,900~19,900 | +25 |
| COGS offline (LLM 옵션) | +20 |
| 자동 갱신 (월정액 어려움·1회 결제 가능) | +5 |
| 락인 (낮음·1회 사용) | +5 |
| 1인 PO 가능 | +10 |
| **합계: 65/100** | |

## 결정

```
market 55 < 60 (경계선)·cashcow 65 ≥ 60·Q5 PASS
→ MAYBE (다음 cycle 단일 기능 세분화 후 결정)
```

## 단일 기능 후보 (세분화 = GO 가능)

1. **출판사 등록명 중복 검색기** (단순·NL Korea seoji 활용·MIT)
2. **원고 메타데이터 → KORMARC 서지 자동** (kormarc-auto + kdc-classify 재활용·founder fit)
3. **ISBN 신청 체크리스트 + 가이드** (NL 절차 자동·offline)

→ 가장 강한 후보 = **#2 (KORMARC 서지 자동·우리 자산 재활용)**.

## 다음 cycle 진행 권장

- monorepo packages/ 승격 (kormarc-auto + kdc-classify + librarian-overtime + freelancer-tax + sidehustle-tracker = 5 사용처 = packages/ 승격 시점) 후 = 1인 출판 도우미 시작
- 또는 = 단순 "출판사 등록명 중복 검색기" = 즉시 GO 가능 (단일 기능 강함)

## 출처

- [1인 출판사 등록 (트레이더 팡팡러)](https://tss.nadamaster.com/entry/1%EC%9D%B8-%EC%B6%9C%ED%8C%90%EC%82%AC-%EB%93%B1%EB%A1%9D-%EB%B0%8F-%EC%8B%A0%EC%B2%AD-%EB%B0%A9%EB%B2%95-%EC%B4%9D%EC%A0%95%EB%A6%AC)
- [ISBN·ISSN·UCI·납본 시스템 (NL Korea)](https://www.nl.go.kr/seoji/)
- [북플레이트 POD 자비출판 (이넷뉴스)](https://www.enetnews.co.kr/news/articleView.html?idxno=48246)
- [BOOKPUB POD](https://bookpub.co.kr/)
- [브런치 1인 출판사 등록 (skychang44)](https://brunch.co.kr/@skychang44/201)
