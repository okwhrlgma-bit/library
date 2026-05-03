# Claude Code 자율 작업 명령문 패키지 v2

**문서 성격**: 1차 보고서 명령문 패키지의 후속·정정판
**대상**: Claude Code (autonomous agent), PO 사서 E
**총 작업 시간**: 약 14~16시간 (9개 모듈, 순차 실행)
**전제 조건**: v0.5.0 완료, PMF 통과(Sean Ellis 62.5%·LTV/CAC 15.8x), 462 tests pass
**핵심 변경**: 외주 마크 시장 흡수형 비즈니스 모델 반영 + 페르소나 5명 시나리오 테스트 + 컴플라이언스 2단계 분리

---

## 사용 방법

각 모듈은 **그대로 Claude Code에 붙여넣어 실행**할 수 있는 단일 명령문이다. 순차 실행이 원칙(M1 → M2 → ... → M9)이지만, 모듈 헤더의 `[의존성]`을 보고 병렬 가능한 것은 병렬화해도 된다.

**워크플로우 규약** (CLAUDE.md 정합):
1. 모듈 시작 전 `git pull origin main` 실행
2. 모듈 종료 시 PROGRESS.md 자동 업데이트 (Claude Code 책임)
3. 모듈 종료 시 commit + push (메시지: `feat(Mn): {모듈명} - v0.5.{n}`)
4. 462 tests를 깨면 **즉시 롤백**, PO에게 보고
5. 헌법 §0(사서 시간 단축) 또는 §12(결제 의향 ↑) 양수 영향 검증 → 음수면 거부

**PO 외부 작업 의존**:
- M1 시작 전: PO가 `사용자_TODO.txt`, `PROGRESS.md`, `pyproject.toml`, `CLAUDE.md`를 web Claude에 첨부 (저장소 비공개라 클로드 코드 외부 도구는 직접 접근 불가, 단 Claude Code는 로컬 작업 가능)
- M9-A 시작 전: PIPA 위탁계약서 템플릿 PO 직접 작성 (법무 영역, Claude Code 작성 불가)

---

## M1 — 인벤토리 + 외주 마크 비교 데이터셋 (1.5h)

**[목적]** 1차 보고서가 GitHub 비공개로 인벤토리에 실패했음. v2에서는 로컬 git log + PROGRESS.md + 코드 트리를 직접 분석하여 정확한 현황표 작성. 추가로 외주 마크 시장 비교 데이터를 수집하여 §0/§12 가치 제안 근거 강화.

**[의존성]** 없음. 단 PO가 web Claude 대화 흐름에서 첨부한 파일들을 참조 자료로 인지

**[명령문]**

```
다음 작업을 순차로 수행하라:

1. 저장소 현황 인벤토리
   - `git log --oneline -100`으로 최근 커밋 100개 분석
   - `find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" | xargs wc -l | tail -30`로 코드 라인 수 상위 30개 파일 추출
   - `pytest --collect-only -q | tail -50`로 테스트 462개의 분류 확인 (단위/통합/e2e/시나리오)
   - `pyproject.toml` 의존성 트리 분석 → 외부 API 의존성 9개(SEOJI, data4library, 알라딘, 국회도서관 등)의 호출 횟수·실패율 측정 코드가 있는지 확인
   - 위 결과를 `docs/research/v2-inventory-2026-05.md`에 작성

2. 외주 마크 비교 데이터셋 구축
   - 새 파일 `data/outsourcing_baseline.csv` 생성
   - 컬럼: 사례_ID, 지역(시도), 기관유형(학교/공공), 단가_원, 기준연도, 출처_URL, 메모
   - 다음 데이터 시드 (최소 15행, 상세는 v2 보고서 §2.1 참조):
     - 경기도 학교도서관 평균 권당 237원 (2021)
     - 학교도서관저널 추정 권당 작업비 880~1,100원
     - 공공도서관 권당 외주 800~1,500원 (지역별 편차)
     - 사립대 분관 권당 1,500~3,000원 (정확도 기준 강화)
     - … (보고서 표 그대로 시드)
   - PO 입력 행을 위한 빈 행 5개 추가

3. 페르소나 5명 시나리오 테스트 픽스처 생성
   - 새 파일 `tests/fixtures/personas/`에 5개 디렉토리 생성:
     - `01_kim_jiwon_school_teacher/` (사립 중학 사서교사, 신간 2,500~3,500권/년)
     - `02_park_seoyeon_small_library/` (작은도서관 관장)
     - `03_lee_minjae_rotating/` (P15 순회사서)
     - `04_jeong_yujin_university_branch/` (사립대 분관)
     - `05_choi_youngja_kolas_loyalist/` (Rejecter)
   - 각 디렉토리에 `scenario.json` 생성 (입력 ISBN 10건, 예상 KORMARC 필드, 거부 시나리오 포함)
   - 본 픽스처는 M7에서 통합 테스트로 활용

