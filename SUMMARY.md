# SUMMARY — kormarc-auto 누적 진척 (Cycle 1 → 60·v0.7.1)

> **갱신**: 2026-05-06 Cycle 60 마무리·v0.7.1 release·UI/UX 통합 완료.
> **이전 SUMMARY** = `docs/archive/SUMMARY-2026-05-04-cycle1-2.md` (B안 §0 적용 시점).
> **단일 진실원**: `STATUS.md` (현재)·본 SUMMARY = 누적 매트릭스.

## 60 사이클 매트릭스 (Cycle 1 → 60)

| Cycle 그룹 | 영역 | tests | ADR | 핵심 산출 |
|---|---|---:|---|---|
| 1~2 (B안 §0) | per-block disaggregation + offline demo + v0.6.0 tag | 645 → 658 | 0024·0025 | regression baseline |
| 3~6 | init/serve·Hypothesis·agent_docs·README.en | 658 → 753 | - | uv tool install |
| 7~14 | STATUS·익명화·결정론·audit·Ghost text·카테고리 신뢰·visible diff·KWCAG | 753 → 903 | 0026~0033 | v0.7.0 종착 |
| 15~21 | KWCAG·KRDS·SEO·블로그·자치구·Hooks·LLM GEO·budget·온보딩·PAVR·Failure Replay·starter v2 | 903 → 1009 | 0034~0036 | V2 §3·§4·§6 |
| 22~28 | V2 자율 인프라 + regression + blocker + UI + operations | 1009 → 1047 | 0037·0038 | invariants 7건 |
| 29~35 | V2 §3 다중 에이전트 4 패턴 (Proposer·N-Vote·Hierarchical·Adversarial) | 1047 → 1083 | 0039 | 100% scaffolding |
| 36~42 | 차단점 동적 + 매출 대시보드 + V2 §3 시나리오 | 1083 → 1107 | 0040 | 13 시나리오 tests |
| 43~49 | V3 외부 256 출처 (Auth·Cost Cap 3-Layer·Audit·Weekly·RUNBOOK·KOLAS3 cron) | 1107 → 1140 | 0041·0042 | invariants 10건 |
| 50~58 | V3 마무리 (Streamlit KOLAS3·revenue Block 4·router_patcher AST·v0.7.1 release) | 1140 → 1152 | (0043) |  |
| 59 | 일괄 검토 + 6 갭 메우기 (README/STATUS/.gitignore/operations/META/ADR 0043) | 1152 | 0043 | 단일 진실원 동기 |
| **60** | **UI/UX 통합 (KWCAG 2.2 + KRDS + Pretendard + 사서 친화)** | **1152 → 1186** | **0044** | **헌법 §12 100%** |
| **61** | **8 ICP 페르소나 깊이 + 상업성/SEO/AEO/GEO + Part 96 + 추가 조사 (커버리지·invariant 11)** | **1186 → 1228** | **0045·0046** | **invariant 11 박제** |
| **62** | **마케팅 노출 30+ 갭 + 콜드 메일 5 + 콘텐츠 캘린더 90일 + press kit + MOU 8** | **1228** | (시드) | **발행 시드 100% scaffolding** |
| **63** | **신경 0 배포 stack (₩0/월·GitHub Pages·Streamlit Cloud) + E-E-A-T + landing about** | **1228** | (workflow + doc) | **15분 활성·도메인 X** |
| **64** | **BaaS 10 옵션 비교·ADR 0047 Accepted (Supabase 미도입)·Phase 1/2/3 stack** | **1228** | **0047** | **자동 결정 완료** |
| **65** | 사서 자가 설치 (.exe 자동 빌드·invariant 12) | 1228 | 0048 | 도서관 RFP 100% |
| **66** | 비즈니스 모델 = Open Core + Hosted SaaS | 1228 | 0049 | "왜 결제?" 박제 |
| **67** | 사업성 1순위·인터뷰 playbook | 1228 | (playbook) | 코드 STOP |
| **68** | B2C "몰래 쓰기" 전환·Supabase 부활 | 1228 | 0050 | 결제권자 = 결제자 |
| **69** | founder fit + B2C 상세 + 앱스토어 + 클리커 | 1228 | (4 doc) | 1차 검증 |
| **70** | B2C 진지 활성 (Supabase scaffold·PWA) | 1228 → 1249 | (5 산출) | 실 활성 가능 |
| **71~76** | 야간 자율 (META·자동 클리커 PoC·인터뷰 분석 도구) | 1249 → 1264 | (도구) | 1주 작업 활성 |
| **77** | 일괄 진행 (자료 동기·ADR 0051·사용자_TODO) | 1264 | **0051** | 11 명령 통합 |
| **65** | **사서 자가 설치 친화 (`.exe` 자동 빌드·launcher.py·5초 가이드)·invariant 12** | **1228** | **0048** | **PO 방문 X·사서 더블클릭** |
| **66** | **비즈니스 모델 Open Core + Hosted SaaS·"왜 결제?" 매트릭스** | **1228** | **0049** | **자가 5%·결제 95%** |

