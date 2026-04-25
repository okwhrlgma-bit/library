# 문헌정보학·서지학·분류학·목록학 참조

> 학술 인용·정부 지원사업·논문 작성 시 활용. 본문은 저작권 보호로 직접 제공 불가 → 출처 명시.

---

## 1. 문헌정보학 (Library and Information Science)

### 1.1 한국 표준 교과서 (대학 학부)

| 책 | 저자 | 출판사 | 분야 |
|---|---|---|---|
| 자료조직론 | 김자후·김효정 등 | 한국도서관협회 | 분류·목록 통합 |
| 정보조직론 | 최석두·정연경 | 한울아카데미 | 분류·메타데이터 |
| 도서관경영론 | 정동열 | 한국도서관협회 | 운영·관리 |
| 도서관·정보학개론 | 정필모·오경묵 | 한울아카데미 | 입문 |
| 정보검색론 | 정영미 | 한국도서관협회 | 검색·DB |
| 참고봉사론 | 김달식 | 한국도서관협회 | 정보봉사 |

### 1.2 주제별 핵심 영역

- **정보조직 (Information Organization)**: 분류·목록·주제명·메타데이터
- **정보봉사 (Reference Services)**: 참고봉사·이용자 교육·정보활용교육
- **도서관 경영 (Library Management)**: 예산·인사·평가
- **정보검색 (Information Retrieval)**: 검색알고리즘·시스템
- **이용자 연구 (User Studies)**: 정보행태·정보요구

---

## 2. 서지학 (Bibliography)

### 2.1 분야
- **분석서지학**: 책 자체의 물리적 특성 (제본·종이·인쇄)
- **기술서지학**: 서지 기술 표준 (KCR·RDA·AACR2)
- **체계서지학**: 분야별·주제별 서지 목록
- **역사서지학**: 출판·간행의 역사

### 2.2 핵심 개념 표준

| 표준 | 풀 이름 | 영역 |
|---|---|---|
| **ISBD** | International Standard Bibliographic Description | 국제 서지기술 |
| **KCR4** | 한국목록규칙 4판 | 한국 표준 (KCR5 초안 2024.5) |
| **RDA** | Resource Description and Access | 국제 신표준 |
| **AACR2** | Anglo-American Cataloguing Rules | 구 영미권 |
| **FRBR** | Functional Requirements for Bibliographic Records | 개체-관계 모델 |
| **FRAD** | Functional Requirements for Authority Data | 전거 데이터 |

### 2.3 한국 서지 표준 운영
- 국립중앙도서관 KORMARC 매뉴얼 (`librarian.nl.go.kr/kormarc/`)
- 한국도서관협회 KCR (개정판)
- KS X 6006-0 (KORMARC 통합서지용)

---

## 3. 분류학 (Classification)

### 3.1 주요 분류법

| 분류법 | 정식명 | 적용 |
|---|---|---|
| **KDC** | 한국십진분류법 (한국도서관협회) | 한국 표준, 6판 (2013) |
| **DDC** | Dewey Decimal Classification (OCLC) | 글로벌 1위, 23판 (유료) |
| **LCC** | Library of Congress Classification | 미국 대학·연구 |
| **UDC** | Universal Decimal Classification | 유럽·중남미 |
| **NDC** | 日本十進分類法 | 일본 표준, 10판 |
| **CCR** | 中国图书馆分类法 | 중국 표준 |
| **콜론분류법** | Colon Classification (Ranganathan) | 학술적, 인도 |

### 3.2 KDC 6판 주류 (이미 우리 `kdc_tree.py`)
000 총류·010 도서학·020 문헌정보학·…·813 한국소설·911 한국사

### 3.3 분류 이론
- **계층적 분류**: 주류 → 강목 → 요목 → 세목 (10진 트리)
- **패싯 분류** (Ranganathan): 5분류 (PMEST: 인격·물질·에너지·공간·시간)
- **자동 분류**: 머신러닝(BERT·FastText), 키워드 추출, 시소러스 기반
- **국회도서관 2024 연구**: BERT 기반 DDC 분류 정확도 80%

### 3.4 우리 매칭
- `classification/kdc_classifier.py` — 다단계(NL Korea → 부가기호 → AI)
- `classification/scheme.py` — KDC/DDC/NDC/LCC/UDC 추상 인터페이스 (확장 가능)
- `librarian_helpers/kdc_tree.py` — KDC 트리 데이터·검색

---

## 4. 목록학 (Cataloguing)

### 4.1 한국 목록 표준
- **KORMARC 통합서지용** (KS X 6006-0): 단행본·연속간행물 통합
- **KORMARC 전거통제용** (KS X 6006-2): 인명·단체명·주제 등
- **KORMARC 소장통제용** (KS X 6006-3): 자료 위치·소장
- **KCR4** 또는 **KCR5 초안** (2024.5)

### 4.2 글로벌 목록 표준
- **MARC 21** (Library of Congress): 미국·영어권
- **UNIMARC** (IFLA): 프랑스·중남미
- **MARCXML** (LC): XML 변형
- **MODS**: 도서관용 메타데이터
- **Dublin Core**: 일반 자원
- **BIBFRAME**: MARC 대체 신표준 (LC 2012~)

### 4.3 우리 매칭
- `kormarc/builder.py` — KORMARC 통합서지용 빌드 (관제 처리 포함)
- `kormarc/validator.py` + `kolas_validator.py` — 검증
- `conversion/marc21.py` — KORMARC ↔ MARC21
- `output/marcxml_writer.py` — MARCXML
- `vernacular/field_880.py` — 한자 병기 880 페어