4. PROGRESS.md 업데이트:
   - `## v0.5.1 (2026-05-XX) - M1 인벤토리 + 외주 비교 데이터셋` 섹션 추가
   - 변경 파일 목록, 추가 코드 라인 수, 다음 모듈 M2 의존성 명시

5. 커밋: `feat(M1): inventory + outsourcing baseline + persona fixtures - v0.5.1`
```

**[검증]** PROGRESS.md에 v0.5.1 섹션 존재 + `data/outsourcing_baseline.csv` 15행 + `tests/fixtures/personas/` 5개 디렉토리 생성 확인.

**[성공 기준]** v2 보고서 §2(시장 정밀화) 데이터를 코드베이스에서 직접 조회 가능한 상태.

---

## M2 — ISBN 바코드 1차 경로 강화 (2h)

**[목적]** 1차 보고서의 핵심 권고 "ISBN 바코드 + SEOJI/data4library 1차 경로"를 실제 코드에 구현. 사진 OCR보다 70% 빠르고 비용 1/10. 사서가 보유한 EAN-13 1D 스캐너 입력을 HID 자동입력으로 받아 KORMARC 12~15개 필드를 1초 내 채운다.

**[의존성]** M1 완료 (외부 API 호출 측정 인프라)

**[명령문]**

```
다음을 구현하라:

1. ISBN 입력 모드 3가지 추가 (`src/kormarc_auto/input/isbn_modes.py`):
   - mode_a: 단일 ISBN 텍스트박스 (현재 v0.5.0 유지)
   - mode_b: HID 스캐너 자동입력 (스캐너가 키보드 에뮬레이션 → ISBN 입력 후 Enter 자동 송신, Streamlit `st.text_input` + `on_change` 콜백 + 입력 후 자동 클리어)
   - mode_c: 연속 스캔 모드 (스캐너로 50권 연속 스캔 → 큐에 적재 → 일괄 처리)
   - 각 모드는 동일한 핸들러 `process_isbn(isbn: str) -> KormarcRecord` 호출

2. SEOJI API 호출 통합 (`src/kormarc_auto/sources/seoji.py`):
   - 국립중앙도서관 ISBN/납본 검색 API 호출
   - 인증키는 환경변수 `SEOJI_API_KEY` (PO가 발급, .env.example에 명시)
   - 재시도 3회 + exponential backoff
   - 응답 → KORMARC 필드 매핑: 020(ISBN), 245(서명), 250(판), 260/264(출판사·연도), 300(형태), 490(총서), 700(저자)
   - 실패 시 fallback: data4library → 알라딘 → 사진 OCR 순서

3. data4library API 호출 추가 (`src/kormarc_auto/sources/data4library.py`):
   - 도서관정보나루 도서소장정보 API
   - SEOJI에 없는 책(특히 외서, 신간 1주 이내) 보완
   - KORMARC 041(언어), 084(KDC), 950(가격) 필드 추가

4. 알라딘 API 백업 경로 (`src/kormarc_auto/sources/aladin.py`):
   - TTBKey 환경변수 `ALADIN_TTB_KEY`
   - SEOJI/data4library 둘 다 실패 시 호출
   - 표지 이미지 URL 추출 (Streamlit UI 미리보기용)

5. 통합 디스패처 (`src/kormarc_auto/sources/dispatcher.py`):
   - 입력: ISBN 13자리
   - 출력: KormarcRecord + source_chain (어느 API에서 어떤 필드를 가져왔는지 추적)
   - 캐싱: SQLite `cache/isbn_cache.db`에 24시간 TTL (동일 ISBN 재호출 방지)
   - 메트릭: 응답시간, 필드 채움률, fallback 발생 횟수 → `metrics/isbn_pipeline.jsonl` 기록

6. 단위 테스트 추가 (tests/test_isbn_pipeline.py, +30 tests):
   - 정상 ISBN 13자리
   - 잘못된 체크섬
   - SEOJI 누락 시 data4library fallback
   - 모두 실패 시 사진 OCR 안내 메시지
   - 페르소나 시나리오 5건 (M1 fixtures 참조)

