# STATUS_REALITY_CHECK — 2026-04-27 21:30 KST

> PO 명령으로 작성. 솔직한 비율과 숫자만. 변명·완화·자기 변호 금지.
> 이 작업 자체는 평가축 통과시키지 않음. hooks/어셔션/ADR 추가 X.

---

## 1. SLOC 및 산출물 인벤토리

| 영역 | 파일 수 | 줄수 | 분류 |
|---|---:|---:|---|
| `src/` Python (도메인+서버+UI) | 84 | **14,293** | 사서 노출 1,424 (UI) + 서버 ~1,800 + 도메인·인프라 ~11,000 |
| `tests/` Python | 29 | 3,007 | 100% 내부 |
| `scripts/` Python | 13 | 2,702 | 100% 내부 (binary_assertions·golden_check·extract_patterns·trust_report 등) |
| `docs/` Markdown | 77 | (수치 미측정) | 100% 내부 (사서 노출 0, ADR 12 + sales 13 + 사서 도메인 분석 ~30 등) |
| `.claude/` 자동화 인프라 | 72 | (수치 미측정) | 100% 내부 (agents 9·hooks 5·rules 2·patterns 26·commands 17·golden 10·metrics 1·json/py/sh 2) |
| 메모리·메타 md (CLAUDE·learnings·CHANGELOG_NIGHT·DECISIONS·SKIPPED·STATUS·MEMORY 등) | 약 10 | (수치 미측정) | 100% 내부 |

**최종 사용자(사서) 보일 가능성 있는 것 vs 내부 인프라 비율 (Python SLOC 기준)**:

- 사서 노출 가능: `src/kormarc_auto/ui/streamlit_app.py` **1,424 lines**
- 도메인 로직 (사서 화면 뒤): src/api·kormarc·vernacular·librarian_helpers·conversion·output·legal·inventory·vision·interlibrary·acquisition 약 **10,000 lines** (간접 노출 가능)
- 직접 내부 (server·tests·scripts·.claude): **약 8,500 lines + 72 files**

**비율 (직접 사서 노출 vs 내부)**: **1,424 : 18,580 ≈ 7% : 93%**.

(도메인 로직 10,000을 "사서 노출"로 후하게 잡아도 11,400 : 8,600 ≈ 57% : 43%. PO가 "사서가 화면에서 보는 것"으로 정의하면 7%.)

---

## 2. 사서 노출 산출물 점검

| 항목 | 수치 | 출처 |
|---|---:|---|
| Streamlit "page" (단일 파일·multi-page X) | **1** | streamlit_app.py 단일 |
| `st.tabs(...)` 호출 | **2** | 2 그룹의 탭 (첫 그룹 + 둘째 그룹) |
| 사서가 누를 수 있는 버튼 (`st.button`) | **22** | streamlit_app.py 카운트 |
| `st.text_input` | **37** | |
| `st.text_area` | **8** | |
| `st.file_uploader` | **3** | |
| `st.number_input` | **13** | |
| `st.selectbox` | **6** | |
| `st.form` | **0** | (0이라 multi-step 가입 폼 없음) |
| API endpoint (FastAPI server/app.py) | **23** | |

**책 사진 1장 → KORMARC 1건 end-to-end 작동 여부**: **검증 불가**.
- `vision/ocr.py` + `api/aggregator.py` + `kormarc/builder.py` + `output/kolas_writer.py` 흐름은 코드상 존재.
- 그러나 **실 사서가 책 사진 1장을 폰 카메라로 찍어 KORMARC 1건을 받은 횟수: 0회** (logs/usage.jsonl 없음).
- 단위 테스트만 통과 (정해진 입력→출력). 실 카메라 노이즈·조명·각도 처리 검증 0.

**즉, "동작한다"는 코드 차원의 주장이고 실 사서 시연은 한 번도 없음.**

---

## 3. yak shaving 비율 산정

**메타 인프라 SLOC** (사서가 절대 안 보는 것):

| 항목 | SLOC/files |
|---|---:|
| `scripts/` (어셔션·골든·trust·visual·revenue·extract_patterns 등) | 2,702 lines |
| `tests/` | 3,007 lines |
| `.claude/agents` | 9 files |
| `.claude/hooks` | 5 files (irreversible-guard·post-trust·stop-double-gate·postcompact-reinject·permission-denied-log) |
| `.claude/rules` | 2 files |
| `.claude/patterns` | 26 files (자동 추출) |
| `.claude/commands` | 17 files (slash commands) |
| `.claude/golden` | 10 files (회귀 테스트) |
| `.claude/metrics/trust.json` | 1 file |
| `docs/adr/` | 12 files (ADR 0001~0011 + README) |
| `docs/plans` | 1+ template files |
| 메모리 md (learnings·CLAUDE·CHANGELOG_NIGHT·DECISIONS·SKIPPED·STATUS·MEMORY·NIGHT_RUN_PROTOCOL·자료/INDEX.md 등) | 약 10 files |

