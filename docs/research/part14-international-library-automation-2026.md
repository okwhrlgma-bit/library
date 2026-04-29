# Part 14 — 국제 도서관 자동화 사례 (LC·BL·NDL·BIBFRAME·Alma·Koha)

> **출처**: PO 4-30 명령 "더 넓게 조사" Agent 8 (token 한도) 대체 직접 작성
> **목적**: 한국 단독 → 국제 비교·차별화·향후 §33 미국·일본·영어권 진출 정량
> **단일 진실**: KORMARC 2023.12 한국 단독 표준·MARC21·UNIMARC·BIBFRAME 양방향 변환 정합

---

## 1. 미국 LC (Library of Congress) BIBFRAME 2.0

| 항목 | 내용 |
|---|---|
| 표준 | BIBFRAME 2.0 (2016 GA → v2.5 2024) |
| 모델 | Work · Instance · Item (3 추상) |
| 데이터 | RDF/Turtle·LOD (Linked Open Data) |
| 도입 도서관 | LC 자체·Princeton·Stanford·HathiTrust·OCLC·UCLA·U Washington |
| 도구 | Sinopia (BIBFRAME 편집)·MarcEdit·LD4P (Linked Data for Production) |
| 한국 현황 | NLK·서울대·KAIST·연세대 검토 단계 (정식 도입 0관) |
| 우리 정합 | ✅ KORMARC ↔ BIBFRAME 변환 (Part 2 §2 의사코드·conversion/marc21.py 기반) |

→ **★ 한국 BIBFRAME 진입 골든 윈도우** (정식 도입 0관·2026~2027 예상).

---

## 2. 영국 BL (British Library) MARC21 + Linked Data

| 항목 | 내용 |
|---|---|
| 표준 | MARC21 + Linked Data (BL Labs) |
| 자료 | 1,500만+ 레코드 |
| 마이그 | MARC21 → BIBFRAME 진척 (2024~) |
| 도구 | Sinopia·MarcEdit·LD4P |
| 우리 정합 | KORMARC ↔ MARC21 (이미 conversion/marc21.py)·향후 BIBFRAME |

---

## 3. 일본 NDL (National Diet Library) MARC

| 항목 | 내용 |
|---|---|
| 표준 | NDL MARC (Japan MARC)·NACSIS-CAT (학술 통합 목록) |
| 가입 | NACSIS-CAT 1,200관·NDL Search 전국 |
| 자료 | 일본어·한자 (KORMARC와 880 페어 유사) |
| 도구 | CiNii·NDL Search·NACSIS-CAT/ILL |
| 한국 정합 | KORMARC vs Japan MARC 차이 (008 코드·245 지시기호 차이) |
| 우리 진출 | Phase 5 (1년+ 후)·일본어 토크나이저 (Mecab·Sudachi) 추가 |

---

## 4. 유럽 UNIMARC (IFLA)

| 항목 | 내용 |
|---|---|
| 운영 | IFLA (국제도서관협회)·UNIMARC Manual |
| 도입 국가 | 이탈리아·프랑스·포르투갈·러시아·동유럽 |
| 자료 | 다국어 (특히 라틴 알파벳 국가) |
| 우리 정합 | KORMARC ↔ UNIMARC 변환 (향후·Phase 5·우선순위 낮음) |

→ 한국 SaaS 진출은 영어권·일본어권 다음.

---

## 5. 글로벌 ILS·LMS 비교

| 시스템 | 운영 | 점유율 (글로벌) | 가격 (도서관/년) | 우리 차별화 |
|---|---|---:|---:|---|
| Ex Libris **Alma** | 이스라엘 (OCLC 인수) | 1순위 (대학·공공) | $50,000~150,000 | 우리 = $400~3,600/년 (1/100) |
| OCLC **WorldCat** | 미국 | 글로벌 통합 목록 | 회원 기관 | 우리 = 한국 단독 |
| **Koha** | 인도·아프리카·남미 | 오픈소스 (무료) | 0 + 자체 호스팅 | 우리 = 한국 KOLAS 전용·SaaS |
| **Evergreen** | 미국 공공 | 오픈소스 | 0 + 자체 호스팅 | 우리 = 한국·SaaS·자동 |
| **FOLIO** | EBSCO 주도 | 오픈소스 차세대 | 0 + 자체 호스팅 | 우리 = 한국 KORMARC 정합 |
| **Tulip·SOLARS** | 미국 일부·소규모 | 마이너 | 사용자별 | 한국 일부·우리 = SaaS |

→ **우리 차별화** = 한국 KORMARC 2023.12·KOLAS 정합·1/100 가격·SaaS·5분 도입.

---

## 6. 글로벌 사서 자동화 도구

