# kormarc-auto

> 한국 도서관용 **KORMARC 자동 생성 도구**.
> ISBN 또는 책 사진을 입력받아 KORMARC 레코드를 만들고, **KOLAS III·독서로DLS** 등에 바로 반입 가능한 `.mrc` 파일로 출력합니다.

---

## 핵심 가치

- **사서의 마크 작업 시간 단축**: 권당 8분 → 2분 (목표)
- **KOLAS 자동 반입 호환**: ISBN을 파일명으로 한 `.mrc` 출력 → 반입 폴더에 두면 자동 인식
- **AI 비전 활용**: ISBN 없는 자료(자비출판·옛 책·기증도서)도 표지 사진 한 장으로 처리
- **KDC 자동 분류**: 다단계 폴백 (NL Korea → 부가기호 → AI 추천 3개)
- **880 한자 병기 자동**: 한자 감지 시 880 페어 필드 자동 생성

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
kormarc-auto info
```

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

## Phase별 진척 (v0.4.15 / 2026-04-26)

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

테스트 **214건 통과**, ruff 0 errors. 자세한 내용은 `CLAUDE.md §11 변경 이력`.

---

## 시스템 통합

### KOLAS III (공공도서관)

생성된 `.mrc` 파일을 KOLAS의 **마크 반입 폴더**에 두면 자동 인식 (파일명이 ISBN과 일치하면 자동 반입).
- `KORMARC_OUTPUT_DIR` 환경변수에 KOLAS 폴더 경로 지정

### 독서로DLS (학교도서관)

DLS의 MARC 반입 메뉴에서 `.mrc` 파일 직접 업로드. (자료유형 자동 판단: 단행본/연속간행물/비도서/장학자료/기타)

### 기타 시스템

- Tulip, SOLARS, Koha, Alma 등은 표준 ISO 2709 KORMARC 호환

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

## 라이선스

Apache 2.0 (코어 엔진). 부가 SaaS 서비스는 상용.
