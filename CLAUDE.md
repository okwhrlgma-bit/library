# CLAUDE.md — kormarc-auto

> Claude Code가 매 세션마다 자동으로 읽는 헌법. 절대적 우선순위.

---

## 0. 프로젝트 정체성

한국 도서관용 **KORMARC 자동 생성 SaaS**. ISBN 또는 책 사진을 입력받아 완성된 KORMARC 레코드를 자동 생성하고, **KOLAS III · 독서로DLS · 기타 사서 시스템에 바로 반입 가능한 형식**으로 출력.

**목표**: 사서의 마크 작업 시간을 권당 8분 → 2분으로 단축.

**PO**: 사서 출신 1인 비개발자 창업자 (`okwhrlgma@gmail.com`).

---

## 1. 의심·검증·정제 3원칙

1. **의심하라** — 요청을 그대로 실행하지 말고 "이게 미션에 기여하는가?" 자문
2. **검증하라** — 추측 금지. 파일 열고 코드 실행하고 공식 문서 확인
3. **정제하라** — 첫 결과는 초안. 자기 비판 후 다시 다듬어라

---

## 2. 도메인 용어 (반드시 정확히 사용)

| 용어 | 정의 |
|---|---|
| **KORMARC** | 한국문헌자동화목록형식 (**KS X 6006-0:2023.12**, NLK 2차 개정). 한국 도서관 표준. **9 자료유형** (단행본·연속·비도서·고서·전자책·전자저널·오디오북·멀티미디어·학위논문). **3 적용 수준** M(Mandatory)·A(Mandatory if applicable)·O(Optional). MARC21 호환↑·시맨틱 웹·링크드 데이터·외부 리소스 연계. 150+ 필드 (001~005 제어번호 ~ 900~980 로컬정보) |
| **MARC21** | 미국 의회도서관 표준 MARC. 글로벌 |
| **MODS XML** | NLK 온라인자료과 디지털 컬렉션 표준 (KORMARC + 별도 변환). 5 자료유형 (멀티미디어·오디오북·전자저널·전자책·학위논문) |
| **KOLAS III** | 국립중앙도서관 보급, 한국 공공도서관 표준 자료관리 시스템. ver.20210322001 (자관 보유). DB 오라클·단행/연속/공통 3 모듈. 책두레 모듈 = NLK 표준 상호대차 |
| **알파스 (ALPAS)** | (주)이씨오 SaaS 도서관 관리. 카카오클라우드 IaaS·99.5% uptime·일일 03:00 백업. KOLAS3 호환·책이음 동기화·책밴드 자체 상호대차 |
| **독서로DLS / KERIS DLS** | 한국 학교도서관 표준 시스템 (2024년 DLS와 통합). KERIS + 17 시·도교육청. 12,200관·사서교사 13.9% 배치·86% 자원봉사 |
| **KOLIS-NET** | 전국 2,000여 도서관 통합 목록 |
| **KLMS** | Korea Library Management System (NLK 클라우드 책이음 통합) |
| **KDC** | 한국십진분류법 (현재 6판) |
| **KCR4** | 한국목록규칙 4판 |
| **880 필드** | 대체문자 표제 — 한자/영문/로마자 병기 자동 생성 대상 (NLK 「서지데이터 로마자 표기 지침(2021)」 정합) |
| **049 필드** | 자관 청구기호 — 도서관별 규칙 (자관 prefix EQ/CQ 정합) |
| **관제(冠題)** | 본표제 앞 수식어. KORMARC 245 지시기호2와 연동 |
| **ISO 2709** | MARC 교환 형식 표준 (.mrc 확장자) |
| **5 상호대차** | 책바다(NLK 5,200원·전국)·책나래(NLD 무료·장애인)·책이음(KOLAS III 통합 회원증)·책두레(KOLAS III 모듈)·책단비(은평구 한정) |

---

## 3. 외부 API (단일 진실 소스)

| API | URL | 인증 | 우선순위 |
|---|---|---|---|
| 국립중앙도서관 ISBN 서지 | `https://www.nl.go.kr/seoji/SearchApi.do` | `cert_key` | 1순위 |
| KOLIS-NET 종합목록 | `https://www.nl.go.kr/NL/search/openApi/searchKolisNet.do` | `key` | 2순위 |
| 도서관 정보나루 | `http://data4library.kr/api/srchBooks` | `authKey` | 3순위 (키워드) |
| 알라딘 OPEN API | `http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx` | `ttbkey` | 4순위 |
| 카카오 책 검색 | `https://dapi.kakao.com/v3/search/book` | `Authorization: KakaoAK <key>` | 5순위 |
| Claude Vision | `https://api.anthropic.com/v1/messages` | `x-api-key` | 사진 입력 시 |