7. PROGRESS.md 업데이트 + 커밋: `feat(M2): ISBN barcode primary path - SEOJI/data4library/aladin - v0.5.2`
```

**[검증]** 462 → 492 tests 모두 pass. 페르소나 01(김지원) 시나리오에서 ISBN 10건 입력 → 평균 응답 1.2초 이내, 필드 채움률 85%+ 확인.

**[성공 기준]** 헌법 §0 양수: 권당 8분 → 30초 단축. 헌법 §12 양수: 외주 비교 시뮬레이터(M5)에서 권당 200원 SaaS의 경제성 자동 산출.

---

## M3 — 사진 OCR 보조 경로 (1.5h)

**[목적]** 1차 보고서대로 사진 OCR을 **보조 경로로 강등**. ISBN 바코드 없는 책(고서, 외서 일부, 손상된 바코드)에 한정 사용. Claude vision 호출은 Haiku 4.5 우선 (Sonnet 4.6은 fallback).

**[의존성]** M2 완료

**[명령문]**

```
다음을 구현하라:

1. 사진 OCR 트리거 조건 명시 (`src/kormarc_auto/input/photo_trigger.py`):
   - 조건 1: 사용자가 ISBN 입력란을 비우고 "사진 사용" 토글 ON
   - 조건 2: ISBN 입력했으나 SEOJI/data4library/알라딘 모두 실패
   - 조건 3: 외서(언어 코드 kor 외)이고 ISBN-13이 아닌 경우
   - 그 외에는 사진 OCR을 호출하지 **않음** (비용 절감)

2. Claude vision 모듈 (`src/kormarc_auto/sources/claude_vision.py`):
   - 1차 시도: claude-haiku-4-5 (단가 $1/$5 per MTok)
   - Haiku 신뢰도 < 0.85이면 2차 시도: claude-sonnet-4-6 ($3/$15)
   - 표지 1장 + 판권면 1장 = 2 이미지 입력
   - 출력: 추출된 텍스트 + 추정 KORMARC 필드 (245/250/260)
   - prompt caching 활성화 (시스템 프롬프트 90% off)

3. OCR → KORMARC 매핑 검증 (`src/kormarc_auto/sources/ocr_validator.py`):
   - OCR 결과의 ISBN-like 패턴(13자리 숫자)을 추출 → SEOJI 재호출
   - 페르소나 04(정유진, 의학 외서) 시나리오: ISBN 없는 분관 인수도서 → OCR로 245/260만 추출 후 사서 수동 보완

4. 비용 측정 강화:
   - `metrics/ocr_pipeline.jsonl`에 권당 토큰 수, 모델, 비용($) 기록
   - 일일 집계 스크립트 `scripts/daily_cost_report.py` 추가

5. 단위 테스트 (+15):
   - ISBN 있을 때 OCR 호출 안 됨 확인
   - Haiku → Sonnet 승격 트리거
   - 외서 시나리오

6. PROGRESS.md + 커밋: `feat(M3): photo OCR as fallback only - Haiku/Sonnet routing - v0.5.3`
```

**[검증]** 1,000권 가상 시뮬레이션에서 OCR 호출 비율 < 15% 확인. 권당 평균 비용 < 20원.

---

## M4 — KDC 자동분류 v2 (KoSimCSE/KURE fine-tune) (2h)

**[목적]** 1차 보고서의 4순위 대안 "KDC 임베딩 모델"을 Phase 1로 시작. Alma 12~24개월 시간창 동안 한국어 KDC 분류 정확도를 SOTA로 끌어올려 **장기 moat** 구축.

**[의존성]** M2 완료 (ISBN으로 코퍼스 수집)

**[명령문]**

```
다음을 구현하라:

1. KDC 학습 코퍼스 수집 (`scripts/build_kdc_corpus.py`):
   - SEOJI API에서 최근 5년 신간 중 KDC 부여된 도서 50,000건 수집
   - 합법성: SEOJI 공개 API 약관 확인, 메타데이터만 수집 (본문 X)
   - 익명화: 도서관 식별자 마스킹
   - 출력: `data/kdc_corpus_v1.parquet` (ISBN, 245, 246, 500, 520(있으면), KDC, KDC6 분류레벨)

2. 임베딩 모델 비교 평가 (`scripts/eval_kdc_embeddings.py`):
   - 후보: KoSimCSE-roberta-multitask, KURE-v1, multilingual-e5-large
   - 5,000건 dev set에서 KDC 3자리 분류 정확도 측정
   - 결과를 `docs/research/kdc-embedding-bench-2026-05.md`에 기록