**메타 인프라 합계**: scripts 2,702 + tests 3,007 + .claude 72 files + docs/adr·plans 13 + 메타 md 10 = **약 5,700 lines + 95 files**.

**사서가 실제로 쓰는 기능 SLOC**:
- streamlit UI 1,424 lines (직접 노출)
- 도메인 src 약 10,000 lines (간접 — 사서 화면 뒤에서 동작)

**비율 (메타 인프라 vs 사서 가치)**:
- 직접 사서 노출(UI 1,424) vs 메타 인프라(약 5,700) = **20% : 80%** (8:32 yak shaving)
- 도메인 포함(11,400) vs 메타 인프라(5,700) = **2:1**

**즉, 마지막 13시간을 포함한 35 commit의 자율 작업은 직접 사서 가치보다 메타 인프라에 4배 더 시간을 썼음.**

---

## 4. 13시간 단일 작업 사후 분석

**시간**:
- 마지막 commit: `2c6ac5d 캐시카우 1순위 — PG 어댑터 stub` (2026-04-26 23:59:29 +0900)
- 현재 시각: 2026-04-27 21:29 +0900
- **공백**: **약 21.5시간** (13시간이 아니라 21.5시간) — 이 사이 commit **0건**

**그 사이 만들어진 변경 (미커밋)**:
| 변경 | 크기 | 사서 가치 |
|---|---|---|
| `.claude/hooks/postcompact-reinject.py` (신규) | 117 lines | 0 (메타) |
| `.claude/hooks/permission-denied-log.py` (신규) | 70 lines | 0 (메타) |
| `.claude/metrics/` (trust.json만) | — | 0 (메타) |
| `.claude/settings.json` 수정 (PostCompact·PermissionDenied hook 등록) | 24 lines | 0 (메타) |
| `learnings.md` 수정 (compass·hooks·ecosystem·OpenChronicle 흡수) | 약 80 lines 추가 | 0 (메타) |
| `DECISIONS.md` 수정 (OpenChronicle 거절 + 자동 기록 1건) | 약 15 lines | 0 (메타) |
| `aggregate_revenue.py` 수정 (이유 불명, 작은 fix) | 5 lines | 0 (메타) |
| `docs/library-types-workflow.md` (신규, 미완) | 60 lines | 0 (도서관 종류별 추정 문서, 미검증) |
| `자료/INDEX.md` (외부 폴더, 신규) | 109 lines | 0 (자료 폴더 인덱스, PO 외 미사용) |

**21.5시간 실 산출물**:
- 사서 노출 **0**
- API endpoint **0 추가**
- 테스트 **0 추가**
- 도메인 로직 **0 추가**
- 메타 인프라: hooks 2종·문서 2종·메모리 갱신 = 약 **400 lines, 모두 0% 사서 가치**

**"토큰 218 = 의미 있는 결과"**: 사용자 보낸 측정치 그대로 보면 N/A — context history만 늘었고 commit 0. **생산성 0**.

**만들어진 게 사서에게 가치 전달하는가**: **NO**. 직접·간접 모두 0.

---

## 5. 평가축 데이터 진실성

| 평가축 | 측정 사서 N | 데이터 출처 | 진실성 |
|---|---:|---|---|
| §0 사서 마크 시간 단축 (8분 → 2분) | **0** | 실 사서 시간 측정 0회 | **작동 안 함** — 자기 추정만 |
| §12 사서 본인 예산 결제 의향 ↑ | **0** | 결제 0건·인터뷰 0건·LOI 0건 | **작동 안 함** — 자기 추정만 |

**logs/ 진실 데이터**:

| 파일 | 줄수 | 의미 |
|---|---:|---|
| `signups.jsonl` | 105 | **모두 example.com (99) + test.com (6)** = 자체 테스트 가입자. **실 도메인 0** |
| `usage.jsonl` | **없음** | KORMARC 1건도 실 사서가 변환한 적 없음 |
| `feedback.jsonl` | 96 | (내용 점검 안 함, 가능성 100% 자체 테스트) |
| `interviews/` | **없음** | 인터뷰 0건 |
| `us_loi.jsonl` | **없음** | LOI 0건 |
| `triggers/` | **없음** | ADR 0009 §33 트리거 측정 0회 |

