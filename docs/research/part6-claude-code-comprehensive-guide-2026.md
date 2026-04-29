# Part 6 — Claude Code 운영 종합 가이드 (2026-04 기준)

> **출처**: PO 다른 대화창 거대 종합 가이드 (4-30 인계)
> **목적**: kormarc-auto 1인 운영의 Claude Code 활용 정점화. 토큰 한도·자동화·.claude/ 디렉토리·MCP·Subagent·Plan Mode·모델 전략 종합.
> **우리 적용**: 5중 자동화 (Cloud routine 3 + GitHub Actions 2) 정합 + 격차 4건 즉시 적용.

---

## 1. 토큰 한도 — Pro/Max 5h + 주간 이중 한도 ★

- **5시간 롤링 윈도우**: 첫 메시지 시각에 고정·claude.ai 웹·Desktop·Code 동일 풀 공유
- **주간 한도** (2025-08-28 도입): Sonnet/Opus 분리 카운트
  - Pro: 약 40~80h Sonnet
  - Max 5x: 약 140~280h Sonnet + 15~35h Opus
- 한도 도달 시 하드 스톱·Pro/Max는 "Extra usage"로 종량제 API 자동 전환
- 잔량 확인: `/usage` `/status` `/context`

### 자동 재실행 패턴 (공식 지원 X)

```bash
#!/usr/bin/env bash
# claude-resume: 한도 도달 시 5분마다 재시도
POLL_INTERVAL="${CLAUDE_POLL_INTERVAL:-300}"
while true; do
  claude "$@"
  [[ $? -eq 0 ]] && break
  echo "Rate-limited. Retrying in ${POLL_INTERVAL}s..."
  sleep "$POLL_INTERVAL" || break
done
```

### 우리 정합 ★

- 우리는 **Cloud routine 3개 등록 완료** (1h·주간·월간) — 자동 재실행 사실상 해결
- prompt cache TTL 5분 → 270초 미만 또는 1200초+ 권장
- 5시간 윈도우 정렬 (warmup): GitHub Actions cron으로 작업 시작 5시간 전 Haiku에 "hi" 1번

---

## 2. Routines — 2026-04-14 출시 ★ (우리 이미 활용)

- 클라우드 cron+API+GitHub webhook 트리거
- CLI: `/schedule`·웹: claude.ai/code/routines
- **일일 한도**: Pro 5건·Max 15건·Team/Enterprise 25건 (구독 한도와 별개)
- GitHub webhook 안전장치: `claude/` 접두 브랜치만 push 가능
- 단점: fresh clone 환경 — `.env.local` 접근 X

### 우리 등록 routine 3개 (2026-04-30)

| Routine | ID | Cron |
|---|---|---|
| 1h sync | `trig_01THW9GZG6G4sorCtwgJaR77` | `0 * * * *` |
| 주간 (월 09 KST) | `trig_01Yb5Ze4eAwn4Z6srKDDu2Ma` | `0 0 * * 1` |
| 월간 (1일 09 KST) | `trig_01JGajzBSdRhMnS8KQPz5H8q` | `0 0 1 * *` |

→ Pro 5건/일 한도 = 1h routine은 사용량에 따라 일부 누락 가능 (24/일 fire 시도 vs 5건 한도)
→ 모니터링: `docs/cloud-routine-monitoring-guide.md`

---

## 3. CLAUDE.md 베스트 프랙티스 ★ (우리 격차 ★)

### 핵심 원칙

> "각 줄마다 '이걸 지우면 Claude가 실수할까?' 자문하라" (Anthropic 공식)

- **200줄 초과 시 Claude가 instruction 균등 무시 시작** (HumanLayer 분석)
- 시스템 프롬프트엔 이미 ~50개 instruction 존재
- IMPORTANT/YOU MUST/NEVER는 강력하지만 남발 시 의미 희석

### 우리 현 상태 격차

- **현재 CLAUDE.md = 323줄** ★ (권장 200줄 초과)
- → 다음 자율 commit으로 slim·핵심 사실만 유지·나머지 docs/로 분리

### 포함 vs 제외

**포함**:
- 추측 불가능한 bash 명령
- 기본값과 다른 코드 스타일
- 테스트 실행법·브랜치/PR 컨벤션
- 프로젝트 특화 아키텍처 결정
- 자주 빠지는 함정

**제외**:
- 코드 읽으면 알 수 있는 정보
- 표준 언어 컨벤션
- 자주 바뀌는 문서
- 파일별 설명

---

## 4. Skills (.claude/skills/) — 2025-10 출시

