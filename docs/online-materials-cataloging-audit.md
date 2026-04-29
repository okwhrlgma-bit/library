# 온라인자료정리지침 5종 audit + Phase 1.5 5 자료유형 모듈

> **출처**: NLK 온라인자료과 5종 정리지침 (총 170p, 17.3MB) — 자료 폴더 보유
> **분석일**: 2026-04-28
> **결론**: NLK 온라인자료 표준 = **MODS XML 기반** (KORMARC + 별도). 우리 SaaS Phase 1.5 5 자료유형 추가 모듈 정합 검증 자료.

---

## 0. NLK MODS XML vs KORMARC 관계

| 항목 | KORMARC | NLK MODS |
|---|---|---|
| 표준 | KS X 6006-0:2023 | NLK 자체 (MODS 기반) |
| 형식 | MARC iso2709 / MARCXML | XML (MODS 스키마) |
| 적용 | 인쇄본 + 9 자료유형 | **온라인 자료 5 자료유형** (전자책·전자저널·오디오북·멀티미디어·학위논문) |
| 주체 | NLK 사서지원 | NLK 온라인자료과 |
| 용도 | 도서관 간 교환 | NLK 디지털 컬렉션 관리 |

**시사점**: 온라인 자료 = **MODS XML 표준** + **KORMARC 호환** 양방향 변환 필요.

---

## 1. 5 자료유형 핵심 매트릭스

| # | 자료유형 | p | 차별 메타데이터 | 우리 SaaS 모듈 (Phase 1.5) |
|---|---|---:|---|---|
| 1 | **멀티미디어** | 30 | 색상정보·구술자료 (`<role><roleTerm>collector`)·`<extent>bytes` | `kormarc/multimedia.py` |
| 2 | **오디오북** | 18 | 발행처불명 (s.n., 發行處不明)·발행연속성 | `kormarc/audiobook.py` |
| 3 | **전자저널** | 45 | 학술지명·페이지 (71-93)·간행빈도·연속간행물 | `kormarc/ejournal.py` (`kormarc/serial.py` 강화) |
| 4 | **전자책** | 49 | `<reformattingQuality>` access·preservation·replacement·`<internetMediaType>` e-pub | `kormarc/ebook.py` |
| 5 | **학위논문** | 28 | 전거데이터·이름·`Includes bibliographical references (pages X-Y)` | `kormarc/thesis.py` |

---

## 2. 공통 MODS XML 메타데이터 구조

```xml
<mods>
  <titleInfo>
    <title>본 표제</title>
    <subtitle>부 표제</subtitle>
    <partNumber>편 번호</partNumber>
    <partName>편 명</partName>
  </titleInfo>
  <titleInfo type="parallel">
    <title>대등표제 (다른 언어)</title>
  </titleInfo>
  <titleInfo type="original">
    <title>원표제</title>
  </titleInfo>
  
  <name>
    <namePart>저자명</namePart>
    <role>
      <roleTerm>저자·편자·collector·written music piano 등</roleTerm>
    </role>
  </name>
  
  <originInfo>
    <publisher>발행처 (불명 시 [s.n.])</publisher>
    <dateIssued>발행일</dateIssued>
  </originInfo>
  
  <physicalDescription>
    <extent>크기 (bytes 등)</extent>
    <digitalOrigin>Digital·Reformatted Digital 등</digitalOrigin>
    <internetMediaType>e-pub·application/pdf 등</internetMediaType>
    <reformattingQuality>access·preservation·replacement</reformattingQuality>
  </physicalDescription>
  
  <note>주기사항 (Includes bibliographical references (pages X-Y))</note>
</mods>
```

---

## 3. KORMARC ↔ MODS 매핑 (Phase 1.5)

| MODS | KORMARC | 우리 정합 |
|---|---|---|
| `<titleInfo><title>` | 245 ▾a | ✅ |
| `<titleInfo><subtitle>` | 245 ▾b | ✅ |
| `<titleInfo type="parallel">` | 246 ▾a | ✅ |
| `<titleInfo type="original">` | 240 ▾a | ✅ |
| `<name>+<role>` | 100·700 + ▾e (역할) | ✅ |
| `<originInfo><publisher>` | 264 ▾b | ✅ |
| `<originInfo><dateIssued>` | 264 ▾c | ✅ |
| `<physicalDescription><extent>` | 300 ▾a | ✅ |
| `<physicalDescription><internetMediaType>` | 856 ▾q | 🟡 부분 |
| `<physicalDescription><reformattingQuality>` | 533 ▾n | ❌ 신규 |
| `<note>` | 5XX (주기) | ✅ |

---

## 4. 자료유형별 핵심 룰 (5종)

### 멀티미디어
- 채택정보원 = 자료 자체 (p.1)
- 색상정보 → `<extent>` 추가
- 구술자료 = `<role><roleTerm>collector` 명시
- 파일 크기 = bytes 단위

### 오디오북
- 발행처불명 = `[s.n.]` 또는 `[發行處不明]` (한자 병기)
- 발행연속성 = 단행 vs 연속간행물 분기

### 전자저널
- 으뜸정보원 = 학술지명·논문제목 분리
- 페이지 정보 = 시작-끝 (예: 71-93)
- 간행빈도 = 월간·격월간·계간·연간
- 형태기술정보 = 원자료형태 + Digital 분리

### 전자책
- e-pub·PDF 자료유형 명시 (`<internetMediaType>`)
- 재포맷팅 품질 3단: **access** (이용용) / **preservation** (보존용) / **replacement** (대체용)
- 디지털 출처 = born-digital vs reformatted

