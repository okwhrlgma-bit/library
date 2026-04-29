# 마스터 명세서 — kormarc-auto

> 이 파일은 PO가 정리한 종합 명세서를 담는 자리입니다.
> 별도 대화에서 받은 긴 명세서(시장 분석·API 상세·KORMARC 매핑·KDC 알고리즘·KOLAS 출력 형식 등)를 여기에 붙여넣으세요.
> **2026-04-29 갱신**: 야간 자율 누적 (50 task / 91+ docs / 91 ADR / 100% 흡수). §명세서 본문 13 영역 자동 채움 (2026-04-28 야간 자율 결과). PO 마스터 액션 플랜 단일 진실: `docs/po-master-action-plan-2026-04-28.md`.

---

## 빠른 참조 (헌법 보완)

### 데이터 흐름 핵심

```
ISBN 입력 (또는 사진 → 바코드 추출)
   ↓
[Stage 1] 국립중앙도서관 ISBN API
   ↓ 부재 시
[Stage 2] KOLIS-NET 통합 목록
   ↓ 부재 시
[Stage 3] 알라딘 ItemLookUp
   ↓ 부재 시
[Stage 4] 카카오 책 검색
   ↓ ISBN조차 없는 경우
[Stage 5] Claude Vision (표지/판권지/목차 분석)
   ↓
[Aggregator] 출처별 신뢰도 가중 통합
   ↓
[Builder] BookData → pymarc.Record
   ↓
[KDC Classifier] AI 추천 3개 (사서 선택)
   ↓
[Vernacular] 한자 감지 → 880 페어 생성
   ↓
[Validator] 008 길이, ISBN 체크섬, 필수 필드
   ↓
[KOLAS Writer] {ISBN}.mrc (UTF-8, ISO 2709)
```

### 데이터 출처 신뢰도 가중

| 소스 | 신뢰도 | 비고 |
|---|---|---|
| 국립중앙도서관 ISBN | 0.95 | 한국 자료 1순위 |
| KOLIS-NET | 0.92 | 다른 도서관 검증 데이터 |
| 알라딘 | 0.80 | 상용 데이터, 출처 표시 의무 |
| 카카오 | 0.75 | 보조 |
| Claude Vision (사진) | 0.65 | 사람 검토 필수 |
| Claude Vision + 외부 API 보강 | 0.85 | 교차 검증 |

### 필드별 자동화 가능성

- **100% 자동**: 005, 008(부분), 020, 040, 264, 300, 336/337/338
- **90%+ (사서 확인)**: 100, 245, 250, 490, 505, 520, 700
- **50~80% (AI 추천 + 사서 결정)**: 056(KDC), 082(DDC), 650(주제명), 049(청구기호)
- **수동 (AI 보조)**: 500(주기), 521(이용대상), 530(부가형식)

---

## 명세서 본문 (2026-04-28 자율 채움 — 야간 자율 26 docs + 84 ADR + 자료 폴더·D 드라이브 100% 흡수 기반)

### 1. 시장 분석

| 시장 | 규모 | 우리 영업 |
|---|---:|---|
| 작은도서관 | **6,830관** | 🟢 1순위 (KOLASYS-NET 사용·1인 사서) |
| 학교도서관 | **12,200관** + 사서교사 13.9% (1,660명) | 🟡 Phase 2~3 (자원봉사 86%) |
| 공공도서관 | 1,271관 (KOLAS III) | 🟡 자관 PILOT 후 |
| 대학도서관 | 별도 (KERIS RISS) | 🔴 Phase 3+ |

**경쟁사**: 북이즈·제이넷·제로보드 (1관 연 수백만원) vs 우리 (권당 100원·월정액 3만원~).
**차별화**: NLK validator 부재 시장 + KORMARC 4단 검증 + 9 자료유형 + Phase 1.5 MODS XML.

**참조**: `docs/competitor-analysis.md`·`docs/market-analysis.md`·`docs/keris-dls-phase2-prd.md`.

---