3. Fine-tune 파이프라인 (`src/kormarc_auto/classify/kdc_classifier_v2.py`):
   - 우승 모델로 분류 head 학습 (1080개 KDC 3자리 클래스)
   - 학습 환경: 로컬 RTX 4090 1장 (4시간 추정) 또는 Colab Pro+ A100
   - 출력: `models/kdc_classifier_v2.safetensors` (모델 파일은 .gitignore)
   - HuggingFace 비공개 저장소 업로드 옵션 (PO 결정)

4. 추론 통합 (`src/kormarc_auto/classify/kdc_infer.py`):
   - 입력: 245(서명) + 520(요약, 있으면) + 출판사
   - 출력: KDC 후보 top-3 + 신뢰도
   - 신뢰도 < 0.7이면 사서 확인 UI에 노란색 표시

5. A/B 테스트 인프라 (`src/kormarc_auto/classify/ab.py`):
   - v1(현재 룰베이스) vs v2(임베딩) 동시 호출
   - 사서 최종 선택 기록 → 모델 개선 데이터로 축적
   - federated learning 설계 문서: `docs/research/federated-learning-plan.md`

6. 단위 테스트 (+20):
   - 동일 ISBN 추론 일관성
   - 신뢰도 < 0.7 시 UI 플래그
   - 페르소나 02(박서연, 작은도서관 800권/년) 시나리오에서 v2 정확도 ≥ v1

7. PROGRESS.md + 커밋: `feat(M4): KDC classifier v2 with embedding fine-tune - v0.5.4`
```

**[검증]** Dev set 정확도 v1 78% → v2 88%+ (목표). 추론 latency < 200ms.

**[성공 기준]** 한국어 KDC 분류에서 Alma(LC 분류 한정)와 비교 우위 데이터 확보 → 영업 자료에 활용 가능.

---

## M5 — Streamlit UI 강화 + 외주 비교 시뮬레이터 (1.5h)

**[목적]** 페르소나 5명 워크플로우 검증 + **외주 vs SaaS 비교 시뮬레이터** 추가 (행정실장·교장에게 보여줄 1페이지 PDF 자동 생성). 1차 보고서에 없던 핵심 매출 도구.

**[의존성]** M2, M4 완료

**[명령문]**

```
다음을 구현하라:

1. 메인 화면 3-탭 재설계 (`src/kormarc_auto/ui/main.py`):
   - 탭 1: "신간 등록" (ISBN 단일/연속 스캔/사진 OCR)
   - 탭 2: "외주 비교 계산기" (NEW)
   - 탭 3: "출력·내보내기" (.mrc 파일, KOLAS 가져오기 양식)

2. 외주 비교 계산기 (`src/kormarc_auto/ui/cost_calculator.py`):
   - 입력 위젯:
     - 연간 신간 수 (슬라이더 500~10,000권)
     - 현재 외주 단가 (드롭다운: 237원/800원/1,500원/직접입력)
     - 사서 시간당 인건비 (기본 25,000원, 학교 기간제 기준)
     - 외주 검수 시간 (권당 분, 기본 3분)
   - 자동 계산:
     - 외주 연 비용 = 신간 × 외주 단가 + 검수 시간 × 인건비
     - SaaS 연 비용 = 신간 × 200원 (학교 200만/년 상한 캡 적용)
     - 절감액 + 회수 기간 (원)
     - 사서 시간 절약 (시간/년)
   - 시각화: 막대 그래프 (matplotlib 또는 Streamlit 내장)

3. 결제자용 1페이지 PDF 생성 (`src/kormarc_auto/ui/admin_pdf.py`):
   - reportlab 또는 weasyprint 사용
   - 내용:
     - 학교명 (입력)
     - 외주 vs SaaS 연 비용 비교표
     - 권당 단가 비교
     - 사서 시간 절약량 → 다른 업무 가능
     - "본 도구는 KORMARC 표준 KS X 6006-0:2023.12 정합" (신뢰 신호)
     - 도입 사례 1건 (PILOT 학교 익명화)
   - 출력: `output/{학교명}_도입제안서_{YYYYMMDD}.pdf`

4. 페르소나별 빠른 시작 가이드 (`src/kormarc_auto/ui/onboarding.py`):
   - 첫 로그인 시 페르소나 선택 (5개 중 선택)
   - 선택에 따라 기본값 자동 설정:
     - 김지원 (학교사서교사) → 신간 3,000권, 외주 단가 237원
     - 박서연 (작은도서관) → 신간 1,000권, 외주 단가 800원
     - 이민재 (P15 순회) → 신간 2,000권 × 15교
     - 정유진 (대학분관) → 신간 6,000권, 외주 단가 1,500원
     - 최영자 (KOLAS 충성) → "이 도구가 적합하지 않을 수 있습니다" 안내 (Rejecter 시나리오)

