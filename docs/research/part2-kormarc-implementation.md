# Part 2 — KORMARC 잘 만들기 구현 디테일

> **대상**: PO (사서 출신·KORMARC 도메인 보유) + Claude Code (구현 명령서로 활용)
> **버전**: v0.4.25 / 222 tests / 어셔션 15/15·골든 15/15·ADR 7·시각회귀·자율성 4단
> **헌법 정합**: `CLAUDE.md` §0~§13 + `.claude/rules/kormarc-domain.md` 절대 규칙 15종 + `autonomy-gates.md` 캐시카우 평가축
> **표준 정합**: KORMARC 통합서지용 KS X 6006-0:2023.12 (NLK 2차 개정)
> **자료 흡수**: 자관 D 드라이브 87 항목 + PO 자료 폴더 91 docs + .mrc 174 (4단 정합 ≥99%)
> **단일 진실 소스**: `docs/spec.md` §명세서 본문 + `docs/marc-fields-guide.md` + `docs/library-services-integration.md` + 본 문서

---

## 0. 본 문서 위치

Part 1 (전략·시장·법) → **Part 2 (구현 디테일)** ← 여기 → Part 3 (운영·영업·캐시카우)

PO 정점 정책 — 토큰·시간 평가축 X. **품질만**. 캐시카우 평가축 (§0 사서 마크 시간 단축 + §12 결제 의향) 양수 영향만 commit.

---

## 1. KORMARC KS X 6006-0:2023.12 정밀 스펙

### 1.1 표준 历사 + 적용 범위

| 버전 | 시기 | 핵심 변경 |
|---|---|---|
| 제정 | 2005 | KORMARC 통합서지용 신설 |
| 1차 개정 | 2014 | 통합서지·전거통제·소장정보 통합 |
| **2차 개정 (현행)** | **2023.12** | MARC21 호환↑ + 시맨틱 웹 + 링크드 데이터 + 외부 리소스 자동 연계 + 통합서지·전거통제·소장정보 용어 통일 |

우리 SaaS는 **2023.12 최신 표준 100% 정합**. NLK 공식 KORMARC validator 부재 시장 = 우리 4단 검증이 사실상 표준.

### 1.2 9 자료유형 모듈별 분기

| # | 자료유형 | LDR 06·07 | 008 06 | 우리 모듈 | 상태 |
|---:|---|---|---|---|---|
| 1 | 단행본 (단일·다권물·분책) | a·m / a·a | s/m | `kormarc/builder.py` | ✅ |
| 2 | 연속자료 (현행·종간) | a·s | c/d | `kormarc/serial.py` | ✅ |
| 3 | 비도서 (전자자료·필름·CD-ROM) | m·m | b/m | `kormarc/non_book.py` | ✅ |
| 4 | 고서 (한국·중국·일본 古書) | t·m | s | `kormarc/rare_book.py` | ✅ |
| 5 | 전자책 | m·m | b/m | `kormarc/ebook.py` | 🟡 Phase 1.5 |
| 6 | 전자저널 | m·s | c | `kormarc/ejournal.py` | 🟡 Phase 1.5 |
| 7 | 오디오북 | i·m | j/m | `kormarc/audiobook.py` | 🟡 Phase 1.5 |
| 8 | 멀티미디어 (DVD·Blu-ray·VR) | g·m | g/m | `kormarc/multimedia.py` | 🟡 Phase 1.5 |
| 9 | 학위논문 (석·박사) | a·m | s + 502 | `kormarc/thesis.py` | 🟡 Phase 1.5 |

자료유형 자동 감지 의사코드 (`kormarc/material_type.py:detect_material_type`):

```python
def detect_material_type(book_data: dict) -> str:
    title    = (book_data.get("title") or "").lower()
    category = (book_data.get("category") or "").lower()
    summary  = (book_data.get("summary") or "").lower()
    add_code = book_data.get("additional_code") or ""

    # 1순위: 명시적 키워드 (사서 입력·NL Korea category)
    KEYWORD_MAP = [
        (("전자책", "ebook", "e-book"),       "ebook"),
        (("오디오북", "audio"),               "audiobook"),
        (("dvd", "비디오", "blu-ray"),         "dvd"),
        (("cd",) + ("음악", "music"),         "music_cd"),
        (("지도", "지도자료"),                "map"),
        (("점자", "점자도서"),                "braille"),
        (("학위논문", "박사학위", "석사학위", "thesis"), "thesis"),
    ]
    for keys, mtype in KEYWORD_MAP:
        if any(k in (title + category + summary) for k in keys):
            return mtype

    # 2순위: 다권물·연속간행물 힌트
    if book_data.get("series_no") or book_data.get("series_title"):
        return "book_multi"
    if any(kw in (title + category) for kw in ("월간", "주간", "계간", "연감", "magazine", "journal")):
        return "serial_current"

    # 3순위: 기본 단행본
    return "book_single"
```

### 1.3 3 적용 수준 (M / A / O) 자동 결정

| 수준 | 정의 | 우리 정합 | 17 핵심 필드 분류 |
|---|---|---|---|
| **M (Mandatory)** | 필수 — 누락 시 4단 검증 fail | ✅ binary_assertions §M | 005·007·008·020(▾a)·245·260/264·300·049·056·090 |
| **A (Mandatory if applicable)** | 적용 가능 시 필수 (자료유형별 분기) | 🟡 자료유형 분기 | 022 (연속간행물 ISSN)·041 (다국어)·082 (DDC 있을 시)·336/337/338 (RDA)·440/490 (총서)·538 (전자자료) |
| **O (Optional)** | 선택 (사서 입력 자유) | 🟢 자유 | 246·250·505·520·600·610·650·653·700·856·880·950 |

자동 결정 알고리즘:

```python
def determine_application_level(field_tag: str, book_data: dict, material_type: str) -> str:
    """필드별 적용 수준 자동 결정 (M/A/O)."""
    M_FIELDS = {"005", "007", "008", "020", "245", "260", "264", "300", "049", "056", "090"}
    if field_tag in M_FIELDS:
        return "M"

    # A — 조건부 필수
    A_RULES = {
        "022": material_type.startswith("serial"),                   # ISSN
        "041": len(book_data.get("languages", [])) > 1,             # 다국어
        "082": bool(book_data.get("ddc")),                          # DDC 있을 때
        "336": True,                                                  # RDA = 항상 적용
        "337": True,
        "338": True,
        "440": bool(book_data.get("series_title")),                 # 총서
        "490": bool(book_data.get("series_title")),
        "538": material_type in {"non_book", "ebook", "ejournal", "multimedia"},
        "502": material_type == "thesis",                           # 학위논문
        "880": has_hanja_anywhere(book_data),                       # 한자 병기
    }
    if field_tag in A_RULES:
        return "A" if A_RULES[field_tag] else "O"
    return "O"
```

### 1.4 008 필드 40자리 정확 매핑 — 자료유형별 분기

008은 KORMARC의 심장. 정확히 40자리. 자료유형별 06·18-21·24-27·33·35-37 위치 의미가 다름.

| 위치 | 자릿수 | 의미 | 단행본 | 연속 | 비도서 | 전자 | 오디오 |
|---:|---:|---|---|---|---|---|---|
| 00-05 | 6 | 입력일자 YYMMDD (시스템 자동) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **06** | 1 | **발행상태** | s/m/n | c/d | b | b/m | j/m |
| 07-10 | 4 | 발행연도1 | YYYY | YYYY | YYYY | YYYY | YYYY |
| 11-14 | 4 | 발행연도2 | (공백) | YYYY/9999 | (공백) | (공백) | (공백) |
| 15-17 | 3 | 발행국부호 | ulk/ggk/xxu... | 동일 | 동일 | 동일 | 동일 |
| **18-21** | 4 | **삽화/발행빈도/특수자료** | 삽화 (a=삽화·b=지도·c=초상...) | 발행빈도 (m=월간·w=주간) | 자료특성 (a=프린트·b=음향) | 매체특성 (a=마이크로·d=DVD) | 음향특성 |
| 22 | 1 | 이용대상 | (공백/j=아동) | (공백) | (공백) | (공백) | (공백) |
| 23 | 1 | 자료형태 | (공백) | (공백) | (공백) | s=온라인/o=오프라인 | (공백) |
| **24-27** | 4 | **내용형식** | a=초록 / b=서지 / d=논문집 | 동일 | 동일 | 동일 | 동일 |
| 28 | 1 | 정부간행물 | (공백/f=연방) | 동일 | 동일 | 동일 | 동일 |
| 29 | 1 | 회의간행물 | 0/1 | 동일 | 동일 | 동일 | 동일 |
| 30 | 1 | 기념회지 | 0/1 | (공백) | (공백) | (공백) | (공백) |
| 31 | 1 | 색인 | 0/1 | (공백) | (공백) | (공백) | (공백) |
| 33 | 1 | **문학형식** | 0=비문학·1=소설·c=만화·d=희곡·j=단편 | (공백) | (공백) | (공백) | (공백) |
| 34 | 1 | 전기 | (공백/a=자서전·b=평전) | (공백) | (공백) | (공백) | (공백) |
| **35-37** | 3 | **언어부호** | kor/eng/jpn... | 동일 | 동일 | 동일 | 동일 |
| 38 | 1 | 수정레코드 | (공백) | 동일 | 동일 | 동일 | 동일 |
| 39 | 1 | 목록전거 | (공백/7=최소수준) | 동일 | 동일 | 동일 | 동일 |

자료유형별 008 빌더 의사코드:

```python
def build_008(book_data: dict, material_type: str) -> str:
    """KORMARC 008 = 정확히 40자리. 자료유형별 분기."""
    today = datetime.now().strftime("%y%m%d")             # 00-05
    codes = MATERIAL_TYPES[material_type]
    pub_status = codes.field_008_06                        # 06
    year1 = (book_data.get("publication_year") or "    ").ljust(4)[:4]   # 07-10
    year2 = "9999" if material_type == "serial_current" else "    "      # 11-14
    place = lookup_publication_country(book_data.get("publication_place")).ljust(3)[:3]  # 15-17

    # 18-21 자료유형별 분기
    if material_type.startswith("serial"):
        special_18_21 = _serial_frequency_code(book_data)   # m/w/q/a
    elif material_type == "ebook":
        special_18_21 = "    "                              # 매체 특성 별도
    elif material_type in {"non_book", "multimedia"}:
        special_18_21 = _carrier_code(book_data)
    else:
        special_18_21 = _illustration_code(book_data)        # a=삽화·b=지도

    # 33 문학형식 (단행본만)
    if material_type.startswith("book"):
        literary = _literary_form_code(book_data)            # 0/1/c/d/j
    else:
        literary = " "

    lang = (book_data.get("language") or "kor").ljust(3)[:3]   # 35-37

    parts = [
        today, pub_status, year1, year2, place,
        special_18_21,                                       # 18-21
        " ",                                                  # 22 이용대상
        " ",                                                  # 23 자료형태
        "    ",                                              # 24-27 내용형식
        " ", " ", " ", " ", " ",                             # 28-32
        literary,                                            # 33
        " ",                                                  # 34 전기
        lang,                                                 # 35-37
        " ", " ",                                            # 38-39
    ]
    result = "".join(parts)
    assert len(result) == 40, f"008 길이 {len(result)} (40 필요)"
    return result
```