### 2. 외부 API 상세 (6 폴백)

`CLAUDE.md §3` 단일 진실 소스. 신뢰도 가중 통합 (`api/aggregator.py`).

| # | API | 신뢰도 | 폴백 순서 |
|---|---|---:|---:|
| 1 | NL Korea ISBN 서지 | 0.95 | 1 |
| 2 | KOLIS-NET 종합목록 | 0.92 | 2 |
| 3 | 도서관 정보나루 | 0.85 | 3 |
| 4 | 알라딘 ItemLookUp | 0.80 | 4 (출처 표시 의무) |
| 5 | 카카오 책 검색 | 0.75 | 5 |
| 6 | Claude Vision (사진) | 0.65 | 6 |

**Phase 1.5 추가 5종**: 국가서지·사서추천·출판예정·소장자료·NLD 책나래 (PO 신청 후).

---

### 3. KORMARC 필드 매핑표 (KS X 6006-0:2023.12)

#### 3 적용 수준

| 수준 | 정의 | 예시 |
|---|---|---|
| **M (Mandatory)** | 필수 | 005·007·008·020·245·260·300·049·056·090 |
| **A (Mandatory if applicable)** | 조건부 | 022 (연속간행물 ISSN)·362 (연속간행물)·538 (전자자료) |
| **O (Optional)** | 선택 | 521·530·653·700 (다중) |

#### 150+ 필드 그룹

| 필드 | 책임 | 자동화 |
|---|---|---|
| 001~005 제어 | 시스템 자동 | 100% |
| 006~008 고정길이 | builder | 100% |
| 010~049 숫자코드 | API + builder | 90~95% |
| 050~099 분류 | KDC AI 추천 | 80% (사서 결정) |
| 100~199 주표목 | API + 전거 활용 | 90% |
| 200~249 표제 | API | 95% |
| 250~299 판·발행 | API | 95% |
| 300~349 형태 | API | 95% |
| 500~599 주기 | AI 보조 | 50~70% |
| 600~699 주제 | NLK 주제명 (650) AI | 70% |
| 700~799 부출 | API + 사서 | 80% |
| 800~899 시리즈 부출 | builder | 85% |
| 900~980 로컬 | 자관 정책 ③ | 자관별 |

**참조**: `docs/marc-fields-guide.md`·`docs/kormarc-2023-standard-audit.md`·`docs/kormarc-spec-summary.md`.

---

### 4. KDC 자동 분류 알고리즘 (3단계)

```
Stage 1: ISBN 부가기호 추출 (95% 정확도, broad class 000~900)
   ↓
Stage 2: NL Korea API 056 필드 우선 (있으면 그대로 사용)
   ↓
Stage 3: AI 추천 (Claude Sonnet, 후보 3개)
   ↓ (사서 선택)
Stage 4: 사서 직접 입력 (자동 X)
```

**자료 자원**:
- `data/kdc6_kanmok.xlsx` (자료 폴더 cf14f7a9 흡수, 101행 × 5열)
- `classification/kdc_tree.md` (NLK 6판)
- 자관 청구기호 형식: `시문학811.7/ㅇ676ㅁ` = 별치 + KDC + 이재철

**참조**: `docs/d-drive-acquisition-audit.md`.

---

### 5. 880 한자·로마자 병기 자동 (NLK 표준)

**감지**: 한자 unicode (U+4E00 ~ U+9FFF) + 한글 unicode 페어 → 880 자동.

**로마자 표기** (NLK 「서지데이터 로마자 표기 지침(2021)」):
- Revised Romanization (RR) — 기본 (예: "한국" → "Hanguk")
- McCune-Reischauer (MR) — 학술 (예: "한국" → "Han'guk")

**필드**: 245·246·880·100·700.

**참조**: `vernacular/field_880.py`·`docs/nlk-cataloging-guidelines-audit.md`.

---

### 6. KOLAS III 자동 반입 형식