5. 결제자 vs 사서 모드 분리:
   - 사서 모드: 카탈로깅 작업 화면 (현재 v0.5.0)
   - 결제자 모드: 비용 계산기 + PDF 다운로드 + 영업 문의 폼

6. 단위 테스트 (+15) 및 e2e 시나리오:
   - 페르소나 01 워크플로우 (탭 1 → 50권 등록 → 탭 3 .mrc 출력)
   - 페르소나 03 워크플로우 (P15 모드, 다관 전환)
   - 결제자 모드 PDF 생성 검증

7. PROGRESS.md + 커밋: `feat(M5): UI tabs + outsourcing calculator + admin PDF - v0.5.5`
```

**[검증]** 결제자 PDF가 실제 행정실장에게 보낼 만한 품질인지 PO 1차 검수.

---

## M6 — FastAPI v2 권당 과금 빌링 (1h)

**[목적]** 1차 보고서의 정액 가정을 권당 과금으로 정정. 학교당 200만/년 상한 캡으로 외주 시장 흡수 가격 모델 구현.

**[의존성]** M2, M5 완료

**[명령문]**

```
다음을 구현하라:

1. 빌링 데이터 모델 (`src/kormarc_auto/billing/models.py`):
   - Tenant (school_id, name, plan_type, cap_amount, billing_cycle)
   - UsageRecord (tenant_id, isbn, source_chain, cost_won, billed_at)
   - Invoice (tenant_id, period, total_won, capped, paid)

2. 권당 과금 로직 (`src/kormarc_auto/billing/charge.py`):
   - plan_a (외주 흡수형, 권당 200원, 학교 200만/년 상한)
   - plan_b (시트 정액형, 사서 1.5만/월 무제한)
   - plan_c (교육청 단가계약, 협상가)
   - 무료 tier: 월 50권까지, 작은도서관 결제자 본인 인증 시 영구 무료 (페르소나 02 박서연용)

3. 상한 캡 (cap) 처리:
   - 누적 사용량이 cap 도달 → UI에 "이번 학년도 상한 도달, 추가 등록 무료" 표시
   - 사서·행정실장 모두에게 이메일 알림 옵션

4. FastAPI 엔드포인트 (`src/kormarc_auto/api/billing.py`):
   - GET /v1/billing/usage?tenant_id=&period= → 사용량 조회
   - POST /v1/billing/invoice/issue → 월말 청구서 발행 (PO 수동 트리거)
   - GET /v1/billing/cap-status → 캡 상태 (UI 위젯용)

5. 외부 결제 통합 미흡 영역 명시:
   - 토스페이먼츠 / KG이니시스 SDK 통합은 **PO 결정 후** 별도 모듈
   - M6에서는 invoice 데이터 모델·발행만 구현, 실제 결제 게이트웨이는 v0.6.x

6. 단위 테스트 (+15):
   - 권당 200원 × 1,000권 = 20만원 정상
   - 학교 11,000권 → 200만 cap 적용 (11,000 × 200 = 220만이지만 cap → 200만)
   - plan_b 정액형 검증
   - 무료 tier (페르소나 02) 영구 무료

7. PROGRESS.md + 커밋: `feat(M6): per-volume billing with school cap - v0.5.6`
```

**[검증]** 462 + (M2~M5 누적 95) → 약 557 tests pass. 빌링 시뮬레이션 3개 시나리오(A/B/C) 모두 정상.

---

## M7 — 테스트 462 → 600+ 페르소나 시나리오 통합 (1.5h)

**[목적]** 1차 보고서의 일반 테스트 확장 권고를 페르소나 5명 시나리오 e2e 테스트로 정밀화.

**[의존성]** M1~M6 완료

**[명령문]**

```
다음을 구현하라:

1. 페르소나 시나리오 e2e 테스트 (`tests/e2e/test_personas.py`):
   - 페르소나 01 (김지원): 신간 50권 입고 → ISBN 연속 스캔 → KDC 자동분류 → KOLAS 가져오기 양식 .mrc 출력 → 검수 시간 측정 (목표: 25분 이내)
   - 페르소나 02 (박서연): 작은도서관 신간 20권 → 무료 tier → 결제 안내 미발생 검증
   - 페르소나 03 (이민재): P15 순회 시뮬레이션 → 학교 A에서 30권 등록 → 학교 B로 전환 → tenant 분리 정상
   - 페르소나 04 (정유진): 의학 외서 5권 (ISBN 없거나 깨짐) → OCR fallback 트리거 → 사서 수동 보완 화면
   - 페르소나 05 (최영자): KOLAS 충성 시나리오 → "이 도구가 적합하지 않을 수 있습니다" 안내 + KOLAS 직접 사용 가이드 링크 (Rejecter는 강제 권유 안 함, 헌법 §12 정합)

