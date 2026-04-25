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

## 빠른 시작 (30분)

### 1. Python 환경

```powershell
# Python 3.12+ 확인
python --version

# 프로젝트 폴더로
cd "C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto"

# 가상환경 생성 + 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -e ".[dev]"
```

### 2. API 키 발급 (필수 4개)

| 키 | 발급처 | 소요 |
|---|---|---|
| `NL_CERT_KEY` | https://www.nl.go.kr/seoji/ | 1~3일 (담당자 승인) |
| `ALADIN_TTB_KEY` | https://www.aladin.co.kr/ttb/ | 1~2일 (블로그 등록 후) |
| `KAKAO_API_KEY` | https://developers.kakao.com | 즉시 |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | 즉시 |

```powershell
Copy-Item .env.example .env
notepad .env  # 위 4개 키 채우기
```

### 3. 실행

```powershell
# ISBN으로 KORMARC 생성
python examples/generate_from_isbn.py 9788936434120

# 결과: output/9788936434120.mrc (KOLAS 자동 반입 형식)
```

### 4. 테스트

```powershell
pytest -v
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

## Phase별 진척

- ✅ Phase 1 — ISBN → KORMARC 변환 + KOLAS 출력
- 🚧 Phase 2 — 책 사진 → KORMARC (vision 모듈, 스텁만)
- 🚧 Phase 3 — KDC 자동 분류 + 880 한자 병기 (스텁만)
- ⏳ Phase 4 — Streamlit 베타 UI (Phase 1~3 검증 후)

다음 세션에서 채워넣을 부분은 각 파일의 `TODO` 주석과 `docs/spec.md`를 참조.

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