## 최신 메트릭 (Cycle 60 마무리)

| 항목 | 값 |
|---|---:|
| Tests | **1,186** passing / 6 skipped (+177 over 38 cycles) |
| ruff | 0 errors |
| binary_assertions | 39/39 |
| 자관 174 round-trip | 100% baseline (regression ≤ 1pp 영구 게이트) |
| 영구 invariants | **10건** (V3 추가 3건·ADR 0041) |
| ADRs 누적 | **0024~0044** (21건) |
| 메모리 | 7건 (901·858·매출·V1·V2·V3·1-명령 1-완료 ⭐⭐⭐⭐⭐) |
| Plan B P29~P52 | 22/24 (P30·P39 외부 의존만) |
| V2 §1·§3·§5·§6·§7·§10·§11 | 100% scaffolding |
| V3 Block 1·2·3·4·5·7 | ✅ scaffolding (Block 6 = 두 번째 SaaS 시작 시) |
| **UI/UX (헌법 §12)** | **KWCAG 2.2 9 항목·KRDS·Pretendard 글로벌 적용** |
| GitHub | origin/main 동기·v0.7.1 tag |

## V3 통합 매트릭스 최종

| Block | Cycle | 상태 | 활성 시점 |
|---|---|---|---|
| 1 Auth | 43 | ✅ doc | 즉시 |
| 2 Cost Cap 3-Layer | 43 | ✅ | Phase 2 (API 키 후) |
| 3 audit.jsonl | 43 | ✅ | 즉시 |
| 4 weekly_report | 47·51·52 | ✅ scaffold + UI + cron | 2026-05-13+ (audit 7일) |
| 5 router_patcher | 53·54 | ✅ scaffold + tests | 2026-06-06+ (30일 데이터) |
| 6 cross-project | - | ⏳ | 두 번째 SaaS 시작 시 |
| 7 RUNBOOK + Makefile | 44·49 | ✅ | 즉시 |

## 영구 invariants 11건

1. 헌법 위반 0건
2. 자관 데이터 git 누설 0건
3. 결정론 (ADR 0028)
4. AI 출처 표시 (ADR 0029)
5. 카테고리형 신뢰 (ADR 0030)
6. KWCAG 2.2 (ADR 0032)
7. KOLAS3 종료일 = 2026-12-31 (ADR 0026)
8. 야간 자율 = cost_supervisor 래핑 (ADR 0041)
9. budget-cap-precheck.sh exit 2 우회 금지 (ADR 0041)
10. audit.jsonl append-only·직접 편집·삭제 금지 (ADR 0041)
11. **페르소나 시뮬 ≠ 실 인터뷰·정직 헤더 의무 (ADR 0046·Cycle 61)**

## 단일 진실원 동기화 (Cycle 59 + 60)

| 파일 | 갱신 시점 |
|---|---|
| README.md (한국어) | Cycle 59 |
| README.en.md (영문) | Cycle 59 |
| STATUS.md | Cycle 59 |
| META_REVIEW.md | Cycle 59 |
| agent_docs/operations.md | Cycle 59 |
| .gitignore | Cycle 59 (V3 8 패턴) |
| docs/RUNBOOK.md | Cycle 44 |
| CHANGELOG.md | Cycle 60 (Unreleased UI/UX) |
| Makefile | Cycle 60 (a11y·ui-test·dashboard) |
| **SUMMARY.md** | **Cycle 60 (이 파일)** |

## 다음 7-cycle 권장 (Cycle 61~67)

| Cycle | 영역 | 의존 |
|---|---|---|
| 61 | weekly_report 1주 데이터 첫 검증 | 2026-05-13+ |
| 62 | KOLAS3 countdown UI A/B | 즉시 |
| 63 | revenue_dashboard 인터랙티브 | 즉시 |
| 64 | router_patcher 30일 첫 분석 | 2026-06-06+ |
| 65 | (P30 PortOne 활성) | PO 사업자 등록 |
| 66 | UI/UX 페르소나 시뮬 재검증 (Part 49 56% 전환) | 즉시 |
| 67 | META_REVIEW Cycle 60~67 + ADR 0045 | 7-cycle 마무리 |

## PO 외부 작업 (불변 차단점)

`docs/external-dependencies-matrix-2026-05.md` 단일 진실원.

| ID | 작업 | 차단 해소 |
|---|---|---|
| PO-PROD-1 | 일반과세자 홈택스 등록 | P30 PortOne 라이브 |
| PO-PROD-5 | NL_CERT_KEY 발급 | 정확도 |
| PO-PROD-6 | ANTHROPIC_API_KEY 발급 | AI 기능 + V3 Phase 2 |
| SALES-1 | 사서 5명 인터뷰 | wedge·P39 사서어 |

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 Cycle 60 · v0.7.1 + UI/UX 통합 · 무중단 자율 38 사이클 누적