2. 외주 비교 시뮬레이터 통합 테스트 (`tests/integration/test_cost_calc.py`):
   - 입력 50가지 조합 (신간 수 × 외주 단가 × 인건비)
   - 결제자 PDF 생성 검증

3. ISBN 파이프라인 회복탄력성 테스트 (`tests/resilience/test_isbn_chain.py`):
   - SEOJI 다운 → data4library fallback
   - data4library 다운 → 알라딘 fallback
   - 모두 다운 → OCR 안내
   - 네트워크 timeout (5초) 시 graceful degradation

4. 회귀 테스트 자동화:
   - GitHub Actions workflow 1개 추가 (.github/workflows/ci-v0.5.7.yml)
   - PR마다 462+138 = 600 tests 실행
   - main 머지 시 PROGRESS.md 자동 갱신

5. binary_assertions 38 → 50+ 확장:
   - 새 단언: KORMARC .mrc 출력이 KS X 6006-0:2023.12 검증기 통과
   - 새 단언: 외주 비교 PDF가 페이지 1장
   - 새 단언: 캡 도달 후 추가 사용량 무료

6. PROGRESS.md + 커밋: `feat(M7): 600+ tests with persona e2e scenarios - v0.5.7`
```

**[검증]** 600+ tests all pass. 페르소나 5개 시나리오 모두 시간/정확도 목표 달성.

---

## M8 — LLM 프로바이더 분리 + Tier 라우팅 (1h)

**[목적]** Anthropic API 비용 권당 < 20원 달성. Haiku 4.5(80%) + Sonnet 4.6(20%) 자동 라우팅. EXAONE 자체호스팅은 30만권/월 도달 후 재검토 (현 단계 X).

**[의존성]** M2, M3 완료

**[명령문]**

```
다음을 구현하라:

1. LLM 프로바이더 인터페이스 (`src/kormarc_auto/llm/provider.py`):
   - ABC LLMProvider {complete(prompt) -> Response, vision(images, prompt) -> Response}
   - 구현체:
     - AnthropicHaiku45 (claude-haiku-4-5-20251001, $1/$5)
     - AnthropicSonnet46 (claude-sonnet-4-6, $3/$15)
     - AnthropicOpus47 (claude-opus-4-7, $5/$25, 디버깅 전용)

2. 라우팅 정책 (`src/kormarc_auto/llm/router.py`):
   - 기본: Haiku 4.5
   - 승격 조건: Haiku 응답 신뢰도 < 0.85, 또는 vision OCR 텍스트 < 20자
   - 승격 대상: Sonnet 4.6
   - Opus는 PO 명시적 호출만 (CLI 플래그 --use-opus)

3. 프롬프트 캐싱 활성화 (`src/kormarc_auto/llm/cache.py`):
   - 시스템 프롬프트 + 페르소나 가이드 + KORMARC 필드 매핑 규칙 = 캐시 대상 (90% off)
   - cache_control: "ephemeral" (5분), "1h" 옵션 검토

4. 배치 API 활용 (`src/kormarc_auto/llm/batch.py`):
   - 야간 일괄 처리 (어제 등록한 도서 KDC 분류 검토): Haiku 배치 50% off
   - 사서가 즉시 결과 필요 X → 다음 영업일 아침까지 처리

5. 비용 모니터링 대시보드 (`src/kormarc_auto/ui/cost_dashboard.py`):
   - 일/주/월 토큰 사용량 (모델별)
   - 권당 평균 비용
   - BEP 권수 (월 11,000권으로 660만/월 도달 가능 검증)

6. 단위 테스트 (+10):
   - Haiku 응답 신뢰도 0.83 → Sonnet 승격 검증
   - 배치 결과가 실시간 결과와 동일한지