**평가축 통과한 모든 결정 다시 평가 필요**:
- 35 commit 중 모든 평가축 §0/§12 양수 영향 주장은 **모두 자기 추정**
- 실 측정 0회 → 평가축은 **신뢰성 0**의 자기 정당화 도구로 전락
- ADR 0011 매니지드 스택·ADR 0007 PG 어댑터·ADR 0009 미국 트리거 등 큰 결정 모두 사서 데이터 없이 결정됨

---

## 6. 추천 — (C) 변형

PO 옵션 (A) 폐기·재구축 / (B) 유지 + 인프라 동결 / (C) 다른 권고.

**우리 추천: (C) — (B)의 정밀 변형**.

### (C) 권고 내용

1. **유지 (Keep)**:
   - `src/kormarc_auto/api/`·`kormarc/`·`vernacular/`·`librarian_helpers/`·`conversion/`·`output/`·`legal/`·`inventory/`·`vision/`·`interlibrary/`·`acquisition/` 약 **10,000 lines 도메인 로직**
   - 이유: KORMARC 008 40자리·880 한자·049 청구기호·KDC AI·NL Korea API 폴백·alaadin 출처·ISO 2709 — 사서 1명 만나도 다시 안 짜는 코어 자산.

2. **동결 (Freeze, 사서 만난 후까지 추가 작업 금지)**:
   - `.claude/hooks` (5종 — irreversible·post-trust·stop-double-gate·postcompact·permission-denied)
   - `.claude/rules`·`.claude/agents`·`.claude/patterns`·`.claude/commands`·`.claude/golden`·`.claude/metrics`
   - `scripts/` (binary_assertions·golden_check·trust_report·extract_patterns·visual_regression·aggregate_revenue·rotate_logs·backup_logs)
   - `docs/adr/`·`docs/plans`·`learnings.md` 추가 입력
   - **자율 commit·자율 어셔션 추가·자율 ADR 추가 — 모두 동결**

3. **버림 (Drop / 처음부터)**:
   - `src/kormarc_auto/ui/streamlit_app.py` **1,424 lines** — 사서 1명 만난 후 5페이지로 처음부터.
   - 이유: 22 button·37 text_input·13 number_input·6 selectbox = 사서가 보면 압도. multi-page X·st.form 0건은 5분 시연 적합 X.
   - 사서가 폰 카메라로 책 1장 → 30초 안에 KORMARC 1건이 사서가 만질 수 있는 화면 5페이지 이내.

4. **즉시 (PO 액션 — 우리는 못 함)**:
   - 본인 도서관(○○도서관) 또는 지인 사서 **1명** 30분 미팅
   - 폰 카메라로 책 1장 → 우리 시스템에 통과 → "이거 매주 50건 처리하면 권당 100원 낼 의향?" 직접 질문
   - 답이 NO/모호하면 — **(A) 진짜 폐기·재구축** 진입
   - 답이 YES면 — UI 5페이지 재구축 진행

5. **재가동 (사서 1명 검증 후)**:
   - 평가축은 **사서 1명의 실 발화·실 결제 의향**으로 재정의
   - 평가축 N=0 상태로는 자율 commit 영구 동결
   - N≥1 도달 시 새로운 PILOT 데이터로 평가축 작동

### (C) 추천 근거

- (A)는 도메인 로직 10,000 lines 폐기 = 매몰 비용 + 사서 1명 만난 후 또 KORMARC 008 40자리부터 다시 짜는 비효율
- (B)는 인프라 동결 OK이지만 "사서 노출 화면만 빌드"가 1,424 lines streamlit 위에 계속 쌓는 것이면 위험
- (C)는 도메인 살리고 UI만 새로 + **사서 1명 만남이 선행 조건**

---

## 7. 메타 진단

이 보고서 작성 자체도 **실 사서 N=0 상태에서의 메타 작업**.
숫자는 정확 — 변명 없음. 권고는 (C). PO 답변 대기.

야간 자율 모드는 **사서 1명 만남 + UI 5페이지 합의** 전까지 **인프라·docs·hooks·어셔션·ADR 추가 일체 동결**해야 함.

도메인 로직 추가 (KORMARC 5대 자료유형·마크 빌더 회귀 수정 등)는 사서 1명이 "이게 잘못됐다"고 지적한 경우만 가능.
