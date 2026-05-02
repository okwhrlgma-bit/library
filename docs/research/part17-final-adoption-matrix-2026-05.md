# Part 17 — 최종 차용 매트릭스 (2026-05-02)

> 누적 조사 14개 영역 × 30+ 사례 → kormarc-auto 즉시·중기·장기 차용 항목 통합 매트릭스
> 출처: 16개 WebSearch + Part 15·16 (이미 작성된 직전 두 Part)
> **목적**: 다음 Cloud routine·다음 PO 결정 세션이 한 화면에서 모든 차용 결정 가능

---

## 0. 조사 영역 14개 (완료)

| # | 영역 | 핵심 산출물 |
|---|------|-------------|
| 1 | 1인 SaaS 캐시카우 (Pieter Levels·Marc Lou·Base44) | Part 16 §1 |
| 2 | 바이브 코딩 사례 (Lovable·Cursor·Claude Code) | Part 16 §2 |
| 3 | Streamlit 수익화 (st-paywall·Webflow 분리) | Part 16 §6 |
| 4 | 버티컬 SaaS / Niche Academy | Part 16 §3 |
| 5 | Ex Libris Alma AI Metadata Assistant | Part 16 §3 |
| 6 | Excel → SaaS (Satva) | Part 16 §4 |
| 7 | 한국 공공조달 (나라장터·S2B) | Part 16 §5 |
| 8 | 한국 도서관 지원 사업 (NLK·서울시·문체부) | Part 17 §1 (이번) |
| 9 | Anthropic Prompt Caching 90% 절감 | Part 17 §2 |
| 10 | Claude Code subagents/parallel | Part 17 §3 |
| 11 | Slash commands / Skills | Part 17 §4 |
| 12 | Hooks 실전 패턴 | Part 17 §5 |
| 13 | MCP Supabase/Stripe 통합 | Part 17 §6 |
| 14 | BIBFRAME 마이그레이션 사례 (UC Davis Blue Core) | Part 17 §7 |

---

## 1. 한국 도서관 지원 사업 — 사서 예산 외 자금원

### 발견 사실

- **NLK 공공도서관 기술지원 누리집**: 2026-02-25 시범 → 2026-03-09 정식 개방
- **책이음서비스 확대**: 작은도서관 대상 → 사서가 직접 책이음 전환 가능
- **학교도서관 책이음 통합**: 학생 독서로 대출기록 통합 관리
- **서울시 자치구 자료구입비·운영비 지원**: 공·사립 작은도서관 대상
- **문체부 2026 전국 도서관 운영평가 지원**: 입찰 공고 진행 중

### 차용 → 영업 전략

| 채널 | 효과 | 차용 행동 |
|------|------|-----------|
| NLK 기술지원 누리집 등록 | 신뢰성 ★★★ | kormarc-auto를 NLK 인증 기술 도구로 등록 시도 → 사서_TODO 추가 |
| 책이음 통합 정책 활용 | 학교도서관 12,200관 진입 | kormarc-auto 출력이 책이음 호환 명시 (이미 적용) → 영업 카피 강화 |
| 서울시 작은도서관 지원 | 운영비 = SaaS 결제 가능 | 자치구 도서관 영업 시 "운영비 지원금 활용 가능" 명시 |
| 문체부 운영평가 | 평가 도구로 등록 가능성 | 운영평가 항목 분석 후 kormarc-auto 정합 검증 → 1.0 로드맵 |

---

## 2. Anthropic Prompt Caching — 운영비 90% 절감

### 발견 사실 (2026 기준)

- **Sonnet 4.6**: input $3 / output $15 / 1M tokens
- **Opus 4.7**: input $5 / output $25 / 1M tokens
- **Cache write**: base × 1.25 (25% 더 비쌈, 1회만)
- **Cache read**: base × 0.10 (90% 절감, 5분 TTL)
- **Notion 사례**: AI 어시스턴트 비용·속도 동시 개선
- **개발자 사례**: $720/월 → $72/월 (90% 절감, 비디오 메타데이터 처리)
- **블로그 자동화**: $40~60 → $15~20 (65% 감소)
- **API 통합 팀**: 60~80% 절감 (캐싱 + batch + 모델 선택 최적화)

### kormarc-auto 차용 (즉시 적용)

| 위치 | 현재 | 차용 후 |
|------|------|---------|
| Claude Code 세션 | CLAUDE.md 매번 로드 (~2K 토큰) | `cache_control: ephemeral` → 90% 절감 |
| 사서 KORMARC 변환 API (가까운 미래) | 매 요청 시스템 프롬프트 풀로드 | 시스템 프롬프트 캐시 → 권당 비용 ₩50→₩10 (Q2 평가축 +5) |
| 4 Agent 동시 launch | 각자 독립 컨텍스트 | 공유 컨텍스트 캐시 → 토큰 4× 절감 가능 |