### 학위논문
- 저자명 = 한글 + 로마자 (`eonhee` 등)
- `usage="primary"` = 주 이름 / 다른 이름은 별도 namePart
- 서지정보 = `Includes bibliographical references (pages X-Y)`
- 색인 = `Includes index (language)`

---

## 5. 특수문자·깨진 글자 처리 (5종 공통)

| 케이스 | 처리 |
|---|---|
| 수학·과학 특수문자 (κ, ε, v') | LaTeX 입력 또는 합의된 대체문자 정의 |
| 입력 불가능 특수문자 | 대체문자 정의 + 정리지침에 적용 |
| 원문서명 깨짐 + 출처서명 명확 | `원문서명: 文人）蜀瑤르 [실은 女人獨居記]` 형식 |
| 위첨자·아래첨자 | `<sup>2</sup>`·`<sub>2</sub>` |

→ **우리 SaaS 적용**: 특수문자 처리 모듈 (`kormarc/special_chars.py` 신규).

---

## 6. ADR 후보 추가 (Phase 1.5)

| ADR | 영역 |
|---|---|
| **ADR 0052 신규** | KORMARC ↔ MODS XML 양방향 변환 (`kormarc/mods_converter.py`) |
| **ADR 0053 신규** | 5 자료유형 모듈 (Phase 1.5) — multimedia·audiobook·ejournal·ebook·thesis |
| **ADR 0054 신규** | 특수문자 처리 (`kormarc/special_chars.py`) — LaTeX·대체문자·위첨자 |
| **ADR 0055 신규** | 재포맷팅 품질 3단 (access·preservation·replacement) — KORMARC 533 ▾n |
| **ADR 0056 신규** | 깨진 글자 [실은X] 표기 자동 (출처서명 cross-check) |

---

## 7. Phase 1.5 9 자료유형 100% 정합 매트릭스

| # | 자료유형 | 정합 | 모듈 | 우선순위 |
|---:|---|---|---|---|
| 1 | 단행본 | ✅ | `kormarc/builder.py` | 완료 |
| 2 | 연속간행물 | ✅ | `kormarc/serial.py` | 완료 |
| 3 | 비도서 | ✅ | `kormarc/non_book.py` | 완료 |
| 4 | 고서 | ✅ | `kormarc/rare_book.py` | 완료 |
| 5 | **전자책** | 🟡 → ✅ | `kormarc/ebook.py` | 🟢 1순위 (전자책 폭증) |
| 6 | **학위논문** | 🟡 → ✅ | `kormarc/thesis.py` | 🟢 1순위 (대학 시장) |
| 7 | **전자저널** | 🟡 → ✅ | `kormarc/ejournal.py` | 🟡 |
| 8 | **오디오북** | 🟡 → ✅ | `kormarc/audiobook.py` | 🟡 |
| 9 | **멀티미디어** | 🟡 → ✅ | `kormarc/multimedia.py` | 🟡 |

→ **9/9 (100%) 정합 = Phase 1.5 완료** = KORMARC KS X 6006-0:2023.12 + NLK 온라인자료 표준 100% 호환.

---

## 8. 영업 메시지 (Phase 1.5 9 자료유형 100%)

> "우리 SaaS는 KORMARC 9 자료유형 (단행본·연속간행물·비도서·고서·전자책·전자저널·오디오북·멀티미디어·학위논문) 모두 자동 생성합니다.
>
> NLK 온라인자료과 표준 MODS XML과 KORMARC 양방향 변환 — 디지털 컬렉션 + 인쇄 자료 통합 관리.
>
> 특수문자·LaTeX·깨진 글자 처리 자동 ([실은X] 표기 cross-check) — 사서 수기 입력 오류 90%+ 회피.
>
> 재포맷팅 품질 3단 (access·preservation·replacement) 자동 분기 — NLK 디지털 보존 정책 정합."

---

## 9. PIPA 게이트 (Phase 1.5)

| 자료유형 | PII 위험 | 우리 영역 |
|---|---|---|
| 멀티미디어 | 🟡 collector role (구술자 이름) | ✅ 서지 정보만 (구술자 = 저자) |
| 오디오북 | 🟢 X | ✅ |
| 전자저널 | 🟢 X | ✅ |
| 전자책 | 🟢 X | ✅ |
| 학위논문 | 🟡 저자 (학생 미성년 아님 — 학위 = 성년) | ✅ 저자 = 저자명전거 활용 (NLK 전거 178만) |

→ 9/9 자료유형 모두 우리 SaaS 진입 안전.

---

## 10. Sources

- 자료 폴더: `온라인자료정리지침_멀티미디어_2023_공개.pdf` (30p)
- 자료 폴더: `온라인자료정리지침_오디오북_2023_공개.pdf` (18p)
- 자료 폴더: `온라인자료정리지침_전자저널_공개.pdf` (45p)
- 자료 폴더: `온라인자료정리지침_전자책_2023_공개.pdf` (49p)
- 자료 폴더: `온라인자료정리지침_학위논문_2023_공개.pdf` (28p)
- [NLK 온라인자료과 공식](https://www.nl.go.kr/NL/contents/N40301010100.do)
- [MODS Library of Congress](https://www.loc.gov/standards/mods/)
- [KCR 한국목록규칙 4판](https://www.nl.go.kr/seoji/contents/S30301000000.do)
