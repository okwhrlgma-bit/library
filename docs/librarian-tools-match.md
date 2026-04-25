# 사서 도구·표준 매칭 보고서

한국 사서가 일상에서 쓰는 도구·표준·시스템 21종에 대해 우리 매칭 상태 점검.

---

## ✅ 완전 매칭 (12종)

| 사서 도구·표준 | 우리 매칭 | 모듈 |
|---|---|---|
| **KOLAS III** (공공도서관) | .mrc 자동 반입 호환 | `output/kolas_writer.py` |
| **독서로DLS** (학교) | .mrc + 521(추천학년)/526(교과연계) | `output/dls_writer.py` |
| **KOLIS-NET** (전국 통합목록) | 다른 도서관 분류 비교 | `api/kolisnet_compare.py` |
| **KORMARC** 표준 | 14필드 자동 빌드 | `kormarc/builder.py` |
| **KCR4** (목록규칙) | 245·100·700 적용 | `builder.py` |
| **KDC 6판** | 후보 3개 + 신뢰도 | `classification/kdc_classifier.py` |
| **DDC** | 082 필드 (NL Korea 응답 시) | `builder.py` |
| **NLSH** (주제명표목표) | 650·653 AI 추천 | `classification/subject_recommender.py` |
| **국립중앙도서관 ISBN API** | 1순위 메타데이터 | `api/nl_korea.py` |
| **알라딘 OPEN API** | 상용 데이터 + 출처 표시 | `api/aladin.py` |
| **카카오 책 검색** | 보조 데이터 | `api/kakao.py` |
| **도서관 정보나루** | 키워드 추출 | `api/data4library.py` |

---

## ✅ 신규 매칭 (이번에 추가, 9종)

| 사서 도구·표준 | 우리 매칭 | 모듈 (신규) |
|---|---|---|
| **MARC21** (LC 표준) | 양방향 변환 (KORMARC ↔ MARC21) | `conversion/marc21.py` |
| **MARCXML** | import + export | `conversion/marcxml.py` |
| **MODS** (LC 메타데이터) | export | `output/mods_writer.py` |
| **Dublin Core** | export (oai_dc/srw_dc) | `output/dc_writer.py` |
| **BibTeX** | export (학술 인용) | `output/bibtex_writer.py` |
| **RIS** | export (Mendeley·Zotero·EndNote) | `output/ris_writer.py` |
| **JSON-LD** (schema.org/Book) | export | `output/jsonld_writer.py` |
| **자료유형 분기** (도서/연속간행물/비도서/전자책) | LDR 06-07 + 008 자동 | `kormarc/material_type.py` |
| **교보문고/예스24** | 클라이언트 스텁 (PO 키 발급 시 활성) | `api/kyobo.py`, `api/yes24.py` |

---

## ⚠ 미매칭 (운영 진입 시 검토)

| 사서 도구 | 미매칭 사유 | 대안 |
|---|---|---|
| **Z39.50 / SRU** (LC·BL·국내외 도서관 직접 검색) | `pyz3950`·`zoom` 라이브러리 무거움 + 베타 사서 수요 적음 | KOLIS-NET이 사실상 같은 역할 |
| **OAI-PMH 수확** (대학도서관 대량 메타데이터) | 대학도서관 진입 시 가치 — 베타 ICP 외 | MVP-2 검토 |
| **Tulip / SOLARS / Alma / Koha** (대학·해외) | 대상 ICP(공공·학교) 외 | MARC21 export로 호환 |
| **RDA 348/388** (관계자 표시 표준) | 한국 적용률 낮음 | 336/337/338로 충분 |
| **DOI / ORCID** (학술) | 단행본 위주라 미사용 | MVP-3 학술도서관 진입 시 |
| **AACR2 ↔ RDA 변환** | 자동 변환 사례 거의 없음 | 사서 수기 |
| **점자도서·시각장애 자료** | 008 24·546 ▾b 사례 적음 | 수동 추가 (UI에서 가능) |
| **상호대차 KIRSS** | 별도 시스템 통신 | 검토 후 필요 시 추가 |

