# 사서 실무 도구 상세 (한국 도서관계)

> KOLAS·DLS·KOLASYS·LAS 등 한국 사서가 일상에서 마주하는 시스템 깊이 정리.
> 우리 도구가 어디서 어떻게 호환·연동되는지 구체화.

---

## 1. KOLAS III (공공도서관 표준)

### 개요
- **운영처**: 국립중앙도서관
- **대상**: 공공도서관 약 1,200곳
- **무료/유료**: 무료 보급
- **특징**: 한국 공공도서관의 사실상 표준

### 핵심 기능
- 자료관리 (서지·소장·분류)
- 이용자관리 (회원·대출·반납)
- 통계·보고서
- KOLIS-NET 연계

### KORMARC 반입 흐름
```
.mrc 파일 → KOLAS 마크 반입 폴더 → 자동 인식 → 자관 DB 적재
```
파일명이 ISBN과 동일하면 **자동 매칭**.

### 우리 호환
- `output/kolas_writer.py` — `{ISBN}.mrc` 자동 생성
- `kormarc/kolas_validator.py` — 반입 거부 사전 경고
- 환경변수 `KORMARC_OUTPUT_DIR=D:/KOLAS/Import` 가능

---

## 2. 독서로DLS (학교도서관)

### 개요
- **운영처**: 한국교육학술정보원(KERIS)
- **대상**: 전국 학교도서관 약 11,000곳
- **무료/유료**: 무료
- **2024년 통합**: 옛 DLS → "독서로DLS"로 통합·개편

### 핵심 기능
- 학교도서관 자료관리
- 학생 대출·반납
- 독서 활동 (독서로 연계)
- 학생·교과 연계 (521·526 필드)

### 사서 추가 작업
- 521 ▾a 추천 학년·이용 대상
- 526 ▾a 교과 연계 (학습참고서)

### 우리 호환
- `output/dls_writer.py` — DLS 별도 폴더 + 521 자동
- `target_grade` 인자로 추천학년 자동 추가

---

## 3. KOLASYS-NET (작은도서관)

### 개요
- **운영처**: 국립중앙도서관
- **대상**: 작은도서관 1,840곳 (전체 작은도서관 6,800곳의 27%)
- **무료/유료**: 무료
- **특징**: 웹 기반, KOLIS-NET 실시간 서지 연계

### 핵심 기능
- 간편 서지 입력 (KOLIS-NET에서 가져오기)
- 자료관리·대출
- 통계
- 데이터 백업

### 한계 (우리 차별화 포인트)
- UI 구식 (2010년대 디자인)
- 모바일 미지원
- 사진 인식·AI 없음
- KOLIS-NET 미등록 자료(자비출판·옛 책) 처리 어려움
- 일괄 업로드 양식 제한

### 우리 호환
- `output/csv_writer.write_kolasys_csv` — 18 컬럼 일괄 업로드 형식
- 사서가 우리 도구로 마크 → CSV 다운로드 → KOLASYS-NET 가져오기

---

## 4. LAS / KOMET (대학·전문도서관, 상용)

### 개요
| 시스템 | 운영처 | 가격 |
|---|---|---|
| **LAS** | 코린(KORIN) | 도서관당 연 수천만원 |
| **KOMET** | 코미시스템 | 유사 |

### 특징
- 풀 ILS (서지·소장·이용자·대출·반납·OPAC·예산)
- KORMARC 표준 + MARC21 옵션
- WorldCat·정보나루 연계
- 대학도서관·기업도서관 위주

### 우리 위치
- 우리 ICP 외 (Phase 2~3)
- MARC21 변환(`conversion/marc21.py`)으로 호환은 가능

---

## 5. Koha / Alma / Tulip / SOLARS (해외·일부)

### Koha
- **개발**: New Zealand 1999~, 오픈소스
- **국내 사용**: ByWater Solutions·자체 운영 일부 도서관
- **장점**: 무료·커스터마이즈 자유
- **단점**: 한국어 지원 부족·운영 부담

### Alma (Ex Libris)
- **개발**: 이스라엘 Ex Libris
- **국내 사용**: 일부 대학 (서울대 등)
- **가격**: 매우 비쌈

### 우리 호환
- MARCXML export로 모두 호환

---

## 6. 외부 데이터 API (사서가 직접 또는 시스템 통해 사용)

### 6.1 국립중앙도서관 ISBN 서지 (NL Korea)
- **URL**: https://www.nl.go.kr/seoji/SearchApi.do
- **인증키**: `NL_CERT_KEY` (1~3일 승인)
- **반환**: KORMARC 형태 직접 매핑 가능
- **특징**: 한국 자료 1순위, KDC 부여
- **우리**: `api/nl_korea.py` 1순위 폴백

### 6.2 KOLIS-NET (전국 통합목록)
- **URL**: https://www.nl.go.kr/NL/search/openApi/searchKolisNet.do
- **인증키**: 공유 (NL_CERT_KEY)
- **반환**: 다른 도서관의 분류·청구기호
- **우리**: `api/kolisnet_compare.py` (분류 의사결정 보조)