**차용 행동** (백로그):
- [ ] **AGENTS.md / CLAUDE.md 캐시 활성화** (Claude Code SDK 사용 시 `cache_control` 명시)
- [ ] **사서 API 시스템 프롬프트 캐시 설계** (1.0 로드맵 — KORMARC 변환 LLM 보조 시점)

---

## 3. Claude Code Subagents·Parallel — 이미 활용 중

### 발견 사실

- **Subagent**: 빠른 보고형 워커 (Read·Grep·Bash·Edit)
- **Agent Teams** (실험적): 공유 task list + peer-to-peer messaging + file locking
- **Split-and-merge**: 의존성 없는 병렬 → 결과 통합
- **Sequential**: 단계별 컨텍스트 전달

### kormarc-auto 정합

- ✅ 이미 적용: 4 Agent 병렬 launch (Part 1~4 매뉴얼 = 시간 1/3)
- ✅ 이미 적용: code-reviewer subagent
- ⏸️ 미적용: **Agent Teams** (Opus 4.6+ 필요, 비용 큼)

**차용 권장**:
- [ ] **NIGHT_RUN_PROTOCOL에 split-and-merge 패턴 명시** (병렬 작업 표준화)
- [ ] **공유 출력 스키마 정의** (병렬 결과 통합 쉽게)

---

## 4. Slash Commands · Skills — 이미 운영 중

### 발견 사실

- **Skills**: `.claude/skills/` (project) 또는 `~/.claude/skills/` (personal)
- **자동 활성화**: 대화 내용 매칭 시 스킬 자동 트리거 (security review·code review 등)
- **Slash Commands**: 사용자 호출 (`/command`) — 단일 파일 단순 프롬프트
- **/loop 명령**: 백그라운드 인터벌 실행 (각 iteration 독립 컨텍스트)

### kormarc-auto 정합

- ✅ 이미 활용: `/ultrareview` `/ultraplan` (Part 6 §12)
- ✅ 이미 활용: cloud routine 3개
- ⏸️ 미적용: **자동 활성화 skill** (보안·리뷰 키워드 트리거)

**차용 권장**:
- [ ] **`.claude/skills/binary-assertions-guard/`** — "commit" 키워드 감지 시 자동 어셔션 실행
- [ ] **`.claude/skills/sales-copy-writer/`** — "영업 메일" 키워드 감지 시 영업 자료 11건 자동 참조

---

## 5. Hooks 실전 패턴

### 발견 사실 (2026 신규)

- **HTTP hooks**: 2026-01 Anthropic 출시 — POST 엔드포인트로 외부 시스템 검증
- **`permissionDecision: "deny"`**: bypassPermissions 모드에서도 차단 가능 (가장 강력)
- **exit 2 = 차단**: PreToolUse + stderr 메시지
- **handler 4종**: command / HTTP / prompt / agent

### kormarc-auto 정합

- ✅ 이미 운영: irreversible-guard.sh (PreToolUse, exit 2)
- ✅ 이미 운영: stop-double-gate.py (Stop hook, pytest + binary_assertions)
- ⏸️ 미적용: **HTTP hook** (외부 검증 서버)
- ⏸️ 미적용: **prompt hook** (단일 턴 평가)

**차용 권장**:
- [ ] **HTTP hook으로 commit 전 PII 검증** (2026-01 신기능)
- [ ] **prompt hook으로 영업 자료 commit 전 톤 검증** (LLM 평가)

---

## 6. MCP Supabase·Stripe 통합

### 발견 사실 (2026)

- **MCP 97M 설치** (2026-03 기준, 산업 표준 자리매김)
- **Supabase MCP**: `mcp.supabase.com` 호스팅 + npm `npx supabase-mcp@latest`
- **`read_only=true` 강제**: 프로덕션 데이터 안전 탐색 (PostgreSQL restricted user)
- **FastMCP 3.0**: 2026-02 출시, 100K+ 다운로드
- **200+ MCP 서버**: GitHub·Slack·PostgreSQL·Stripe·Figma·Docker·Kubernetes 등

### kormarc-auto 차용