---

## 사서 일상 흐름 매칭

### 1. 신착도서 단건 마크 (가장 빈번)
```
ISBN 입력 → KORMARC 자동 → 사서 검토 → 049 청구기호 추가 → 반입
```
- 우리 매칭: ✓ ISBN 탭 + mrk 미리보기 + 049 제안

### 2. ISBN 없는 자료 (옛 책·기증·자비출판)
```
표지·판권지 사진 → AI 메타 추출 → 사서 검토 → 반입
```
- 우리 매칭: ✓ 사진 탭 (Vision Sonnet) — AI 켜야 작동

### 3. 다권물·시리즈 (전집·문학상 수상작)
```
1권 마크 → 권차 분리 → 시리즈 마크 + 각권 마크
```
- 우리 매칭: ✓ 049 ▾v 권차 (`librarian_helpers/call_number.py`)
- 강화: `material_type.py`에서 m=다권물 자동 (008 06)

### 4. 비도서 자료 (DVD·CD·점자도서)
```
자료유형 결정 → LDR 06-07 + 008 부호화
```
- 우리 매칭: ✓ 신규 `material_type.py` — 도서/연속/비도서/전자책 4분기

### 5. 검색·확인 (다른 도서관 분류 참고)
```
ISBN/표제 검색 → 다른 도서관 KDC·청구기호 확인 → 본인 결정
```
- 우리 매칭: ✓ 검색 탭 + KOLIS-NET 비교

### 6. 학술자료·외국 자료 (대학·연구도서관)
```
LC/외국 카탈로그에서 MARC21 받음 → KORMARC로 변환 → 자관 반입
```
- 우리 매칭: ✓ 신규 `conversion/marc21.py` — 양방향 변환

### 7. 전자자원 처리
```
EPUB·PDF 메타데이터 → KORMARC + 856(URL)
```
- 우리 매칭: △ 자료유형 분기 + 856 자동 (PO 데이터 있을 시)

### 8. 학술 인용 형식 변환
```
도서 → 논문 인용용 BibTeX/RIS
```
- 우리 매칭: ✓ 신규 `output/bibtex_writer.py`, `ris_writer.py`

### 9. 도서관 통합 검색 노출
```
우리 카탈로그 → Dublin Core/MODS/JSON-LD → 검색엔진 인덱싱
```
- 우리 매칭: ✓ 신규 다중 출력 포맷

### 10. 교보·예스24 자가 발행 도서 (출판사 직거래)
```
서지 검색 → 메타 가져오기
```
- 우리 매칭: ✓ 클라이언트 추가 (PO 키 발급 시 활성)

---

## ICP별 우선순위

| ICP | 가장 중요한 매칭 |
|---|---|
| **1인 학교도서관 사서** | KOLAS·DLS .mrc, 049, 자료유형, 검색 |
| **신규 작은도서관** | KOLAS .mrc, KDC 추천, 청구기호 휴리스틱 |
| **대학도서관** | MARC21, MODS, Dublin Core, OAI-PMH (MVP-2) |
| **출판사** | ISBN→KORMARC, 납본용 마크 (현 동작) |

---

## 결론

**공공·학교 도서관 ICP에 필요한 도구·표준은 모두 매칭** (KOLAS·DLS·KORMARC·KDC·NLSH 핵심 라인업).

대학·해외 도서관 ICP까지 확장 시 추가 필요:
- Z39.50/SRU (실제 도서관 카탈로그 직접 검색)
- OAI-PMH 수확 (대량 메타데이터)
- RDA 348/388 (관계자 표시)

이번 추가로 **글로벌 호환성**(MARC21·MODS·Dublin Core)과 **학술 호환성**(BibTeX·RIS)까지 확보.