폴백 순서를 바꾸지 마라. 비용·정확도 최적화된 순서다.

---

## 4. 코딩 규칙 (HARD RULES)

### 4.1 절대 하지 말 것
- ❌ API 키를 코드에 하드코딩 (`.env` 사용 + `python-dotenv`)
- ❌ 알라딘 데이터 사용 시 출처 표시 누락 ("도서 DB 제공 : 알라딘 인터넷서점")
- ❌ 100% 자동화 약속 (사서 검토 필수)
- ❌ 외부 API 호출 시 timeout 미지정
- ❌ 원본 ISBN/데이터 임의 수정
- ❌ try/except 없이 외부 호출
- ❌ `print` 디버깅 (로깅은 `logging` 모듈)
- ❌ 한국어 변수명 (식별자는 영문, 주석/docstring은 한국어 OK)

### 4.2 반드시 할 것
- ✅ 모든 외부 API 호출에 `timeout=10` 명시
- ✅ 모든 함수에 한국어 docstring (간결하게)
- ✅ Pydantic 또는 dataclass로 입력 검증
- ✅ 변환 결과에 `confidence` 필드 포함 (0.0~1.0)
- ✅ 데이터 출처 추적 (`source_map`: 어느 API에서 온 정보인지)
- ✅ `pymarc` 사용 시 8/UTF-8 인코딩 명시

### 4.3 코드 스타일
- 함수명: `snake_case`, 동사 + 목적어 (`fetch_isbn_metadata`, `build_kormarc_record`)
- 클래스명: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- 타입 힌트 필수 (mypy strict 통과)
- 한 함수 30줄 이하
- `ruff` + `mypy` 통과 후 커밋

---

## 5. KORMARC 빌드 핵심 규칙

### 5.1 008 필드 (40자리 정확히)
```
00-05: 입력일자 (YYMMDD, 시스템 자동)
06: 발행상태 ('s'=단일발행, 'm'=다권물 등)
07-10: 발행연도1
11-14: 발행연도2 (없으면 공백)
15-17: 발행국부호 ('ulk'=서울, 'ulg'=경기 등, 없으면 'xx ')
35-37: 언어부호 ('kor', 'eng' 등)
나머지는 공백 또는 도서 유형별 부호
```

### 5.2 020 필드
- ISBN-13만 사용 (10자리는 13자리로 변환)
- 하이픈 제거
- 부가기호는 `▾g`에 별도 (5자리)
- 가격은 `▾c`에 (예: `₩13000`)

### 5.3 245 필드
- `▾a` 본표제, `▾b` 부표제 (앞에 `: `), `▾c` 책임표시 (앞에 ` / `)
- 관제 있으면 원괄호로 묶고 지시기호2에 글자수+1 (관제 길이만큼 정렬 무시)
- 한자 병기 있으면 880 자동 생성

### 5.4 040 필드
- `▾a` 우리 도서관 부호 (기관 설정에서 가져옴)
- `▾b` 사용 언어 (`kor`)
- `▾c` 편목기관 (자기 자신)

### 5.5 049 필드 (한국 특수)
- `▾l` 등록번호
- `▾c` 복본기호
- `▾f` 별치기호
- `▾v` 권차기호

상세는 `docs/spec.md` 참조.

---

## 6. 자율성 4단계 + 종료 규약

| Level | 행동 | 예시 |
|---|---|---|
| 1 | 자율 실행 | 오타 수정, 린트 오류 |
| 2 | 실행 후 보고 | 로드맵에 있는 기능 구현, 버그 수정 |
| 3 | 계획 후 승인 | 새 외부 API 추가, DB 스키마 변경, 의존성 메이저 버전 |
| 4 | 절대 금지 (PO만) | 운영 키 입력, 운영 배포, 실 결제 설정 |