### 6.3 알라딘 OPEN API
- **URL**: http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx
- **인증키**: TTBKey (블로그 등록 1~2일)
- **반환**: 상용 메타 (표제·저자·요약·표지)
- **출처 표시 의무**: "도서 DB 제공: 알라딘 인터넷서점"
- **일일 한도**: 5,000회
- **우리**: `api/aladin.py`

### 6.4 카카오 책 검색
- **URL**: https://dapi.kakao.com/v3/search/book
- **인증키**: REST API 키 (즉시)
- **일일 한도**: 30,000회
- **우리**: `api/kakao.py` (현 활성)

### 6.5 도서관 정보나루
- **URL**: http://data4library.kr
- **인증키**: authKey (즉시)
- **반환**: 키워드·대출통계
- **우리**: `api/data4library.py` (650/653 보조)

### 6.6 비공식·제휴 필요
- 교보문고 API: 제휴
- YES24 API: 비공식

---

## 7. 분류·목록 보조 도구 (종이·웹)

| 도구 | 형태 | 가격 |
|---|---|---|
| KDC 6판 | 종이책 (KLA) | 5만원 |
| DDC 23판 | 종이책 (OCLC) | $300 |
| WebDewey | 웹 구독 (OCLC) | $1,000+/년 |
| 이재철 저자기호표 | 종이 | 1만원 |
| 박봉석 저자기호표 | 종이 | 1만원 |
| NLSH | 웹 (NL) | 무료 |

### 우리 매칭
- KDC 트리: `librarian_helpers/kdc_tree.py` (전체 데이터 내장)
- 저자기호: `librarian_helpers/call_number.make_author_mark` (단순 휴리스틱)
- NLSH: AI 추천 (`subject_recommender.py`)

---

## 8. 라벨·바코드·인쇄 도구

### 사서 평소 사용
- **Avery 스티커**: L7160 (3×7=21장)·L7159 (3×8=24장)
- **바코드 프린터**: Code 128·EAN-13
- **A4 레이저 프린터**

### 우리 호환
- `output/labels.py` — A4 PDF, Avery L7160·L7159 호환
- `python-barcode` Code 128 자동
- `[labels]` 의존성 그룹

---

## 9. 사서 작업 PC 환경

### 일반적
- Windows 10·11
- 한글·MS Office (보고서)
- KOLAS·DLS 클라이언트 설치
- 정보나루 즐겨찾기

### 우리 도구 적합성
- ✅ Streamlit 웹 UI (브라우저만 있으면)
- ✅ Cloudflare Tunnel (모바일 접속)
- ✅ Windows 더블클릭 .bat 시작
- ✅ 한글 인코딩 자동 (utf-8-sig)

---

## 10. 사서 일상 한 사례 (1인 학교도서관 가정)

```
09:00 출근
09:15 학생 응대 (대출·반납·질문)
10:00 신착도서 박스 개봉 (이번 주 50권)
10:30 마크 작업 시작:
       권당 8분 × 50권 = 약 400분 = 6시간 40분
       → 본업 못 하고 마크만 함
12:00 점심
13:00 마크 작업 계속
15:00 독서 프로그램 (학생 동아리)
16:30 마크 작업 마무리 (오늘 처리: 30권)
17:30 청구기호 라벨 인쇄
18:00 퇴근 (마크 20권 남김 → 내일)
```

→ 우리 도구로 권당 8분 → 2분 단축 시:
- 50권 × 2분 = 100분 = 1시간 40분
- **하루에 신착 마크·라벨까지 다 끝남**
- 다른 본업·학생 응대 가능

이게 사서가 월 3만원을 결제할 만한 가치.

---

## 11. 우리 도구 호환성 요약 매트릭스

| 사서 시스템·표준 | 우리 호환 |
|---|---|
| KOLAS III | ✅ `.mrc` 자동 반입 |
| 독서로DLS | ✅ DLS 별도 + 521 |
| KOLASYS-NET | ✅ CSV 18 컬럼 |
| LAS | ✅ MARCXML |
| KOMET | ✅ MARCXML |
| Koha | ✅ MARC21·MARCXML |
| Alma | ✅ MARC21·MARCXML |
| WorldCat (해외) | ✅ MARC21 (Phase 3) |
| KORMARC | ✅ 17필드 + 관제 + 880 |
| KCR4·5 | △ 부분 (245·100·700) |
| KDC 6판 | ✅ 트리·AI·NL Korea |
| NLSH | ✅ AI 추천 |
| 정보나루 | ✅ API |
| KOLIS-NET | ✅ 비교 |
| 알라딘·카카오 | ✅ API |
| Code 128 바코드 | ✅ PDF 라벨 |
| Avery L7160·L7159 | ✅ |

→ **공공·학교·작은도서관에 필요한 도구 100% 매칭**.
대학도서관(LAS·KOMET·Alma)도 MARC21 변환으로 호환.