| MCP | 활용 | 우선순위 |
|-----|------|----------|
| **Supabase MCP** | 자관 PILOT DB 직접 쿼리·migration | 🟢 즉시 (Phase 2) |
| **Stripe MCP** | 결제 영업 시 customer/subscription 조회 | 🟡 매출 발생 후 |
| **GitHub MCP** | PR 리뷰·이슈 자동화 | 🟢 이미 활용 가능 |
| **Sentry MCP** | 운영 에러 추적 → kormarc-auto 자동 수정 | 🟡 Phase 2 운영 시 |
| **PortOne MCP** | 한국 결제 통합 (자체 구축 필요?) | 🟡 매출 발생 후 |

**차용 행동**:
- [ ] **Supabase MCP 통합** (`.mcp.json` 추가) — `read_only=true` 패턴
- [ ] **GitHub MCP 통합** — PR 자동 리뷰 강화

---

## 7. BIBFRAME 마이그레이션 사례 ⭐ (도서관 도메인 직접)

### 발견 사실

- **Library of Congress**: 2025년 신규 ILS 도입, 2026년 RDA 공식 시행
- **Blue Core 컨소시엄**: Stanford·Cornell·UC Davis 공동 (linked data 협업 카탈로깅)
- **UC Davis BIBFLOW**: 2013년 IMLS 자금 지원 시작 → 2023-11 BIBFRAME publish to OCLC 테스트 → **2024-06 production 전환** ★
- **Alma 하이브리드 모델**: MARC + BIBFRAME 공존 → 점진적 마이그레이션

### kormarc-auto 차용 (1.0 로드맵 핵심)

이미 영업 자료 `outreach-bibframe-lod-2026-05.md`에 BIBFRAME 영업 시작. 추가:

| 차용 항목 | 평가축 | 우선순위 |
|----------|--------|----------|
| **UC Davis BIBFLOW 패턴 학습** (10년 노하우) | Q3 자산 +3 | 🟢 즉시 — 학습만 |
| **Alma 하이브리드 모델 모방** (KORMARC+BIBFRAME 공존) | Q4 락인 +5 | 🔴 1.0 로드맵 핵심 |
| **Blue Core 컨소시엄 참여 시도** | Q3 자산 +5 (협업 자산) | 🟡 PO 검토 영역 |
| **OCLC publishing 통합** | Q4 락인 +3 (글로벌 진입) | 🟡 1.0 로드맵 |

**차용 행동**:
- [ ] **BIBFRAME 변환 모듈 1.0 설계 ADR-0023** (UC Davis BIBFLOW 패턴 차용)
- [ ] **Alma 하이브리드 모델 분석 → kormarc-auto Phase 2 설계 문서**
- [ ] **Blue Core 컨소시엄 참여 가능성 검토** → 사용자_TODO에 추가

---

## 8. 종합 우선순위 매트릭스

### 즉시 (이번 Cloud Routine 또는 다음 1주)

| # | 작업 | 평가축 | 출처 |
|---|------|--------|------|
| 1 | streamlit_app.py SEO 메타 주입 | Q1+1 | Part 15 |
| 2 | landing/ 키워드 페이지 4종 | Q1+2 | Part 15 |
| 3 | 영업 자료 4건 → 정적 HTML | Q1+2, Q4+1 | Part 15 |
| 4 | Webhook 서명 검증 강화 | Q5+1 | Part 15 |
| 5 | 가격 정책 v2 — 정액+종량 (Niche Academy) | Q1+3, Q4+3 | Part 16 |
| 6 | "Alma AI 70% 동일" 영업 카피 12건째 | Q1+1 | Part 16 |
| 7 | PO 트위터/카톡 매출 투명 공개 routine | Q1+1, Q3+1 | Part 16 |
| 8 | **Prompt Caching 활성화** (Claude Code SDK) | Q2+5 (운영비 90% 절감) | Part 17 §2 |
| 9 | Supabase MCP 통합 (`read_only=true`) | Q3+2, Q5+1 | Part 17 §6 |

### 중기 (1.0 로드맵)

| # | 작업 | 평가축 | 출처 |
|---|------|--------|------|
| 10 | BIBFRAME 변환 모듈 ADR-0023 | Q3+5, Q4+5 | Part 17 §7 |
| 11 | Alma 하이브리드 모델 분석 → Phase 2 설계 | Q4+5 | Part 17 §7 |
| 12 | 사서 API 시스템 프롬프트 캐시 설계 | Q2+5 | Part 17 §2 |
| 13 | HTTP hook으로 PII 검증 | Q5+3 | Part 17 §5 |
| 14 | 자동 활성화 skill 2종 (binary-assertions·sales-copy) | 효율 +20% | Part 17 §4 |

### 장기 (PO 결정 후)