### 한국어 정책 (PO 가이드 §8.12)
- PO 프롬프트는 한국어, 응답도 한국어
- 영어 유지: 식별자·파일명·git commit·API 경로·인라인 주석
- 한국어 유지: 사용자 메시지·도메인 용어 (KORMARC·KDC·관제 등)
- 절대 금지: `결제Service` 같은 단일 식별자 내 혼용
- 한국어 BPE 1.5~2× 토큰 — 헤더는 영어로 (이 §처럼)

### 종료 규약 (Stop hook 마커)
작업이 진짜 끝났을 때만 응답 마지막 줄에 `<<<TASK_COMPLETE>>>` 마커 출력.
이중 게이트: 마커 + `pytest 통과` + `binary_assertions 18/18` 모두 충족 시에만 종료.

### 5대 멈춤 패턴 회피 (`.claude/rules/autonomy-gates.md`)
- 모호한 결정 → 더 안전·보수적 + DECISIONS.md
- 테스트 3회 실패 → SKIPPED.md + 다음
- 자가 디버그 루프 → max-iterations 30
- 컨텍스트 한계 → 핵심은 이 CLAUDE.md
- 의존성 실패 → 새 의존성 금지 + 오프라인 우선

---

## 7. 자기 비판 체크리스트 (커밋 전 필수)

- [ ] 외부 API 호출에 try/except + timeout 있는가
- [ ] 신뢰도 점수가 결과에 포함되는가
- [ ] 데이터 출처가 추적되는가 (`source_map`)
- [ ] 008 필드가 정확히 40자리인가
- [ ] ISBN-13 체크섬 검증 통과하는가
- [ ] 한자 있는 데이터에 880 페어가 생성되는가
- [ ] 알라딘 데이터 사용 시 출처 표시가 어딘가에 있는가
- [ ] M/A/O 적용 수준 검증 (`validator.validate_record_full`) 통과하는가
- [ ] 자관 .mrc 99.82% 정합 회귀 X (`scripts/validate_real_mrc.py`)
- [ ] `pytest`와 `ruff check` 통과하는가

---

## 8. 참조 문서

| 문서 | 언제 |
|---|---|
| `docs/spec.md` | 도메인·기능 상세 의문 시 |
| `docs/test_results.md` | 정확도·회귀 추적 |
| `tests/samples/golden/` | 변환 기준 정답 |
| `pymarc` 공식 문서 | `https://pymarc.readthedocs.io` |
| LC MARC 21 Bibliographic | `https://www.loc.gov/marc/bibliographic/` |
| 국립중앙도서관 KORMARC | `https://www.nl.go.kr` |

---

## 9. 슬래시 명령 + 서브에이전트

`.claude/commands/`:
- `/test` — pytest + ruff + mypy 일괄
- `/lint-fix` — ruff 자동 수정
- `/add-isbn <ISBN>` — 단일 변환
- `/batch-isbns <file>` — 일괄 변환
- `/quality-check` — 품질 5축 종합
- `/daily` — 매일 시작 루틴

`.claude/agents/`:
- `researcher` — 코드베이스 탐색 (별도 컨텍스트)
- `librarian-reviewer` — KORMARC 표준 + 사서 실무 관점 검토
- `kormarc-expert` — 필드 매핑·880·KORMARC vs MARC21 차이 자문

자동 호출 규칙:
- 새 KORMARC 필드 처리 추가 시 → `kormarc-expert` 자문
- 빌더 결과를 PO에게 보여주기 전 → `librarian-reviewer` 검토
- 코드 30곳 이상 grep 필요 → `researcher` 호출

---

## 10. 핵심 모듈 인덱스

| 모듈 | 책임 |
|---|---|
| `cli.py` | argparse 진입점 (isbn/batch/photo/validate/info) |
| `constants.py` | URL·타임아웃·신뢰도·기본값 단일 소스 |
| `logging_config.py` | 시크릿 마스킹 로거 |
| `api/_http.py` | 공유 requests Session + 재시도 + 30일 디스크 캐시 |
| `api/aggregator.py` | 다중 소스 폴백 + 신뢰도 가중 통합 |
| `kormarc/builder.py` | dict → pymarc.Record |
| `kormarc/validator.py` | ISBN-13 체크섬 + 008 길이 + 필수 필드 |
| `vernacular/field_880.py` | 한자 감지 → 880 페어 자동 |
| `output/kolas_writer.py` | ISBN.mrc (KOLAS 자동 반입 형식) |

---

## 11. 변경 이력

