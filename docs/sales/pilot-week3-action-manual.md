# PILOT 3주차 액션 매뉴얼 — 종합 사서 4명 90분 시연

> **대상**: 자관 「내를건너서 숲으로 도서관」 김기수·박세진·박지수(종합)·신은미 (3순위 ICP)
> **시간**: 5월 셋째주 협의 시간 90분 (자관 폐관 직후 권장)
> **목표**: 종합 워크플로우 (장서점검·월간 보고·연체 통계) 자동화 검증 + 4명 동시 NPS·Q1

---

## 0. 시연 전 5분

| ☐ | 항목 |
|---|---|
| ☐ | 노트북 + Wi-Fi (mobile hotspot 백업) |
| ☐ | `kormarc-auto info` 환경 진단 |
| ☐ | EasyOCR 모델 사전 다운로드 (장서점검 사진 OCR) |
| ☐ | 자관 책장 사진 5장 사전 촬영 (장서점검 데모) |
| ☐ | 자관 4월 운영 통계 (대출·반납·연체) 데이터 준비 |
| ☐ | 4명 동시 사용 테스트 (노트북 1대로 화면 공유) |

---

## 1. 시연 90분 시나리오

### 1-1. 인사 + 1·2주차 결과 공유 (10분)

> "사서님 4분께. 1주차 매크로 사서·2주차 수서 사서 결과는 [요약]입니다. 오늘 3주차는 종합 사서 4분이 일상 처리하시는 장서점검·월간 보고·연체 통계 자동화 90분 검증입니다. 마지막 15분은 4명 통합 NPS·결제 의향 측정."

### 1-2. 장서점검 사진 OCR 자동 (20분)

```powershell
kormarc-auto inspect --image data/shelf_2026-05.jpg --library 내를건너서_숲으로
```

- 책장 사진 → EasyOCR → 자관 DB 대조
- 오배가·미등록·중복 자동 검출
- 신은미·김기수 사서 결정 보조 (사서 책임 영역)

**측정**:
- 100권 점검 시간: 수동 60분 → 자동 ___ 분 (목표 < 5분)
- 정확도: ★ 사서 자기 평가
- 오배가 검출률: ___ /실제

### 1-3. 월간 운영 보고서 PDF 자동 (15분)

```powershell
kormarc-auto report monthly --year 2026 --month 4 --library 내를건너서_숲으로
```

- 신착·대출·반납·연체·이용자 자동 집계
- PDF 출력 (사서 검수 후 관장 보고)
- 자관 통계.xlsx 자동 import 옵션

### 1-4. 연체 통계 집계 (PII 자관 알파스 위임·15분)

```powershell
kormarc-auto report overdue --year 2026 --month 4
```

- 연체 통계 집계만 (회원 PII X)
- PIPA 옵션 C 정합 (회원 정보 = 자관 알파스 위임)
- 박세진·박지수(종합) 실무 검증

### 1-5. 신착 안내문·라벨 PDF (10분)

```powershell
kormarc-auto report announcement --type new_arrivals
kormarc-auto label --input new_arrivals.csv --format avery
```

- 신착 안내문 PDF (자관 양식)
- A4 Avery 라벨 (청구기호·바코드)

### 1-6. 4 페르소나 통합 NPS·Q1 (15분 ★)

**PO 발화**:
> "사서님 4분께. 4 페르소나 (매크로·수서·종합·영상) 모두 시연 완료. 각자 NPS (0~10)와 Q1 결제 의향 (HIGH/MID/LOW/0)을 솔직히 말씀해주세요. 학교운영비 또는 자치구 카드 결제 가능 여부도."

**4명 각자 기록**:
| 사서 | NPS | Q1 | 코멘트 |
|---|---|---|---|
| 김기수 | | | |
| 박세진 | | | |
| 박지수(종합) | | | |
| 신은미 | | | |

### 1-7. KLA 5.31 발표 인용 동의 (5분)

> "5월 31일 KLA 전국도서관대회 발표 신청에 4분 코멘트 인용해도 괜찮을까요? 익명 처리 가능합니다."

→ 동의 사서 명단 별도 기록 (PIPA 정합)

---

## 2. 시연 후 PO 즉시 액션 (1시간)

| ☐ | 액션 |
|---|---|
| ☐ | 4명 각자 `kormarc-auto pilot-collect --persona general --library 내를건너서_숲으로` |
| ☐ | KLA outline S8 (종합 4명) 4명 코멘트 모두 채워넣기 |
| ☐ | `kormarc-auto sales-funnel` 실행 → 종합 사서 funnel 분석 |
| ☐ | `aggregate_interviews.py` 실행 → 페르소나별 통합 보고서 |
| ☐ | 4명 카카오톡 감사 + 4주차 (통합·KLA) 일정 확정 |
| ☐ | 영상 사서 김신학 명시 제외 확인 (정직 영업·video persona X) |

---

## 3. 위험 시나리오

| 위험 | 회피 |
|---|---|
| EasyOCR 모델 다운로드 실패 | 사전 다운로드 (`easyocr.Reader(['ko', 'en'])` 1회) |
| 4명 동시 시연 시간 부족 | 90분 → 60분 (1-2 + 1-3 + 1-6만) |
| 일부 사서 부정 반응 | 정직 받기·"어떤 부분이 안 맞으신지" |
| KLA 인용 동의 X | 익명 처리 옵션 명시 |

---

## 4. 다음 주차 미리보기

- **4주차** (5월 넷째주·5/25~30): 4 페르소나 통합 NPS·결제 의향 종합 + KLA 5.31 발표 슬라이드 사서 8명 검수 + 5/31 KLA 발표 신청 마감

---

## Sources

- `docs/sales/pilot-week1-action-manual.md`·`pilot-week2-action-manual.md`
- `docs/sales/pilot-package-2026-04-29.md` §1.4 (종합 4명 90분 시나리오)
- `scripts/pilot_collect.py --persona general`
- `kormarc-auto inspect`·`report` CLI