- **Progressive disclosure 아키텍처**:
  - Level 1 (description): 항상 시스템 프롬프트 로드
  - Level 2 (SKILL.md 본문): 관련 시 자동 로드
  - Level 3 (scripts/·references/): 필요 시에만
- v2.1.101 (2026-04) 이후 custom commands가 skills로 통합
- **description은 "pushy"하게 작성** — "Use whenever..." 강하게

### kormarc-auto 적용 권장

- `scaffold-crud` — Prisma 모델 → CRUD endpoint 자동
- `db-migrate` — Prisma migration + 사람 검토 강제
- `book-import` — 알라딘 ISBN → DB upsert
- `kormarc-validate` — M/A/O + .mrc 검증 (이미 모듈로 있음·skill 화 가능)

---

## 5. Hooks — 17 lifecycle 이벤트

- **PreToolUse**: 유일하게 차단 가능 (exit code 2)
- PostToolUse / SessionStart / Stop
- 2026-02부터 command 외 http·mcp·prompt(Haiku에 yes/no 위임) 추가
- ⚠️ **Stop hook 무한루프 함정**: exit 2로 Stop 차단 시 반드시 `stop_hook_active` 체크

### kormarc-auto 적용 (이미 운영 중)

- `.claude/hooks/irreversible-guard.sh` (PreToolUse·7 패턴)
- `.claude/hooks/stop-double-gate.py` (이중 게이트)
- `.claude/hooks/post-trust.py` (Trust Counter)
- `.claude/hooks/postcompact-reinject.py` (압축 후 핵심 룰 재주입)
- `.claude/hooks/permission-denied-log.py` (auto-mode 거부 로그)

---

## 6. MCP 커넥터 (코딩 워크플로우)

```json
{
  "mcpServers": {
    "github":     { "type": "http",  "url": "https://api.githubcopilot.com/mcp/" },
    "context7":   { "type": "stdio", "command": "npx", "args": ["-y", "@upstash/context7-mcp@latest"] },
    "library-db": { "type": "stdio", "command": "npx", "args": ["-y", "@bytebase/dbhub", "--dsn", "postgresql://readonly:pass@localhost:5432/library_dev"] },
    "playwright": { "type": "stdio", "command": "npx", "args": ["-y", "@playwright/mcp@latest"] },
    "sentry":     { "type": "http",  "url": "https://mcp.sentry.dev/mcp" }
  }
}
```

- **Context7**: "use context7" 한 마디로 최신 라이브러리 문서 → 환각 ↓
- **DBHub**: read-only DSN으로 스키마 인지하면서 안전 쿼리
- ⚠️ DB MCP는 반드시 read-only 계정·신뢰 출처에서만

### kormarc-auto 적용 후보 (Phase 1+)

- DBHub: SQLite/PostgreSQL 마이그레이션 후
- Playwright MCP: streamlit_app E2E 테스트
- Sentry MCP: 운영 에러 추적 (사업자 등록 후)

---

## 7. Subagents — 컨텍스트 품질 보존

- **자체 200K 윈도우·자체 도구 권한·자체 시스템 프롬프트**
- 결과만 부모에 반환 → signal-to-noise 보존
- 우선순위: session > project > user > plugin

### 모델별 분담 권장

- architect → opus (큰 설계·아키텍처)
- implementer/reviewer/test-writer → sonnet (구현)
- doc-writer/explorer → haiku (탐색·문서)
- 평균 비용 60~70% 절감

### kormarc-auto 적용 (이미 운영)

- `.claude/agents/` 9 에이전트 (researcher·librarian-reviewer·kormarc-expert 등)
- 자동 호출 룰 정합

---

## 8. Plan Mode — Boris Cherny 권장 워크플로

```
1. Plan Mode 진입 (Shift+Tab x2 또는 /plan)
2. 코드베이스 탐색 (읽기 전용)
3. plan 작성
4. Ctrl+G로 plan 직접 편집
5. Shift+Tab으로 빠져나와 Auto-Accept
6. "Implement the plan"
```

- v2.1.0+ `/plan` 슬래시 명령
- ⚠️ Windows v2.1.3+ Shift+Tab 버그 → `Alt+M` 또는 `/plan`
- ⚠️ `exit_plan_mode` 기본 옵션 = "clear context" → 컨텍스트 날아감 주의

---

## 9. 모델 라인업 (2026-04 기준)