전체 이력 → `CHANGELOG_NIGHT.md` (현재 v0.4.37·자관 .mrc 99.82% 정합·Phase 0 MVP 4단 검증 완성).

<!-- ARCHIVED to CHANGELOG_NIGHT.md (2026-04-30 CLAUDE.md slim Step 1):
- 2026-04-25 v0.1 — 최초 작성. Phase 1 (ISBN→KORMARC) 구현 시작
- 2026-04-25 v0.2 — `cli.py` + `constants.py` + `logging_config.py` + `api/_http.py` 추가. 캐싱·재시도 도입. 슬래시 명령 6종 + 에이전트 3종.
- 2026-04-25 v0.3 — Phase 2 (Vision: Haiku→Sonnet 2단계) + Phase 3 (KDC AI) + Phase 3+ (Subject AI) 실구현. `_anthropic_client.py` 신규 (prompt caching + diskcache + tenacity). FastAPI 서버 (`server/`) + Streamlit UI (`ui/`) + 키워드 검색 (`api/search.py`) 추가. 사서 가치 모듈 3종(`librarian_helpers/call_number.py`, `kormarc/kolas_validator.py`, `api/kolisnet_compare.py`) 추가. 모바일 cloudflared/ngrok 자동 설치 + 권한 사전 등록. 수익화 인프라 (`server/usage.py` 사용량 카운터 + 결제 안내). 슬래시 명령 6종 신규 (/serve, /ui, /search, /vision-test, /kdc-test, /mobile-status). §12 수익 모델 헌법화.
- 2026-04-26 v0.4.10 — PO 제공 자료 4종 HIGH 흡수: `acquisition/wishlist.py`(희망도서→자관 중복+KDC 균형+예상 비용, 장서개발지침 §2). 1인 사서 수서 시간 30분→5분. CLI `wishlist`. 테스트 193건.
- 2026-04-26 v0.4.9 — 상호대차 어댑터 `interlibrary/exporters.py`. 책나래(13컬럼)·책바다(서명 컬럼)·RISS(12컬럼) CSV/XLSX. 책나래 운영자 업무지침서 p3-15 흡수. CLI `interlibrary`. 테스트 186건.
- 2026-04-26 v0.4.8 — 등록번호 자동 부여 `librarian_helpers/registration.py`. 12자리 EM01YY00001 + 누락번호 검출 + 다권본 일괄 (245▾n+490▾v). 알파스 매뉴얼 p72-89 흡수. CLI `registration {next,missing,multivolume}`. 테스트 181건.
- 2026-04-26 v0.4.7 — 납본 별지 제3호서식 PDF `legal/deposit_form.py`. 도서관법 §21 + 시행규칙 §4 + 시행령 §15. 부수 자동 산정(정부3/보존1/표준2). CLI `deposit form`, `/legal/deposit-form`. 테스트 171건.
- 2026-04-26 v0.4.6 — CLI `account export/delete` (개인정보보호법 §35-3·§36).
- 2026-04-26 v0.4.5 — 정식 이용약관 + 개인정보처리방침 v1.0. signup 응답에 terms_url/privacy_url. 운영 감사 HIGH #1 흡수.
- 2026-04-26 v0.4.4 — `/account/export`·`/account/delete` 엔드포인트 (자기결정권). 테스트 160건.
- 2026-04-26 v0.4.3 — UX 감사 즉시 수정 + 법적 준수 + B2B 가이드. `streamlit_app.py` UX Top 10 적용(첫 화면 안내·용어 부드럽게·해결법 카드·예상시간), `scripts/rotate_logs.py`(90일/365일 정책, 개인정보보호법 §21), `docs/b2b-vendor-guide.md`(도서납품업체 5분 도입+마진 계산+KOLAS 마이그 메일). 테스트 156건.
- 2026-04-26 v0.4.2 — 청구·B2B·KOLAS 마이그·사서 친화 UI. `server/billing.py`(월간 집계+청구서 JSON+영수증 PDF+권장 플랜), 신규 엔드포인트 3종(`/batch-vendor` 도서납품업체 1000건/회, `/migrate-from-kolas` 영업, `/billing/monthly/{y}/{m}` 관리자), `streamlit_app.py` Pretendard·네이비/살구·16px 사서 친화 테마. 테스트 152건.
- 2026-04-26 v0.4.1 — 사서 미충족 영역 4종: `inventory/inspection.py`(책장 사진 OCR → 자관 DB 대조 = 장서점검), `output/reports.py`(신착 안내문·월간 운영 보고서·일괄 검증 리포트 PDF). CLI `inspect`/`report`, FastAPI `/inspect`·`/report/{announcement,monthly,validate}`, Streamlit 도구 탭 2개 신규(장서점검·보고서). 테스트 11건 추가 (총 108).
- 2026-04-26 v0.4 — PO 실 도서관 자료 30+종 흡수 + KORMARC 5대 자료유형 모듈 신규.
-->

