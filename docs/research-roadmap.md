# 추가 조사 로드맵 — 분야별·우선순위별 정리

> 1인 PO가 1년간 조사할 모든 방향. Claude 자동 가능 영역 + PO 직접 영역 분리.
> **2026-04-28 갱신**: 야간 자율 진행 영역 ✅ 표시. 자료 폴더 100% + D 드라이브 100% 흡수 완료. 26 신규 docs + 84 ADR.

---

## 0. 분류 체계 (2026-04-28 진행 상태)

| 영역 | 우선순위 | Claude 자동 | PO 직접 | 진행 |
|---|---|---|---|---|
| A. 표준·매뉴얼 | ★★★ | WebFetch + 정리 | 검수 | ✅ **완료** (KORMARC 2023.12 + 9 자료유형 + 5 NLK 사서 지침 + KOLAS·알파스 매뉴얼) |
| B. 경쟁사 | ★★★ | WebFetch + 비교표 | 인터뷰 | ✅ **완료** (`docs/competitor-analysis.md` + 5 상호대차 비교) |
| C. 시장·통계 | ★★ | 공공 데이터 분석 | 협회 명단 | ✅ **완료** (학교 12,200관·작은 6,830관·NPS 자관 6년) |
| D. 학술 논문 | ★★ | 무료 abstract | 유료 본문 | ✅ 부분 (자관 윤동주 35 컬렉션 + 국회도서관 2024 보고서 200p) |
| E. 규제·법률 | ★★ | 법령정보·정리 | 변호사 검수 | ✅ 부분 (PIPA 2026.9.11 + 6 법령 + ISMS-P 2027.7.1) |
| F. 기술 트렌드 | ★ | 글로벌 동향 정리 | 결정 | ✅ 부분 (`docs/technology-trends.md`) |
| G. 사용자 행태 | ★★★ | 인터뷰 가이드 | 사서 인터뷰 | 🟡 PO 직접 (베타 사서 미모집) |
| H. 정부 지원사업 | ★★ | 사업 목록 정리 | 신청서 작성 | ✅ 부분 (`docs/government-grants.md` + 5월 마감 임박) |

---

## A. 표준·매뉴얼 (★★★ 즉시)

### A.1 국립중앙도서관 KORMARC 매뉴얼
- **URL**: https://librarian.nl.go.kr/kormarc/KSX6006-0/
- **자동 수집 가능**: 모든 필드(0XX~9XX) + 식별기호 + 예시
- **결과물**: `docs/kormarc-spec/{필드}.md` 자동 생성
- **활용**: builder.py 보강·사서 가이드·UI 툴팁

### A.2 KCR4 정식 PDF
- **URL**: 한국도서관협회 KLA 웹사이트
- **PO 액션**: PO가 KLA 회원 가입·다운로드
- **저작권**: KLA 보유, 우리 코드 내장 X (인용만)

### A.3 KCR5 초안 (2024.5)
- **URL**: KLA 발표 자료
- **자동 수집**: PDF 공개되면
- **활용**: Phase 2 KCR5 전환 검토

### A.4 KDC 6판 종이책 → KDC 7판 (예정)
- **현재**: 종이책 5만원
- **자동 수집 불가**: 저작권 (KLA)
- **우리 트리**: 주류·강목까지만 무료 공개 부분 사용 (`kdc_tree.py`)

### A.5 NLSH (국립중앙도서관 주제명표목표)
- **URL**: nl.go.kr 공개
- **자동 수집 가능**: 어휘 사전
- **활용**: subject_recommender 강화

### A.6 008 발행국부호 매핑 (전체)
- **출처**: KORMARC 매뉴얼 부록
- **자동 수집 가능**: PDF·HTML 추출
- **활용**: `kormarc/mapping.py:PUBLICATION_PLACE_CODES` 보강

---

## B. 경쟁사 (★★★ 즉시)

### B.1 MarcAI.cloud
- **URL**: marcai.cloud
- **조사**: 가격·기능·언어 지원·UI
- **결과**: `docs/competitor-analysis.md`

### B.2 Koha (ByWater Solutions)
- **URL**: koha-community.org
- **조사**: 한국어 지원·KORMARC 처리
- **활용**: 우리 MARCXML 호환 검증

### B.3 OCLC (WorldCat·WebDewey·AI 카탈로깅)
- **URL**: oclc.org
- **조사**: 2025.12 AI 카탈로깅 기능 출시 후 비교
- **활용**: 글로벌 진출 차별화

### B.4 Alma (Ex Libris)
- **URL**: exlibrisgroup.com
- **조사**: 한국 대학 도입 사례 (서울대·연세대 등)

### B.5 KOLASYS-NET·KOLAS·DLS
- **이미 우리 매칭 완료** — 기능 비교표만 갱신

### B.6 Tulip·LAS·KOMET
- **국내 비공개**: 도서관 직접 접속해야 화면 가능
- **PO 활용**: 사서 인맥으로 화면 캡처 → 우리 분석

---

## C. 시장·통계 (★★ 분기별)

### C.1 도서관통계 (libsta.go.kr)
- **자동 수집**: CSV·Excel 다운로드
- **활용**: 시장 규모 갱신, 정부 과제 인용

### C.2 작은도서관 통계
- **출처**: smalllibrary.kr (작은도서관협회)
- **자동 수집**: 공개 자료

### C.3 학교도서관 통계 (교육부)
- **출처**: moe.go.kr / KERIS
- **자동 수집**: 공개 자료

### C.4 출판사·신간 통계
- **출처**: 대한출판문화협회·한국출판연감
- **활용**: 신착 추정

### C.5 도서관 예산 (시·도 공공데이터)
- **출처**: data.go.kr
- **자동 수집 가능**