**메뉴**: `[단행 > 정리 > 목록완성 > 입력 > 반입 > MARC반입]`
**파일**: `{ISBN}.mrc` (UTF-8, ISO 2709)
**필수**: leader·005·007·008·020·049·056·090·245·260·300

**자관 검증** (.mrc 234 레코드 100% 정합):
- 005·007·008·020·049·056·090·245·260·300 모두 100% 출현
- 700 평균 2~3건 (부저자)·020 평균 1.2건 (ISBN 다중)

**참조**: `output/kolas_writer.py`·`docs/kolas-iii-audit.md`·`docs/d-drive-mrc-validation-audit.md`.

---

### 7. KERIS DLS 출력 형식 (Phase 2~3)

**시스템**: KERIS + 17 시·도교육청
**참여**: 12,200 학교도서관 (사서교사 13.9% 배치)
**표준**: KORMARC iso2709 동일 + DLS 양식 export 추가

**참조**: `docs/keris-dls-phase2-prd.md` (학교도서관 86% 미배치 → 자원봉사 친화 UI).

---

### 8. 5 상호대차 통합 매트릭스

| 시스템 | 운영 | 적용 | 비용 | 우리 영역 |
|---|---|---|---|---|
| **책바다** | NLK | 전국 | 5,200원 | csv·xlsx export |
| **책나래** | NLD | 1,166관 (장애인) | 무료 | csv (크롬 회피) |
| **책이음** | NLK + KLMS | 1,000+ (회원증) | 무료 | 양식만 (PII X) |
| **책두레** | NLK (KOLAS 모듈) | KOLAS 사용 | 무료 | F12 엑셀 자동 |
| **책단비** | 은평구 한정 | 11관 + 무인대출기 5 | 무료 | hwp 자동 (자관 양식) |
| **책밴드** | 알파스 (이씨오) | 알파스 사용 | 무료 | (알파스 위임) |

**참조**: `docs/interlibrary-5systems-comparison.md`·`docs/seoul-25gu-interlibrary-naming.md`·`docs/yangsik-matrix.md`.

---

### 9. UI/UX 와이어프레임 + 11 UIUX 매트릭스

**Top 4 추천** (`docs/keris-alphas-integration-audit.md`):

1. ★ **Folder Watcher** (점수 86): KOLAS F12 엑셀 자동 감지·검증 (`watchers/download_watcher.py`)
2. **Browser Extension** (점수 85): 알파스 카탈로깅 화면 인라인 button (별도 repo)
3. **System Tray App** (점수 84): 정시 09·18·22시 toast + 핫키 (`pystray`)
4. **OS File Association** (점수 84): .marc·.kormarc 우리 SaaS 핸들러

**현행**: Streamlit 모바일 반응형 (`ui/streamlit_app.py`).

---

### 10. 테스트 골든 데이터셋

**자관 .mrc 174 파일** = `tests/integration/d_drive_mrc_validation.py` 직접 활용 (8,700 레코드 추정).

**골든**: `tests/samples/golden/` 50건 (NL Korea/KOLIS-NET 응답 자동 수집).

**검증 어셔션**: `scripts/binary_assertions.py` 23/23 + M/A/O 분기 (ADR 0045).

---

### 11. 법적·윤리적 주의사항

#### PIPA 5대 코드 패턴 (생존 조건, 시행 2026-09-11)

1. **Reader/Borrower/Patron entity ERD 부재** — ✅ 자관 알파스 위임
2. **암호화 (bcrypt·AES-256·TLS 1.2+)** — 🟡 logging PII 5종 보강 필요
3. **DSAR (제35·36·37·35조의2)** — ✅ /account/export·delete
4. **72h 신고 자동화** — ❌ 베타 PILOT 도달 시
5. **audit_log + 해시 체인** — ❌ 5만명+ 도달 시

#### 도서관법

| 법령 | 시행일 | 우리 영역 |
|---|---|---|
| 도서관법 (제19592호) | 2023.8.8 | §20 납본 (출판사 의무, 우리 셀링) |
| 도서관법 시행령 | 2024.5.28 | |
| 도서관법 시행규칙 | 2022.12.8 | |

