# 영업 자료 INDEX (2026-04-30)

> **목적**: PO가 5초 안에 필요한 영업 자료 찾기. 5월 KLA 5.31·자관 PILOT 4주·사서교육원·도서관저널·작은학교 영업 모두 정합.
> **단일 진실**: 자관 .mrc 174 파일·3,383 레코드 → 99.82% 정합 ★

---

## 우선순위 — 5월 액션 순

### ★★★ 1순위 — 자관 PILOT 4주 (5월 첫주~5.31)

| 자료 | 사용 시점 | 분량 |
|---|---|---|
| **[pilot-week1-action-manual.md](pilot-week1-action-manual.md)** | 5/1주 월요일 18:00 (조기흠 30분 시연) | 165 lines |
| **[pilot-package-2026-04-29.md](pilot-package-2026-04-29.md)** | 자관 4주 시나리오 + 4 페르소나 메일 + Q&A 10건 | 257 lines |
| **[librarian-5min-cheatsheet.md](librarian-5min-cheatsheet.md)** | PILOT 시연 후 사서에게 인쇄 (A4 1장) | 110 lines |

### ★★★ 2순위 — KLA 5.31 발표 (마감 임박 ★)

| 자료 | 사용 시점 |
|---|---|
| **[kla-2026-presentation-outline.md](kla-2026-presentation-outline.md)** | 5/30 슬라이드 채움 + 5/31 발표 |

### ★★ 3순위 — 6~7월 영업 채널 확장

| 자료 | 사용 시점 |
|---|---|
| **[saseo-academy-proposal-2026-05.md](saseo-academy-proposal-2026-05.md)** | 5월 末 사서교육원·KSLA 메일 발송 |
| **[library-journal-article-2026-05.md](library-journal-article-2026-05.md)** | 5/25 도서관저널 + 6월 블로그·카카오 |
| **[outreach-small-school-libraries-2026-05.md](outreach-small-school-libraries-2026-05.md)** | 5/31 ~ 6월 작은·학교·KOLAS 마이그 메일 250통 |
| **[kakao-channel-content-2026-04-29.md](kakao-channel-content-2026-04-29.md)** | 5월 첫주 카카오 채널 개설 + 발행 |

---

## 영업 정량 ★ (모든 자료 공통 인용)

| 정량 | 출처 | 활용 |
|---|---|---|
| **자관 .mrc 174 파일·3,383 레코드 99.82% 정합** | `scripts/validate_real_mrc.py` (4-29) | KLA·메일·블로그·README 첫 화면 |
| 자관 일 39h 절감 (사서 5명 풀타임 가치) | Part 3 시뮬 | 영업 메일 후크 |
| 권당 8분 → 2분 (75% 단축) | Phase 0 MVP 측정 | ICP 매크로 사서 후크 |
| 자관 5년 1,328건 책단비 | 자관 D 드라이브 실측 | 책단비 영업 후크 |
| 049 prefix EQ·CQ·WQ 자동 발견 | 4-29 측정 | 다른 자관 5분 도입 |

---

## 4 페르소나 매트릭스

| 페르소나 | 비중 | 권장 플랜 | 영업 자료 |
|---|---|---|---|
| ★ Excel 매크로 사서 (조기흠) | 1순위·전국 1,500~2,500명 | 월 5만원 | pilot-week1·pilot-package §2.1 |
| 수서 사서 (박지수) | 2순위·KOLAS 1,271관 | 월 3~15만원 | pilot-package §2.2 |
| 종합 사서 (4명) | 3순위·학교 12,200관 86% 자원봉사 | 월 3~5만원 | pilot-package §2.3·outreach-small-school §2 |
| 영상 편집 사서 | 영업 X | - | pilot-package §2.4 |

---

## 5월 정밀 일정 (KLA 5.31 마감)

| 주차 | 날짜 | 액션 | 자료 |
|---|---|---|---|
| 5/1주 | 5/4 ~ 5/10 | Phase 0 MVP 안정화 + 자관 사서 8명 PILOT 4주 회의 | pilot-week1 |
| 5/2주 | 5/11 ~ 5/17 | PILOT 1주 (조기흠 매크로 사서·30분 시연) | pilot-week1·cheatsheet |
| 5/3주 | 5/18 ~ 5/24 | PILOT 2주 (책단비 hwp 자동 60분) | pilot-package §1.2 |
| 5/4주 | 5/25 ~ 5/30 | PILOT 3주 (수서 박지수 60분) + KLA 슬라이드 채움 + 도서관저널 메일 | kla outline·library-journal |
| 5/5주 | 5/31 | ★ KLA 전국도서관대회 발표 신청 마감 + 부스 PILOT 모집 | kla outline |
| 6/1주 | 6/1 ~ 6/7 | 학교·작은·공공 PILOT 5관 모집 메일 250통 | outreach-small-school |

---

## PO 즉시 액션 (오늘 30분)

| ☐ | 액션 | 자료 |
|---|---|---|
| ☐ | GitHub repo push (`git push -u origin main`) | (cloud routine 활성) |
| ☐ | 카카오 채널 「kormarc-auto」 개설 (5분) | kakao-channel-content §0 |
| ☐ | KLA 5.31 발표 신청 양식 다운로드 | kla outline §15 |
| ☐ | 자관 사서 8명 PILOT 4주 안내 회의 일정 잡기 | pilot-package §3 |
| ☐ | 4 페르소나 메일 1차 PO 검수·맞춤 수정 | pilot-package §2 |

---

## 측정 도구 (영업 funnel)

| 도구 | 명령 |
|---|---|
| **사서 인터뷰 누적 분석** | `python scripts/aggregate_interviews.py` |
| **PILOT 시연 결과 1줄 수집** | `python scripts/pilot_collect.py --persona macro` |
| **영업 funnel (가입→결제)** | `python scripts/sales_funnel.py` |
| **자관 .mrc 정합 검증** | `python scripts/validate_real_mrc.py` |
| **다른 자관 049 prefix 자동** | `kormarc-auto prefix-discover "D:\<자관>\수서"` |
| **관리자 대시보드 (모든 KPI 통합)** | `GET /admin/stats` (X-API-Key 관리자) |

---

## Sources

- 자관 「내를건너서 숲으로 도서관」 4주 PILOT (5월 진행)
- `docs/research/part3-librarian-workflows.md` (4 페르소나 일일 시간 분포)
- `docs/research/part4-uiux-seo-marketing-deployment.md` (영업 채널·SEO·배포)
- `docs/research/part5-tools-and-automation.md` (외부 도구 12종)
- `CLAUDE.md §0 + §12` (헌법 평가축)
- `.claude/rules/business-impact-axes.md` (사업 5질문 셀프 오딧)
