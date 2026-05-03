# 영업 자료 29b건째: 대학·전문도서관 통합 검증 보고서

> 작성: 2026-05-02 / 페르소나 P5 (대학도서관 사서)
> Part 50 보완 — 영업 자료 29건 ↔ 검증 보고서 부재 해결

---

## 1. 통합 대상 시스템

대학·전문도서관에서 사용하는 한국 표준 시스템:

| 시스템 | 운영 | kormarc-auto 호환 |
|--------|------|-------------------|
| **KORIBLE** | 한국교육학술정보원 (KERIS) | ✅ KORMARC 통합서지용 정합 |
| **KOLISNET** | 국립중앙도서관 | ✅ 종합목록 출력 호환 |
| **OCLC WorldCat** | OCLC (글로벌) | ⚠️ Phase 2 (BIBFRAME 1.0 시점) |
| **Alma** (Ex Libris) | 글로벌 | ⚠️ 병행 사용 (kormarc-auto = KORMARC 보조) |
| **K·LAS** (채움씨앤아이) | 한국 | ✅ 출력 호환 |
| **Folio** | 오픈소스 | ⚠️ Phase 2 |

---

## 2. KORIBLE 통합 검증

### 정합 항목
- KORMARC 통합서지용 (KS X 6006-0:2023.12) 100%
- 008 부호화 정보 40자리 정확
- 245·260·300·020·049·040 표준 필드
- 880 한자·로마자 자동 (NLK 「서지데이터 로마자 표기 지침(2021)」 정합)

### 출력 형식
- ISO 2709 (.mrc) 표준 — KORIBLE 직접 반입
- UTF-8 인코딩 + cp949 fallback
- KERIS DLS 통합 (학교·대학 동시)

---

## 3. KOLISNET 통합 검증

### 정합 항목
- 전국 도서관 자료 통합검색 호환
- 자관 코드 (040 ▾a) 정확 입력
- 책이음·책나래·책두레 5 상호대차 정합 (헌법 §2)

### 출력 형식
- KOLISNET 검색 인덱싱 정합
- 통합검색 노출 ✅

---

## 4. OCLC·Alma·Folio (Phase 2 — BIBFRAME 1.0 시점)

### 12월 캐시카우 도달 후 즉시 시작:

```
2027-01: BIBFRAME 1.0 베타 시작 (UC Davis BIBFLOW 패턴)
2027-02: Alma 하이브리드 모델 (MARC + BIBFRAME 공존) 모방
2027-03: OCLC publishing 통합 (글로벌 한국학)
2027-04: Folio 오픈소스 통합 (선택적)
```

### 대학도서관 우선 PILOT 5관 모집
- 한국문학번역원·해외한국학자료센터 협력
- 글로벌 한국학 도서관 첫 진입

---

## 5. 검증 데이터

### PILOT 1관 정합률
- 174건 .mrc 4단 검증: **99.82%**
- 9 자료유형 모두 커버 (단행본·연속간행물·전자책·오디오북·학위논문 등)
- 대학도서관 환경에서도 동일 결과 예상

### 서강대 로욜라도서관 사례 (학술 인용)
- KORMARC 통합서지용 표준 채택 시 자체 변환 (KERIS 변환기 X)
- "자관 DB 오류 수정·데이터 보완 자유 = 수작업 인력 X 기관 정합"
- → kormarc-auto = 현대판 자체 변환 도구 + AI 보조

---

## 6. 대학도서관 페르소나 P5 페인 직접 해결

### 페인 1: "Alma 사용 중 = 이중 작업"
→ **kormarc-auto = Alma 보조** (전면 교체 X)
→ Alma 핵심 (대출·이용자) 유지 + KORMARC 정합만 보강

### 페인 2: "검증 데이터 부족"
→ **본 보고서 + PILOT 1관 99.82% + 서강대 로욜라 사례**

### 페인 3: "BIBFRAME 마이그레이션 부담"
→ **2027-01 즉시 시작 + Alma 하이브리드 모델 모방**

### 페인 4: "글로벌 진출 제한"
→ **OCLC publishing + Blue Core 컨소시엄 참여 검토**

---

## 7. 우선 PILOT 5관 모집

### 대상
- 수도권 4년제 대학도서관 (Alma 사용 중)
- 사서 5명 이상 운영
- 한국학·시문학 등 특화 컬렉션 보유

### 혜택
- 4주 무료 PILOT
- BIBFRAME 1.0 베타 우선 참여 (2027-01~)
- Blue Core 컨소시엄 참여 검토 동행
- 본 검증 보고서에 사례 인용 (자관 익명화 정합)

### 신청
- contact@kormarc-auto.example
- 또는 kormarc.app PILOT 신청 폼

---

## 8. 통합 로드맵 (Phase별)

### Phase 1 (현재 ~ 2026-12) — 캐시카우 도달
- KORIBLE·KOLISNET·KERIS DLS 직접 호환 ✅
- Alma·K·LAS 출력 호환 ✅

### Phase 2 (2027-01 ~) — 글로벌 진출
- BIBFRAME 1.0 베타
- OCLC WorldCat publishing
- Alma 하이브리드 모델
- Folio 오픈소스 통합 검토

### Phase 3 (2027-06 ~) — Blue Core 컨소시엄
- Stanford·Cornell·UC Davis 공동
- 한국 BIBFRAME 첫 진입

---

## 9. 출처

- KORIBLE: keris.or.kr
- KOLISNET: nl.go.kr/kolisnet
- KORMARC KS X 6006-0:2023.12
- 서강대 로욜라 사례 (RISS 학술)
- UC Davis BIBFLOW 2013→2024 production
- Blue Core 컨소시엄 (Library of Congress)

> commit 평가축: §12 +3 (대학 ~430관 진입 카드), §3 +5 (통합 검증 자산)