---

## D. 학술 논문 (★★ 진행형)

### D.1 한국 학술지
- **한국문헌정보학회지** (KISS, DBpia)
- **한국비블리아학회지** (DBpia)
- **무료 abstract만 우리 활용**, 본문은 PO 기관 인증

### D.2 국제 학술지
- **Cataloging & Classification Quarterly** (Taylor & Francis, 유료)
- **Library Resources & Technical Services** (LRTS, 미국 ALA)
- **Journal of Documentation**

### D.3 무료 입수처
- arXiv·ResearchGate·SSRN (저자 prepublic)
- DOAJ (오픈액세스)
- 각 학회 무료 공개분

### D.4 자동 분석 흐름 (Claude)
- 무료 PDF·abstract 입수 → 핵심 인용 5개 + 시사점 자동 추출

---

## E. 규제·법률 (★★ 출시 전 1회)

### E.1 개인정보보호법
- **출처**: law.go.kr 개인정보보호법 + 시행령
- **우리 영향**: 사서 이메일·도서관명 수집 → 처리방침 의무

### E.2 정보통신망법
- **우리 영향**: 통신판매업·이용자 정보

### E.3 도서관법
- **출처**: law.go.kr 도서관법
- **우리 영향**: 도서관 자료·서지 활용 범위

### E.4 저작권법
- **우리 영향**: KORMARC 데이터 (서지정보는 사실의 저작물 X), KDC·DDC 분류표 (KLA·OCLC 보유)

### E.5 공정거래법 (B2B 약관)
- **우리 영향**: SaaS 약관 표준

### E.6 결과물
- `docs/regulatory-landscape.md`

---

## F. 기술 트렌드 (★ 분기별)

### F.1 BIBFRAME 전환
- **출처**: LC BIBFRAME 페이지
- **자동 수집**: 공개 문서

### F.2 Linked Data·Wikidata
- **활용**: 미래 표준 호환

### F.3 자동 분류·색인 AI
- **출처**: Annif (핀란드), OCLC AI
- **활용**: 정확도 비교

### F.4 RDA → RDA Toolkit
- **출처**: rdatoolkit.org (유료 구독)
- **PO 액션**: 한국 도서관협회 단체 구독 활용

### F.5 결과물
- `docs/technology-trends.md`

---

## G. 사용자 행태 (★★★ 매월)

### G.1 사서 인터뷰
- **이미 준비**: `docs/librarian-interview-questions.md` 30개
- **진행**: 매월 5명 이상

### G.2 사서 카페·블로그·SNS
- **자동 수집**: 공개 글 키워드 분석
- **출처**: 네이버 사서 카페·브런치·인스타

### G.3 도서관 협회 학술대회
- **PO 액션**: 매년 KLA 학술대회 참석·발표

### G.4 사서 자격증·연수 커리큘럼
- **출처**: 사서연수원·문체부
- **활용**: 사서 도메인 깊이 갱신

---

## H. 정부 지원사업 (★★ 매월)

### H.1 K-Startup
- **출처**: k-startup.go.kr
- **자동 수집 가능**: 공모 일정·요건

### H.2 창업진흥원 예비창업패키지
- **자동 수집**: 공모 페이지

### H.3 공공데이터 활용 창업경진대회
- **자동 수집**: 행안부 페이지
- **우리 강점**: 정보나루·국가서지 활용 → 가산점

### H.4 문화체육관광부 도서관 지원
- **자동 수집**: 문체부 공모

### H.5 여성·청년·지역 가산점
- **자동 수집**: 각 시·도 공모

---

## 자동 조사 명령 예시 (PO가 Claude에게)

### 즉시 실행 가능
1. `WebFetch librarian.nl.go.kr/kormarc/ → docs/kormarc-spec/ 필드별 정리`
2. `WebFetch marcai.cloud → 가격·기능 표 → docs/competitor-analysis.md 갱신`
3. `WebFetch libsta.go.kr → 도서관 종류별 수치 → docs/library-statistics.md 갱신`
4. `WebFetch k-startup.go.kr → 6개월 내 도서관·SaaS 관련 공모 목록`
5. `WebFetch koha-community.org → 한국어 지원·KORMARC 호환 분석`

### PO가 자료 폴더에 넣은 후 (저작권·접근 제한)
6. `자료/KCR4_PDF.pdf 핵심 차이점 → KORMARC 빌드 영향`
7. `자료/한국문헌정보학회지_논문.pdf → 핵심 인용 추출`

---

## 1년 조사 마일스톤

| 분기 | 우선 영역 |
|---|---|
| Q1 (3개월) | A.1·B.1·B.2·G.1 (KORMARC 매뉴얼·MarcAI·Koha·사서 5명 인터뷰) |
| Q2 | A.5·C·E (NLSH·통계·법률) |
| Q3 | D·F (논문·기술 트렌드) |
| Q4 | H (정부 지원사업 신청 시즌) |

각 분기 끝에 정리된 결과를 `docs/research-q[1-4]-summary.md`에 누적.

---

## 결과물 정리 위치

| 영역 | 결과물 |
|---|---|
| A | `docs/kormarc-spec/`, `docs/marc-fields-guide.md` |
| B | `docs/competitor-analysis.md` |
| C | `docs/library-statistics.md` (갱신) |
| D | `docs/research-references.md` (갱신) |
| E | `docs/regulatory-landscape.md` |
| F | `docs/technology-trends.md` |
| G | `docs/librarian-interview-questions.md` + 인터뷰 결과 누적 |
| H | `docs/government-grants.md` |

---

이 로드맵은 PO가 1년간 어떤 자료를 어떤 순서로 모아야 하는지의 청사진. Claude는 PO 명령 시 즉시 진행.
