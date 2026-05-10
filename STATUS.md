# STATUS — kormarc-auto 단일 진실원 (B안 P6)

> Plan B Cycle 7 (P6) — STATUS_REALITY_CHECK.md → `docs/archive/STATUS_REALITY_CHECK-2026-04-27.md`로 이동·이 파일이 단일 진실원
> **갱신**: 2026-05-06 Cycle 58 (v0.7.1 release·V3 외부 256 출처 통합 마무리)

## 현재 상태 (2026-05-06 Cycle 61 마무리·페르소나 깊이 시뮬 + 상업성/SEO/AEO/GEO)

| 항목 | 값 |
|---|---|
| 버전 | **v0.7.1** (tag push 완료) + Cycle 60·61 [Unreleased] |
| Tests | **1,287** passing / 6 skipped (+23 from Cycle 78·B2C 메트릭) |
| ruff | 0 errors |
| binary_assertions | 39/39 |
| 자관 174 round-trip | 100% baseline (regression ≤ 1pp 영구 게이트) |
| 영구 invariants | **10건** (Cycle 27·V3 추가 3건·ADR 0041) |
| ADRs | **0024~0050** (27건 누적·Cycle 68 = ADR 0050 B2C 전환) |
| 메모리 | 7건 (901·858·매출·V1·V2·V3·1-명령 1-완료 ⭐⭐⭐⭐⭐) |
| Plan B P29~P52 | 22/24 (P30·P39 외부 의존만) |
| V2 §1·§3·§5·§6·§7·§10·§11 | 100% scaffolding |
| V3 Block 1·2·3·4·5·7 | ✅ scaffolding (Block 6 = 두 번째 SaaS 시작 시) |
| **헌법 §12 (UI/UX)** | **doc → 코드 100% 적용 (Cycle 60·ADR 0044)** |
| **8 ICP 페르소나 깊이 시뮬** | **Cycle 61·Part 96·매트릭스 + tests 25 신규 (인터뷰 0건·가설)** |
| **상업성·SEO·AEO·GEO** | **Cycle 61~62 매트릭스 박제·발행 = PO 외부 작업 후** |
| **마케팅·노출 (Cycle 62)** | **30+ 갭 식별·콜드 메일 5 페르소나·콘텐츠 캘린더 90일·press kit·MOU 8 기관 시드** |
| **신경 0 배포 (Cycle 63)** | **GitHub Pages + Streamlit Cloud + GitHub Actions = ₩0/월·도메인 X·git push 자동** |
| **E-E-A-T 4 신호** | **Cycle 63 매트릭스·Author/About/Schema Person·landing index + about** |
| **BaaS 자동 검토 (Cycle 64)** | **ADR 0047 Accepted·Supabase 미도입·Phase 1=streamlit-authenticator·Phase 2=AWS Cognito·Phase 3=NCP CSAP** |
| **사서 자가 설치 (Cycle 65)** | **`.exe` 자동 빌드 (Win·Mac·Linux)·launcher.py·5초 설치 가이드·도서관 RFP 100% 통과** |
| **비즈니스 모델 (Cycle 66)** | **Open Core + Hosted SaaS·코드 Apache-2.0·결제 = 외부 API + 법적 + SLA + 결재 통과·ADR 0049** |
| **🚨 사업성 1순위 (Cycle 67)** | **PO 명령: "사업성이 1순위·없는 게 가장 큰 문제"·인터뷰 가이드 박제·코드 STOP·PO 외부 작업 1주 = 60 사이클 가치 검증** |
| **다음 단계 (필수)** | **사서 5명 인터뷰 (Mom Test 5문항·1주·docs/research/librarian-interview-playbook-2026-05.md)** |
| **🔄 B2C 전환 (Cycle 68)** | **PO 명령: "사서 B2C·몰래 쓰기·결제권자=결제자"·ADR 0050·Supabase 부활 (B2C 한정)·₩9,900/월·docs/landing/b2c.md** |
| **자동 클리커 후보 SaaS** | **별도 폴더 박제·`후보_아이디어/auto-clicker-saas/`·README + concept doc·Phase 0 시드** |
| **🟢 founder-market fit (Cycle 69)** | **PO 통찰: "사서 프로그램 = 내가 필요해서 만든·있으면 사서 썼을 것"·1차 검증 신호·B2C 1순위 정합** |
| **B2C 상세 설계 (Cycle 69)** | **`docs/sales/b2c-detailed-design-2026-05.md`·UI·서비스·온보딩·결제·영업 채널·founder 스토리** |
| **앱스토어 분석 (Cycle 69)** | **`docs/automation/app-store-and-distribution-2026-05.md`·웹/PWA/`.exe`/Play/iOS 매트릭스** |
| **자동 클리커 시장 조사** | **`후보_아이디어/auto-clicker-saas/docs/market-research-2026-05.md`·게임 영역 + 법적 분석** |
| **🟢 B2C 활성 (Cycle 70)** | **Supabase Auth scaffold·env only·헌법 §3·invariant 12 정합·tests 21·plan 4 (free/personal/pro/founding)** |
| **PWA (Cycle 70)** | **manifest.json·sw.js·핸드폰 홈 추가·앱스토어 X·KRDS Korea blue 60 theme** |
| **사서 추출 시드 (Cycle 70)** | **`docs/sales/librarian-cafe-recruit-2026-05.md`·5 채널 글 시드·founder 강조** |
| **🌙 야간 자율 (Cycle 71~76)** | **META 7-cycle·자동 클리커 PoC scaffold·인터뷰 분석 도구·TEMPLATE.md·tests + Makefile (interviews·b2c-status)** |
| **🌙 야간 자동화 (Cycle 78~83)** | **B2C 메트릭 (MRR·activation·churn·시간 절감)·자동 클리커 시나리오 2 (SNS 자동)·tests +23 (1287)** |
| **🎮 자동 클리커 Phase 2 (Cycle 84)** | **모바일 게임 레이드 PoC (PO 통찰·핵전쟁 게임)·옵트인·면책·LLM Vision prompt 시드·안전 체크리스트 8건** |
| **⛔ NO offline activities (Cycle 85·PO 2026-05-07·ADR 0052)** | **PO 명령: "인터뷰 같은 코딩 외 활동 진행 안 할 예정"·인터뷰·카페·cold·등록·발사 = 0건·코드·자료·시뮬만 자율·invariant 11 보류** |
| **🎯 30 apps portfolio (Cycle 85·PO 2026-05-07·ADR 0053)** | **단일 대박 X → 30개 단일 기능 앱 포트폴리오·인디 검증 MRR $22K·1주 1앱 Claude 자율·6 카테고리 (도서관/자영업/게임/생산성/교육/창작)·#1 kormarc-auto = 완성 = 유지보수** |
| **📚 외부 advanced research 흡수 (Cycle 85·PO 2026-05-07·ADR 0054)** | **17 P-series + B2C 시장 심층 보고서 2건 박제·docs/research/external-2026-05/·Pieter Levels·Tony Dinh·Marc Lou 인디 패턴·γ + α Tier 1 페르소나·KOLAS III D-238·일본 수출·9 즉시 자율 + 5 부분 + 3 외부 차단 분류** |
| **🚀 30 apps #2 kdc-classify (Cycle 85·자율 야간)** | **30-apps/02-kdc-classify/ 신규 (MIT)·BookInput → KDC 3 후보·룰 기반 (offline·헌법 §14)·70+ 키워드·31 tests + ruff 0·CLI 작동 검증·README 한국어·다음 cycle = LLM 옵션 + UI** |
| **🚀 30 apps #4 librarian-overtime (Cycle 86·자율 야간)** | **30-apps/04-librarian-overtime/ 신규 (MIT)·WorkDay → OvertimeReport·번아웃 4 카테고리 (KOSHA 정합)·외부 research 사실 인용 (감정노동 67.9%·임금 박탈 65.2%)·29 tests + ruff 0·CLI 작동·founder fit** |
| **🎯 페인 발굴 게이트 (Cycle 86·PO 2026-05-08·ADR 0055)** | **PO 명령: 신규 앱 = 4 단계 게이트 (페인 → 시장 ≥60 → 캐시카우 ≥60 → GO/NO-GO)·1차 시연 = 4 후보 → 2 GO + 2 NO_GO·#31 freelancer-tax-helper 신규 추가·sunk cost 0** |
| **🚀 30 apps #31 freelancer-tax-helper (Cycle 87·자율 야간)** | **30-apps/31-freelancer-tax-helper/ 신규 (MIT)·페인 게이트 통과 (90/100·100/100)·Receipt → TaxReport·한국 종소세 단순경비율 8 사업코드·누진세율 8 구간·접대비 50%·vendor 자동 분류 vendor 키워드 50+·33 tests + ruff 0·CLI 작동 (3,000만 IT 940100 → 환급 ₩447,480 추정)** |
| **📊 30 apps 누적 (Cycle 87)** | **3 신규 앱 = 93 tests passing·#1 kormarc + #2 kdc-classify (31t) + #4 librarian-overtime (29t) + #31 freelancer-tax (33t)·페인 게이트 ADR 0055 = 1 GO 시연·박제: docs/process·docs/pain-discovery·docs/portfolio·docs/research/external·docs/adr/0050~0055** |
| **🚀 30 apps #32 sidehustle-tracker (Cycle 88·자율 야간 무한)** | **30-apps/32-sidehustle-tracker/ 신규 (MIT)·페인 P-2026-006 GO (100/100 + 100/100·완벽)·TimeBlock → SideHustleReport·본업/부업/수면/break 4 type·SsJum 룰 (수면 6h 이하 2주 = 자동 중단)·KOSHA 번아웃 4 단계·시간당 매출 자동·27 tests + ruff 0·CLI 작동 (RED 80.5h 시연)** |
| **📊 30 apps 누적 (Cycle 88·무한 자율)** | **4 신규 앱 = 120 tests passing·페인 게이트 6 후보 검토 → 3 GO + 3 NO_GO·sunk cost 회피 21시간·박제 docs: process + pain-discovery (candidates·approved·rejected) + portfolio + research/external + adr/0050~0055** |
| **🎯 무한 자율 모드 (Cycle 89·PO 영구 2026-05-08·ADR 0056)** | **PO 명령 7건: 무한 자율·중간 멈춤 X·1 응답 다중 작업·매 응답 = 페인 검색 + 평가 + 코딩 + 박제 묶음·CLAUDE.md §8G + feedback_unstoppable_continuous_mode ⭐⭐⭐⭐⭐** |
| **💰 조건부 배포 허용 (Cycle 89·PO 2026-05-08·ADR 0058)** | **PO 명령: 캐시카우 검증 4 조건 (시장 ≥75·캐시카우 ≥80·벤치마크 1+·Q5 PASS) 통과 시 배포 허용·#31 + #32 = 동시 통과·배포 후보·ADR 0052 부분 supersede** |
| **📋 아이디어 인덱스 분류화 (Cycle 89·PO 명령)** | **docs/ideas/INDEX.md·docs/ideas/I-001~I-002·휘발 방지·NO_GO 모음 (8건·중복 방지)·6개월 후 재검토 (3건)·인디 적중률 38% (5+2/13·Pieter 5% 대비 7.6x)** |
| **🚀 30 apps #31·#32 Streamlit UI (Cycle 89)** | **30-apps/31·32/streamlit_app.py·Habit Pixel + 삼쩜삼 변형·KWCAG 2.2 AA·헌법 §11/14 정합·_shared/payments wrapper (PortOne·Stripe·LS 3 옵션)·_shared/legal_templates/privacy_policy_kr.md·배포 코드 준비 완료 (외부 가입 = PO 결정 시)** |
| **❌ 영구 NO_GO 누적 (Cycle 89)** | **8건 영구 폐기: P-001 결제+PDF·P-003 자영업 종합·P-005 Zotero·P-007 전세사기·P-008 학부모·P-010 미국 주식 숏츠·P-011 펫 케어·I-002 정치 콘텐츠 (법적 위험)·sunk cost 회피 ≈ 56시간** |
| **🤖 수익화 팀 페르소나 (Cycle 89)** | **CEO (PO) + 7 Claude 팀원 (CTO·CMO·CFO·CSM·Designer·Legal·Growth)·docs/team/REVENUE_TEAM_PERSONAS.md·매 cycle 자동 활성·기존 74 페르소나 통합** |
| **🔍 자기 진단 (Cycle 89·정직)** | **PO 명령 23건 검토·정합 100%·박제 인플레이션 인지·실 검증 0건·외부 901 진단 재발 위험·ADR 0061 박제 (박제·코드 균형 의무·박제 ≤ 50%·코드 ≥ 50%)** |
| **💡 Claude 수익화 조사 (Cycle 89·PO 명령)** | **Claude Code $2.5B 실행률·기업 4배 성장·Skills Marketplace 2026 emerging·Agent37·VoltAgent·Composio 호스팅·I-003 = SKILL.md 변환 GO (시장 95·캐시카우 90)·#1·#2·#31 = 즉시 변환 가능** |
| **🔧 _shared 인프라 6 모듈 (Cycle 89)** | **payments (PortOne·Stripe·LS)·legal_templates (PIPA)·flow (8 단계)·roadmap (6 Phase)·**auth (Better Auth·bcrypt·CSRF)**·**email (Resend·전자상거래법 §13·§17)**·5 사용처 도달·packages/ 승격 시점** |
| **📊 종합 (Cycle 89~117·29 cycle)** | **30 apps 5 정식 (1,463 tests)·_shared v0.1.0 정식 패키지 (Sandi Metz AHA)·자동 평가 v6 (정확도 89%)·SKILL.md 3건·페인 24건 (5+3+18)·ADR 17 (0050~0066)·메모리 6건·CLAUDE §8 8 항·sunk cost 회피 ≈ 126h** |
| **🚀 외부 발사 준비 완료 (Cycle 117)** | **#31·#32/.env.example·_shared/DEPLOYMENT_GUIDE.md·PO 외부 1시간 = 매출 가능·매출 가설 ₩29,700→₩990K/월 (Habit Pixel 벤치마크)·비용 ₩50K/년 + PG 2.5~3.5%** |
| **🚦 Type 1 차단점 5건 (PO 외부·게임 체인저)** | **사업자 등록 (홈택스·30분)·통신판매업 (정부24)·PortOne 가입 (1시간)·Streamlit Cloud (5분)·도메인 (₩15K/년)·ANTHROPIC_API_KEY GitHub Actions** |
| **🚀 SKILL.md 변환 (Cycle 90·I-003 GO·코드 우선)** | **3 SKILL.md 박제: kormarc-auto/.claude/skills/generate-kormarc·30-apps/02-kdc-classify/.claude/skills/classify-kdc·30-apps/31-freelancer-tax-helper/.claude/skills/freelancer-tax·Anthropic Skills Marketplace 변환 (Agent37·VoltAgent·Composio 호스팅 후보)·캐시카우 가설 = $0.5/실행 (BYOK 옵션)** |
| **🤖 24/7 자동 작동 의무 (Cycle 89·ADR 0063)** | **Cron `ac6a2cd4` 매 5분·`scripts/cron_health_check.py` 자가 점검·만료 24h 전 자동 재등록·idle 시만 발사 (Claude Code 본질·고칠 수 없음)·진정 24/7 = PO 외부 인프라 1건 필요** |
| **✅ Blanket authorization (Cycle 90·PO 2026-05-08·ADR 0064)** | **PO 명령: "여러 허용 안물어봐도 됨·심각한 것 외 다 허용"·매 결정 자율·"허용 부탁" 멘트 X·차단 = 헌법 §3·§14·법적·비가역·ADR 0052 외부 발사·PO STOP만·feedback_blanket_authorization ⭐⭐⭐⭐⭐·CLAUDE §8J** |
| **🔧 GitHub Actions autonomous-6h 수정 (Cycle 90)** | **`.github/workflows/autonomous-6h.yml` continue-on-error 강화·silent skip 모든 step·ANTHROPIC_API_KEY 미등록 시 알림 only·PO commit 17763c3 시점 코드 = remote push 시 활성** |
| **🌐 _shared/landing 템플릿 (Cycle 90·코드 ADR 0061 정합)** | **30-apps/_shared/landing/__init__.py·LandingConfig·5 FAQ 표준·면책 의무·전자상거래법 §17·KWCAG 2.2 AA·5번째 _shared 모듈 (payments·legal·flow·roadmap·auth·email·landing)·Sandi Metz AHA 정합** |
| **📋 미완 작업 (다음 cycle)** | **페인 발굴 1건 (다른 niche)·zip 9 강의 검토 (8 미진행)·#31·#32 smoke test 5건·SKILL.md 코드 페어·.claude/skills hosting 검토** |
| **영구 invariant 11** | **페르소나 시뮬 ≠ 실 인터뷰 (ADR 0046·CLAUDE.md §13)** ※ Cycle 85 보류 (PMF 결정 자체 보류) |
| **mypy** | strict = true·실 검증 = 다음 사이클 |
| **bandit (보안 스캔)** | ⏳ 미설치·다음 사이클 도입 권장 |
| GitHub | 동기 (origin/main = 로컬·v0.7.1 tag pushed) |
| 39 사이클 누적 (Cycle 22 → 61) | tests 1,009 → 1,211 (+202) |