7. PROGRESS.md + 커밋: `feat(M8): LLM tier routing Haiku 80% Sonnet 20% with caching - v0.5.8`
```

**[검증]** 1,000권 시뮬레이션 평균 비용 < 15원/권. 응답 latency Haiku < 800ms, Sonnet < 1.5s.

---

## M9 — 컴플라이언스 2단계 (M9-A PIPA + M9-B ISMS-P) (2h)

**[목적]** 1차 보고서의 단일 M9를 2단계로 분리. M9-A는 PIPA 2026.09.11 시행 대응 (필수), M9-B는 ISMS-P 2027.07.01 시행 대응 (선택, 매출 5억 도달 후 의무화).

**[의존성]** 모든 M1~M8 완료

### M9-A — PIPA 2026.09.11 시행 대응 (1h)

**[명령문]**

```
다음을 구현하라:

1. 개인정보 처리방침 (`docs/legal/privacy_policy_v2.md`):
   - 개정 PIPA 정합 (2026.03.10 공포, 2026.09.11 시행)
   - 수집 항목: 사서 이메일, 학교명, 사용량 메트릭
   - 수집 안함: 도서 대출자 정보, 이용자 PII (LMS 영역)
   - 위탁: Anthropic API (해외 이전), AWS Seoul (국내), 토스페이먼츠 (결제)
   - CPO 지정: PO 본인 (1인 사업자 단계)

2. 처리 현황 ROPA (`docs/legal/ropa_2026-05.md`):
   - 처리 항목, 보유 기간, 위탁 대상, 국외이전 여부 표
   - PIPC 신고 양식 호환

3. 동의 양식 강화 (`src/kormarc_auto/auth/consent.py`):
   - 회원가입 시 필수 동의 분리 (필수 vs 선택)
   - AI 학습 데이터 활용 동의는 **선택** (헌법 §12 부정 영향 최소화)
   - 14세 미만 가입 차단 (학교 도서관 사서는 성인이지만 안전장치)

4. 데이터 익명화 파이프라인 (`src/kormarc_auto/privacy/anonymize.py`):
   - KDC 학습 코퍼스에서 사서 식별자, 학교 식별자 마스킹
   - 익명화 검증 스크립트 (k-익명성 5+ 보장)

5. 개인정보영향평가 (PIA) 면제 검토:
   - 공공기관 아님 + 5만 명 미만 + 민감정보 X → 면제 가능성
   - 면제 요건 체크리스트 `docs/legal/pia_exemption_checklist.md`

6. PIPA 위탁계약서 템플릿 (`docs/legal/template_outsourcing_contract.md`):
   - 학교/공공도서관과 위수탁 관계일 때 사용
   - **PO 직접 검토 필요** (법무 영역, Claude Code 자동 작성 한계)

7. PROGRESS.md + 커밋: `feat(M9-A): PIPA 2026-09-11 compliance - privacy policy + ROPA + consent - v0.5.9`
```

**[검증]** PIPA 자가점검 80개 항목 중 70+ 통과 (`docs/legal/pipa_self_assessment.md`).

### M9-B — ISMS-P 2027.07.01 대응 사전 작업 (1h)

**[명령문]**

```
다음을 구현하라:

1. ISMS-P 자가점검 80개 항목 (`docs/legal/isms_p_checklist.md`):
   - KISA 자가점검 양식 그대로 복제
   - 각 항목 현재 상태(O/X/N/A) + 보완 계획
   - 1인 사업자 단계 제외 가능 항목 식별

2. 침해사고 대응 절차 (`docs/legal/incident_response.md`):
   - 24시간 / 72시간 신고 의무
   - 모의훈련 시나리오 3개 (DDoS, 데이터 유출, 랜섬웨어)
   - 사이버보험 가입 권고 (메리츠/DB/삼성/KB/에이스 5개사 견적 비교 문서)

3. 접근통제 강화 (`src/kormarc_auto/auth/rbac.py`):
   - 역할: 사서 / 결제자 / 관리자 / 감사관
   - 권한 매트릭스 (CRUD)
   - 감사 로그 (`audit_log` 테이블)

4. 암호화 강화 검토:
   - DB 저장 시 AES-256 (현재 평문 → 마이그레이션)
   - 전송 시 TLS 1.3 (Cloudflare Tunnel 정합)
   - 비밀키 관리: AWS Secrets Manager 또는 HashiCorp Vault 검토

5. 매출 5억 도달 시점 의무화 알림:
   - PROGRESS.md에 "ISMS-P 의무화 트리거: 매출 5억/년 또는 1만 명 이상 사용자" 명시
   - 트리거 도달 시 인증 신청 (예상 비용: 인증 5,000만 + 컨설팅 3,000만)

6. 사이버보험 견적 자동 요청 양식:
   - PO가 보험사에 보낼 RFP 템플릿 `docs/legal/cyber_insurance_rfp.md`

