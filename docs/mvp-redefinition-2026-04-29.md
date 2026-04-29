# MVP 재정립 + 6 Phase 로드맵 (2026-04-29)

> **PO 명령** (CHAPTER 9): "MVP는 최소 기능 제품이지 모든 기능의 미완성 버전이 아니다. docs 작성 중단·코드 우선."
> **단일 진실**: `자료/po_comprehensive_report_2026_04_29_evening.md` CHAPTER 9.

---

## 0. MVP 정의 (지금까지 없었던 명확한 정의) ★

```
진짜 MVP = 단 한 가지만 완벽:
ISBN 입력 → KORMARC .mrc 출력
- 웹 브라우저 접속
- ISBN 수동/스캔
- NL Korea API 호출
- 4단 검증
- .mrc 다운로드

이것만. 연체·수서·회원증·통계 X.
```

### MVP 완성 기준 (4 KPI)

| KPI | 목표 |
|---|---|
| 사서 1명 실제 사용 가능 | ✅ |
| **.mrc → KOLAS 실제 반입 ✅** | ★ 1순위 |
| 에러율 | < 5% |
| 응답 시간 | < 5초 |

→ 자관 PILOT 1주 첫날 **자관 KOLAS에 우리 .mrc 실제 반입 테스트** 필수.

---

## 1. 6 Phase 로드맵

### Phase 0 (지금~2주) — MVP

```
ISBN → KORMARC .mrc 단건 처리
- 웹 브라우저
- NL Korea API 폴백 (1순위)
- 4단 검증 (M·A·O 분기)
- .mrc 다운로드
- KOLAS 실제 반입 검증 ★
```

**Phase 0 완성 = 자관 PILOT 시작 가능**.

### Phase 1 (2~4주) — 책단비 + 자관 PILOT

| 기능 | ADR |
|---|---|
| F12 엑셀 → 책단비 hwp 자동 (만료·반납·제공·지하철) | 0021 |
| python-hwpx 의존성 + 자관 토큰 |
| 자관 PILOT 4주 시작 (5월 첫주) |
| KLA 5.31 발표 슬라이드 |

### Phase 2 (1~2개월) — 일괄 처리

| 기능 | ADR |
|---|---|
| F12 엑셀 일괄 import | 0058 |
| Folder Watcher (KOLAS Downloads 자동 감지) | 0016 |
| watchdog 의존성 |

### Phase 3 (2~3개월) — 사용자 관리 (PIPA 옵션 C)

| 기능 | ADR |
|---|---|
| 회원증 양식 mail merge (PII X·Formtec 정합) | 0115 |
| 연체 통계 집계 (PII X·집계만) | 0114 |
| 알림 메시지 템플릿 (발송 X·자관 위임) | 0117 |
| 희망 도서 통계 | 0116 |

→ PIPA 옵션 C: 회원 PII = 자관 알파스 위임. 우리 = 양식·통계·템플릿만.

### Phase 4 (3~6개월) — 수서 지원

| 기능 | ADR |
|---|---|
| 수서 추천 대시보드 (정보나루 인기 대출) | 0072 |
| 중복 소장 알리미 (도서관 정보나루 libBookExist) | 0072 |
| KOLIS-NET 5종 API 통합 폴백 |

### Phase 5 (6개월+) — 통계·관장 ROI

| 기능 | ADR |
|---|---|
| 관장 ROI 대시보드 (시간 절감 카운터) | 0099 |
| 연간 통계 자동 (문체부 제출용) | 0067 |
| 장서 점검 목록 자동 (CHAPTER 1-3) |
| 폐기 후보 자동 추출 (CHAPTER 1-4) |

---

## 2. 5월 1~31일 PHASE 0·1 정밀 일정

### 5월 1주차 — Phase 0 MVP 완성

```
□ MVP 단일 기능 안정화 (ISBN → .mrc)
□ NL Korea API 인증키 신청 (PO 직접·1~3일)
□ 4단 검증 + M/A/O 분기
□ Streamlit UI 단순화 (ISBN 입력 + .mrc 다운로드만)
□ 자관 .mrc 174건 전수 검증 정합률 측정
```

### 5월 2주차 — Phase 1 책단비 + PILOT 1주

```
□ chaekdanbi/auto_label_generator.py 구현 (python-hwpx)
□ 자관 PILOT 1주 (★ 매크로 사서 = 조기흠 페르소나)
   - 책단비 hwp 4 양식 자동
   - 자관 .mrc → 실제 KOLAS 반입 검증 ★
   - Q1 결제 의향 측정
```

