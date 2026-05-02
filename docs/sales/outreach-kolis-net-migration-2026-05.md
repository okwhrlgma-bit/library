# KOLIS-NET 마이그레이션 영업 메일 (작은도서관 6,830관)

> **대상**: KOLIS-NET 가입 작은도서관 6,830관 (NLK 통합 목록)
> **단가**: 작은도서관 = 월 3만원 (자치구 카드 결제)
> **단일 진실**: 자관 .mrc 99.82% 정합 + 049 prefix 자동 발견 (5분 도입)
> **영업 시기**: 6~7월 + 11~12월 자치구 예산 편성 골든타임

---

## 1. KOLIS-NET 한눈

| 항목 | 내용 |
|---|---|
| 운영 | 국립중앙도서관 (NLK) |
| 가입 | 작은도서관 6,830관 + 공공도서관 통합 목록 |
| API | 5종 (NL Korea·KOLIS-NET·NL 검색·연도별 통계·키워드) |
| 우리 정합 | NL Korea API 1순위 폴백 (CONFIDENCE 0.95) |

---

## 2. 영업 메일 — KOLIS-NET 가입 작은도서관

**제목**: "KOLIS-NET 가입 작은도서관께 — KORMARC 자동 + 049 prefix 5분 도입 (월 3만원)"

```
안녕하세요. 사서 출신 1인 개발자 [PO 이름]입니다.

KOLIS-NET 가입 작은도서관 6,830관에 KORMARC 자동화 SaaS 제안드립니다.
NL Korea API 1순위 폴백으로 통합 목록 정합도가 매우 높습니다.

[정량]
- 자관 「○○도서관」 .mrc 174 파일·3,383 레코드 → ★ 99.82%
  정합 검증 완료 (한국 KOLAS 실무 정합·2026-04-29)
- 049 prefix 자동 발견 (자관 EQ·CQ·WQ → 5분 도입)
- 신뢰도 0.95 (NL Korea API)

[제안]
- 첫 50건 무료 + 월 3만원 (작은도서관·500건)
- `kormarc-auto prefix-discover "D:\<자관>\수서"` 1줄로 도입
- 자치구 카드 결제 또는 사서 본인 예산 (락인 X)

[작은도서관 특화]
- 1인 사서·자원봉사 사서 친화 (5분 가입·CLI/GUI 양쪽)
- KOLIS-NET 통합 목록 정합 (NL Korea API 1순위)
- 책나래·책바다·책이음 5 상호대차 양식 자동
- 책단비 hwp 자동 (은평구 한정·다른 지역 양식 추가 가능)

[5월 KLA 5.31 발표 후속]
- 자관 PILOT 4주 결과 → KLA 발표 (5.31)
- 작은도서관 PILOT 1관 모집 (4 페르소나 중 1관·6월 中)
- 사서교육원·도서관저널 강의·기고 (5~7월)

okwhrlgma@gmail.com · 카카오 채널 「kormarc-auto」
github.com/okwhrlgma-bit/library
```

---

## 3. 발송 일정

| 시기 | 발송 |
|---|---|
| 2026-06-01 ~ 06-15 | KOLIS-NET 가입 작은도서관 50통 |
| 2026-09 (PIPA 시행 직후) | 옵션 C 정합 영업 가속 50통 |
| 2026-11~12 (예산 편성) | 자치구 차년도 예산 영업 100통 |

---

## 4. 답장률 목표

| 시기 | 발송 | 회신 목표 | PILOT 가입 |
|---|---:|---:|---:|
| 6월 | 50통 | 5건 (10%) | 1관 |
| 9월 | 50통 | 5건 (10%) | 1관 |
| 11~12월 | 100통 | 15건 (15%·예산 골든타임) | 3~5관 |
| **합계** | **200통** | **25건** | **5~7관** |

→ 작은도서관 단독 영업으로 6~12월 5~7관 PILOT 가입 목표.

---

## 5. 도구·자료 정합

- `docs/sales/pilot-package-2026-04-29.md` (4 페르소나 메일 기본)
- `docs/sales/data4library-guide-2026-05.md` (정보나루 활용)
- `docs/sales/librarian-5min-cheatsheet.md` (사서 인쇄 A4 1장)
- `docs/sales/outreach-small-school-libraries-2026-05.md` (작은·학교 통합)
- `kormarc-auto prefix-discover` CLI (5분 도입)
- `scripts/sales_funnel.py` (영업 funnel 측정)

---

## Sources

- 국립중앙도서관 KOLIS-NET (kolisnet.nl.go.kr)
- `src/kormarc_auto/api/nl_korea.py` (1순위 폴백)
- `docs/research/korean-library-systems-comparison-2026.md` §6
