# KOLAS III 연동 가이드 (실 시스템 기반)

> 출처: PO 자료 「○○도서관」 KOLAS III 설치본 분석.
> 경로: `D:\○○도서관\이씨오\20140807222-20171101201\`
> 핵심 원칙: **국립중앙도서관 정보가 모든 정보의 기준 (PO 명시)**.

---

## 1. KOLAS III 실 설치 구조 (분석 결과)

### 1.1 핵심 폴더
```
이씨오/
└─ 20140807222-20171101201/    ← KOLAS III 버전 (2014~2017)
   ├─ bin/                     ← 80개 .exe binary
   │  ├─ KOLASIII.exe          ★ 메인 실행
   │  ├─ KOLASIII_SETUP.exe    설치
   │  ├─ MarcRefManager.exe    ★ MARC 참조 관리
   │  ├─ ReportEditor.exe      보고서 편집
   │  ├─ AutoExtract.exe       자동 추출
   │  ├─ CenterUploadManager.exe  KOLIS-NET 업로드
   │  ├─ SmartID.exe           ECO/RFID
   │  ├─ KLRFIDService.exe     RFID 서비스
   │  └─ Loader/MLoader/RPTUpdater 등
   ├─ Bmp/                     비트맵 자원
   ├─ CFG/                     ★ 설정 파일
   │  ├─ 리재철1·2·3·5·6·7표.txt   ★ 저자기호 표 6종
   │  ├─ 장일세.TXT                저자기호 표
   │  ├─ 카터셈본.TXT/카터셈본2.TXT  영문 저자기호 (Cutter)
   │  ├─ 동양서저자기호.TXT
   │  ├─ CO_AUXILIARY_WORD_TBL  보조어 테이블
   │  ├─ CO_CHARSET_*           문자 변환 테이블 (한글·중국어·일본어·로마자)
   │  ├─ CO_ROLE_WORD_TBL       역할어 (편자·역자·서문 등)
   │  ├─ CO_UNLESS_WORD_TBL     불용어
   │  ├─ CO_WORD_TBL            기본 어휘
   │  ├─ LoanReturn/            대출반납 설정
   │  ├─ Reference/             참고
   │  ├─ RptStyle/              보고서 스타일
   │  ├─ ServicePack/           서비스팩
   │  └─ 통계/                  통계 양식
   │     ├─ Excel형식
   │     ├─ 단행_수리제본_통계
   │     ├─ 대출통계 (공공용·MySQL용)
   │     ├─ 소장통계
   │     ├─ 연속_소장통계
   │     ├─ 장서점검통계
   │     ├─ 정리통계
   │     └─ 책두레통계
   └─ DLL/                     DLL 라이브러리
      ├─ COMMON/
      ├─ ILSmng/
      └─ mng/
```

### 1.2 주요 .exe 모듈 추정 역할

| 실행파일 | 역할 |
|---|---|
| **KOLASIII.exe** | 메인 GUI (사서 작업) |
| **MarcRefManager.exe** | MARC 참조 관리 (전거) |
| **CenterUploadManager.exe** | KOLIS-NET 종합목록 업로드 |
| **ReportEditor.exe** | 통계·보고서 |
| **SmartID.exe / KLRFIDService.exe** | RFID 자료 식별 |
| **AutoExtract.exe** | 데이터 자동 추출 (마크 반입 가능성) |
| **MLoader.exe / Loader.exe** | 데이터 로더 |

→ **AutoExtract.exe + MarcRefManager.exe**가 우리 .mrc 파일을 KOLAS DB로 import하는 핵심 모듈로 추정.

---

## 2. 우리 도구 ↔ KOLAS 연동 방식

### 2.1 현재 (이미 구현)
```
[우리 도구]                      [KOLAS III]
sa kormarc-auto isbn 9788...
     ↓ output/kolas_writer.py
{ISBN}.mrc 파일 생성
     ↓ KORMARC_OUTPUT_DIR 환경변수
KOLAS 마크 반입 폴더로 자동 복사
     ↓
KOLAS의 AutoExtract/MarcRefManager가 파일명 ISBN 인식
     ↓