#### 저작권법

- 알라딘 출처 표시: ✅ `api/aladin.py`
- KDC 분류표 KLA 보유 권리: ✅ 주류·강목 무료분만
- KORMARC 데이터 자체 = 저작권 X

**참조**: `docs/legal-references.md`·`docs/regulatory-landscape.md`·`docs/privacy-policy.md`·`docs/terms-of-service.md`.

---

### 12. Phase 로드맵

| Phase | 시기 | 영역 | 자료유형 |
|---|---|---|---:|
| Phase 1 | 완료 | ISBN→KORMARC | 4/9 |
| Phase 1.5 | 진행 | MODS XML + 5 자료유형 | **9/9 (100%) ✅** |
| Phase 2 | Q3 2026 | 학교도서관 (KERIS DLS) | + DLS 양식 |
| Phase 3 | Q4 2026 | 대학도서관 (KERIS RISS) | + RISS 호환 |
| Phase 3+ | 2027 | 글로벌 (MARC21·BIBFRAME) | + 영어·중국어 |

---

### 13. 자관 PILOT (영업 1순위)

**자관 = 「내를건너서 숲으로 도서관」 (은평구공공도서관 11개 중 1개)**:
- 시문학·윤동주 특화 도서관 (35 컬렉션)
- 사서 8명 운영 (수서·종합·매크로·콘텐츠)
- 5 시스템 동시 운영 (KOLAS·알파스·다우오피스·Formtec·한셀)
- 6년 NPS·5년 책단비·1년 40 차수·3년 정시 캡처 历사
- .mrc 174 KORMARC iso2709 직접 검증 자료

**참조**: 8 자관 audit docs (`d-drive-*`).

---

## 다음 세션 작업 큐

### 완료 (2026-04-25 v0.3)
- [x] Phase 2: Claude Vision 2단계 (Haiku ISBN → Sonnet 종합)
- [x] Phase 3: KDC AI 분류 (Sonnet + tool_use + prompt caching)
- [x] Phase 3+: Subject(650) NLSH AI 추천
- [x] Phase 4: Streamlit UI (모바일 반응형, 4탭)
- [x] Phase 5: FastAPI REST 서버 + 인증 + 사용량 카운터
- [x] 검색: NL/알라딘/카카오 키워드 통합 검색
- [x] 출력 포맷: DLS·MARCXML·CSV·KOLAS 모두
- [x] 사서 가치: 049 청구기호, KOLAS 사전 검증, KOLIS-NET 비교
- [x] 모바일 인프라: cloudflared/ngrok 자동 설치 + 권한 사전 등록
- [x] 수익화 가설 §12 헌법화 + pricing.md

### 다음 세션
- [ ] **PO 액션**: ANTHROPIC_API_KEY/NL_CERT_KEY 등 .env 채우기
- [ ] **PO 액션**: cloudflared 1회 로그인 (`docs/mobile-tunnel.md`)
- [ ] **PO 액션**: 베타 사서 1~2명 모집
- [x] **자동화**: 골든 데이터셋 — NL Korea/KOLIS-NET 응답을 정답으로 자동 수집 (`scripts/build_golden_dataset.py`). PO 키 채우면 `python scripts/build_golden_dataset.py` 1회로 50건 .mrc + .json + _index.csv 자동 생성.
- [x] **자동화**: 정확도 측정 — 풀 파이프라인 vs 골든 필드별 일치율 (`scripts/accuracy_compare.py`)
- [ ] 사서 베타 인터뷰 → 우선순위 재조정 (PO 액션)
- [ ] 결제 시스템 정식화 (포트원/토스, MVP-2)
- [ ] 008 발행국부호 매핑 전체 보강 (KORMARC 매뉴얼 PDF 입수)
- [ ] librarian_helpers/call_number 도서관별 규칙 JSON 1관 작성 (베타 도서관 협조 시)