| # | 작업 | 평가축 | 출처 |
|---|------|--------|------|
| 15 | 나라장터 등록 (PO 작업) | Q1+5 | Part 16 §5 |
| 16 | 학교장터 S2B 등록 (PO 작업) | Q1+5 ★★★ | Part 16 §5 |
| 17 | NLK 공공도서관 기술지원 등록 | Q3+3 | Part 17 §1 |
| 18 | Blue Core 컨소시엄 참여 검토 | Q3+5 | Part 17 §7 |
| 19 | Stripe MCP (글로벌 결제 시) | Q1+2 (글로벌) | Part 17 §6 |

---

## 9. Sources (이번 조사 추가 분)

### 한국 도서관 지원
- [국립중앙도서관 공공도서관 기술지원](https://books.nl.go.kr/)
- [서울도서관 자치구 운영지원](https://lib.seoul.go.kr/rwww/html/ko/serviceSupport.jsp)
- [문체부 2026 전국 도서관 운영평가](https://www.mcst.go.kr/site/s_notice/notice/bidView.jsp?pSeq=18561)
- [한국도서관협회 KLA](https://www.kla.kr/)

### Prompt Caching
- [Anthropic Prompt Caching 공식](https://www.anthropic.com/news/prompt-caching)
- [$720→$72 사례 — Du'An Lightfoot Medium](https://medium.com/@labeveryday/prompt-caching-is-a-must-how-i-went-from-spending-720-to-72-monthly-on-api-costs-3086f3635d63)
- [Claude Prompt Caching 90% 가이드 — TopicTrick](https://topictrick.com/blog/claude-prompt-caching-guide)
- [Cut Anthropic API Costs 90% 2026 — Markaicode](https://markaicode.com/anthropic-prompt-caching-reduce-api-costs/)

### Subagents·Parallel
- [Claude Code Subagents 공식](https://code.claude.com/docs/en/sub-agents)
- [Agent Teams Setup 2026 — claudefa.st](https://claudefa.st/blog/guide/agents/agent-teams)
- [Multi-agent Orchestration — Shipyard](https://shipyard.build/blog/claude-code-multi-agent/)

### Skills/Slash Commands
- [Common workflows 공식](https://code.claude.com/docs/en/common-workflows)
- [awesome-claude-code GitHub](https://github.com/hesreallyhim/awesome-claude-code)
- [Master 80% Claude Code 15 Concepts — Geeky Gadgets](https://www.geeky-gadgets.com/master-claude-code-15-concepts/)

### Hooks
- [Claude Code Hooks 공식](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code Hooks 12 Lifecycle Events — claudefa.st](https://claudefa.st/blog/tools/hooks/hooks-guide)
- [20+ Hook Examples 2026 — aiorg.dev](https://aiorg.dev/blog/claude-code-hooks)
- [Hooks Mastery GitHub — disler](https://github.com/disler/claude-code-hooks-mastery)

### MCP
- [Supabase MCP 공식 — Supabase Docs](https://supabase.com/docs/guides/getting-started/mcp)
- [MCP Complete Guide 2026 — Essa Mamdani](https://www.essamamdani.com/blog/complete-guide-model-context-protocol-mcp-2026)
- [Supabase MCP Server AI Integration 2026 — DesignRevision](https://designrevision.com/blog/supabase-mcp-server)
- [supabase-mcp GitHub](https://github.com/supabase-community/supabase-mcp)

### BIBFRAME
- [BIBFRAME 공식 — Library of Congress](https://www.loc.gov/bibframe/)
- [BIBFRAME implementation ALA core MARC — Tandfonline 2025](https://www.tandfonline.com/doi/full/10.1080/07317131.2025.2467578)
- [Linked Data Editors to Alma ILS UC Davis case — DCMI](https://dcpapers.dublincore.org/files/articles/952433788/dcmi-952433788.pdf)
- [MARC to BIBFRAME Linked Data — Ex Libris Group](https://exlibrisgroup.com/blog/from-marc-to-bibframe-what-linked-data-means-for-libraries-in-practice/)
- [BIBFRAME-to-MARC Conversion Tools — LoC](https://www.loc.gov/bibframe/news/bibframe-to-marc-conversion.html)

---

> **이 파일 위치**: `kormarc-auto/docs/research/part17-final-adoption-matrix-2026-05.md`
> **AUTONOMOUS_BACKLOG 우선순위 0-3 등록**: §8 즉시 항목 5건 신규
> **사용자_TODO.txt 추가**: NLK 등록·Blue Core 참여 검토·BIBFRAME ADR-0023 결정