## Plan B 사이클 진행 (B안 §0)

| Cycle | P | 상태 | commit |
|---|---|---|---|
| 1 | P1-(1) per-block disaggregation | ✅ | e7d74f6 |
| 2 | P1-(2) offline demo + v0.6.0 tag | ✅ | c292b6d |
| 3 | P2 init/serve subcmd + .bat 안내 | ✅ | 1a4c019 |
| 4 | P3 Hypothesis 정식 + 4 KORMARC property | ✅ | d736864 |
| 5 | P4 agent_docs/ 3 신규 reference | ✅ | 4898711 |
| 6 | P5 README.en.md + vhs SKIPPED | ✅ | cd7540f |
| **7** | **P6 STATUS 통합 + ADR 0026 + 익명화** | **진행 중** | (이 commit) |
| 8+ | P29 처리방침 / P30 PortOne v2 / P31 가격 페이지 (외부 858 출처 신설) | 대기 | - |
| 9~28 | P7~P28 (T3~T6) | 대기 | - |

## ADR 누적

- ADR 0024: 솔로 PO 가드레일 (외부 901 출처)
- **ADR 0025: Plan B 무중단 자율** (0024 supersede·active)
- **ADR 0026: 한국 SaaS 프로덕션 결정** (외부 858 출처·active)