| 모델 | $/MTok (Input/Output) | Context | 특징 |
|---|---|---|---|
| Opus 4.7 | $5 / $25 | 200K (1M beta) | 87.6% SWE-bench, ★ 새 tokenizer ~35% 더 많은 토큰 |
| Opus 4.6 | $5 / $25 | 1M | Fast Mode 베타 |
| Sonnet 4.6 | $3 / $15 | 1M | Claude Code 기본 |
| Haiku 4.5 | $1 / $5 | 200K | 최저가 현세대 |

- **공식 권장**: "Don't start with Opus and work down. **Start with Haiku and work up.**"
- Prompt caching: cached input 90% 할인
- Batch API: 50% 할인
- 결합 시 최대 95% 절감

### Thinking 키워드 (Claude Code CLI 전용)

| 키워드 | 토큰 예산 | 사용 시점 |
|---|---|---|
| think | 4,000 | 일상 작업·단순 버그 |
| think hard / megathink | 10,000 | API 설계·아키텍처 결정 |
| think harder / **ultrathink** | 31,999 | 복잡 리팩토링·마이그레이션 |

---

## 10. 컨텍스트 관리 — /clear vs /compact

- `/context` 사용량 시각화
- 새 작업 = 새 세션 (`/clear`) 원칙
- `/compact` = 손실적 요약 → 변수명·미묘한 결정 사라짐
- ⚠️ 한국어는 토큰 효율 저하 → **80~100k 도달 전 적극 /clear** (Threads @qjc.ai)

---

## 11. 한국 개발자 커뮤니티 팁

- **토스** (toss.tech "소프트웨어 3.0"): Claude Code = LLM Harness·Skill 폭발 안티패턴 경고
- **하이퍼리즘**: Shift-Tab 모드·ESC 복원·Git Worktree 멀티 세션
- **GeekNews**: claw-code (Python 클린룸 재작성·30K★)
- **revfactory/claude-code-mastering**: 한국어 13장 가이드북
- **모두의AI** (modu-ai/cc-plugins): 한다체/해요체/서사체 한국어 작성 토큰

### 우리 정합

- CLAUDE.md "한국어 응답·식별자 영문" 헌법 정합 ✅
- learnings.md "Windows cp949 출력 fix·이모지 사용 X" ✅

---

## 12. 즉시 적용 격차 4건 ★ (4-30 진행 결과)

| # | 격차 | 적용 |
|---|---|---|
| 1 | ✅ CLAUDE.md 323→206줄 slim | 5 step 완료 (ADR-0013) |
| 2 | 🟡 `/ultrareview`·`/ultraplan` (v2.1.111+) | 활용 시점: PILOT 4주차 (5/29) 발표 직전 슬라이드 종합 검토. cloud 멀티에이전트 무료 플랜 한도 내 작동. 권장: `/ultrareview` 정기적으로 main 브랜치 회귀 검토 |
| 3 | ✅ Routines Pro 5건/일 한도 | `docs/cloud-routine-monitoring-guide.md §7` 추가·1h routine cron 4h 변경 권장 |
| 4 | ✅ Stop hook 안전장치 | `stop-double-gate.py:39` `stop_hook_active` 체크 정합 검증 |

---

## 13. 라이브러리 앱 추천 스택 (1인 빠른 빌드)

> 본 가이드는 일반 라이브러리(도서 관리) 앱 권장. **kormarc-auto는 KORMARC 자동 생성 SaaS**라 다른 도메인이지만 일부 패턴은 적용 가능.

- Next.js 15 + Prisma + PostgreSQL + NextAuth v5 + shadcn/ui + Tailwind + Zod
- 우리 = FastAPI + Streamlit + Cloudflare Tunnel (이미 정점)
- 도메인 다름 — 본 추천은 별도 라이브러리 앱 빌드 시 참조

---

## 14. 보안 체크리스트 (CVE-2025-29927)

- Next.js 11.1.4–15.2.2 미들웨어 인증 우회 (CVSS 9.1)
- 인증 검사를 미들웨어에만 두지 말고 **Data Access Layer 패턴** (Server Component 내부 `requireUser()`)
- 우리 = FastAPI라 무관·streamlit_app 인증 패턴은 별도 점검 (Part G Step 2 streamlit-authenticator 정합)

---

## Sources

- Anthropic 공식 베스트 프랙티스 (claude.com/docs)
- HumanLayer CLAUDE.md 분석
- Boris Cherny (Claude Code 창시자) 권장 워크플로
- 토스 tech blog "소프트웨어 3.0"
- 하이퍼리즘 (tech.hyperithm.com)
- GeekNews (news.hada.io) 28000+ 시리즈
- 사용자 다른 대화창 (4-30 인계 거대 종합 가이드)