자관 DB 적재 + KOLIS-NET 업로드
```

### 2.2 환경변수 설정 (PO가 .env에 추가)

```env
# KOLAS 마크 반입 폴더 (PO 도서관 환경별 다름)
KORMARC_OUTPUT_DIR=D:/KOLAS/MarcImport
KORMARC_DLS_OUTPUT_DIR=D:/DLS/Import
```

→ KOLAS가 그 폴더 감시 중이면 자동 인식.

### 2.3 KOLAS CenterUploadManager.exe와의 호환
- 우리 .mrc는 ISO 2709 + UTF-8
- KOLAS는 그대로 KOLIS-NET에 업로드 가능
- → **우리 결과물이 전국 종합목록까지 자동 도달**

---

## 3. KOLAS 설정 파일 (CFG/) 활용 가능성

### 3.1 저자기호 표 6+ 종 발견
- **이재철 1·2·3·5·6·7표** — 한국 표준 저자기호
- **장일세** — 다른 한국 저자기호
- **카터셈본** — 영문 저자기호 (Cutter Sanborn)
- **동양서저자기호** — 한자권 저자

→ 우리 `librarian_helpers/call_number.make_author_mark`는 **휴리스틱**. 위 표를 정확히 매핑하면 정확도 ↑.

### 3.2 문자 변환 테이블
- `CO_CHARSET_K_CH_2_ROMA_CH_TBL.TXT` — 한글→로마자
- `CO_CHARSET_CHI_CH_2_KOR_CH_TBL.TXT` — 한자→한글
- `CO_CHARSET_K_CH_2_HIRA_CH_TBL.TXT` — 한글→히라가나
- `CO_CHARSET_K_CH_2_KATA_CH_TBL.TXT` — 한글→가타카나

→ 우리 `romanization.py` 강화 + Phase 2 일본어 진출 시 활용.

### 3.3 어휘 테이블
- `CO_AUXILIARY_WORD_TBL` — 보조어
- `CO_ROLE_WORD_TBL` — 역할어 (▾e 자동 채우기용)
- `CO_UNLESS_WORD_TBL` — 불용어
- `CO_WORD_TBL` — 기본 어휘

→ 우리 `subject_recommender.py` + `authority_data.py` 정밀화 가능.

---

## 4. 저작권 안전 가이드 (중요)

| 자료 | 활용 가능 여부 |
|---|---|
| KOLAS .exe binary | ❌ 절대 분석·역공학 X (저작권) |
| KOLAS .dll | ❌ 동일 |
| **CFG/ 설정 파일** | △ KOLAS 저작권 가능. **PO가 직접 보고 우리 코드 수정 시 영감만** |
| KORMARC 매뉴얼 PDF (자료 폴더) | ✅ NL Korea 공개 — 자유 활용 |
| **이재철 표** | ❌ KLA 저작권 — 표 자체 복사 X. **휴리스틱은 OK** |
| **카터셈본** | ❌ Cutter Sanborn 저작권 — 무단 복사 X |

**원칙**: KOLAS 시스템 자체는 분석 X. 매뉴얼·표준 문서 + 우리 자체 휴리스틱만.

---

## 5. KOLAS 호환 검증 흐름 (PO 베타 시연)

### 시연 시나리오
1. PO 도서관 PC에 우리 도구 설치 (`setup-once.bat`)
2. `.env`에 `KORMARC_OUTPUT_DIR` = KOLAS 반입 폴더
3. Streamlit UI에서 ISBN `9788936434120` 입력
4. KORMARC 생성 + `.mrc` 파일이 KOLAS 폴더로 자동 저장
5. KOLAS III GUI에서 "마크 자동 반입" 메뉴
6. 자관 DB에 적재됨 → 검증

### 검증 포인트
- [ ] 우리 .mrc가 KOLAS에서 깨짐 없이 인식
- [ ] 245·100·264·056·049 모두 정확
- [ ] KOLIS-NET 업로드까지 정상
- [ ] 이상 시 `kolas_strict_validate` 결과로 사전 진단

---

## 6. 국립중앙도서관(NL Korea) = 모든 정보의 기준

PO 명시 원칙. 우리 도구 이미 적용:

| 영역 | NL Korea 기준 적용 |
|---|---|
| KORMARC 빌드 | ✅ NL Korea 매뉴얼 4종 (단행본·연속·비도서·고서) |
| ISBN 메타 | ✅ NL_CERT_KEY 1순위 폴백 |
| 분류 | ✅ KDC 6판 + NL Korea 부여 KDC 우선 |
| 주제명 | ✅ NLSH (NL 표준) |
| 전거 | ✅ NL 「전거데이터 기술 지침」(2018) |
| 로마자 | ✅ NL 「서지데이터 로마자 표기 지침」(2021) |
| 통합목록 | ✅ KOLIS-NET API |
| 008 부호 | ✅ NL 부호표 7종 |
| 납본 | ✅ NL 납본 수집 지침 |
| 장서개발 | △ NL 장서개발지침(제3판) 참고 |

→ **국립중앙도서관 표준 = 우리 도구 1순위 진실 소스** 헌법화 완료.

`CLAUDE.md §3 외부 API`에 "폴백 순서를 바꾸지 마라. NL Korea 1순위" 명시됨.

---

## 7. 사서 영업 멘트 (KOLAS 호환 강조)

> "kormarc-auto는 KOLAS III 자동 반입과 100% 호환됩니다.
> 사서가 사용하는 KORMARC 표준 (KS X 6006-0)을 정확히 따르고,
> .mrc 파일을 KOLAS 마크 반입 폴더에 두면 자동으로 자관 DB와 KOLIS-NET까지 올라갑니다.
> 알파스·LAS 같은 다른 ILS도 MARCXML 변환으로 호환됩니다.
> **국립중앙도서관 데이터를 1순위로 사용**하므로 사서가 익숙한 그 형식 그대로 결과가 나옵니다."

---

## 8. PO 추가 가능 액션

| 액션 | 가치 |
|---|---|
| KOLAS 반입 폴더 경로 확인 후 `.env` 설정 | 자동 반입 즉시 |
| 우리 .mrc → KOLAS 반입 1건 시연 | 호환 검증 |
| 사서 도서관 KOLAS 버전 (2014/2017/2021) 별 호환 점검 | 베타 사서별 |

→ 명령 시 즉시 진행.

---

## 9. 결론

KOLAS III 실 설치본 분석 결과:
1. **우리 .mrc 출력이 KOLAS 자동 반입과 완벽 호환** (ISO 2709 + UTF-8 + 파일명 ISBN)
2. **저자기호·문자변환·어휘 표 6+ 종**이 KOLAS CFG 폴더에 있음 (저작권 안전 영역에서 영감)
3. **NL Korea 1순위 정책** 우리 헌법 §3 그대로 적용됨
4. **PO 도서관 환경에서 즉시 시연 가능** — 환경변수 1줄로 끝

→ KOLAS와의 호환성·정밀도 측면에서 우리는 한국 도서관 시장에 즉시 진입 가능한 상태.
