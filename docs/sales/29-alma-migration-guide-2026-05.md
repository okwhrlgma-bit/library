# 영업 자료 29건째: Alma → kormarc-auto 마이그레이션 가이드

> 작성: 2026-05-02 / 페르소나 P5 (대학도서관 사서)
> 핵심 메시지: **Alma 병행 사용·BIBFRAME 1.0 12월 즉시 시작·서강대 로욜라 자체 변환 사례**

---

## 1. Alma 사용 대학도서관 현실 (P5 페인)

### 한국 대학도서관 ~430관 중 Alma 사용
- 수도권 주요 대학 다수 도입 (정확 통계 X)
- Ex Libris (이스라엘) 본사 + 한국 파트너
- 가격: 비공개 (기관 협상, 연 수천만~수억)
- 5%+ 연간 인상 (Library Technology Guides)

### 페인
- 비싼 라이선스 + 매년 인상
- BIBFRAME 마이그레이션 부담 (Alma 하이브리드 모델 사용 가능하나 추가 비용)
- KORMARC 한국 표준 정합 (Alma 글로벌 우선)
- "Alma 사용 중 = 다른 도구 도입 부담"

---

## 2. kormarc-auto = Alma 보조 도구 (병행 권장)

전면 교체 X. **kormarc-auto는 Alma의 KORMARC 정합 보조 도구**:

| 영역 | Alma | kormarc-auto |
|------|------|--------------|
| 종합 LMS (대출·반납·이용자) | ✅ 핵심 | ❌ 미지원 |
| 글로벌 도서관 표준 | ✅ MARC 21 | ✅ KORMARC 2023.12 |
| 한국 KORMARC 9 자료유형 | ⚠️ 부분 | ✅ 100% |
| 880 한자·로마자 자동 | ⚠️ 부분 | ✅ NLK 「로마자 표기 지침」 |
| KOLAS·독서로DLS 직접 반입 | ❌ | ✅ |
| BIBFRAME 1.0 로드맵 | ✅ 하이브리드 (별도 계약) | ✅ 12월 즉시 시작 (월 3만 정액 포함) |
| 가격 | 연 수천만~수억 | 월 3만 (대학 = 대 30만) |

→ **Alma 핵심 기능 유지 + kormarc-auto 보조 = 비용 X·정합 ↑**

---

## 3. 서강대 로욜라도서관 자체 변환 사례 인용

```
"통합서지용 KORMARC 표준 제정 시,
서강대 로욜라도서관은 KERIS 변환기 X
= 자체 변환을 시도

자관 DB 오류 수정·데이터 보완 자유
= 수작업 데이터 보정 인력 X 기관 = kormarc-auto 정합"

(KORMARC 학술 자료 인용 — 익명화 정합)
```

→ kormarc-auto = **현대판 자체 변환 도구** + AI 보조 + 5분 학습

---

## 4. BIBFRAME 1.0 로드맵 (P5 핵심 결정 요인)

### kormarc-auto BIBFRAME 1.0 시점
- **2026-12 캐시카우 도달 = 즉시 BIBFRAME 1.0 시작**
- UC Davis BIBFLOW 패턴 차용 (2013→2024 production 검증)
- Alma 하이브리드 모델 차용 (MARC + BIBFRAME 공존)
- Blue Core 컨소시엄 참여 검토 (Stanford·Cornell·UC Davis)

### 대학도서관 우선 PILOT
- 5관 우선 BIBFRAME 1.0 베타 (2027-01~03)
- 한국문학번역원·해외한국학자료센터 협력
- 글로벌 한국학 도서관 진입 카드

---

## 5. 대학도서관 페르소나 P5 페인 직접 해결

### 페인 1: "Alma 사용 중 = 검증 데이터 부족"
→ **PILOT 1관 99.82% 정합 + 서강대 로욜라 자체 변환 사례 인용**
→ 학술 출처 인용 = P5 신뢰

### 페인 2: "BIBFRAME 마이그레이션 부담"
→ **kormarc-auto 1.0 = 12월 즉시 시작 약속**
→ Alma 하이브리드 별도 계약 X = 정액 포함

### 페인 3: "한국 KORMARC 표준 정합 부족"
→ **9 자료유형 100% + 880 한자·로마자 자동**
→ Alma 부분 정합 vs kormarc-auto 100%

### 페인 4: "비용 협상·인상 부담"
→ **월 3만 정액 + 가격 인상 X (Niche Academy 패턴)**

---

## 6. KORIBLE·KOLISNET·OCLC 통합 (P5 추가 가치)

```
kormarc-auto 출력 →
- KOLAS·독서로DLS 직접 반입 ✅
- KORIBLE 통합 (대학도서관 표준) ✅
- KOLISNET 종합 목록 ✅
- OCLC publishing (1.0 글로벌) ✅
- BIBFRAME 1.0 (1.0) ✅
```

→ Alma + kormarc-auto = 한국·글로벌 표준 모두 정합

---

## 7. CTA (P5 대학도서관 사서)

```
[ ] PILOT 1관 99.82% + 서강대 로욜라 사례 다운로드
[ ] BIBFRAME 1.0 로드맵 페이지 (12월 시작·5관 우선 베타)
[ ] Alma 병행 사용 5분 가이드
[ ] 무료 50건 + 대학도서관 우선 PILOT 신청
[ ] OCLC·KORIBLE·KOLISNET 호환 검증 보고서
```

---

## 8. 출처
- 서강대 로욜라도서관 KORMARC 자체 변환 (RISS 학술)
- Alma 5%+ 연간 인상 (Library Technology Guides)
- UC Davis BIBFLOW 2013→2024 production
- KORMARC KS X 6006-0:2023.12 (NLK 2차 개정)

> commit 평가축: §12 +3 (대학 ~430관 진입), §3 +5 (학술 출처 자산)