### 1.5 245 지시기호1·2 자동 결정

KORMARC 245는 모든 레코드의 표제 — 1지시기호와 2지시기호 둘 다 자동 결정.

#### 1지시기호 = 책임표시 자동 부출 여부

```python
def decide_245_ind1(book_data: dict, has_main_entry_100: bool) -> str:
    """1지시기호 = 100/110/111 주표목 존재 여부.

    1 = 주표목 있음 (100/110/111이 별도 부출되어 있어 245 ▾c와 같지 않을 때 부출 안 함)
    0 = 주표목 없음 (245 ▾c가 곧 주표목 — 800/810/811로 부출 안 함)
    """
    return "1" if has_main_entry_100 else "0"
```

#### 2지시기호 = 관제 길이 + 1 (정렬 무시 글자수)

KORMARC 한국 특수 — 본표제 앞 수식어 (관제, 冠題)가 있으면 그 글자수를 무시하고 정렬해야 함.

```python
def decide_245_ind2(title: str, crown: str) -> str:
    """2지시기호 = 정렬 무시 글자수.

    예: "(개정증보판) 작별하지 않는다"
        crown = "개정증보판" (5자)
        full_title = "(개정증보판) 작별하지 않는다"
        ind2 = len("(개정증보판) ") = 8 (하지만 9 초과 시 9로 캡)

    예: 관제 없으면 0
    """
    if not crown:
        return "0"
    leading = f"({crown}) "
    return str(min(9, len(leading)))
```

자관 builder 정합 (`kormarc/builder.py:104-123`):

```python
crown = book_data.get("crown_title") or ""
if crown:
    full_title = f"({crown}) {title}"
    ind2 = str(min(9, len(crown) + 3))   # "(관제) " = len + 3 (괄호 2 + 공백 1)
else:
    full_title = title
    ind2 = "0"
ind1 = "1" if primary_author else "0"
```

#### 245 서브필드 분리 규칙

| 서브필드 | 의미 | 앞뒤 구두점 | 예시 |
|---|---|---|---|
| ▾a | 본표제 | (없음 → 단독) | `작별하지 않는다` |
| ▾b | 부표제 | 앞에 ` : ` | ` : 한강 장편소설` |
| ▾c | 책임표시 | 앞에 ` / ` | ` / 한강 지음` |
| ▾n | 권차 | 앞에 ` ` | `v. 1` |
| ▾p | 권명 | 앞에 ` , ` 또는 ` . ` | ` . 첫째 권` |
| ▾h | 자료유형표시 | 대괄호 | `[전자책]` |

### 1.6 020 ▾a·▾g·▾c 분리 알고리즘

```python
def parse_020(raw_isbn_with_metadata: str) -> dict:
    """국립중앙도서관 SeoJi API 응답 등 ISBN 통째 string → 020 분리.

    예: "9788936434120 03810 ₩15000"
        ▾a 9788936434120
        ▾g 03810
        ▾c ₩15000
    """
    parts = raw_isbn_with_metadata.split()
    isbn_raw = parts[0] if parts else ""
    isbn = normalize_isbn(isbn_raw)         # 13자리 정규화 (10→13 변환 + 체크섬 재계산)

    add_code = ""
    price = ""
    for p in parts[1:]:
        if p.isdigit() and len(p) == 5:
            add_code = p                     # 부가기호 5자리
        elif p.startswith("₩") or p.startswith("\\"):
            price = p
        elif p.replace(",", "").isdigit():
            price = f"₩{p.replace(',', '')}"

    return {"a": isbn, "g": add_code, "c": price}
```

부가기호 5자리 의미 (Q3 자산 — 다른 모듈에서 재사용):
- 1자리 (독자대상): 0=교양·1=실용·2=여성·3=구분없음·4=청소년·5/6/8=학습참고서·7=아동·9=전문
- 2자리 (발행형태): 0=문고본·1=사전·2=신서·3=단행본·4=전집·5=전자책·6=도감·7=그림책·9=기타
- 3-5자리 (KDC 주류 대응): 첫 자리가 KDC 주류 (0=총류·1=철학·2=종교·...·8=문학·9=역사)

### 1.7 880 페어 자동 생성 (한자 + 로마자 RR/MR)

KORMARC 880 = 대체 문자 표제. 한국 특수 — 한자/한글 병기, 로마자 병기.

#### 식별기호 6 페어링 규칙

```
원본 245 필드:    245 10 ▾6 880-01 ▾a 三國史記 ...
880 한글 페어:    880 10 ▾6 245-01/$1 ▾a 삼국사기 ...
880 로마자 페어:  880 10 ▾6 245-01/(B ▾a Samguk sagi ...
```

`$1` = CJK 한자 스크립트, `(B` = ASCII 로마자.

#### 자동 생성 의사코드 (`vernacular/field_880.py` 정합)

```python
PAIRABLE_TAGS = {"100", "245", "246", "490", "505", "700"}

def add_880_pairs(record: Record, *, romanize: str = "RR") -> int:
    """한자 감지 → 880 페어 자동.

    Args:
        romanize: "RR" (Revised Romanization, 기본·NLK 2021 지침)
                  "MR" (McCune-Reischauer, 학술·국제)
    """
    pair_count = 0
    for tag in PAIRABLE_TAGS:
        for field in record.get_fields(tag):
            has_any_hanja = any(has_hanja(sf.value) for sf in field.subfields)
            if not has_any_hanja:
                continue

            pair_count += 1
            link_no = f"{pair_count:02d}"

            # 1) 원본 필드에 ▾6 880-NN 추가 (pos=0 = 첫 서브필드)
            field.add_subfield(code="6", value=f"880-{link_no}", pos=0)

            # 2) 880 한글 페어 (한자 → 한글 변환)
            hangul_subfields = [Subfield("6", f"{tag}-{link_no}/$1")]
            for sf in field.subfields:
                if sf.code == "6":
                    continue
                converted = hanja_to_hangul(sf.value) if has_hanja(sf.value) else sf.value
                hangul_subfields.append(Subfield(sf.code, converted))
            record.add_field(Field(tag="880", indicators=field.indicators, subfields=hangul_subfields))

            # 3) 880 로마자 페어 (옵션 — RR 또는 MR)
            if romanize:
                roman_subfields = [Subfield("6", f"{tag}-{link_no}/(B")]
                for sf in field.subfields:
                    if sf.code == "6":
                        continue
                    roman = hangul_to_romaji(hanja_to_hangul(sf.value), scheme=romanize)
                    roman_subfields.append(Subfield(sf.code, roman))
                record.add_field(Field(tag="880", indicators=field.indicators, subfields=roman_subfields))

    return pair_count
```