---

## 12. 수익 모델 (헌법)

**목표**: 한국 도서관 사서가 본인 예산으로 결제할 만한 SaaS. PO(사서 출신 1인 창업자) 매출 발생.

### 가격 (재조정, MVP-1)

| 플랜 | 가격 | 대상 |
|---|---|---|
| 무료 체험 | 50건 | 모든 신규 키 |
| 권당 과금 | 100원/건 | 소규모·간헐 |
| **월 정액 (작은도서관)** | **3만원 / 500건** ★ | 1인 사서·동네 도서관 |
| 월 정액 (소) | 5만원 / 1,000건 | 학교/소규모 공공 |
| 월 정액 (중) | 15만원 / 5,000건 | 일반 공공 |
| 월 정액 (대) | 30만원 / 무제한 | 대규모·기업 |

**광고 모델 채택 안 함** — 도서관 트래픽 광고 부적합 + 사서 거부감 + 운영비 적자.

**캐시카우 도달**: 200곳 × 평균 3.3만원 ≈ 월 660만원 (Phase 3, 24~36개월). 자세한 단계는 `docs/sales-roadmap.md`.

### 비용 구조 (PO 입장, 권당 약 7원 추정)

- Anthropic Vision/KDC + prompt caching로 권당 약 2원
- 외부 API (NL Korea/알라딘/카카오) 무료 한도 내 0원
- 서버 호스팅 분담 약 5원

권당 100원이면 **마진 ≈ 93%**.

### 모든 기능 결정의 평가 기준

> "이 변경이 사서의 지불 의향을 높이는가, 매출 발생 시점을 앞당기는가?"

**높은 우선순위**:
- 사서가 매일 부딪히는 작업 단축 (마크 시간, 청구기호, 별치)
- 정확성 향상 (AI 후보 → 사서 결정)
- 폰에서 사용 가능 (현장 즉시 처리)

**낮은 우선순위 / 미루기**:
- 기술적 호기심 (불필요한 통합)
- 대형 시스템 호환 (지금은 사서 개인 도구로 충분)
- 100% 자동화 약속 (사서 책임 영역 침범)

### 차별화 (vs 북이즈·제이넷·제로보드)

- 가격: 도서관 1관 연 수백만원 → **권당/월정액** 모델
- 도입: 시스템 교체 → **API 호출만**, 기존 KOLAS와 병행
- 매체: PC 전용 → **폰 브라우저로도**
- 옛 책·기증: 수기 → **Vision 자동**
- 셋업: 컨설팅 1주 → **5분 (가입 + 키)**

### 베타 ICP

- 1인 사서 학교도서관 (시간 압박 최대)
- 신규 작은도서관 (마크 인력 부재)
- 출판사 자가 KORMARC 생성 (기증·납본)

---

## 13. 모바일 운영 (Phase 5)

### 인프라

| 도구 | 용도 | 셋업 |
|---|---|---|
| FastAPI (`kormarc-server`) | REST API | `kormarc-server` |
| Streamlit (`kormarc-ui`) | 사서 GUI (모바일 반응형) | `kormarc-ui` |
| Cloudflare Tunnel | 외부 접속 (영구·무료) | `cloudflared tunnel ...` (`docs/mobile-tunnel.md`) |
| ngrok | 단발 접속 (백업) | `ngrok http 8000` |

### 보안

- 모든 API는 `X-API-Key` 필수 (`KORMARC_USER_KEYS`)
- 외부 노출은 터널만 (직접 0.0.0.0 바인딩 deny)
- `.env` 시크릿은 `logging_config`가 자동 마스킹

### 모바일 Claude Code 권한

`.claude/settings.json` (전역·프로젝트) 둘 다 `streamlit`/`uvicorn`/`cloudflared`/`kormarc-*` 사전 허용 — 모바일에서 권한 묻지 않고 실행.