---

## 5. 주제명 (Subject Headings)

### 5.1 표준
- **NLSH** 국립중앙도서관 주제명표목표 (한국)
- **LCSH** Library of Congress Subject Headings (미국)
- **MeSH** Medical Subject Headings (의학·NLM)
- **GND** 독일 통합전거파일
- **FAST** Faceted Application of Subject Terminology

### 5.2 우리 매칭
- `classification/subject_recommender.py` — NLSH 스타일 AI 추천
- 도정나 키워드 결합

---

## 6. 핵심 학술 논문·보고서

### 6.1 한국
| 자료 | 출처 | 우리 활용 |
|---|---|---|
| **인공지능 시대 국회도서관 지식정보 구조화 방안 연구 (2024.12)** | 국회도서관 | `자료/1733711161563.pdf` 보유, 인용 |
| 도서관 자동화 시스템 비교 연구 | 한국문헌정보학회지 | 학술 인용 가능 |
| 한국형 BIBFRAME 적용 방안 | 한국비블리아학회지 | 글로벌 진출 시 |
| KCR5 초안 (2024.5) | 한국도서관협회 | 명세서 갱신 시 |

### 6.2 국제
| 논문 | 저자·연도 | 주제 |
|---|---|---|
| Suominen et al. (2018~) Annif | 핀란드 국립도서관 | 자동 주제색인 오픈소스 |
| Aycock 2024 케이스 스터디 | Cataloging & Classification Quarterly | AI 카탈로깅 실험 |
| Taniguchi 2024 | C&CQ | 자동 서지 생성 |
| Godby, Wang, Mixter (2015) | OCLC | BIBFRAME 변환 |

### 6.3 무료 입수처
- arXiv·ResearchGate·저자 홈페이지 (대부분 prepublic 버전)
- DBpia, KISS (한국 학술지) — 기관 인증 필요
- Cataloging & Classification Quarterly — Taylor & Francis 구독 필요

---

## 7. 도서관 통계

### 7.1 한국 통계 출처
| 출처 | URL/시스템 | 데이터 |
|---|---|---|
| **도서관통계 (libsta.go.kr)** | 문화체육관광부 | 전국 도서관 종합 |
| **국립중앙도서관 통계** | nl.go.kr | 장서·이용 |
| **한국도서관연감** | KLA | 연간 종합 |
| **교육부 학교도서관 통계** | 교육부 | 학교도서관 |

### 7.2 핵심 수치 (2024 기준 추정)

| 항목 | 수 | 비고 |
|---|---|---|
| 공공도서관 | 약 1,200곳 | KOLAS 사용 |
| 학교도서관 | 약 11,000곳 | DLS 사용 |
| 작은도서관 | 약 6,800곳 | KOLASYS-NET 1,840곳 |
| 대학도서관 | 약 460곳 | LAS·KOMET·Alma |
| 특수도서관 | 약 800곳 | 다양 |
| **총 도서관 수** | **약 20,300곳** | |

### 7.3 우리 시장 추정 (실질 SOM)
- TAM (전체): 20,300곳
- SAM (실 SaaS 가능): 약 30% = 6,000곳
- SOM (1~3년 도달 가능): 1~3% = **160~400곳**

→ Phase 3 BEP 200곳은 SOM의 50%. 도전적이지만 달성 가능 범위.

---

## 8. 정부·공공 데이터셋 (활용 가능)

| 데이터 | 출처 | 형식 |
|---|---|---|
| 정보나루 | data4library.kr | API + CSV |
| 공공데이터포털 | data.go.kr | 다양 |
| 국가서지 | nl.go.kr/seoji | API |
| KOLIS-NET | nl.go.kr | OAI-PMH |
| 도서관통계 | libsta.go.kr | Excel |

---

## 9. 추가 학습 권장 자료

### 9.1 PO 정독 권장 (우선순위)
1. **국회도서관 2024 보고서 5·6장** (`자료/1733711161563.pdf` p.4~6 + 결론) — 1시간
2. **KORMARC 매뉴얼 1·2부** (NL 웹사이트) — 2시간
3. **KCR5 초안** (KLA) — 1시간

### 9.2 Claude 자동 정리 가능 (PO 시간 들어가지 않음)
- KORMARC 매뉴얼 전체 → 필드별 마크다운 (WebFetch)
- KOLASYS-NET CSV 양식 분석 (`api.aladin.co.kr/ttb/api`처럼 공개 사이트)
- 한국문헌정보학회지 무료 초록 → 분야별 트렌드 정리

PO가 "이거 자동화해줘" 명령 시 즉시 가능.

---

## 10. 우리 도구가 사서 도메인에 기여하는 부분

| 도메인 | 우리 기여 |
|---|---|
| 자료조직론 | KORMARC 자동 + KDC 추천 + NLSH 주제명 + 880 한자 |
| 분류학 | 다중 시스템 추상화 (KDC·DDC·NDC·LCC·UDC) |
| 목록학 | KORMARC ↔ MARC21 변환·MODS·Dublin Core |
| 청구기호·라벨 | 049 + A4 라벨 PDF |
| 통계·보고서 | 자관 DB 인덱스 + KDC 분포 |
| 사서 교육 | KORMARC 17필드 가이드·KDC 트리 |

도서관계 학술 활동·정부 지원사업·사서 교육에 인용 가능한 수준의 깊이.