NLK 「서지데이터 로마자 표기 지침(2021)」 정합:
- **RR (Revised Romanization)**: 기본. 한글 발음 그대로 (예: 김철수 → Kim Cheolsu)
- **MR (McCune-Reischauer)**: 학술·국제. ALA-LC 표준 (예: 김철수 → Kim Ch'ŏlsu)

### 1.8 049 자관 청구기호 (등록번호·복본·별치·권차)

KORMARC 049는 한국 특수. 자관 정책에 따라 prefix·자릿수 변형 가능 (정책 ③).

| 서브필드 | 의미 | 예시 | 자관 정책 |
|---|---|---|---|
| ▾l | 등록번호 | EM01260012345 | 정책 ③ — `config.yaml.kolas_register.registration_prefix` 자관별 |
| ▾c | 복본기호 | c.1, c.2, c.3 | 자동 |
| ▾f | 별치기호 | EB(전자책)·R(참고)·J(어린이)·Y(청소년)·GO(고서)·K(향토)·L(장학) | KDC + 부가기호 매핑 |
| ▾v | 권차기호 | v.1, v.2, v.3 | 다권물 자동 |

자관 (내숲) prefix 정책 (헌법 §13): EQ(일반) / CQ(아동) — 다른 도서관은 EM(일반)·BM(별치)·AM(아동)·CM(연속)으로 변형.

등록번호 12자리 알파스 표준 (`librarian_helpers/registration.py`):

```
EM 01 26 00012345
│  │  │  └─ 일련번호 5자리
│  │  └─ 연도 2자리 (2026)
│  └─ 차수 2자리 (1차 등록)
└─ 등록구분 2자리 (Each Material 일반)
```

자관 청구기호 형식 (헌법 §13):

```
{별치}{KDC분류}/{이재철 도서기호}
예: 시문학811.7/ㅇ676ㅁ
    ├ 별치   = 시문학
    ├ KDC    = 811.7 (한국 시)
    ├ /      = 구분자
    └ 도서기호 = ㅇ676ㅁ (이재철 한국 저자기호표)
```

### 1.9 핵심 17 필드 의사코드 풀세트

#### 040 — 목록작성기관 (M)

```python
record.add_field(Field(
    tag="040", indicators=Indicators(" ", " "),
    subfields=[
        Subfield("a", config.cataloging_agency),    # OURLIB·211009 등
        Subfield("b", "kor"),                        # 사용 언어
        Subfield("c", config.cataloging_agency),    # 편목기관 = 자기 자신
        Subfield("d", config.cataloging_agency),    # 수정기관 (수정 시 추가)
    ],
))
```

#### 041 — 본문 언어 (A — 다국어 시 적용)

```python
languages = book_data.get("languages") or []
if isinstance(languages, list) and len(languages) > 1:
    subfields = [Subfield("a", lang) for lang in languages[:5]]
    if book_data.get("original_language"):
        subfields.append(Subfield("h", book_data["original_language"]))   # 원작 언어
    record.add_field(Field(tag="041", indicators=Indicators("0", " "), subfields=subfields))
    # ind1: 0=원작·1=번역
```

#### 100 — 주표목 (개인저자, M if 개인저자)

```python
primary_author = _split_first_author(book_data.get("author") or "")
if primary_author:
    subfields = [Subfield("a", primary_author)]
    if book_data.get("birth_year"):
        subfields.append(Subfield("d", f"{book_data['birth_year']}-"))
    if book_data.get("author_role"):
        subfields.append(Subfield("e", book_data["author_role"]))   # 지음·역·편 등
    record.add_field(Field(tag="100", indicators=Indicators("1", " "), subfields=subfields))
    # ind1: 0=성·1=성+이름·3=가족명
```

#### 245 — 표제 + 책임표시 (M, 위 §1.5 참조)

#### 246 — 변형표제 (O)

```python
if book_data.get("alternative_title"):
    record.add_field(Field(
        tag="246", indicators=Indicators("3", " "),    # ind1: 1=주기 자동·3=주기 없음
        subfields=[Subfield("a", book_data["alternative_title"])],
    ))
```

#### 250 — 판차 (A — 2판 이상 시 필수)

```python
if book_data.get("edition"):
    record.add_field(Field(
        tag="250", indicators=Indicators(" ", " "),
        subfields=[Subfield("a", str(book_data["edition"]))],   # "2판", "개정증보판"
    ))
```

#### 260/264 — 발행사항 (M — 264 권장)

```python
# RDA 2023 — 264 권장 (260 deprecated)
pub_subfields = []
if place:                       pub_subfields.append(Subfield("a", f"{place} :"))
if book_data.get("publisher"):  pub_subfields.append(Subfield("b", f"{book_data['publisher']},"))
if book_data.get("publication_year"):
    pub_subfields.append(Subfield("c", str(book_data["publication_year"])))

record.add_field(Field(tag="264", indicators=Indicators(" ", "1"), subfields=pub_subfields))
# ind2: 0=제작·1=발행·2=배포·3=인쇄·4=저작권
```

#### 300 — 형태사항 (M)

```python
extent = []
if book_data.get("pages"):
    pages = str(book_data["pages"]).strip()
    if pages.isdigit():
        pages = f"{pages} p."
    extent.append(Subfield("a", pages))
if book_data.get("illustrations"):
    extent.append(Subfield("b", "삽화"))
if book_data.get("book_size"):
    size = str(book_data["book_size"]).strip()
    if size.isdigit():
        size = f"{size} cm"
    extent.append(Subfield("c", size))
if book_data.get("accompanying"):    # 부록 (CD-ROM 1매)
    extent.append(Subfield("e", book_data["accompanying"]))
record.add_field(Field(tag="300", indicators=Indicators(" ", " "), subfields=extent))
```

#### 440/490 — 총서사항 (A — 총서 있을 시)

```python
if book_data.get("series_title"):
    series_subfields = [Subfield("a", str(book_data["series_title"]))]
    if book_data.get("series_no"):
        series_subfields.append(Subfield("v", str(book_data["series_no"])))
    record.add_field(Field(
        tag="490", indicators=Indicators("1", " "), subfields=series_subfields))
    # ind1: 0=부출 안 함·1=부출 함 (800·830으로 별도 부출)
    # 부출 함이면 800/830 자동 생성 (작가 + 총서)
    if book_data.get("series_creator"):
        record.add_field(Field(
            tag="800", indicators=Indicators("1", " "),
            subfields=[
                Subfield("a", book_data["series_creator"]),
                Subfield("t", book_data["series_title"]),
            ]))
```

#### 500/502/504/505/520 — 주기 (O / A 학위논문은 502 M)

```python
# 500 일반주기
if book_data.get("general_note"):
    record.add_field(Field(tag="500", indicators=Indicators(" ", " "),
        subfields=[Subfield("a", str(book_data["general_note"])[:1000])]))

# 502 학위논문 주기 (학위논문 자료유형이면 M)
if material_type == "thesis":
    thesis_subfields = []
    thesis_subfields.append(Subfield("a", book_data.get("degree_type", "박사학위논문")))
    if book_data.get("granting_institution"):
        thesis_subfields.append(Subfield("c", book_data["granting_institution"]))
    if book_data.get("degree_year"):
        thesis_subfields.append(Subfield("d", str(book_data["degree_year"])))
    record.add_field(Field(tag="502", indicators=Indicators(" ", " "), subfields=thesis_subfields))

# 504 서지·색인 주기
if book_data.get("bibliography_note"):
    record.add_field(Field(tag="504", indicators=Indicators(" ", " "),
        subfields=[Subfield("a", str(book_data["bibliography_note"])[:500])]))

# 505 내용주기 (목차)
if book_data.get("toc"):
    toc_clean = str(book_data["toc"]).replace("\n", " -- ")[:2000]
    record.add_field(Field(tag="505", indicators=Indicators("0", " "),
        subfields=[Subfield("a", toc_clean)]))
    # ind1: 0=완전·1=불완전·2=부분

# 520 요약·초록
if book_data.get("summary"):
    record.add_field(Field(tag="520", indicators=Indicators(" ", " "),
        subfields=[Subfield("a", str(book_data["summary"])[:2000])]))
```

#### 650 — 일반주제명 (NLSH, O)

```python
for subject in book_data.get("subjects", []):
    record.add_field(Field(
        tag="650", indicators=Indicators(" ", "8"),    # ind2: 8 = NLSH (한국 표준)
        subfields=[Subfield("a", subject)],
    ))
# ind2 의미:
# 0 = LCSH (미국)
# 1 = LC 어린이 (미국)
# 2 = MeSH (의학)
# 4 = 비통제·자체
# 7 = 출처 ▾2 명시
# 8 = NLSH (한국 표준 ★)
```

#### 700 — 부출표목 (O)

```python
additional_authors = _split_additional_authors(book_data.get("author") or "")
for add_author in additional_authors[:3]:
    subfields = [Subfield("a", add_author)]
    if "역" in add_author or "옮긴이" in add_author:
        subfields.append(Subfield("e", "옮김"))
    elif "편" in add_author:
        subfields.append(Subfield("e", "편"))
    record.add_field(Field(tag="700", indicators=Indicators("1", " "), subfields=subfields))
```

#### 856 — 전자자료 URL (A — 전자자료 시 M)

```python
if book_data.get("url"):
    record.add_field(Field(
        tag="856", indicators=Indicators("4", "0"),    # ind1: 4=HTTP, ind2: 0=직접접근
        subfields=[
            Subfield("u", str(book_data["url"])),
            Subfield("y", str(book_data.get("url_label") or "전자자료")),
            Subfield("z", "공공도서관 회원만 이용 가능") if book_data.get("restricted") else None,
        ],
    ))
```

#### 880 — 한자/로마자 병기 (A — 한자 감지 시 자동, 위 §1.7)

---

## 2. MARC21 호환 + BIBFRAME + MODS XML

### 2.1 KORMARC ↔ MARC21 매핑 차이

`conversion/marc21.py` 정합:

| 한국 특수 (KORMARC만) | MARC21 등가 | 비고 |
|---|---|---|
| 049 청구기호 (▾l ▾c ▾f ▾v) | 852 (소장정보) | LC·BL이 049 무시 가능 → 852 권장 |
| 056 KDC | 082 DDC | 분류 체계 다름 — 직접 변환 불가 |
| 950 가격 | 020 ▾c 또는 037 ▾c | MARC21은 020에 포함 |
| 953 (한국 특수 코드) | (등가 X) | 보존만 |
| 880 ▾6 = `(B` 로마자 | 동일 | MARC21도 880 표준 |
| 245 2지시기호 = 관제 길이 | 동일 의미 | 정렬 무시 글자수 |

| MARC21 특수 (KORMARC X) | KORMARC 등가 | 비고 |
|---|---|---|
| 050 LCC | (등가 X) | KORMARC는 LCC 사용 안 함 |
| 090 LC 자관 청구 | 049 | KORMARC는 049로 통일 |
| 650 ▾2 lcsh | 650 ▾2 nlsh + ind2=8 | 주제명 표준 다름 |

변환 의사코드:

```python
def kormarc_to_marc21(record: Record, *, drop_korea_specific: bool = False) -> Record:
    """KORMARC → MARC21. 049·950 등 한국 특수 보존 또는 제거."""
    new_record = Record(force_utf8=True, leader=str(record.leader))
    KOREA_SPECIFIC_TAGS = {"049", "950", "953", "956"}

    for field in record.fields:
        if drop_korea_specific and field.tag in KOREA_SPECIFIC_TAGS:
            continue

        # 049 → 852 변환 (선택적)
        if field.tag == "049" and not drop_korea_specific:
            new_record.add_field(field)        # 보존
            new_record.add_field(_049_to_852(field))   # 852 추가
        # 056 KDC → 082 DDC 변환은 불가 (분류 체계 다름)
        # 사서가 별도 082 DDC 추가하도록 안내만
        else:
            new_record.add_field(field)

    return new_record


def get_conversion_warnings(record: Record, target: str) -> list[str]:
    """변환 시 사서가 알아야 할 경고."""
    warnings = []
    if target == "marc21":
        if record.get_fields("049"):
            warnings.append("049 청구기호는 한국 특수 — LC·BL은 무시할 수 있음 (852로 대체 권장)")
        if record.get_fields("950"):
            warnings.append("950 가격은 한국 특수 — MARC21에선 020 ▾c 권장")
        if record.get_fields("056") and not record.get_fields("082"):
            warnings.append("056 KDC만 있고 082 DDC 없음 — MARC21 도서관은 DDC 선호")
    return warnings
```

### 2.2 BIBFRAME 2.0 변환 (Work · Instance · Item)

KORMARC = MARC21 호환 → BIBFRAME = LC가 추진하는 차세대 시맨틱 웹 표준. KORMARC 2023.12 개정의 "시맨틱 웹·링크드 데이터" 정합.

| BIBFRAME 클래스 | KORMARC 매핑 | 의미 |
|---|---|---|
| **bf:Work** | 100 + 245 ▾a + 240 (통일표제) + 765 (원작) | 추상적 저작 (사상·내용) |
| **bf:Instance** | 020 + 245 + 250 + 264 + 300 + 336/337/338 | 물리적 표현 (특정 판본) |
| **bf:Item** | 049 + 852 + 876 | 개별 책 (등록번호 가진 1권) |
| bf:Agent | 100/110/111/700/710/711 | 사람·단체·회의 |
| bf:Topic | 650 | 주제 |
| bf:Place | 264 ▾a | 발행지 |

변환 의사코드 (Phase 2~3 후보):

```python
def kormarc_to_bibframe(record: Record) -> dict:
    """KORMARC → BIBFRAME 2.0 RDF (JSON-LD)."""
    work_uri    = f"http://example.org/work/{_uuid()}"
    instance_uri = f"http://example.org/instance/{_uuid()}"

    work = {
        "@id": work_uri,
        "@type": "bf:Work",
        "bf:title": _extract_245a(record),
        "bf:contribution": [
            {"@type": "bf:Contribution", "bf:agent": _100_to_agent(f)}
            for f in record.get_fields("100", "110", "111")
        ],
        "bf:subject": [{"@type": "bf:Topic", "rdfs:label": _650a(f)}
                       for f in record.get_fields("650")],
    }
    instance = {
        "@id": instance_uri,
        "@type": "bf:Instance",
        "bf:instanceOf": {"@id": work_uri},
        "bf:identifiedBy": [{"@type": "bf:Isbn", "rdf:value": _020a(record)}],
        "bf:provisionActivity": _264_to_provision(record),
        "bf:extent": _300_to_extent(record),
    }
    return {"@graph": [work, instance], "@context": BIBFRAME_CONTEXT}
```

### 2.3 MODS XML 변환 (NLK 온라인자료과 5 자료유형 표준)

MODS = Metadata Object Description Schema (LC). NLK 온라인자료과가 디지털 컬렉션 표준으로 채택. 5 자료유형 한정:

| MODS 자료유형 | KORMARC 자료유형 | NLK 지침 PDF | 우리 모듈 |
|---|---|---|---|
| 멀티미디어 | non_book / multimedia | 자관 보유 (2023) | `kormarc/multimedia.py` |
| 오디오북 | audiobook | 자관 보유 (2023) | `kormarc/audiobook.py` |
| 전자저널 | ejournal | 자관 보유 | `kormarc/ejournal.py` |
| 전자책 | ebook | 자관 보유 (2023) | `kormarc/ebook.py` |
| 학위논문 | thesis | 자관 보유 (2023) | `kormarc/thesis.py` |

KORMARC ↔ MODS 핵심 매핑:

| KORMARC | MODS XML |
|---|---|
| 245 ▾a | `<mods:title>` |
| 245 ▾b | `<mods:subTitle>` |
| 245 ▾c | `<mods:statementOfResponsibility>` |
| 100 ▾a | `<mods:name type="personal"><mods:namePart>` |
| 264 ▾a | `<mods:originInfo><mods:place>` |
| 264 ▾b | `<mods:originInfo><mods:publisher>` |
| 264 ▾c | `<mods:originInfo><mods:dateIssued>` |
| 300 ▾a | `<mods:physicalDescription><mods:extent>` |
| 020 ▾a | `<mods:identifier type="isbn">` |
| 056 ▾a | `<mods:classification authority="kdc">` |
| 650 ▾a | `<mods:subject><mods:topic>` |
| 856 ▾u | `<mods:location><mods:url>` |

### 2.4 LOD/링크드 데이터 연계

| 외부 LOD | 연계 방식 | 우리 정합 |
|---|---|---|
| **KOLIS-NET** | 통합 목록 5종 API (위 §3) | ✅ `api/kolisnet_compare.py` |
| **BIBFRAME (LC)** | 위 §2.2 변환 | 🟡 Phase 2~3 |
| **VIAF** (전거 통합) | 100 ▾0 → URI | 🟡 Phase 2~3 |
| **Wikidata** | Q번호 매핑 | 🔴 Phase 4+ |
| **DBpedia** | 작가·작품 sameAs | 🔴 Phase 4+ |

---

## 3. 외부 시스템 import/export 포맷

### 3.1 KOLAS III — F12 엑셀 9 컬럼 + .mrc ISO 2709

KOLAS III 핵심 단축키:
- **F11**: 그리드 환경설정
- **F12**: 책두레 엑셀출력 (★ 우리 자동화 핵심 진입점)

#### F12 엑셀 9 컬럼 정밀 스펙

자관 5년 .xlsm 매크로 1,328 파일 분석 결과 (헌법 §10 + `chaekdanbi-workflow-audit.md`):

| # | 컬럼명 | 형식 | 예시 |
|---:|---|---|---|
| 1 | 신청번호 | 문자 (자관 자동) | 20260429-001 |
| 2 | 신청일자 | YYYY-MM-DD | 2026-04-29 |
| 3 | 등록번호 | 12자리 (EQ/CQ prefix) | EQ01260012345 |
| 4 | 서명 | 텍스트 (한자 가능) | 작별하지 않는다 |
| 5 | 저자 | 텍스트 | 한강 지음 |
| 6 | 출판사 | 텍스트 | 문학동네 |
| 7 | 발행년도 | YYYY | 2021 |
| 8 | 청구기호 | KDC + 도서기호 | 813.7/ㅎ225ㅈ |
| 9 | 비고 | 텍스트 | (만료/반납/제공/지하철) |

#### 등록번호 12자리 EQ/CQ prefix 규칙

자관 (내숲) 정책 ③ — 다른 도서관은 EM·BM·AM·CM 등 자유 변형:

```python
REGISTRATION_FORMAT = re.compile(
    r"^(?P<kind>[A-Z]{2,3})"      # EQ·CQ·EM·BM·AM·CM (등록구분)
    r"(?P<turn>\d{2})"             # 차수 (1~99)
    r"(?P<year>\d{2})"             # 연도 (2자리)
    r"(?P<serial>\d{4,6})$"       # 일련번호 (4~6자리)
)

KIND_MEANING = {
    "EQ": "일반 (자관 prefix·내숲)",
    "CQ": "아동 (자관 prefix·내숲)",
    "EM": "Each Material 일반 (알파스 표준)",
    "BM": "별치 (Branch)",
    "AM": "아동 (Adolescent)",
    "CM": "연속간행물 (Continuous)",
}
```

#### .mrc ISO 2709 형식

KOLAS III 자동 반입 규칙: **파일명이 ISBN과 동일하면 자동 인식**.

`output/kolas_writer.py` 정합:

```python
def write_kolas_mrc(record: Record, isbn: str, *, output_dir: Path) -> Path:
    """KORMARC → KOLAS 자동 반입 .mrc.

    - 파일명 = {ISBN}.mrc (KOLAS 자동 인식)
    - 인코딩 = UTF-8 (KOLAS III 유니코드 3.0 기반)
    - 형식   = ISO 2709 (pymarc.Record.as_marc())
    """
    isbn_clean = "".join(c for c in isbn if c.isdigit())
    if len(isbn_clean) != 13:
        raise ValueError(f"ISBN은 13자리: {isbn}")

    out_path = output_dir / f"{isbn_clean}.mrc"
    out_path.write_bytes(record.as_marc())     # ISO 2709 binary
    return out_path
```

### 3.2 알파스 (ALPAS) — KOLAS3 호환 + 책밴드 + 일일 03:00 백업

| 항목 | 정보 |
|---|---|
| 운영 | (주)이씨오 SaaS |
| 인프라 | 카카오클라우드 IaaS·99.5% uptime |
| 백업 | 일일 03:00 자동 |
| 호환 | KOLAS3 호환·책이음 동기화·책밴드 자체 상호대차 |
| 등록번호 | 12자리 (EM/BM/AM/CM prefix·자관 정책) |

알파스 import/export:
- ✅ MARCXML export로 알파스 import 호환
- ✅ 우리 .mrc → 알파스 마크 반입 직접 가능
- 영업 메시지: "KOLAS·알파스 모두 호환"

### 3.3 KERIS DLS / 독서로DLS

| 항목 | 정보 |
|---|---|
| 학교도서관 수 | **12,200관** (2024 기준) |
| 사서교사 배치율 | **13.9%** (1,660명) |
| 자원봉사 비율 | **86%** |
| 시스템 | 2024년 DLS와 통합 (KERIS + 17 시·도교육청) |
| import 형식 | MARCXML + .mrc (ISO 2709) |
| export 형식 | DLS 자체 양식 (XML) |

핵심 페인포인트: 86%가 자원봉사 = MARC 작업 부담 ↑ → 우리 SaaS 1순위 ICP.

### 3.4 KOLIS-NET 통합 목록 5종 API

NLK 운영 전국 2,000여 도서관 통합 목록.

| API | 용도 | 우리 정합 |
|---|---|---|
| 종합목록 검색 | 전국 도서관 보유 자료 검색 | ✅ `api/_http.py` 폴백 2순위 |
| 사서추천 | NLK 사서가 추천한 도서 | 🟡 Phase 1.5 |
| 출판예정 | 출간 예정 도서 (예약수서) | 🟡 Phase 4 |
| 소장자료 | 특정 도서관 소장 여부 | 🟡 Phase 4 |
| 국가서지 | NLK 공식 서지 | 🟡 Phase 1.5 |

### 3.5 5 상호대차 양식 어댑터

`interlibrary/exporters.py` 정합 + `docs/interlibrary-5systems-comparison.md`:

| 시스템 | 운영 | 비용 | 양식 컬럼 | 우리 어댑터 |
|---|---|---|---|---|
| **책바다** | NLK | 5,200원/책 | 11 (서명·저자·...) | ✅ `chaekbada_csv` |
| **책나래** | NLD | 무료 (장애인) | 13 (도서명·저자·...) | ✅ `chaeknarae_csv` |
| **책이음** | NLK | 무료 (회원증) | (회원 영역·우리 X) | 🔴 |
| **책두레** | NLK (KOLAS III 모듈) | 무료 | KOLAS F12 9 컬럼 | ✅ `kolas_f12` |
| **책단비** | 은평구 한정 | 무료 | 자관 hwp 4 양식 | ✅ `chaekdanbi_hwp` (Phase 1) |

핵심 어댑터 의사코드:

```python
def export_interlibrary(book_list: list[dict], system: str, output_path: Path) -> Path:
    """5 상호대차 시스템별 양식 자동 변환."""
    ADAPTERS = {
        "chaekbada":   (CHAEKBADA_COLUMNS,  _book_to_chaekbada_row),
        "chaeknarae":  (CHAEKNARAE_COLUMNS, _book_to_chaeknarae_row),
        "kolas_f12":   (KOLAS_F12_COLUMNS,  _book_to_kolas_f12_row),
        "chaekdanbi":  (None,                _book_to_chaekdanbi_hwp),    # hwp mail merge
        "riss":        (RISS_COLUMNS,       _book_to_riss_row),
    }
    columns, row_func = ADAPTERS[system]

    if system == "chaekdanbi":
        return row_func(book_list, output_path)    # hwp 별도 처리

    # CSV/XLSX 공통 처리
    rows = [row_func(book) for book in book_list]
    if output_path.suffix == ".xlsx":
        _write_xlsx(output_path, columns, rows)
    else:
        _write_csv(output_path, columns, rows)
    return output_path
```

---

## 4. 외부 API 폴백 전략 정밀화

### 4.1 6 폴백 + 신뢰도 가중

| # | API | URL | 신뢰도 | timeout | 캐시 TTL |
|---:|---|---|---:|---:|---:|
| 1 | NL Korea ISBN | `https://www.nl.go.kr/seoji/SearchApi.do` | **0.95** | 10s | 7일 |
| 2 | KOLIS-NET 종합목록 | `https://www.nl.go.kr/NL/search/openApi/searchKolisNet.do` | **0.92** | 10s | 7일 |
| 3 | 도서관 정보나루 | `http://data4library.kr/api/srchBooks` | **0.85** | 10s | 7일 |
| 4 | 알라딘 (출처 표시 의무 ★) | `http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx` | **0.80** | 10s | 7일 |
| 5 | 카카오 책 검색 | `https://dapi.kakao.com/v3/search/book` | **0.75** | 10s | 7일 |
| 6 | Claude Vision (사진) | `https://api.anthropic.com/v1/messages` | **0.65** | 30s | 30일 |

### 4.2 신뢰도 가중 통합 알고리즘

`api/aggregator.py` 정합 + 정밀화:

```python
FIELD_PRIORITY: dict[str, list[str]] = {
    "title":            ["nl_korea", "kolisnet", "data4library", "aladin", "kakao"],
    "author":           ["nl_korea", "kolisnet", "data4library", "aladin", "kakao"],
    "publisher":        ["nl_korea", "kolisnet", "aladin", "kakao"],
    "publication_year": ["nl_korea", "kolisnet", "aladin"],
    "kdc":              ["nl_korea"],            # NLK가 1순위·다른 소스는 신뢰도 낮음
    "ddc":              ["nl_korea"],
    "summary":          ["aladin", "nl_korea", "kakao"],   # 알라딘이 풍부
    "toc":              ["aladin", "nl_korea"],
    "cover_url":        ["aladin", "kakao"],
    "price":            ["nl_korea", "aladin"],
    "pages":            ["nl_korea"],
    "book_size":        ["nl_korea"],
    "series_title":     ["nl_korea", "aladin"],
    "additional_code":  ["nl_korea"],            # 부가기호 5자리는 NLK만
}

def aggregate_by_isbn(isbn: str) -> dict:
    """6 폴백 + 신뢰도 가중 통합."""
    results: dict[str, dict] = {}

    # 1순위: NL Korea (KORMARC 표준 - 한국 자료)
    try:
        r = nl_korea.fetch_by_isbn(isbn)        # timeout=10
        if r: results["nl_korea"] = r
    except nl_korea.NLKoreaAPIError as e:
        logger.warning("NL Korea 실패, 폴백: %s", e)

    # 2순위: KOLIS-NET (다른 도서관 검증 데이터)
    try:
        r = kolisnet.fetch_by_isbn(isbn)
        if r: results["kolisnet"] = r
    except KolisNetError as e:
        logger.warning("KOLIS-NET 실패, 폴백: %s", e)

    # 3순위: 도서관 정보나루 (키워드 + 인기 통계)
    if "title" not in _aggregate_titles(results):
        try:
            r = data4library.fetch_by_isbn(isbn)
            if r: results["data4library"] = r
        except Data4LibraryError as e:
            logger.warning("정보나루 실패: %s", e)

    # 4순위: 알라딘 (출처 표시 의무 ★)
    try:
        r = aladin.fetch_by_isbn(isbn)
        if r:
            results["aladin"] = r
            # 알라딘 출처 표시 의무 (헌법 §4.1)
            r["attribution"] = "도서 DB 제공 : 알라딘 인터넷서점"
    except aladin.AladinAPIError as e:
        logger.warning("알라딘 실패: %s", e)

    # 5순위: 카카오 (NL+알라딘 모두 실패 시만 — 한도 절약)
    if not results:
        try:
            r = kakao.fetch_by_isbn(isbn)
            if r: results["kakao"] = r
        except KakaoAPIError:
            pass

    if not results:
        return {"isbn": isbn, "sources": [], "confidence": 0.0,
                "source_map": {}, "attributions": []}

    merged = _merge_by_priority(results)
    merged["isbn"] = isbn
    merged["sources"] = list(results.keys())
    merged["confidence"] = max(r["confidence"] for r in results.values())
    merged["attributions"] = [r["attribution"] for r in results.values() if r.get("attribution")]
    return merged


def _merge_by_priority(results: dict) -> dict:
    """필드별 우선순위 + source_map."""
    merged = {}
    source_map = {}
    all_fields = set().union(*(r.keys() for r in results.values()))
    all_fields -= {"source", "confidence", "attribution", "raw"}

    for field in all_fields:
        priority = FIELD_PRIORITY.get(field, list(results.keys()))
        for source in priority:
            if source in results:
                value = results[source].get(field)
                if value not in (None, "", [], {}):
                    merged[field] = value
                    source_map[field] = source       # ★ 출처 추적 (헌법 §4.2)
                    break
    merged["source_map"] = source_map
    return merged
```

### 4.3 timeout/재시도/디스크캐시

```python
# constants.py
HTTP_TIMEOUT_SECONDS = 10           # 헌법 §4.2 ★
HTTP_RETRIES = 3
HTTP_BACKOFF_FACTOR = 0.5
CACHE_TTL_SECONDS = 60 * 60 * 24 * 7    # 7일

# api/_http.py — tenacity + diskcache
@retry(
    stop=stop_after_attempt(HTTP_RETRIES),
    wait=wait_exponential(multiplier=HTTP_BACKOFF_FACTOR, max=10),
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
)
def http_get(url: str, params: dict, *, cache_key: str) -> dict:
    """공유 HTTP — timeout 강제 + 재시도 + 디스크 캐시 7일."""
    cache = get_disk_cache()
    if cache_key in cache:
        return cache[cache_key]

    response = requests.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    cache.set(cache_key, data, expire=CACHE_TTL_SECONDS)
    return data
```

### 4.4 비용·정확도 최적화 의사코드

```python
def cost_optimized_fetch(isbn: str) -> dict:
    """비용 최소화 — NL Korea·KOLIS-NET 무료 → 알라딘·카카오 무료 한도 → Vision 유료 마지막."""
    # Phase 1: 무료 API (정부 운영)
    for api in [nl_korea, kolisnet]:
        try:
            r = api.fetch_by_isbn(isbn)
            if r and r.get("confidence", 0) > 0.85:
                return r                # 신뢰도 충분 → 즉시 반환·비용 0
        except APIError:
            continue

    # Phase 2: 무료 한도 API (상용)
    for api in [data4library, aladin, kakao]:
        try:
            r = api.fetch_by_isbn(isbn)
            if r and r.get("confidence", 0) > 0.75:
                return r                # 무료 한도 내 → 비용 ≈ 0
        except APIError:
            continue

    # Phase 3: 유료 (Vision) — 마지막 수단
    if has_image_input():
        return claude_vision_fetch(isbn)    # 권당 약 2원

    return {"isbn": isbn, "confidence": 0.0}
```

---

## 5. AI 결정 보조 (사서 책임 영역 침범 금지)

**원칙**: AI는 **후보**만 제시. 최종 결정은 사서. 헌법 §0 "100% 자동화 약속 금지".

### 5.1 KDC 6판 후보 3개

`classification/kdc_classifier.py` 정합:

```python
_KDC_TOOL = {
    "name": "recommend_kdc_codes",
    "description": "KDC 6판 분류기호 후보 3개를 신뢰도 순으로 추천한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "candidates": {
                "type": "array", "minItems": 1, "maxItems": 3,
                "items": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "KDC 6판 (예: 813.7)"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "rationale": {"type": "string", "description": "1~2문장 추천 이유"},
                    },
                    "required": ["code", "confidence", "rationale"],
                },
            }
        },
        "required": ["candidates"],
    },
}

def recommend_kdc(book_data: dict, api_key: str) -> list[dict]:
    """1. NL Korea가 KDC 부여 → 신뢰도 0.95 (즉시 반환).
    2. ISBN 부가기호 첫 자리 → 주류 매핑 (보조, 신뢰도 0.40).
    3. 두 가지 부족 시 Claude AI 후보 3개."""
    if book_data.get("kdc"):
        return [{"code": book_data["kdc"], "confidence": 0.95, "rationale": "NL Korea 부여"}]

    candidates = []
    if book_data.get("additional_code"):
        first = book_data["additional_code"][0]
        kdc_main = ADDITIONAL_CODE_TO_KDC_MAIN.get(first)
        if kdc_main:
            candidates.append({"code": kdc_main, "confidence": 0.40, "rationale": "ISBN 부가기호 매핑"})

    # Claude AI 호출 (BYOK)
    response = cached_messages(
        model=DEFAULT_TEXT_MODEL,
        system=KDC_SYSTEM_PROMPT,         # cache_control: ephemeral
        messages=[{"role": "user", "content": f"메타데이터: {json.dumps(book_data, ensure_ascii=False)}"}],
        tools=[_KDC_TOOL],
        api_key=api_key,
    )
    ai_candidates = response["candidates"][:3]
    return ai_candidates + candidates       # AI 후보 + 부가기호 보조
```

### 5.2 주제명 NLSH (650) 후보

```python
def recommend_subjects(book_data: dict, api_key: str) -> list[dict]:
    """650 NLSH 주제명 후보 (사서 선택)."""
    response = cached_messages(
        model=DEFAULT_TEXT_MODEL,
        system=SUBJECT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"제목: {book_data['title']}\n요약: {book_data.get('summary', '')[:500]}"}],
        tools=[_SUBJECT_TOOL],          # NLSH 통제어 후보 5개
        api_key=api_key,
    )
    return response["subjects"]         # [{"term": "한국 소설", "confidence": 0.85}, ...]
```

### 5.3 Vision 2단계 (Haiku ISBN → Sonnet 종합)

`vision/photo_pipeline.py` 정합:

```python
def vision_pipeline(image_bytes: bytes, api_key: str) -> dict:
    """2단계 비용 최적화.

    Stage 1 (Haiku — 저렴): 표지 이미지에서 ISBN 바코드만 추출.
    Stage 2 (Sonnet — 정확): ISBN 없으면 표지·판권지·목차 종합 분석.
    """
    # Stage 1: Haiku (₩0.5/이미지)
    isbn_response = cached_messages(
        model="claude-haiku-4-7",
        system="이미지에서 ISBN-13 바코드만 추출. 다른 정보 X.",
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": _b64(image_bytes)}}
        ]}],
        tools=[_ISBN_EXTRACT_TOOL],
        api_key=api_key,
    )
    isbn = isbn_response.get("isbn")

    if isbn and validate_isbn13(isbn):
        # ISBN 추출 성공 → 외부 API 폴백으로 이동 (비용 절감)
        return aggregate_by_isbn(isbn)

    # Stage 2: Sonnet (₩2/이미지·종합 분석)
    return cached_messages(
        model="claude-sonnet-4-7",
        system=VISION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": _b64(image_bytes)}}
        ]}],
        tools=[_BOOK_METADATA_TOOL],     # title·author·publisher·year·KDC 후보
        api_key=api_key,
    )
```

### 5.4 prompt caching (Anthropic SDK)

`_anthropic_client.py` 정합:

```python
def cached_messages(*, model: str, system: str, messages: list, tools: list, api_key: str) -> dict:
    """prompt caching = system 프롬프트 재사용 → 90% 비용 절감.

    cache_control: {"type": "ephemeral"} 자동 부여.
    """
    client = _build_client(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=ANTHROPIC_DEFAULT_MAX_TOKENS,
        system=[
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}    # ★ 캐싱
        ],
        messages=messages,
        tools=tools,
        timeout=ANTHROPIC_TIMEOUT_SECONDS,      # 헌법 §4.2 ★
    )

    # tool_use 응답 자동 파싱
    for block in response.content:
        if block.type == "tool_use":
            return block.input

    return {}
```

비용 영향:
- system 프롬프트 (KORMARC 가이드 + 도메인 컨텍스트) ≈ 5,000 tokens
- cache_control 적용 시: 입력 cost 90% 절감 ($0.30 → $0.03 / 1M tokens)
- Phase 3 사서 1명 월 500권 사용 시: 권당 비용 ₩2 → ₩0.5

---

## 6. 검증 4단

### 6.1 어셔션 (binary_assertions.py 18종)

`scripts/binary_assertions.py` 정합 — 매 commit 직후 자동:

| # | 어셔션 | 검증 |
|---:|---|---|
| 1 | 008 길이 = 40 | `validator.py:validate_008` |
| 2 | ISBN-13 체크섬 | `validator.py:validate_isbn13` |
| 3 | 245 ▾a 존재 | `validator.py:validate_record` |
| 4 | 040 ▾a 자관 부호 | `builder.py:add_040` |
| 5 | 020 ▾g 5자리 | `mapping.py:parse_020` |
| 6 | 한자 감지 → 880 페어 | `field_880.py:add_880_pairs` |
| 7 | 알라딘 사용 시 attribution | `aggregator.py:attributions` |
| 8 | timeout=10 모든 외부 호출 | `_http.py + grep` |
| 9 | 자료유형별 LDR 분기 | `material_type.py:build_leader` |
| 10 | 264 ind2 = 1 (발행) | `builder.py:add_264` |
| 11 | 336/337/338 RDA 존재 | `builder.py:add_rda` |
| 12 | KDC 6판 (▾2 = 6) | `builder.py:add_056` |
| 13 | 650 ind2 = 8 (NLSH) | `builder.py:add_650` |
| 14 | source_map 모든 필드 | `aggregator.py:_merge_by_priority` |
| 15 | confidence ∈ [0, 1] | `aggregator.py:aggregate_by_isbn` |
| 16 | 049 12자리 등록번호 | `registration.py:parse_registration_number` |
| 17 | 502 학위논문 자료유형 시 | `thesis.py:add_502` |
| 18 | M/A/O 적용 수준 분기 | `determine_application_level` |

### 6.2 골든 (golden_check.py 15종)

`tests/samples/golden/` — KORMARC 생성 결과를 사람이 검수한 정답과 비교:

```python
def golden_check(generated_record: Record, golden_path: Path) -> tuple[bool, list[str]]:
    """golden 정답 .mrc와 필드별 비교."""
    golden = MARCReader(golden_path.open("rb")).__next__()
    diffs = []

    # 모든 태그 비교
    all_tags = set([f.tag for f in generated_record.fields] + [f.tag for f in golden.fields])
    for tag in all_tags:
        gen_fields = generated_record.get_fields(tag)
        gold_fields = golden.get_fields(tag)
        if len(gen_fields) != len(gold_fields):
            diffs.append(f"{tag}: 개수 {len(gen_fields)} vs {len(gold_fields)}")
            continue
        for gf, golden_f in zip(gen_fields, gold_fields):
            if str(gf) != str(golden_f):
                diffs.append(f"{tag}: {gf} vs {golden_f}")

    return (len(diffs) == 0, diffs)
```

15 골든 케이스:
1. 단행본 (한국 소설·한강)
2. 단행본 (다권물·반지의 제왕 3권)
3. 다국어 단행본 (영한 대역)
4. 한자 병기 단행본 (三國史記)
5. 연속간행물 (월간 잡지)
6. 연속간행물 (종간)
7. 비도서 (CD-ROM)
8. 고서 (조선 고서·間紙)
9. 전자책 (PDF)
10. 전자저널
11. 오디오북
12. DVD (멀티미디어)
13. 학위논문 (박사)
14. 점자도서
15. 키트 (교구)

### 6.3 시각 회귀 (visual_regression.py)

UI/PDF 출력을 PNG 스냅샷으로 비교 → 회귀 검출:

```python
def visual_regression_check() -> bool:
    """Streamlit UI + 보고서 PDF 시각 회귀."""
    snapshots = [
        ("ui_main",         "tests/snapshots/ui_main.png"),
        ("report_monthly",  "tests/snapshots/report_monthly.png"),
        ("interlibrary_csv", "tests/snapshots/interlibrary_csv.png"),
    ]
    for name, path in snapshots:
        new = render_to_png(name)
        old = Image.open(path)
        diff = pixel_diff(new, old)
        if diff > VISUAL_REGRESSION_THRESHOLD:    # 5% 이내
            return False
    return True
```

### 6.4 자관 .mrc 174 전수 정합률 ≥99%

자관 D 드라이브 .mrc 174 파일 전수 검증:

```python
def validate_jagwan_174() -> dict:
    """자관 .mrc 174 전수 검증 — 영업 신뢰성 핵심."""
    jagwan_dir = Path("D:/내를건너서 숲으로 도서관/.mrc/")
    files = list(jagwan_dir.glob("*.mrc"))
    assert len(files) == 174, f"자관 .mrc {len(files)}개 (174 기대)"

    pass_count = 0
    fail_records = []
    for mrc_path in files:
        with mrc_path.open("rb") as f:
            for record in MARCReader(f, force_utf8=True):
                if record is None:
                    continue
                errors = validate_record(record)
                if not errors:
                    pass_count += 1
                else:
                    fail_records.append({"file": mrc_path.name, "errors": errors})

    rate = pass_count / len(files)
    assert rate >= 0.99, f"정합률 {rate:.2%} (≥99% 필요)"
    return {"total": len(files), "pass": pass_count, "rate": rate, "failures": fail_records}
```

자관 PILOT 영업 시 인용 가능: "**자관 174 KORMARC 전수 검증 정합률 ≥99%**" — Q3 자산 점수 ↑.

---

## 7. Claude Code 명령서 풀세트 (★ 가장 중요)

> 각 프롬프트는 **그대로 복사해서 Claude Code에 던지면 동작**하는 수준의 디테일.
> 헌법 §4 절대 규칙 (timeout·확률·source_map·880 자동) 정합 강조.
> 자율성 4단 정합 (L1/L2 = 즉시 자율 / L3 = ADR 후 / L4 = PO 수동).

### 7.1 프롬프트 #1 — Phase 0 MVP "ISBN → .mrc 단건"

```text
[작업] kormarc-auto Phase 0 MVP — ISBN 단건 → KORMARC .mrc 변환.

[목표] 사서 1명이 웹 브라우저에서 ISBN 입력 → 5초 내 .mrc 다운로드 → KOLAS III 실제 반입 성공.

[제약 — 헌법 §4 절대 규칙]
- 모든 외부 API 호출에 timeout=10 명시
- 모든 결과에 confidence (0~1) + source_map 포함
- 한자 감지 시 880 페어 자동 생성 (vernacular/field_880.py)
- 알라딘 사용 시 attribution "도서 DB 제공 : 알라딘 인터넷서점" 표시
- 008 정확히 40자리 (validator.py:validate_008 통과)
- ISBN-13 체크섬 검증 (validator.py:validate_isbn13)

[구현 순서]
1. src/kormarc_auto/cli.py — `kormarc isbn 9788936434120` 명령 동작 확인
2. src/kormarc_auto/api/aggregator.py:aggregate_by_isbn() 폴백 1순위 NL Korea만 활성화 (Phase 0)
3. src/kormarc_auto/kormarc/builder.py:build_kormarc_record() 호출
4. src/kormarc_auto/vernacular/field_880.py:add_880_pairs() 실행
5. src/kormarc_auto/kormarc/validator.py:validate_record() 통과 확인
6. src/kormarc_auto/output/kolas_writer.py:write_kolas_mrc() 출력
7. tests/test_phase0_mvp.py — golden 1건 (한강 「작별하지 않는다」 9788936434120) 통과

[KOLAS 반입 검증 (★ 1순위 KPI)]
- 자관 PILOT 1주차 첫날 자관 KOLAS III에 우리 .mrc 실제 반입
- 메뉴: [단행 > 정리 > 목록완성 > 입력 > 반입]
- 파일명 = {ISBN}.mrc (KOLAS 자동 인식 규칙)
- 인코딩 = UTF-8 (KOLAS III 유니코드 3.0 기반)
- 결과: 사서가 KOLAS UI에서 1건 시각 확인

[검증 4단]
- pytest -q (222 tests 모두 통과)
- scripts/binary_assertions.py --strict (18/18)
- scripts/golden_check.py (15/15)
- scripts/validate_jagwan_174.py (≥99%)

[자율성] L2 — 자율 실행 후 보고. ADR 불필요 (이미 Phase 0 = MVP 정의).

[종료 마커] <<<TASK_COMPLETE>>>
```

### 7.2 프롬프트 #2 — Phase 1 "책단비 hwp 자동 생성기"

```text
[작업] kormarc-auto Phase 1 — KOLAS F12 엑셀 → 책단비 hwp 4 양식 자동 생성기.

[배경 — chaekdanbi-workflow-audit.md]
- 자관 (내숲) = 은평구 11개관 책단비 5년 1,328 .xlsm 매크로 历사 보유
- 사서 매일 26~31분 → 우리 SaaS 6~7분 (77% 단축)
- 책단비 4 양식: 만료·반납·제공·지하철
- 띠지 1장 = 65권 (도서관 20 + 지하철 30 + 여유 15) 또는 ver.2 = 50권 (도서관 20 + 지하철 30)

[모듈 신규] src/kormarc_auto/chaekdanbi/auto_label_generator.py

[구현 의사코드]
```python
def generate_chaekdanbi_label(
    kolas_f12_xlsx_path: Path,
    library_name: str = "내숲",      # 자관 → config.yaml.library_name
    target_libraries: list[str],      # ["은평", "마포", "서대문"] 또는 지하철역
    label_type: Literal["만료", "반납", "제공", "지하철"],
    template_dir: Path = Path("data/chaekdanbi_templates/"),
    output_path: Path,
) -> Path:
    """KOLAS F12 엑셀 9 컬럼 → 책단비 hwp 띠지 자동.

    토큰 구조: <[자관명]><[상태]><[상대도서관]><권>
    예: <[내숲]><만료><[은평]><권>
    """
    # 1. KOLAS F12 엑셀 read (openpyxl)
    f12_rows = read_kolas_f12_xlsx(kolas_f12_xlsx_path)   # 9 컬럼

    # 2. 등록번호 EQ/CQ prefix 정합 검증
    for row in f12_rows:
        parse_registration_number(row["등록번호"])    # ValueError 시 reject

    # 3. 책단비 hwp 양식 read (python-hwpx)
    template_path = template_dir / f"책단비팀_공통_양식_{label_type}.hwpx"
    hwp_doc = python_hwpx.open(template_path)

    # 4. mail merge — 65권 단위로 띠지 생성
    for i, row in enumerate(f12_rows):
        token = f"<[{library_name}]><{label_type}><[{target_libraries[i % len(target_libraries)]}]><{row['청구기호']}>"
        hwp_doc.replace_token("{권}", token)

    # 5. 저장
    hwp_doc.save(output_path)
    return output_path
```

[의존성 추가 (L3 — ADR 0021 기존)]
- python-hwpx (또는 pyhwpx) — pip install python-hwpx
- openpyxl (이미 의존성)

[자관 양식 등록 (정책 ③)]
- data/chaekdanbi_templates/책단비팀_공통_양식_만료.hwpx (자관 보유)
- data/chaekdanbi_templates/책단비팀_공통_양식_반납.hwpx
- data/chaekdanbi_templates/책단비팀_공통_양식_제공.hwpx
- data/chaekdanbi_templates/책단비팀_공통_양식_지하철.hwp (HWP 5.0 OLE2)

[CLI]
- kormarc chaekdanbi --input kolas_f12.xlsx --type 만료 --output 만료_띠지.hwp
- kormarc chaekdanbi --type 만료 --watch ~/Downloads/  (Folder Watcher Phase 2)

[테스트]
- tests/test_chaekdanbi_auto.py — 자관 5년 .xlsm 1건 → hwp 생성 → 텍스트 추출 검증
- 사서 시간 ≥77% 단축 측정 (Q1 점수 100)

[5질문 셀프 오딧 (Beta 가중치)]
Q1 = 100 (권당 ≥10분 절감)
Q2 = 95 (비용 ≈ 0)
Q3 = 80 (시그너처 기능)
Q4 = 70 (락인)
Q5 = PASS (PII 0)
종합 = 92 → ★ 즉시 ACCEPT

[자율성] L3 — ADR 0021 (책단비 자동 — 자관 PILOT 1순위) 작성 후. architect-deep 자문 필수.

[종료 마커] <<<TASK_COMPLETE>>>
```

### 7.3 프롬프트 #3 — Phase 2 "F12 엑셀 일괄 importer"

```text
[작업] kormarc-auto Phase 2 — KOLAS F12 엑셀 9 컬럼 일괄 importer.

[배경]
- KOLAS III F12 엑셀출력 = 사서 매일 사용 (책두레 모듈)
- 9 컬럼: 신청번호·신청일자·등록번호·서명·저자·출판사·발행년도·청구기호·비고
- 등록번호 EQ/CQ prefix (자관) / EM/BM/AM/CM (알파스 표준)
- rapidfuzz로 서명·저자 모호 매칭 (오타·띄어쓰기 차이 흡수)

[모듈 신규] src/kormarc_auto/inventory/kolas_f12_importer.py

[구현 의사코드]
```python
def import_kolas_f12(
    xlsx_path: Path,
    *,
    library_db: LibraryDB,
    fuzzy_threshold: int = 85,    # rapidfuzz 0~100
) -> dict:
    """KOLAS F12 9 컬럼 엑셀 일괄 import → 우리 자관 인덱스.

    모호 매칭: 서명·저자가 자관 인덱스와 fuzzy_threshold 이상 유사 시 자동 매칭.
    그렇지 않으면 사서 검토 큐로 이동.
    """
    rows = read_kolas_f12_xlsx(xlsx_path)
    matched = 0
    review_queue = []

    for row in rows:
        # 1. 등록번호 prefix 정합 검증
        try:
            reg_no = parse_registration_number(row["등록번호"])
        except ValueError as e:
            review_queue.append({"row": row, "reason": f"등록번호 형식 오류: {e}"})
            continue

        # 2. 자관 인덱스 검색 (서명 + 저자 fuzzy)
        candidates = library_db.search_by_title_author(row["서명"], row["저자"])
        best = max(candidates, key=lambda c: rapidfuzz.fuzz.ratio(c["title"], row["서명"]), default=None)

        if best and rapidfuzz.fuzz.ratio(best["title"], row["서명"]) >= fuzzy_threshold:
            library_db.update_record(best["id"], registration_number=reg_no)
            matched += 1
        else:
            review_queue.append({"row": row, "reason": "자관 인덱스 매칭 실패", "candidates": candidates[:5]})

    return {
        "total": len(rows),
        "matched": matched,
        "review_queue": review_queue,
        "match_rate": matched / len(rows) if rows else 0,
    }
```

[Folder Watcher (ADR 0016)]
- watchdog 의존성 추가 (L3)
- ~/Downloads/ 자동 감지 → KOLAS_*.xlsx 패턴 시 자동 import

[CLI]
- kormarc f12-import --xlsx ~/Downloads/KOLAS_20260429.xlsx
- kormarc f12-import --watch ~/Downloads/ --threshold 85

[검증]
- tests/test_kolas_f12_importer.py — 자관 5년 .xlsm 샘플 10건 일괄 import → match_rate ≥ 90% 측정
- binary_assertions §16 (049 12자리 등록번호) 통과

[자율성] L3 — ADR 0058 (F12 일괄 importer) 작성 후.

[종료 마커] <<<TASK_COMPLETE>>>
```

### 7.4 프롬프트 #4 — Phase 3 "회원증 mail merge (PII 자관 위임)"

```text
[작업] kormarc-auto Phase 3 — 회원증 양식 mail merge (Formtec 정합·PII 자관 위임).

[★ 헌법 §4 + PIPA 옵션 C]
- 회원 PII (이름·주민번호·전화·주소) = 우리 SaaS 절대 저장 X
- 자관 알파스/KOLAS에서 PII export → 우리 SaaS = 양식 변환만 → 자관 PII 즉시 삭제
- 우리 SaaS DB에는 회원 PII 0 = PIPA 위반 0 = Q5 PASS

[모듈 신규] src/kormarc_auto/membership/card_generator.py

[구현 의사코드]
```python
def generate_membership_cards(
    member_csv_path: Path,             # 자관 알파스 export (PII 포함)
    formtec_template_path: Path,       # Formtec 명함 양식
    output_pdf_path: Path,
    *,
    delete_input_after: bool = True,   # ★ PIPA — import 후 즉시 삭제
) -> Path:
    """회원증 양식 자동 mail merge.

    PII 흐름:
    자관 알파스 → CSV → 우리 SaaS (메모리만) → Formtec PDF → 자관 인쇄
                                  ↓
                        ★ delete_input_after=True 즉시 CSV 삭제
                        ★ 우리 SaaS DB에는 PII 저장 X
    """
    members = read_csv_pii(member_csv_path)    # 메모리만, DB 저장 X

    pdf = FPDF()
    formtec_layout = parse_formtec_template(formtec_template_path)   # 명함 8개/페이지

    for i, member in enumerate(members):
        if i % 8 == 0:
            pdf.add_page()
        x, y = formtec_layout.position(i % 8)
        pdf.text(x, y, member["이름"])
        pdf.text(x, y + 5, member["회원번호"])
        # 바코드 생성 (Code39 또는 QR)
        pdf.image(barcode_image(member["회원번호"]), x=x, y=y + 10, w=40, h=10)

    pdf.output(output_pdf_path)

    # ★ PIPA — 입력 CSV 즉시 삭제
    if delete_input_after:
        member_csv_path.unlink()

    # 우리 SaaS는 양식 위치·템플릿만 저장. PII 0.
    return output_pdf_path
```

[Formtec 정합]
- Formtec 3×8 명함 양식 (한국 표준)
- 명함 1장 = 90mm × 50mm (Formtec 3110)
- 8개/페이지 = 4×2 배치 (Formtec 3115)

[PIPA 5 패턴 (Q5 게이트)]
1. Reader/Borrower/Patron entity ERD = 우리 SaaS X (자관 위임) ✅
2. 암호화 (bcrypt·AES-256·TLS 1.2+) = 우리 SaaS 사용 X (PII 저장 X) ✅
3. DSAR (제35·36·37·35조의2) = 우리 SaaS X (PII 저장 X) ✅
4. 72h 신고 자동화 = 우리 SaaS X (PII 저장 X) ✅
5. audit_log + 해시 체인 = 우리 SaaS X (PII 저장 X) ✅
→ Q5 = PASS (모든 5 패턴 영역 X)

[CLI]
- kormarc card-generate --members 자관_export.csv --template formtec_3115.pdf --output cards_20260429.pdf

[자율성] L3 — ADR 0115 (회원증 mail merge) 작성 후.

[종료 마커] <<<TASK_COMPLETE>>>
```

### 7.5 프롬프트 #5 — Phase 4 "수서 추천 대시보드"

```text
[작업] kormarc-auto Phase 4 — 수서 추천 대시보드 (정보나루 인기 대출 + 중복 소장).

[배경]
- 정보나루 API: srchModifyList (인기 대출 도서)
- 정보나루 API: libBookExist (특정 도서관 소장 여부)
- 사서 수서 시간 30분 → 5분 (장서개발지침 §2)

[모듈 신규] src/kormarc_auto/acquisition/recommendation_dashboard.py

[구현 의사코드]
```python
def build_recommendation_dashboard(
    library_code: str,          # 우리 도서관 정보나루 코드
    *,
    region: str = "ulk",        # 발행지 (서울 = ulk)
    age_group: str = "전체",     # 전체/아동/청소년/일반
    period_days: int = 30,
) -> dict:
    """수서 추천 대시보드 — 인기 대출 100권 + 자관 보유 여부.

    출력:
    - top_100: 정보나루 인기 100권
    - already_owned: 자관 보유 (중복 — 수서 X)
    - recommended: 미보유 (수서 후보)
    - kdc_balance: KDC 주류별 균형 (010~990)
    - estimated_cost: 권당 평균 가격 × 권수
    """
    # 1. 정보나루 srchModifyList 호출 (timeout=10)
    top_100 = data4library.fetch_popular(
        library_code=library_code, region=region, age=age_group, period=period_days
    )

    # 2. 자관 보유 여부 (libBookExist 또는 자관 DB)
    owned = []
    recommended = []
    for book in top_100:
        if library_db.exists_by_isbn(book["isbn"]):
            owned.append(book)
        else:
            recommended.append(book)

    # 3. KDC 주류 균형 측정 (장서개발지침 §2)
    kdc_balance = {f"{i}00": 0 for i in range(10)}
    for book in recommended:
        main = (book.get("kdc") or "000")[0] + "00"
        kdc_balance[main] += 1

    # 4. 예상 비용
    avg_price = sum(book.get("price", 15000) for book in recommended) / len(recommended)
    estimated_cost = avg_price * len(recommended)

    return {
        "top_100": top_100,
        "already_owned": owned,
        "recommended": recommended,
        "kdc_balance": kdc_balance,
        "estimated_cost": estimated_cost,
        "owned_rate": len(owned) / len(top_100),
    }
```

[Streamlit 대시보드]
- src/kormarc_auto/ui/pages/recommendation_dashboard.py
- 차트: KDC 균형 (Plotly bar)
- 테이블: 추천 100권 (sortable·filterable)
- 다운로드: 추천 .csv (수서 신청용)

[자율성] L3 — ADR 0072 (수서 추천 대시보드).

[종료 마커] <<<TASK_COMPLETE>>>
```

### 7.6 프롬프트 #6 — Phase 5 "관장 ROI 대시보드"

```text
[작업] kormarc-auto Phase 5 — 관장 ROI 대시보드 (시간 절감 카운터).

[배경 — 캐시카우 평가축 §0]
- 사서 마크 시간 단축 = 우리 SaaS 핵심 가치
- 관장에게 ROI 시각화 = 결제 의향 ↑ (Q1·Q4 동시 양수)
- 자관 6년 NPS 활용 (2018~2023)

[모듈 신규] src/kormarc_auto/ui/pages/roi_dashboard.py

[구현 의사코드]
```python
def build_roi_dashboard(library_id: str, period: str = "month") -> dict:
    """관장 ROI 대시보드 — 시간 절감 + 비용 절감 + NPS.

    KPI:
    - time_saved_hours: 권당 (T_manual − T_auto) × 처리 권수
    - cost_saved_won: time_saved × 사서 시급 (≈ ₩15,000)
    - records_processed: 처리 건수
    - mrc_quality_rate: 자관 .mrc 정합률 (binary_assertions 통과율)
    - chaekdanbi_count: 책단비 자동 처리 건수
    - nps_trend: 사서 NPS 추세 (자관 6년 历사)
    """
    # 1. 처리 건수 + 시간 절감
    records = stats_db.count_records(library_id=library_id, period=period)
    T_manual = 8 * 60      # 8분 (수기 마크)
    T_auto   = 2 * 60      # 2분 (우리 SaaS)
    time_saved_seconds = (T_manual - T_auto) * records
    time_saved_hours = time_saved_seconds / 3600

    # 2. 비용 절감
    librarian_hourly = 15000      # 사서 시급
    cost_saved = time_saved_hours * librarian_hourly

    # 3. 품질 (binary_assertions 통과율)
    mrc_quality_rate = stats_db.get_assertion_pass_rate(library_id=library_id, period=period)

    # 4. 책단비 자동 처리 (Phase 1 이후)
    chaekdanbi_count = stats_db.count_chaekdanbi_labels(library_id=library_id, period=period)

    # 5. NPS 추세 (자관 6년)
    nps_trend = nps_db.get_trend(library_id=library_id, years=6)

    return {
        "records_processed": records,
        "time_saved_hours": round(time_saved_hours, 1),
        "cost_saved_won": int(cost_saved),
        "mrc_quality_rate": round(mrc_quality_rate, 3),
        "chaekdanbi_count": chaekdanbi_count,
        "nps_trend": nps_trend,
        "monthly_subscription": 30000,        # 작은도서관 플랜
        "roi_multiplier": cost_saved / 30000,  # ROI 배수
    }
```

[Streamlit 대시보드]
- 카드: 시간 절감·비용 절감·ROI 배수 (큰 숫자)
- 차트: NPS 추세 (자관 6년 line chart)
- 차트: 자료유형별 처리 건수 (KORMARC 9 자료유형)
- 다운로드: 월간 ROI 보고서 PDF (관장 보고용)

[영업 메시지]
> "월 3만원 → 시간 절감 ₩{roi_amount}원/월 → ROI {roi_multiplier:.1f}배"
> "자관 PILOT 6년 NPS = {nps_score} (★★★★★ 사서 만족도)"

[자율성] L3 — ADR 0099 (관장 ROI 대시보드).

[종료 마커] <<<TASK_COMPLETE>>>
```

---

## 부록 A — Claude Code 명령서 사용 가이드

### A.1 자율성 4단별 사용

| 단계 | 프롬프트 | 사용 시점 |
|---|---|---|
| L2 (자율 + 보고) | #1 (Phase 0 MVP) | 즉시 |
| L3 (ADR 후) | #2 (책단비) · #3 (F12) · #4 (회원증) · #5 (수서) · #6 (ROI) | architect-deep 자문 후 |
| L4 (PO 수동) | (운영 키 입력·운영 배포·실 결제) | PO만 |

### A.2 프롬프트 사용 순서 (Phase 0 → 5)

```
프롬프트 #1 (Phase 0 MVP) → 자관 PILOT 1주차 시작
            ↓
프롬프트 #2 (Phase 1 책단비) → 자관 PILOT 2~4주차 (★ Q1 = 100)
            ↓
프롬프트 #3 (Phase 2 F12 일괄) → KOLAS Folder Watcher
            ↓
프롬프트 #4 (Phase 3 회원증) → PIPA 옵션 C 정합
            ↓
프롬프트 #5 (Phase 4 수서) → 정보나루 통합
            ↓
프롬프트 #6 (Phase 5 ROI) → 관장 결제 의향 ↑ → 캐시카우 도달
```

### A.3 헌법 §4 절대 규칙 정합 체크 (커밋 전)

매 프롬프트 완료 후 자동 체크:
- [ ] timeout=10 모든 외부 API 호출에 명시
- [ ] confidence (0~1) 모든 결과에 포함
- [ ] source_map 모든 통합 결과에 포함
- [ ] 한자 감지 → 880 페어 자동 (vernacular/field_880.py)
- [ ] 알라딘 사용 시 attribution 표시
- [ ] 008 정확히 40자리
- [ ] ISBN-13 체크섬 통과
- [ ] 4단 검증 모두 통과 (어셔션 18·골든 15·시각 회귀·자관 174 ≥99%)

### A.4 5질문 셀프 오딧 (commit message 명시)

```
Q1 = N (점수)
Q2 = N
Q3 = N
Q4 = N
Q5 = PASS|FAIL
종합 = N
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

[헌법 §4 정합]
- timeout=10 ✅
- source_map ✅
- 880 자동 ✅
- 알라딘 attribution ✅ (or N/A)
- 008 = 40 ✅
```

### A.5 ADR 작성 트리거 (L3+ 필수)

L3 자율 액션 = ADR 작성 필수 (`docs/adr/`):
- 새 외부 API 추가 → ADR
- DB 스키마 변경 → ADR
- 의존성 메이저 버전 → ADR
- 프롬프트 #2~#6 모두 ADR 0021/0058/0115/0072/0099 정합

ADR 템플릿:
```markdown
# ADR NNNN — {제목}

## Status
{Proposed | Accepted | Deprecated}

## Context
{왜 필요한가 — 캐시카우 평가축 §0 또는 §12 양수 영향}

## Decision
{무엇을 결정했는가}

## Consequences
{긍정·부정 영향}

## 5질문 셀프 오딧
- Q1 = N
- Q2 = N
- Q3 = N
- Q4 = N
- Q5 = PASS|FAIL
- 종합 = N
```

---

## 부록 B — 참조 인덱스

| 영역 | 파일 |
|---|---|
| 헌법 | `CLAUDE.md` §0~§13 |
| 도메인 절대 규칙 | `.claude/rules/kormarc-domain.md` |
| 자율성 게이트 | `.claude/rules/autonomy-gates.md` |
| 5질문 평가축 | `.claude/rules/business-impact-axes.md` |
| 빌더 | `src/kormarc_auto/kormarc/builder.py` |
| 자료유형 | `src/kormarc_auto/kormarc/material_type.py` |
| 008 매핑 | `src/kormarc_auto/kormarc/mapping.py` |
| 880 페어 | `src/kormarc_auto/vernacular/field_880.py` |
| 검증 | `src/kormarc_auto/kormarc/validator.py` |
| 등록번호 | `src/kormarc_auto/librarian_helpers/registration.py` |
| 청구기호 | `src/kormarc_auto/librarian_helpers/call_number.py` |
| 통합 폴백 | `src/kormarc_auto/api/aggregator.py` |
| MARC21 변환 | `src/kormarc_auto/conversion/marc21.py` |
| KOLAS 출력 | `src/kormarc_auto/output/kolas_writer.py` |
| 상호대차 양식 | `src/kormarc_auto/interlibrary/exporters.py` |
| AI 클라이언트 | `src/kormarc_auto/_anthropic_client.py` |
| KDC AI | `src/kormarc_auto/classification/kdc_classifier.py` |
| MVP 재정립 | `docs/mvp-redefinition-2026-04-29.md` |
| KORMARC 표준 audit | `docs/kormarc-2023-standard-audit.md` |
| KOLAS III audit | `docs/kolas-iii-audit.md` |
| 5 상호대차 비교 | `docs/interlibrary-5systems-comparison.md` |
| 책단비 워크플로우 | `docs/chaekdanbi-workflow-audit.md` |
| 사서 도움말 | `docs/marc-fields-guide.md` |
| 종합 명세서 | `docs/spec.md` |

---

## 변경 이력

- **2026-04-29 v1.0** — Part 2 최초 작성. 7 섹션 (KORMARC 정밀 스펙·MARC21/BIBFRAME/MODS·외부 import/export·API 폴백·AI 결정 보조·검증 4단·Claude Code 명령서 풀세트 6) + 부록 2 (사용 가이드·참조 인덱스). v0.4.25 / 222 tests / KS X 6006-0:2023.12 정합 / 자관 .mrc 174 정합률 ≥99% 영업 인용 가능.

<<<TASK_COMPLETE>>>
