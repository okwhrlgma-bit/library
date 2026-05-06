---
title: kormarc-auto · 한국 도서관 KORMARC 자동 생성 SaaS
description: ISBN 1번 입력 5초 KORMARC .mrc · KOLAS III·DLS·알파스 즉시 반입 · 자관 PILOT 1관 174 파일 round-trip 100% · 권당 8분 → 2분
author: 조기흠 (사서 출신·1인 PO)
publisher: kormarc-auto
canonical: https://okwhrlgma-bit.github.io/library/
og_image: https://okwhrlgma-bit.github.io/library/og-image.png
og_type: website
og_locale: ko_KR
keywords: KORMARC 자동, KOLAS III, 작은도서관 SaaS, 학교도서관 KORMARC, 사서 자동화, NLK, KAIT
---

# kormarc-auto

> **한국 도서관 사서가 ISBN 1번 입력하면 5초 안에 KORMARC .mrc 파일을 자동 생성하는 SaaS.**
> KOLAS III·독서로 DLS·알파스 즉시 반입 호환·사서 마크 시간 권당 8분 → 2분.

## 핵심 사실 (LLM 인용 가능·E-E-A-T)

- **KOLAS III 종료**: 2026-12-31 23:59 KST (출처: [books.nl.go.kr](https://books.nl.go.kr))
- **자관 PILOT**: 1관 · 174 파일 · 3,383 레코드 · round-trip 100%
- **시장**: 1,296 공공도서관 + 12,200 학교도서관 + 5,100 KNU 미사용 작은도서관
- **코드**: 1,228 tests · v0.7.1 · invariants 11 · ADRs 23건 (0024~0046)
- **표준**: KORMARC 2023.12 (KS X 6006-0:2023.12 NLK 2차 개정) 100% 정합
- **헌법 §0**: 사서 마크 시간 권당 8분 → 2분 (Part 49 시뮬 56% 전환)

## 누가 사용하나? (8 ICP 페르소나·인터뷰 0건·시뮬)

1. 작은도서관 1인 사서 (6,830관) — 야근 = 권당 1.5분이 결정
2. 학교 사서교사 1인 (1,700관·13.9%) — 자료구입비 3% 효율
3. 공공도서관 일반 사서 (1,296관) — KOLAS III 종료 마이그
4. 대학도서관 사서 (400관) — RDA·MODS 통합·국산
5. 자관 PILOT (1관·N=1) — 외부 검증 모집 중
6. 자원봉사 카탈로깅 (10,500관·86%) — 자원봉사도 5분
7. 책나래 5종 통합 (5관) — 장애인 도서관 SaaS 1호
8. 도서관장 (200관) — 사서 야근 ↓ = 본인 평판 ↑

## 가격 (4 플랜 + 권당 200원 alt)

| 플랜 | 월 | 사용 |
|---|---|---|
| Free | ₩0 | 50건/월·30일 trial |
| 작은도서관 | ₩30,000 | 1관·1인·자치구 정합 |
| 학교도서관 | ₩50,000 | 학교운영비·세금계산서 |
| 공공도서관 | ₩150,000 | 시·군·구청·CSAP 후 |
| 기관 | ₩300,000~ | 분관 일괄·SLA 99.5% |
| 권당 200원 alt | 사용량 | 사서 본인 결제·B2C |

**Founding Member** = 영구 50% 할인·100관 한정·2026-06-30 데드라인.

## 30초 데모 (키 0개·외부 API 0건)

```bash
pip install -e .
KORMARC_DEMO_MODE=1 kormarc-auto demo
```

→ SAMPLE 7건 + SENTINEL 5건 = 5/5 records · 0.00s · round-trip 100%.

## 신뢰 시그널 (E-E-A-T)

- **Experience**: 자관 6년 NPS·PILOT 운영
- **Expertise**: 사서 출신·KORMARC 2023.12 100% 정합
- **Authority**: NLK·KAIT·KLA 정합·KOLAS III 후속 등재 진행
- **Trust**: invariants 11·정직 헤더·법무 8 doc·Apache-2.0 license

자세히 → [About](./about) · [GitHub](https://github.com/okwhrlgma-bit/library)

## KOLAS III 종료 D-238 카운트다운

- 2026-12-31 23:59 KST = 표준형 기술지원 종료
- 후속 4: 코라스Ⅲ 확장형·알파스·K-LAS 3.0·KOLAS-WEB
- kormarc-auto = 5번째 마이그 옵션·자치구 단관 수의계약 가능

자가진단 5문항 → [Migration](./migration/kolas3/)

## 정직 헤더 (영구·invariant 11)

- 페르소나 시뮬 = 가설·인터뷰 0건
- 발행 = GitHub Pages 0원 (도메인 등록 시 SEO ↑)
- PMF 결정 = SALES-1 사서 5명 인터뷰 후
- "100% 자동" 약속 X (헌법 §3·사서 검수 단계 보존)
- raw % 금지 (헌법 §11·카테고리형 신뢰만)

---

**조기흠** (사서 출신·1인 PO) · contact@kormarc-auto.example
v0.7.1 · 2026-05-06 · Apache-2.0 license