| 도구 | 용도 | 사용자 | 우리 정합 |
|---|---|---|---|
| **MarcEdit** (Terry Reese) | MARC 편집·전 세계 사서 표준 (무료) | 100만+ 추정 | 우리 = 자동 (사용자 학습 0) |
| **Sinopia** (LC + Stanford) | BIBFRAME 편집·LD4P | 학술 도서관 | 우리 = 향후 통합 (Part 2 §2) |
| **OpenRefine** | 데이터 정제·전 세계 | 사서·연구자 | 우리 = 자관 .mrc 일괄 검증 (validate_real_mrc.py) |
| **Catmandu** (Perl) | 도서관 데이터·유럽 | 학술 사서 | 우리 = Python·KORMARC 특화 |
| **OCLC Connexion** | OCLC 목록 편집 | 회원 기관 | 우리 = 한국 단독 |
| **YAZ Toolkit** (Index Data) | Z39.50 클라이언트 | 도서관 IT | 우리 = HTTP API |

---

## 7. 한국 진출 (ADR 0009 §33 미국 동아시아 컬렉션)

### 7-1. Tier 1 — 미국 동아시아 11관

| 도서관 | 한국 자료 (추정) |
|---|---:|
| UC Berkeley | 80,000+ |
| Harvard | 100,000+ |
| Stanford | 50,000+ |
| Yale | 60,000+ |
| Princeton | 40,000+ |
| UCLA | 70,000+ |
| U Chicago | 30,000+ |
| Columbia | 50,000+ |
| Cornell | 25,000+ |
| U Washington | 60,000+ |
| U Hawaii | 40,000+ |
| **합계** | **약 605,000+권** |

→ KORMARC ↔ MARC21 자동 변환 (이미 conversion/marc21.py 정합).

### 7-2. 트리거 충족 조건 (ADR 0009)

- [ ] 자관 PILOT 4주 완료 (5월)
- [ ] 미국 동아시아 1관 LOI (의향서)
- [ ] 영문 영업 자료 (KORMARC vs MARC21·BIBFRAME)
- [ ] Stripe PG (한국 외 결제·ADR 0007 분기)

→ 충족 시 ACTIVATED=True (현재 inactive).

### 7-3. 영업 메시지 (영문)

```
"kormarc-auto: Korean KORMARC ↔ MARC21 automated conversion.
99.82% accuracy verified on 174 .mrc files (3,383 records).
Direct integration with Korean libraries' KOLAS III.

Pricing: $50/month (basic·1,000 records) — 1/100 of Alma.

Ideal for: East Asian Library, Korean Studies, K-Studies."
```

---

## 8. Tier 2 — 일본 NACSIS·NDL

- 일본 학교 12만관 + 공공 3,200관 + 대학 700관
- NDL MARC ↔ KORMARC 변환 (한자·한자음 정합)
- 일본어 토크나이저 (Mecab·Sudachi) 추가
- Phase 5 (1년+) 진출

---

## 9. Tier 3 — 영어권 (호주·캐나다·뉴질랜드·싱가포르·홍콩) 한국 도서관

- 호주 South Australia State Library (한국 자료)
- 캐나다 University of Toronto (Korean Studies)
- 싱가포르 NUS Korean Studies
- 홍콩 University of Hong Kong (한국학)
- KORMARC ↔ MARC21·1/100 가격 영업

---

## 10. ★ 차별화 정리

| 차별화 | 글로벌 평균 | 우리 |
|---|---|---|
| 한국 KORMARC 2023.12 정합 | X (한국 단독) | ★ 100% |
| 가격 | $50,000~150,000/년 (Alma) | $400~3,600/년 (1/100) |
| 도입 시간 | 1~6개월 (Alma·Koha 자체 호스팅) | 5분 (prefix-discover CLI) |
| 사서 친화 | 학습 4시간+ (Alma·Koha) | 5분 cheat sheet (A4 1장) |
| AI 자동 | X (대부분 수동) | ★ Vision·KDC·880·049·M/A/O |
| 한자·일본어·로마자 | 부분 | ★ 880 페어 자동·NLK 「로마자 표기 지침(2021)」 정합 |

---

## Sources

- LC BIBFRAME 2.0 (loc.gov/bibframe)
- BL Labs Linked Data (bl.uk/labs)
- NDL Search·NACSIS-CAT (ndl.go.jp·nii.ac.jp)
- IFLA UNIMARC Manual
- Ex Libris Alma·OCLC WorldCat·Koha·Evergreen·FOLIO 공식
- MarcEdit (terry reese)·Sinopia (LD4P)·OpenRefine·Catmandu
- ADR 0009 (us-east-asian-activation-trigger)
- Part 2 §2 (KORMARC ↔ MARC21·BIBFRAME 변환)
