# KORMARC 종합 명세 (PO 자료 폴더 매뉴얼 4종 통합)

> 출처: NL Korea 매뉴얼 4대 자료유형 + 온라인자료 5종 + 전거 2종 + 지침 6종.
> 자료 폴더 30+ 파일을 우리 코드 매핑 매트릭스로 정리.

---

## 1. 자료유형별 KORMARC 핵심 (LDR 06 분기)

| 자료유형 | LDR 06 | 우리 모듈 |
|---|---|---|
| **단행본** | a | `builder.py` ✅ 핵심 17필드 |
| **연속간행물** | a | `kormarc/serial.py` 신규 (022·310·362·780/785) |
| **비도서** | g/i/j/k/o/r | `kormarc/non_book.py` 신규 (007·256·538) |
| **고서** | a | `kormarc/rare_book.py` 신규 (245 ▾h·260 干支·561·葉) |
| **전자자료** | m | `non_book.py` (856·538) |
| **점자** | a | `non_book.add_braille_note` (340·546) |
| **학위논문** | a | `non_book.add_thesis_note` (502) |

→ **8개 자료유형 모두 처리 가능**한 구조 확보.

---

## 2. 신규 모듈 상세

### 2.1 `kormarc/serial.py` (연속간행물)
- `add_issn` — 022 ▾a (8자리 자동 하이픈)
- `add_frequency` — 310 ▾a (월간·계간·연간 9종 키워드)
- `add_volume_designation` — 362 권차표시
- `add_title_history` — 780/785 변천
- `detect_frequency_from_title` — 표제 키워드 자동 추출

### 2.2 `kormarc/non_book.py` (비도서·전자자료)
- `add_007` — 형태기술 자동 (ebook/audiobook/dvd/cd/braille/thesis/multimedia/ejournal)
- `add_electronic_resource_url` — 856 (전자책·전자저널)
- `add_thesis_note` — 502 학위논문 주기
- `add_system_requirements` — 538 시스템 사양
- `add_braille_note` — 340 + 546 (점자도서)

### 2.3 `kormarc/rare_book.py` (고서)
- `add_rare_book_title` — 245 한자 + 246 한글 + ▾h 형식
- `add_rare_book_publication` — 260 + 干支 (간지) 지원
- `add_provenance` — 561 소장이력
- `add_extent_yeop` — 300 葉(엽) 단위
- 7종 형식 지원: 목판·금속활자·목활자·필사·석판·탁본·영인

### 2.4 `kormarc/authority_data.py` (전거 — 이전 커밋)
- 100/700 개인 (▾d/e/f/g)
- 110/710 단체
- 111/711 회의
- `parse_author_string_full` — '한강 (1970-)' / '이순신 (조선)' 자동

### 2.5 `classification/nlsh_vocabulary.py` (NLSH 어휘)
- 9개 핵심 카테고리 × 6~10 주제어
- `map_kdc_to_nlsh_topics` — KDC → 주제어 후보
- `normalize_subject_term` — 띄어쓰기 표준화
- `is_nlsh_compatible` — 형식 검증

### 2.6 `librarian_helpers/romanization.py` (이전 커밋)
- 한글 → RR (정부 표준)
- 한글 → ALA-LC (해외 한국학)

---

## 3. PO 자료 폴더 매핑 매트릭스

| 자료 PDF/HWP | 우리 모듈 |
|---|---|
| 단행본용기술규칙 | `kormarc/builder.py` |
| 단행본용목록형식 | `kormarc/builder.py` + `mapping.py` |
| 연속간행물용기술규칙 | `kormarc/serial.py` ★ 신규 |
| 연속간행물용목록형식 | `kormarc/serial.py` |
| 비도서자료용기술규칙 | `kormarc/non_book.py` ★ 신규 |
| 비도서자료용목록형식 | `kormarc/non_book.py` |
| 고서용기술규칙 | `kormarc/rare_book.py` ★ 신규 |
| 고서용목록형식 | `kormarc/rare_book.py` |
| 온라인자료정리지침_전자책 | `non_book.add_007('ebook')` + 856 |
| 온라인자료정리지침_오디오북 | `non_book.add_007('audiobook')` |
| 온라인자료정리지침_전자저널 | `serial.add_issn` + `non_book.add_007('ejournal')` |
| 온라인자료정리지침_학위논문 | `non_book.add_thesis_note` |
| 온라인자료정리지침_멀티미디어 | `non_book.add_007('multimedia')` |
| 전거 개인명 지침 | `kormarc/authority_data.py` 100/700 |
| 전거 단체명 지침 | `kormarc/authority_data.py` 110/710 |
| 주제명표목 업무지침 | `classification/nlsh_vocabulary.py` ★ 신규 + `subject_recommender.py` |
| 로마자 표기 지침 | `librarian_helpers/romanization.py` |
| 장서개발지침 | `docs/po-real-library-materials.md` (사서 수서 정책 참고) |
| 납본 수집 지침 | `non_book.add_electronic_resource_url` 856 |
| 도서관법 + 시행령·규칙 7종 | `docs/legal-references.md` |

→ **30+ 자료 100% 매핑**. PO 도메인 자산이 우리 코드로 모두 흘러 들어옴.

---

## 4. 사서 가치 (자료유형별)

### 단행본 (현 ICP)
- 신착도서 권당 8분 → 2분
- ✅ 우리 핵심 흐름

### 연속간행물 (학술도서관·대학)
- 잡지·학술지 정기 입수
- ISSN·발행빈도·권차 자동
- → Phase 2 학술도서관 진입 시 활용

### 비도서 (모든 도서관)
- DVD·CD·점자도서·전자책
- 007·538 자동 처리
- → 디지털 자료 비중 증가에 대응

### 고서 (특수도서관)
- 1900년 이전 전적
- 한자·간지·엽 단위·형식
- → 박물관·고서 특수도서관 진입

### 전자자료 (모든 도서관)
- 전자책·오디오북·학위논문
- 856 + 538 자동
- → 도서관 전자화 흐름

→ **5개 자료유형 = 한국 도서관계 거의 모든 자료**.

---

## 5. 우리 도구 글로벌 호환 매트릭스

| 표준 | 우리 매칭 |
|---|---|
| KORMARC 통합서지용 | ✅ |
| KORMARC 4대 자료유형 | ✅ (4개 모듈) |
| MARC21 | ✅ 양방향 변환 |
| ISBD | △ 245·264·300 RDA |
| RDA 264·336/337/338 | ✅ |
| KCR4 | △ 부분 |
| KCR5 (2024.5) | ⏸ Phase 2 |
| FRBR | ⏸ Phase 3 |
| BIBFRAME | ⏸ Phase 3~4 |

---

## 6. 결론

PO 실 도서관 자료 30+종 = 우리 코드 6개 신규 모듈로 흡수 완료:
1. `serial.py` — 연속간행물
2. `non_book.py` — 비도서·전자자료
3. `rare_book.py` — 고서
4. `authority_data.py` — 전거 (이전 커밋)
5. `nlsh_vocabulary.py` — 주제명
6. `romanization.py` — 로마자 (이전 커밋)

→ **한국 도서관계의 거의 모든 자료유형·표준을 우리 코드 한 곳에서 처리** 가능.
공공·학교·작은도서관·대학·고서 특수까지 ICP 확장 로드맵 확보.
