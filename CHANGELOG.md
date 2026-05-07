# Changelog

이 스타터의 변경 이력. [Keep a Changelog](https://keepachangelog.com/) 형식.

> 새 SaaS에 적용 시 어느 버전을 가져왔는지 `decisions.md`에 기록하면 추후 동기화가 쉬워집니다.

## [Unreleased] - Cycle 60·61 UI/UX + 페르소나 깊이 시뮬 + 상업성/SEO/AEO/GEO

### Added (Cycle 61·Part 96·ADR 0045)
- `docs/research/part96-deep-persona-simulation-2026-05.md` — 8 ICP × 앱 5 영역 매트릭스
- `src/kormarc_auto/personas/__init__.py` + `deep_simulation.py` — 8 페르소나·점수·gaps
- `tests/test_deep_personas.py` — 25 신규 tests (페르소나·PMF·결제권 분리)
- `docs/sales/persona-message-matrix-2026-05.md` — 8 페르소나별 영업 메시지 5 분기
- `docs/sales/commercial-seo-checklist-2026-05.md` — 상업성 10 + SEO 12 매트릭스
- `docs/sales/aeo-geo-strategy-2026-05.md` — SEO + AEO + GEO 6 원칙·8 페르소나 query
- ADR 0045 (12 추가 고려 영역 매트릭스·결제 채널 분리·PMF 3 단계 등)
- CLI `kormarc-auto status` 신규 = STATUS.md 요약 + 차단점 1순위
- `.github/workflows/daily-blocker.yml` = 매일 차단점 자동 감지
- `.github/workflows/a11y-ci.yml` = 헌법 §12 PR 회귀
- `.claude/skills/a11y-audit/SKILL.md` 신규
- `analytics/three_stage_funnel.py` = 사용자/추천자/결제자 3 분리

### Changed
- 정직 헤더 명시: 페르소나 시뮬 = 가설·인터뷰 0건·SALES-1 우선

### Tests
- 1,186 → **1,228** (+42·three_stage_funnel 17 추가)

### Added (Cycle 61 추가 조사·ADR 0046)
- `tests/test_three_stage_funnel.py` (17 신규·Cycle 61 미커버 해소)
- ADR 0046 = 영구 invariant 11 (페르소나 시뮬 ≠ 실 인터뷰·정직 헤더 의무)
- CLAUDE.md §13 박제 (페르소나 시뮬 ≠ 인터뷰)
- 추가 조사 결과: bandit 미설치 (다음 사이클)·mypy strict 실 검증 (다음 사이클)

### Added (Cycle 78~83·야간 자동화·B2C 메트릭·SNS 자동)
- src/kormarc_auto/b2c/__init__.py + metrics.py
  * SubscriptionTier 4 플랜 (FREE·PERSONAL·PRO·FOUNDING) enum
  * MRR 계산·activation (100권+보고서·Lenny 2.5x)·churn 4 단계
  * 시간 절감 환산 (6분/권·시급 ₩20K·ROI 20:1)
  * demo snapshot (50 trial / 5 paid / ₩49,500 MRR)
- tests/test_b2c_metrics.py (23 신규)
  * SubscriptionTier·MRR·Activation·TimeSaved·Churn·Constitution
- 후보_아이디어/auto-clicker-saas/poc/sns_multipost.py
  * 시나리오 2 (인스타·X·페이스북 동시 업로드·법적 안전)
  * LLM Vision 이미지 분류·캡션·해시태그·검수 워크플로우
  * 자영업 ROI 30:1+ (15분→5분·매월 ₩300K~₩1.2M)

### Added (Cycle 71~76·야간 자율·자료·통합·실 활성)
- META_REVIEW Cycle 64~70 7-cycle row 추가 (V2 §6.1 자동)
- 후보_아이디어/auto-clicker-saas/poc/naver_review_responder.py
  * 자영업 리뷰 답변 PoC scaffold (Phase 1·법적 안전)
  * LLM prompt 빌더·평점별 톤·시간 환산·사용자 검수 워크플로우
- docs/research/librarian-interviews-2026-05/TEMPLATE.md
  * 인터뷰 박제 표준 형식 (Mom Test 5문항·익명 ID·invariant 2 정합)
  * Q1~Q5 + 도입 가능성 점수 + 핵심 인용 + PO 학습
- scripts/analyze_interviews.py = 인터뷰 결과 분석 자동
  * 통계 결정적·LLM 호출 0 (V3 §4.10)
  * 결정 트리 4 분기 (B2C 진행·B2B 우위·5명 추가·MarcEdit 모델)
  * 페르소나 분포·결제 의향·경쟁자 빈도
- tests/test_analyze_interviews.py (18 신규)
- Makefile: `make interviews`·`make b2c-status` 추가

### Added (Cycle 69·founder-market fit·B2C 상세·앱스토어·자동 클리커 깊이)
- PO 통찰 박제: "사서 프로그램 = 내가 필요해서 만든·있으면 사서 썼을 것"
  * founder-market fit = 강력 PMF 신호·B2C 1순위 정합
  * 외부 사서 5명 인터뷰 = 2차 검증·페르소나 v2 재작성
- docs/sales/b2c-detailed-design-2026-05.md = B2C 상세 설계
  * UI·서비스 방법·온보딩·결제 흐름·영업 채널·founder 스토리
  * 시장 정확 측정 (TAM 31,500·SOM 1,500~3,000)
  * 진지 검토 (옵션 A·B·C 비교·사서 B2C 권고)
- docs/automation/app-store-and-distribution-2026-05.md = 앱스토어 매트릭스
  * Apple App Store 거절 정책 (4.2.2·5.2.1)
  * Google Play 자동화 카테고리·게임 거절
  * PWA + GitHub Releases + Streamlit Cloud = 1순위
  * 결제 30% 수수료 회피 = PWA + PortOne
- 후보_아이디어/auto-clicker-saas/docs/market-research-2026-05.md = 깊이 조사
  * 8 시나리오 (게임 5 + 안전 3·PO 핵전쟁 게임 정합)
  * LLM Vision 비용·마진 모델 (사용자당 $0.1~$1/월)
  * 법적 매트릭스 (안전·회색·위험)
  * 모바일 한정 (PC = 회피·PO 통찰 정합)

### Added (Cycle 68·B2C 전환·"몰래 쓰기"·Supabase 부활)
- ADR 0050 = 사서 B2C 방향 전환 (결제권자 = 결제자 일치·"몰래 쓰기")
  * 8 페르소나 중 7 = 결제 권한 X·B2B 영업 어려움
  * B2C 사서 본인 = ₩9,900/월·체크카드·세금계산서 X·결재 X
  * 시간 환산 = ₩200K/월 절감 = 20:1 ROI
  * ADR 0047 부분 supersede = B2C 한정 Supabase Auth 부활
- docs/landing/b2c.md = "몰래 쓰기" B2C 랜딩 페이지
  * 본인 결제 메시지·5초 시작·Founding Member ₩4,950/월
  * Supabase Auth + PortOne v2 (Phase 2)
- 후보_아이디어/auto-clicker-saas/ 폴더 신설 (별도 PoC)
  * README 박제·concept-2026-05.md (5 시나리오 시드)
  * LLM 의사결정·다중 chain·자동 복구 차별화
  * Phase 0 = 시장 조사·자영업 5명 인터뷰·PoC 1건

### Added (Cycle 66·비즈니스 모델 Open Core + Hosted SaaS)
- ADR 0049 = Open Core + Hosted SaaS 결정 (Apache-2.0 영구 + 결제 서비스 패키지)
  * 검증 사례: Koha (1,399 도서관)·FOLIO (100+)·GitLab·Sentry
  * 반례: MarcEdit (영구 무료·매출 ₩0·26년·우리 ≠)
  * 자가 빌드 = 5% (가난한 사서)·결제 = 95% (학교·자치구·공공·기관·도서관장)
- docs/sales/why-pay-2026-05.md = "왜 결제?" 도서관장·사서 친화 영업 자료
  * 무료 vs SaaS 비교표 (시간·법적·결재 통과)
  * 학교운영위 결재 시나리오 A·B
  * 페르소나별 결제 가능성 정직 분석

### Added (Cycle 65·사서 자가 설치 친화)
- `.github/workflows/build-exe.yml` = PyInstaller 3 OS 자동 빌드 (Windows·Mac·Linux)
  * tag push `v*` = 자동 빌드 + GitHub Releases 자동 업로드
  * 사서 IT 자신감 L1·L2 (60%) 친화 = Python 설치 X·명령어 X·더블클릭만
- `scripts/launcher.py` = `.exe` 진입점
  * Streamlit 자동 실행·브라우저 자동 열기·offline demo 모드 자동
  * 사서 친화 에러 메시지 + GitHub Issues link
- `docs/landing/install.md` = 5초 설치 가이드
  * 옵션 A URL 클릭·옵션 B `.exe` 다운로드·옵션 C 명령어 (개발자)
  * Windows·Mac·Linux 3 OS 단계별 스크린샷 시드
  * 사서 자주 묻는 질문 6선
- README.md "빠른 시작" 섹션 강화 = 옵션 A·B 사서 친화

### Added (Cycle 64·BaaS 자동 검토)
- ADR 0047 = Supabase 도입 검토 → **Accepted (옵션 A 채택·Supabase 미도입)**
  * Phase 1: streamlit-authenticator + yaml (자관 100% 로컬·★★★★★)
  * Phase 2: AWS Cognito + Lightsail Seoul (한국 호스팅·PIPA 정합·★★★★)
  * Phase 3: NCP Cloud + CSAP (자치구 진입·★★★)
- `docs/automation/baas-comparison-2026-05.md` = 10 옵션 × 7 기준 매트릭스
  * Supabase 미도입 이유: 미국 호스팅·PIPA §28의8 6수신자 추가·도서관 인지도 ↓
  * AWS Cognito + Lightsail Seoul 우위: 동일 50K MAU 무료 + 한국 호스팅
- 영구 invariant 12 후보: 자관 .mrc·PII = 외부 BaaS 절대 X
- AUTONOMOUS_BACKLOG.md = Cycle 60~64 누락 row 갱신
- decisions.md = Cycle 60~64 5 결정 박제 (V2 §4.4 표준)

### Added (Cycle 63·신경 0 배포 + E-E-A-T)
- `.github/workflows/github-pages.yml` = GitHub Pages 자동 deploy (₩0·도메인 X)
- `.streamlit/secrets.toml.example` = Streamlit Community Cloud 무료 호스팅 가이드
- `docs/automation/zero-cost-deploy-2026-05.md` = ₩0/월·신경 0 배포 stack 매뉴얼
- `docs/sales/e-e-a-t-trust-signals-2026-05.md` = E-E-A-T 4 신호 매트릭스 + 코드 적용 가이드
- `docs/landing/index.md` = 메인 랜딩 (E-E-A-T 통합·핵심 사실 LLM 인용 친화)
- `docs/landing/about.md` = About 페이지 (Experience·Expertise·Authority·Trust 4 영역)
- 자동 sitemap.xml + robots.txt + llms.txt (GitHub Pages 빌드 시)
- LLM Allow (GPTBot·ClaudeBot·PerplexityBot·Yeti)

### Added (Cycle 62·마케팅 노출 30+ 갭 점검)
- 30+ 갭 식별: SEO 12 + AEO 6 + GEO 5 + 마케팅 16 + 측정 5
- `docs/sales/cold-email-templates-2026-05.md` = 5 페르소나 (P1·P2·P3·P5·P8) 콜드 메일
- `docs/sales/content-calendar-90-days-2026-05.md` = 16 키워드 × 14주 = 36 발행 시드
- `docs/sales/press-kit-2026-05.md` = 5 분기 보도자료 + FAQ 10 + About + 통계 박스
- `docs/sales/partnership-mou-matrix-2026-05.md` = 8 기관 (KLMA·KLA·NLK·KAIT·KERIS 등)
- 정직 헤더 영구 (invariant 11) = 시뮬·인터뷰 0건·발행 0건 모두 명시

## [Unreleased] - Cycle 60 UI/UX 통합 (헌법 §12 정합)

### Added
- `.streamlit/config.toml` — KRDS 색상 토큰·Pretendard·KWCAG 1.4.4 base 16px·Telemetry 차단 (헌법 §3)
- `src/kormarc_auto/ui/a11y_inject.py` — 글로벌 KWCAG 2.2 Level AA + Pretendard CDN
  * 9 KWCAG 정합 (1.3.1·1.4.3·1.4.4·1.4.13·2.3.3·2.4.1·2.4.7·2.5.5)
  * `inject_global_a11y()` = 모든 페이지 진입점 1회 호출
  * `render_confidence_chip()` = 카테고리형 신뢰 (헌법 §11·raw % 금지)
  * `render_ai_ghost()` = AI 생성 표시 (헌법 §10·인공지능 기본법 §31)
- `src/kormarc_auto/ui/librarian_ux.py` — 사서 친화 UI 헬퍼
  * `LIBRARIAN_DAILY_CYCLE` 5 단계 (수서·정리·배가·이용·납본)
  * `LIBRARIAN_VOCABULARY` IT → 사서 어휘 매핑
  * `time_saved_estimate()` = 헌법 §0 (8분 → 2분) 시각화
  * `render_librarian_friendly_error()` = 5 사서 친화 에러 (PIPA 정합)
  * `render_workflow_position()` = 일과 위치 마이크로 카피
  * `cite_authority()` = 5 권위 인용 (NLK·KAIT·MCST·KLA·KLMA)
- `tests/test_a11y_inject.py` (34 신규 tests)
  * KWCAG 2.2 9 항목·헌법 §10·§11·§12 invariants
  * 사서 친화 에러·시간 절감·workflow position 검증

### Changed
- `streamlit_app.py`·`revenue_dashboard.py` 진입부에 `inject_global_a11y()` 호출
- `Makefile` 3 신규 명령 (`make a11y`·`ui-test`·`dashboard`)

### Tests
- 1,152 → **1,186** (+34·UI/UX 회귀)

## [0.7.1] - 2026-05-06 — V3 외부 256 출처 마무리 통합

### Added (Cycle 43~56)
- **V3 Block 1 Auth**: `docs/automation/HEADLESS_AUTH.md` — 인증 우선순위·5 디버깅 케이스
- **V3 Block 2 Cost Cap 3-Layer**:
  - `automation/cost_supervisor.py` — stream-json 단일 세션 watchdog
  - `.claude/hooks/budget-cap-precheck.sh` — PreToolUse exit 2 차단
- **V3 Block 3 Audit Schema**: `.claude/hooks/audit-log.sh` — PostToolUse append-only
- **V3 Block 4 Weekly Report**: `automation/weekly_report.py` — 13 메트릭 통계 결정적 (LLM 호출 0)
- **V3 Block 5 Router Patcher** (scaffold): `automation/router_patcher.py` — AST 패치 + 백업·자동 머지 X
- **V3 Block 7 RUNBOOK**: `docs/RUNBOOK.md` — Tonight's command·incident response
- **Phase 2 Wrapper**: `automation/po_loop_with_cost_guard.sh` — po_loop + cost_supervisor
- **KOLAS3 Cron**: `scripts/automation/kolas3-daily-update.sh` — 매일 D-day 자동 갱신
- **GitHub Actions**: `.github/workflows/weekly-report.yml` — 매주 월 리포트
- **UI 통합**:
  - Streamlit KOLAS3 D-day 실시간 카드 (Cycle 50)
  - revenue_dashboard에 weekly_report 통합 (Cycle 51)

### Changed
- `Makefile`: 3 신규 명령 (`make weekly`·`make kolas3`·`make night-loop`)
- `pyproject.toml`·`__init__.py`: 0.7.0 → 0.7.1
- `META_REVIEW.md`: 21 → 28 사이클 누적

### ADRs
- ADR 0041 — V3 Block 1+2+3 통합
- ADR 0042 — Cycle 43~49 V3 마무리 통합

### Tests
- 1,107 → **1,170+** (+60·V3 §4 13 메트릭 결정적 검증)
- 신규: test_cost_supervisor (23)·test_weekly_report (21)·test_router_patcher (12)

### Invariants
- 7 → **10건** (V3 추가): cost_supervisor 래핑·budget-cap 우회 금지·audit append-only

## [1.0.0] - 2026-05-06

### Added — 1차 출시

**핵심 인프라**
- `CLAUDE.md` 템플릿 — 매 세션 자동 로드되는 컨벤션·금지사항
- `.claude/settings.json` — permissions·hooks 통합 설정 (allow/deny)
- 5개 SessionStart/PreToolUse/PostToolUse/Stop/PreCompact hook
- `.claudeignore` 컨텍스트 절약

**자율 시스템 (V2 자율성)**
- `automation/router.py` — Haiku 기반 8 카테고리 분류기
- `automation/proposer_critic.py` — Sonnet 제안 + Opus 비평 패턴
- `automation/supervisor.py` — 멀티 SaaS 우선순위 큐
- `automation/daily-autonomy.sh` — 일일 자율 루프

**비코드 자동화**
- `automation/content_pipeline.py` — SEO 블로그 자동 초안 (Sonnet→Opus 검증)
- `automation/support_triage.py` — 고객지원 티켓 분류·응답 (Haiku→Sonnet)
- `automation/dunning.py` — Stripe 결제 실패 던닝 (4단계 톤 차별)

**서브에이전트 4개**
- code-reviewer · test-writer · debugger · researcher

**슬래시 커맨드 8개**
- `/pavr` · `/deploy` · `/refine-claudemd`
- `/fix-bug` · `/add-feature` · `/review-pr` · `/test-this` · `/explain-this-code`

**Skills 5개**
- payment-handling · db-migration-safely · tdd-workflow · add-feature-flag · incident-response

**보안 hook 9개**
- `validate-bash.sh` — `rm -rf`, `sudo`, `curl|sh`, fork bomb 차단
- `scan-secrets.sh` — Anthropic/Stripe/AWS/GitHub/Slack/JWT/PEM 패턴 차단
- `budget-guard.sh` — 일일 USD 예산 하드 스톱
- `auto-format.sh` · `append-progress.sh` · `append-learning.sh`
- `update-usage.sh` · `inject-recent-learnings.sh` · `backup-transcript.sh`

**운영 도구**
- `scripts/emergency-stop.sh` — 5단계 즉시 정지
- `scripts/rollback.sh` — 안전한 PR 복구
- `scripts/health-check.sh` — 셋업 검증
- `scripts/audit-query.sh` · `cost-report.sh` · `notify.sh` · `backup-state.sh`
- `scripts/new-project.sh` — 이 스타터를 새 SaaS로 복제

**GitHub Actions 4개**
- `claude-pr-review.yml` — PR 자동 코드 리뷰
- `nightly-autonomy.yml` — 매일 03:00 KST 자율 작업
- `security-audit.yml` — 매주 월요일 보안 스캔
- `test-hooks.yml` — 모든 PR에서 보안 hook 회귀 테스트

**테스트**
- `tests/test-hooks.sh` — hook이 실제 차단하는지 회귀 검증
- shellcheck 정적 분석 (CI)

**문서**
- `README.md` · `docs/ONBOARDING.md` · `docs/ROLLBACK_PLAYBOOK.md`
- `docs/DEBUGGING.md` · `docs/NON_CODE_AUTOMATION.md` · `docs/PROMPT_LIBRARY.md`
- `SECURITY.md`

**부트스트랩**
- `bootstrap.sh` · `Makefile` (16 타깃) · `.env.example`

---

## 변경 정책

- **Major (X.0.0)**: 디렉터리 구조 변경, hook API 변경, 호환 깨짐
- **Minor (1.X.0)**: 새 자동화 스크립트, 새 skill, 새 슬래시 커맨드
- **Patch (1.0.X)**: 버그 수정, 문서 개선, hook 패턴 추가

새 SaaS에 동기화 시:
1. 현재 사용 중인 버전 확인 (`cat VERSION`)
2. 이 CHANGELOG에서 그 버전 이후 변경사항 검토
3. 필요한 변경만 cherry-pick
4. `decisions.md`에 동기화 기록