7. PROGRESS.md + 커밋: `feat(M9-B): ISMS-P 2027-07 prep - self-assessment + incident response - v0.6.0`
```

**[검증]** ISMS-P 자가점검 80개 중 50+ 항목 O 또는 N/A 처리 (1인 사업자 단계 적정 수준).

---

## 모듈 간 통합 검증 (M1~M9 완료 후)

**[최종 검증 명령문]**

```
다음을 순차로 수행하라:

1. 전체 테스트 실행: pytest -v --tb=short → 600+ tests pass 확인
2. 페르소나 5명 시나리오 통합 실행:
   - python scripts/run_persona_simulation.py --all
   - 출력: 페르소나별 시간 단축, 비용 절감, 거부 사유 (페르소나 05) 리포트
3. 외주 비교 PDF 5개 자동 생성 (페르소나 1~4):
   - python scripts/generate_admin_pdfs.py
4. PROGRESS.md 최종 업데이트:
   - v0.5.0 → v0.6.0 변경 요약 (Δ 코드 라인, Δ 테스트 수, Δ 비용/권, Δ 시간/권)
5. README.md 업데이트:
   - 외주 흡수형 비즈니스 모델 1줄 소개
   - 페르소나 5명 카드 링크
   - PIPA·ISMS-P 컴플라이언스 배지

6. 최종 커밋: `release: v0.6.0 - persona-validated, outsourcing-absorbing, PIPA-ready`
7. tag: git tag -a v0.6.0 -m "v0.6.0 - 660만/월 캐시카우 도달 가능 패키지"
8. PO에게 보고: 다음 단계는 PILOT 학교 5곳 콜드 콘택트 (페르소나 카드 §6 참조)
```

---

## PO 외부 작업 의존 (Claude Code 외부)

다음은 **Claude Code가 자동으로 처리할 수 없는** 작업이므로 PO가 직접 수행:

1. **GitHub 저장소 web Claude 첨부** (M1 시작 전, 5분)
2. **SEOJI API 인증키 발급** (M2 시작 전, 국립중앙도서관 신청, 1~3일)
3. **data4library API 인증키** (M2 시작 전, 도서관정보나루, 즉시)
4. **알라딘 TTBKey** (M2 시작 전, 알라딘 개발자센터, 즉시)
5. **PIPA 위탁계약서 법무 검토** (M9-A 후, 변호사 자문 권고)
6. **사이버보험 5개사 견적 RFP** (M9-B 후, PO 발송)
7. **PILOT 학교 콜드 콘택트** (M9 완료 후, 페르소나 카드 §6 참조)
8. **학교도서관저널 7월호 또는 9월호 기고** (M5 완료 후 시작 가능)

---

## 일정 가이드

| 일자 | 모듈 | PO 외부 작업 병렬 |
|---|---|---|
| Day 1 (오전) | M1 | GitHub 첨부 |
| Day 1 (오후) | M2 | API 키 3개 발급 |
| Day 2 (오전) | M3 | — |
| Day 2 (오후) | M4 (1차 시작) | KDC 코퍼스 합법성 PO 1차 검토 |
| Day 3 (전일) | M4 (학습 마무리) + M5 | — |
| Day 4 (오전) | M6 | 권당 가격 PO 최종 결정 |
| Day 4 (오후) | M7 | — |
| Day 5 (오전) | M8 | — |
| Day 5 (오후) | M9-A | PIPA 위탁계약서 변호사 자문 시작 |
| Day 6 (전일) | M9-B + 통합 검증 | 사이버보험 RFP 발송 |

**총 약 5~6 영업일 (반나절 × 2 = 1일 가정 시 3일도 가능, 단 KDC 학습은 GPU 시간 별도)**

---

## 헌법 정합 최종 체크 (M9 완료 시)

| 모듈 | §0 사서 시간 단축 | §12 결제 의향 ↑ |
|---|---|---|
| M1 | — | △ (현황 파악) |
| M2 | ◎ 권당 8분 → 30초 | ◎ 외주 대비 매력적 |
| M3 | ◯ ISBN 없는 책 보완 | △ (보조 경로) |
| M4 | ◯ KDC 자동분류 | ◎ 장기 moat |
| M5 | △ (UI 개선) | ◎ 결제자 PDF |
| M6 | — | ◎ 권당 과금 |
| M7 | — | ◯ 품질 신뢰 |
| M8 | — | ◯ 비용 절감 |
| M9 | — | ◎ 신뢰 신호 |

**모든 모듈이 §0 또는 §12 양수**. 헌법 §12 거부 사유 없음.

---

**문서 끝.**
