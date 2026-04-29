# kormarc-auto — 한국 도서관 KORMARC 자동 생성 SaaS

> **사서가 만든 사서를 위한 KORMARC 자동화 도구**.
> ISBN 1번 입력 → KORMARC `.mrc` 5초 → **KOLAS III·독서로DLS·알파스 즉시 반입**.
> **자관 .mrc 174 파일·3,383 레코드 → 99.82% 정합 검증 완료** (2026-04-29).

[![tests](https://img.shields.io/badge/tests-293%20passed-brightgreen)]() [![ruff](https://img.shields.io/badge/ruff-0%20errors-brightgreen)]() [![assertions](https://img.shields.io/badge/binary_assertions-34%2F34-brightgreen)]() [![KORMARC](https://img.shields.io/badge/KORMARC-2023.12-blue)]() [![Korean](https://img.shields.io/badge/Korean-KOLAS실무%20정합-blue)]() [![자관 정합](https://img.shields.io/badge/자관_.mrc-99.82%25-brightgreen)]() [![Cloud routine](https://img.shields.io/badge/Cloud_routine-3개_24%2F7-blue)]()

**한국 도서관 사서**가 매일 부딪히는 KORMARC 마크 작업을 권당 8분 → 2분으로 단축. 사서 출신 1인 개발자가 자관 「내를건너서 숲으로 도서관」 PILOT을 거쳐 만든 SaaS.

> **검색 키워드**: KORMARC 자동, MARC 자동 생성, 도서관 사서 마크 자동화, ISBN MARC 변환, KOLAS 반입, 1인 사서 자동화, 작은도서관 마크, 학교도서관 KORMARC, 880 한자 병기 자동, KDC 자동 분류, 책단비 hwp 자동, 책나래 책바다 양식

---

## 핵심 가치 (★ 영업 정량)

- ★ **자관 .mrc 174 파일·3,383 레코드 99.82% 정합** (KORMARC 2023.12 한국 KOLAS 실무 정합 검증 완료)
- **권당 마크 시간**: 8분 → **2분** (75% 단축)
- **KOLAS 자동 반입**: ISBN을 파일명으로 한 `.mrc` 출력 → 반입 폴더 자동 인식 (cp949·utf-8·euc-kr 자동 fallback)
- **AI 비전**: ISBN 없는 자료(자비출판·옛 책·기증도서)도 표지 사진 한 장으로 처리
- **KDC 자동 분류**: 다단계 폴백 (NL Korea → 부가기호 → AI 추천 3개·사서가 최종 선택)
- **880 한자 병기 자동**: 한자 감지 시 880 페어 자동 (NLK 「서지데이터 로마자 표기 지침(2021)」 정합)
- **9 자료유형**: 단행본·연속·비도서·고서·전자책·전자저널·오디오북·멀티미디어·학위논문 모두 정합
- **자관 049 prefix 자동 발견**: `kormarc-auto prefix-discover <dir>` 1줄 → 5분 도입
- **권당 100원 또는 월 3·5·15·30만원** (작은 / 학교 / 일반 / 대규모)

---

## 빠른 시작 (5분, 더블클릭만)

### 1. 최초 셋업 (1회)

`setup-once.bat` 더블클릭 → Python·venv·의존성 자동 설치.

### 2. API 키 채우기

`.env` 파일을 메모장으로 열어 4개 키 입력:

| 키 | 발급처 | 소요 |
|---|---|---|
| `NL_CERT_KEY` | https://www.nl.go.kr/seoji/ | 1~3일 (담당자 승인) |
| `ALADIN_TTB_KEY` | https://www.aladin.co.kr/ttb/ | 1~2일 (블로그 등록 후) |
| `KAKAO_API_KEY` | https://developers.kakao.com | 즉시 |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | 즉시 |

(`KORMARC_ADMIN_KEYS`·`KORMARC_DEMO_KEY`는 자동 생성 완료 — 그대로 두거나 교체)

### 3. 실행 (3가지 옵션)

| 더블클릭 | 결과 |
|---|---|
| `start-all.bat` | API + UI + 랜딩 3개 창 동시 시작 (가장 편함) |
| `start-server.bat` | API 서버만 (8000) — 다른 클라이언트가 호출 |
| `start-ui.bat` | Streamlit UI만 (8501) — 사서 직접 사용 |
| `start-tunnel.bat` | Cloudflare 단발 터널 → 폰에서 접속할 URL 발급 |

### 4. 사서에게 공유

- 랜딩 URL: `start-tunnel.bat` 실행 → 8080 선택 → 발급 URL을 카카오톡 등으로 공유
- 사서가 랜딩에서 이메일 입력 → 자동 키 발급 → UI 사용

### 5. CLI 사용 (개발자용)

```powershell
.\.venv\Scripts\Activate.ps1
kormarc-auto isbn 9788936434120
kormarc-auto search "한강 작별"
kormarc-auto photo cover.jpg
kormarc-auto prefix-discover "D:\<자관>\수서"   # 049 prefix 자동 발견 (다른 자관 PILOT 5분)
kormarc-auto info
```

### 5-1. 사서 GUI (PowerShell·CLI 미숙해도 5분)

```powershell
streamlit run src/kormarc_auto/ui/prefix_discover_app.py
```

→ 브라우저에서 자관 .mrc 디렉토리 입력 → 049 prefix 자동 발견 + config snippet 즉시 복사. 자관 사례 EQ·CQ·WQ → 99.82% 정합 도달.

### 6. 테스트·검증

```powershell
.\.venv\Scripts\python.exe -m pytest -q       # 단위 54건
.\.venv\Scripts\python.exe scripts\accuracy_check.py  # 알려진 ISBN 5건 회귀
```

---

## 프로젝트 구조

```
kormarc-auto/
├── pyproject.toml              # 의존성 + 빌드 설정
├── .env.example                # 환경변수 템플릿
├── README.md                   # 이 파일
├── CLAUDE.md                   # Claude Code 헌법 (자동 로드)
├── docs/
│   ├── spec.md                 # 마스터 명세서 (별도 페이지에서 붙여넣을 자리)
│   └── test_results.md         # 테스트 결과 누적
├── src/kormarc_auto/
│   ├── api/                    # 외부 API 클라이언트
│   │   ├── nl_korea.py         # 국립중앙도서관 ISBN API
│   │   ├── aladin.py           # 알라딘 OPEN API
│   │   ├── kakao.py            # 카카오 책 검색 API (보조)
│   │   ├── data4library.py     # 도서관 정보나루 (보조)
│   │   └── aggregator.py       # 다중 소스 통합 + 신뢰도 점수
│   ├── kormarc/                # KORMARC 빌더
│   │   ├── builder.py          # dict → pymarc.Record
│   │   ├── validator.py        # 008 길이, ISBN 체크섬 검증
│   │   └── mapping.py          # 외부 데이터 → MARC 필드 매핑
│   ├── classification/         # KDC + 주제명
│   │   ├── kdc_classifier.py   # 다단계 KDC 분류 (NL → 부가기호 → AI)
│   │   └── subject_recommender.py  # 주제명 추천
│   ├── vernacular/             # 한자 병기
│   │   ├── hanja_converter.py  # hanja 라이브러리 래퍼
│   │   └── field_880.py        # 880 페어 자동 생성
│   ├── vision/                 # 책 사진 분석
│   │   ├── barcode.py          # pyzbar ISBN 인식
│   │   ├── claude_vision.py    # Claude Vision으로 메타데이터 추출
│   │   └── photo_pipeline.py   # 사진 → KORMARC 통합 흐름
│   └── output/                 # 출력 형식
│       ├── kolas_writer.py     # KOLAS 호환 .mrc (ISBN.mrc)
│       ├── dls_writer.py       # 독서로DLS 호환
│       └── marcxml_writer.py   # MARCXML
├── tests/
│   ├── test_isbn.py
│   ├── test_vision.py
│   ├── test_kdc.py
│   └── samples/
│       ├── golden/             # 정답 KORMARC .mrc 파일들
│       └── covers/             # 테스트 표지 사진들
├── examples/
│   ├── generate_from_isbn.py   # CLI 예제: ISBN → .mrc
│   └── generate_from_photo.py  # CLI 예제: 사진 → .mrc
└── .claude/
    └── commands/               # 슬래시 명령 (추후)
```

---

## 사서 페르소나별 사용 시나리오

| 페르소나 | 비중 | 우리 모듈 | 권장 플랜 |
|---|---|---|---|
| **★ Excel 매크로 자작 사서** (조기흠) | 1순위 ICP·전국 1,500~2,500명 | 책단비 4 양식 hwp 자동 | 월 5만원 |
| **수서 사서** (박지수) | 2순위·KOLAS 1,271관 | 정보나루 인기 대출 + 자관 중복 알리미 | 월 3~15만원 |
| **종합 사서** (김기수·박세진·신은미) | 3순위·학교 12,200관 86% 자원봉사 | 장서점검·월간 보고·연체 통계 | 월 3~5만원 |

자관 「내를건너서 숲으로 도서관」 8명 사서 = 4 페르소나 직접 검증. 자세한 시나리오는 `docs/research/part3-librarian-workflows.md`.

---

## Phase별 진척 (v0.4.37 / 2026-04-29)

- ✅ Phase 1 — ISBN → KORMARC + KOLAS 자동 반입
- ✅ Phase 2 — Vision 2단계 (Haiku ISBN → Sonnet 종합) + prompt caching
- ✅ Phase 3 — KDC AI 추천 + 880 한자 병기 자동
- ✅ Phase 4 — Streamlit 14탭 + 모바일 반응형 + Pretendard 사서 친화 테마
- ✅ Phase 5 — FastAPI REST + X-API-Key + 사용량 카운터 + B2B + 결제 안내

### v0.4.x 자율 흡수 (PO 자료 기반)

| 모듈 | 근거 | 사서 효과 |
|---|---|---|
| `legal/deposit_form.py` | 도서관법 §21 별지 제3호서식 | 발행→납본서 PDF 5초 (자가출판 사서) |
| `librarian_helpers/registration.py` | 알파스 매뉴얼 p72-89 | 12자리 등록번호+누락+다권본 자동 |
| `interlibrary/exporters.py` | 책나래 운영자 업무지침서 | 책나래·책바다·RISS 양식 1초 |
| `acquisition/wishlist.py` | 장서개발지침 §2 | 100건 희망도서 분석 5분 |
| `output/disposal_form.py` | 도서관법 §22 + 장서개발지침 §3.2 | 분기 제적심의 결재서식 자동 |
| `output/annual_statistics.py` | 도서관법 §22의2 + 학교진흥법 §6 | KOLIS-NET·RISS 양식 자동 |
| `classification/nlsh_relations.py` | 주제명표목 업무지침(2021) | 비우선어 → 우선어 자동 치환 |
| `server/billing.py` | 사업화 플레이북 §7.8 | 월간 청구·영수증 PDF |

### Streamlit 도구 탭 14종

로마자·라벨·자관 검색·KDC 트리·식별기호 도움말·**장서점검**·**보고서**·**알림**·**납본**·**등록번호**·**상호대차**·**수서 분석**·**제적·폐기**·**연간 통계**

### 신규 엔드포인트 v0.4.x

- `POST /batch-vendor` — B2B 도서납품업체 (1,000건/회)
- `GET  /migrate-from-kolas` — KOLAS III 종료(2026-12-31) 영업
- `GET  /billing/monthly/{year}/{month}` — [관리자] 월간 청구
- `GET  /account/export` — 본인 데이터 다운로드 (개인정보보호법 §35-3)
- `DELETE /account/delete` — 본인 데이터 영구 삭제 (§36)
- `POST /legal/deposit-form` — 납본 별지 제3호서식 PDF

테스트 **269건 통과**, binary_assertions **27/27**, ruff 0 errors. 자세한 내용은 `CLAUDE.md §11 변경 이력`.

### 4-Part 종합 매뉴얼 (113,500자)

- `docs/research/part1-vibe-coding-and-claude-code.md` — 바이브 코딩 + Claude Code 깊이
- `docs/research/part2-kormarc-implementation.md` — KORMARC/KOLAS/DLS 구현 디테일 + 명령서 풀세트
- `docs/research/part3-librarian-workflows.md` — 사서 실무 워크플로우 (페르소나별)
- `docs/research/part4-uiux-seo-marketing-deployment.md` — UI/UX + SEO + 마케팅·배포

### 영업 자료

- `docs/sales/pilot-package-2026-04-29.md` — 자관 PILOT 4주 + 4 페르소나 메일 + Q&A 10건
- `docs/sales/kla-2026-presentation-outline.md` — KLA 5.31 발표 outline 1차 (15 슬라이드)

---

## 시스템 통합

### KOLAS III (공공도서관)

생성된 `.mrc` 파일을 KOLAS의 **마크 반입 폴더**에 두면 자동 인식 (파일명이 ISBN과 일치하면 자동 반입).
- `KORMARC_OUTPUT_DIR` 환경변수에 KOLAS 폴더 경로 지정

### 독서로DLS (학교도서관)

DLS의 MARC 반입 메뉴에서 `.mrc` 파일 직접 업로드. (자료유형 자동 판단: 단행본/연속간행물/비도서/장학자료/기타)

### 알파스 (ALPAS) — (주)이씨오 SaaS 도서관 관리

KOLAS3 호환 + 책이음 동기화 + 책밴드 자체 상호대차. `.mrc` import 그대로 가능.

### KERIS DLS / 독서로DLS (학교도서관)

12,200관·사서교사 13.9% 배치·86% 자원봉사. `output/dls_writer.py` 521 자동 + 자료유형 분기.

### 기타 시스템

- Tulip, SOLARS, Koha, Alma 등은 표준 ISO 2709 KORMARC 호환

### 5 상호대차 시스템

책나래(NLD 무료·장애인) · 책바다(NLK 5,200원·전국) · 책이음(KOLAS III 통합 회원증) · 책두레(KOLAS III 모듈) · 책단비(은평구 한정·자관 5년 1,328건). `interlibrary/exporters.py` 모두 정합.

---

## 헌법

모든 개발 결정은 `CLAUDE.md`를 우선합니다. 핵심:

- 외부 API 호출은 **반드시 try/except + timeout=10초**
- 변환 결과에 **신뢰도 점수** 포함
- **원본 데이터는 절대 수정하지 말고 보존**
- 사서 검토 단계 필수 (100% 자동 약속 금지)
- **API 키 하드코딩 절대 금지** (`.env`로만)
- **알라딘 데이터 사용 시 출처 표시** ("도서 DB 제공 : 알라딘 인터넷서점")

---

## PILOT 신청 + 컨택

- 카카오 채널: (개설 예정·5월 KLA 발표 전)
- 메일: okwhrlgma@gmail.com
- KLA 전국도서관대회 부스 (2026-05-31): PILOT 5분 시연 + 직접 신청 가능

**5월 학교·작은·공공 PILOT 5관 추가 모집** (4 페르소나별 1관). 무료 50건 + Q1 결제 의향 직접 측정만 부탁드립니다.

---

## 사용처

- ★ 자관 「내를건너서 숲으로 도서관」 (시문학·윤동주 특화·은평구공공도서관 11개 중 1개·8명 사서·4 페르소나)
- 5월 PILOT 모집 자관 (학교·작은·일반 공공·기증도서·자가출판 5관 예정)

GitHub topics: `library`, `marc`, `kormarc`, `kolas`, `korean-library`, `cataloging`, `book-classification`, `kdc`, `880-field`, `bibframe`, `mods`, `librarian-tool`, `saas`, `streamlit`, `fastapi`, `claude-code`

---

## 라이선스

Apache 2.0 (코어 엔진). 부가 SaaS 서비스는 상용.
