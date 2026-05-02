# PILOT 4주차 통합 액션 매뉴얼 — KLA 5.31 마감 직전

> **대상**: 자관 사서 8명 통합 + KLA 발표 슬라이드 사서 검수
> **시간**: 5/25 ~ 5/30 (KLA 신청 5.31 마감 직전 1주)
> **목표**: 4 페르소나 통합 NPS·결제 의향 + KLA 슬라이드 100% 채움 + 5/31 발표 신청

---

## 0. 5/25 월요일 — 4 페르소나 통합 분석 (60분)

### 자료 수집

```powershell
cd kormarc-auto
git pull origin main   # cloud routine 자동 commit 받기
.\.venv\Scripts\Activate.ps1

# 1주~3주차 결과 통합
.\.venv\Scripts\python.exe scripts\aggregate_interviews.py
.\.venv\Scripts\python.exe scripts\sales_funnel.py --json reports/funnel_2026-05.json
```

확인:
- ☐ 4 페르소나별 NPS 평균 (목표 ≥7)
- ☐ Q1 결제 의향 분포 (목표 ≥3 페르소나 HIGH/MID)
- ☐ 시간 절감 평균 (목표 ≥75%)
- ☐ KLA 인용 가능 사서 수 (`consent_kla_quote=true`)

### KLA 슬라이드 채움 (60분)

`docs/sales/kla-2026-presentation-outline.md` 열어서 ★ 표시 빈칸 모두 채움:

| 슬라이드 | 채움 |
|---|---|
| S5 | 핵심 정량 표 (PILOT 1주 측정값·NPS 평균·결제 의향·자관 일 39h) |
| S6 | 사서 E 코멘트 + 책단비 시간 단축 |
| S7 | 사서 A 코멘트 + 정보나루 + KDC 균형 |
| S8 | 사서 B·사서 C·사서 D 코멘트 (3건) |
| S9 | 4주 통합 NPS·결제 의향 |
| S15 | 발표 직후 PILOT 신청 부스 안내 |

---

## 1. 5/26 화요일 — 자관 사서 8명 검수 회의 (30분)

> "사서님 8분께. 5/31 KLA 발표 슬라이드 1차 초안입니다. 4 페르소나별 코멘트와 99.82% 정합 정량을 인용했습니다. 본인 코멘트가 익명·실명 중 어떻게 처리되길 원하시는지·수정 사항 있으신지 확인 부탁드립니다."

각 사서별 동의 형식:
- ☐ 사서 B (실명/익명·수정 사항)
- ☐ 사서 C (실명/익명·수정 사항)
- ☐ 사서 A (실명/익명·수정 사항)
- ☐ 사서 D (실명/익명·수정 사항)
- ☐ 사서 E (실명/익명·수정 사항·매크로 사서 영업 1순위)
- ☐ 김신학 (영상 사서·명시 제외 동의)
- ☐ 나머지 2명 (실명/익명·수정 사항)

---

## 2. 5/27~28 — 슬라이드 PDF 변환 + 명함·부스 준비

| ☐ | 항목 |
|---|---|
| ☐ | KLA 슬라이드 → Marp 또는 PowerPoint PDF 변환 |
| ☐ | 시연 5분 데모 영상 사전 녹화 (장애 대비) |
| ☐ | 명함 100매 인쇄 (PO·okwhrlgma@gmail.com·카카오 채널 「kormarc-auto」·GitHub) |
| ☐ | KLA 부스 신청 (PILOT 신청 직접 받기) |
| ☐ | 카카오 채널 KLA 발표 알림 콘텐츠 1건 (5/30 발행 예정) |

---

## 3. 5/29 — 발표 리허설 + 자관 사서 1~2명 동석 약속

| ☐ | 항목 |
|---|---|
| ☐ | 30분 발표 리허설 (PO 본인) |
| ☐ | 자관 사서 1~2명 KLA 동석 동의 (강력·강사 신뢰성 ↑) |
| ☐ | Q&A 10건 (`docs/sales/pilot-package-2026-04-29.md` §4) 답변 다시 점검 |

---

## 4. 5/30 — 최종 검수 + 카카오 채널 발행

| ☐ | 항목 |
|---|---|
| ☐ | 슬라이드 최종 (S6~S9·S15·S5 정량 모두 100%) |
| ☐ | KLA 발표 신청서 양식 작성·첨부 PDF |
| ☐ | 카카오 채널 「v0.4.37 + KLA 5.31 발표 안내」 콘텐츠 발행 |
| ☐ | 도서관저널 기고문 (`docs/sales/library-journal-article-2026-05.md`) 발송 메일 |

---

## 5. ★ 5/31 — KLA 전국도서관대회 발표 신청 마감 ★

| 시간 | 액션 |
|---|---|
| 09:00 | KLA 전국대회 도착·부스 셋업 |
| 발표 시간 | 30분 발표 (자관 사서 1~2명 동석) |
| Q&A | 15분 답변 (Q&A 10건 답변 정합) |
| 부스 | PILOT 신청 직접 받기 (사서 카카오 채널 가입 안내) |
| 23:59 | KLA 발표 신청 마감 (★ 가장 임박) |

---

## 6. 6월 1주 — KLA 후속 영업 가속

| ☐ | 액션 |
|---|---|
| ☐ | KLA 부스에서 받은 PILOT 신청 사서 즉시 회신 (24h SLA) |
| ☐ | 학교·작은·공공·대학·전문 PILOT 8~10관 모집 메일 발송 (250+125통) |
| ☐ | GitHub Release v0.5.0 (PILOT 4주 결과 + KLA 발표) |
| ☐ | 사서교육원·KSLA 강의 일정 확정 |

---

## 7. 4주 통합 KPI 측정 (PO 5/30 종합)

| 지표 | 목표 | 실측 |
|---|---|---|
| 4 페르소나 NPS 평균 | ≥7 | |
| 결제 의향 HIGH | ≥3 페르소나 | |
| 시간 절감 평균 | ≥75% | |
| KLA 인용 가능 사서 | ≥6/8 | |
| KLA 발표 슬라이드 100% | ✓ | |
| 5/31 마감 신청 | ✓ | |
| 자관 사서 1~2명 동석 | ✓ | |

→ 4주 통합 KPI = `docs/sales/kla-2026-presentation-outline.md` 데이터 기반

---

## 8. PILOT 4주 종료 후 (6월 中)

- 학교·작은·공공·대학·전문 PILOT 5관 → 8~10관 모집 진행
- 사서교육원 강의 (60분 또는 30분) 6~7월 일정
- 도서관저널 7월호 기고 (5/25 발송 → 6/15 회신)
- GitHub Release v0.5.0 + 정식 결제 자동 (사업자 등록 후 포트원)
- Phase 1 (책단비 hwp 자동) 정식 v1.0 release 6월 中

---

## Sources

- `docs/sales/pilot-week1·2·3-action-manual.md` (1·2·3주차 결과 누적)
- `docs/sales/kla-2026-presentation-outline.md` (★ 5/31 슬라이드)
- `docs/sales/library-journal-article-2026-05.md` (도서관저널 기고)
- `docs/sales/saseo-academy-proposal-2026-05.md` (사서교육원 강의)
- `docs/sales/outreach-small-school-libraries-2026-05.md` + `outreach-university-special-libraries-2026-05.md` (영업 메일 250+125통)
- `scripts/aggregate_interviews.py`·`sales_funnel.py` (4 페르소나 통합 데이터)