## 영구 invariants (B안 §4)

1. 헌법 위반 0건 (raw 확률·100% 자동·본문 LLM 송신·사서 검토 우회)
2. 자관 데이터 git 누설 0건 (D:\ commit 시도 = 자율 정지)

## 자동 머지 차단 게이트 6건 (B안 §0)

1. ruff check . = 0 errors
2. pytest -q = 전수 통과
3. binary_assertions 39/39
4. 자관 174 회귀 ≤ 1pp
5. demo 30초 5건 round-trip 100%
6. CLAUDE.md 헌법 위반 0건

## STOP 조건 7건 (B안 §5)

1. 회귀 게이트 5 사이클 연속 위반
2. 자관 데이터 git 누설 시도
3. 본문 LLM 송신 시도
4. API 키 commit 시도
5. 우선순위 큐 모든 항목 SKIPPED
6. PO "STOP" / "PAUSE" 입력
7. 동일 P 항목 3 사이클 연속 SKIPPED

## SKIPPED 누적 (`SKIPPED.md`)

- vhs GIF 생성 (Cycle 6 P5 부분·외부 도구 미설치·PO 작업 등록)
- GitHub Release 자동 생성 (Cycle 2·gh CLI 미설치·PO 수동)

## 외부 보고서 흡수 (메모리 영속)

- 901 출처: 솔로 PO 진단 (4중 패턴·Plan B 채택 트리거)
- 858 출처: 한국 SaaS 프로덕션 (사업자·결제·영업·가격·인프라·법무 7 영역·ADR 0026)

## PO 외부 작업 (사용자_TODO P0 재배치 후)

1. 일반과세자 홈택스 등록 (722000·자택)
2. 통신판매업 신고 (PG 가입 → 구매안전서비스 → 정부24)
3. 사업자통장 (카뱅/토스 + 시중은행 1)
4. NL_CERT_KEY + ANTHROPIC_API_KEY 발급
5. 사서 5명 cold outreach (Mom Test)
6. GitHub v0.6.0 Release 수동 생성
7. 청년 마음건강 신청 (1577-0199·1393)

## 이전 STATUS_REALITY_CHECK (참조)

`docs/archive/STATUS_REALITY_CHECK-2026-04-27.md` — 2026-04-27 시점 회고. 이후 사이클 1~7에서 상당수 항목 해소·이 파일이 현행 진실원.

---

작성: Claude Opus 4.7 (1M context) · 2026-05-04 · Plan B Cycle 7 P6 STATUS 통합