### 5월 3주차 — Phase 1 + PILOT 2주

```
□ inventory/kolas_f12_importer.py 구현 (9 컬럼)
□ 자관 PILOT 2주 (수서 사서 = 박지수 수서)
□ KLA 발표 슬라이드 1차 초안
```

### 5월 4주차 — PILOT 3주

```
□ 자관 PILOT 3주 (종합 사서 4명)
□ KLA 발표 슬라이드 PILOT 1·2·3주 결과 통합
```

### 5월 5주차 — PILOT 4주 + KLA 5.31 마감

```
□ PILOT 4주 (통합 + 영상 X 명시 + PILOT 후 NPS)
□ KLA 전국도서관대회 발표 신청 ★ (5.31 마감)
□ 사서교육원 강의 제안서
```

---

## 3. PO 즉시 행동 (오늘 30분)

| # | 액션 | URL |
|---|---|---|
| 1 | 알라딘 TTBKey 신청 | aladin.co.kr/ttb |
| 2 | 카카오 개발자 API Key | developers.kakao.com |
| 3 | 도서관 정보나루 가입 | data4library.kr |
| 4 | NL Korea 서지 API 신청 | librarian.nl.go.kr |

→ 오늘 30분 = MVP Phase 0 진입 가능 (4 API 모두 무료 즉시 발급).

### 이번 주 (5월 1주)

| # | 액션 |
|---|---|
| 1 | 사업자 등록 (홈택스·5분·무료) |
| 2 | KLA 전국도서관대회 발표 신청 (5.31 마감) |
| 3 | 자관 (내를건너서 숲으로 도서관) 연락 → PILOT 제안 |
| 4 | 북이즈·제이넷 체험판 가입 (경쟁사 직접 사용) |

---

## 4. Claude Code 즉시 명령 (PO 보고서 CHAPTER 10)

### 지금 당장 구현 시작 3건

1. **chaekdanbi/auto_label_generator.py**
   - python-hwpx 의존성 (PO ADR 0021 결정 후)
   - KOLAS F12 엑셀 read
   - 책단비 4 양식 hwp 자동 생성
   - 자관 토큰 config.yaml 연동
   - 완성 후 실제 F12 엑셀로 테스트

2. **inventory/kolas_f12_importer.py**
   - xlsx 9 컬럼 자동 매핑
   - EQ/CQ prefix 인식
   - fuzzy 컬럼명 매처 (rapidfuzz)

3. **api/aggregator.py**
   - NL Korea 서지 API 1순위
   - 알라딘 표지 이미지 폴백
   - timeout=10·diskcache TTL=7일

### 검증

3개 완성 후 자관 .mrc 174건 전수 검증 테스트.

→ **docs 작성 중단·코드 우선** (PO 보고서 CHAPTER 10 명령).

---

## 5. 이전 ADR 91 → 138+ 누적 매핑

| Phase | ADR |
|---|---|
| Phase 0 MVP | 0044·0045 (KORMARC 2023.12·M/A/O 분기) |
| Phase 1 책단비 | 0021·0022 |
| Phase 2 일괄 | 0016·0017·0058 |
| Phase 3 사용자 관리 (옵션 C) | 0113~0118 |
| Phase 4 수서 | 0072·0073 |
| Phase 5 통계·ROI | 0067·0081·0099 |
| 11 CHAPTER 신규 | 0119~0140 (장서점검·폐기·기증·문화·독서교육·납본·지역·이동·하드웨어·전자책·독서통장·교육·공공데이터·AI 추천·손상 감지·예산 ROI) |

→ ADR 누적 91 → **140+ (지속 갱신)**.

---

## 6. 영업 메시지 (MVP 재정립 후)

### Phase 0 MVP (5월 첫주)

> "ISBN 1번 입력 → KORMARC .mrc 5초. 자관 KOLAS 실제 반입 검증 완료. 사서 권당 8~15분 → 2분 (87% 단축)."

### Phase 1 책단비 (5월 末)

> "자관 5년 책단비 1,328건 자동화 검증 완료. 자관 PILOT 4주 결과 → KLA 5.31 발표."

---

## 7. Sources

- 자료/po_comprehensive_report_2026_04_29_evening.md (CHAPTER 9·10)
- 자료/po_strategy_report·po_api_report·po_missing_analysis·po_missing_25·po_pipa_decision (5 보고서)
- 자관 D 드라이브 100% 흡수
- ADR 누적 138+
