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

---

## 12. 수익 모델 (헌법)

**목표**: 한국 도서관 사서가 본인 예산으로 결제할 만한 SaaS. 캐시카우 200관 × 3.3만원 ≈ 월 660만원 (Phase 3, 24~36개월).

**평가 기준 (모든 commit·기능 결정)**:
> "이 변경이 §0 사서 마크 시간 단축 OR §12 결제 의향 ↑ 양수 영향인가?" 음수면 거부.

상세 → `docs/sales/INDEX.md` (영업 자료 12건·가격 4단·4 페르소나·5월 일정) + `docs/pricing.md` + `docs/sales-roadmap.md` + `docs/sales/annual-calendar-2026-2027.md`.

---

## 13. 모바일 운영 (Phase 5)

상세 → `docs/mobile-tunnel.md` (Cloudflare Tunnel·ngrok 셋업·X-API-Key 보안·모바일 Claude Code 권한 사전 허용).
