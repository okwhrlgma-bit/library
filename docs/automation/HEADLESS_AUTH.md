# Headless Authentication (V3 Block 1·외부 256 출처)

> 야간 무중단 자율 운영 시 인증 분리·외부 256 출처 V3 §2 정합.
> kormarc-auto 환경 (Windows·로컬 PO 운영) 정합으로 condensed.

## 핵심 결론

야간 Docker 루프 또는 Claude Code 헤드리스 = **`ANTHROPIC_API_KEY` (night-scoped Console workspace)** 1순위.

### 이유 (V3 §2.3 결정 트리)

1. 5시간/주간 한도 X = Max 구독 카운트 안 깎음
2. Console workspace 별 spend cap 사전 설정 (월 $300 등)
3. env 한 줄 안정 주입 = refresh race condition X
4. 사고 시 Console에서 즉시 revoke = 본인 Max 구독 무영향

## 인증 우선순위 (공식 code.claude.com/docs/en/authentication)

1. Cloud provider (`CLAUDE_CODE_USE_BEDROCK/VERTEX/FOUNDRY`)
2. `ANTHROPIC_AUTH_TOKEN` (Bearer·게이트웨이)
3. `ANTHROPIC_API_KEY` (X-Api-Key·Console)
4. `apiKeyHelper`
5. `/login` OAuth

**핵심 함정**: `ANTHROPIC_API_KEY` 환경변수 = Max 구독 무시·토큰당 과금. **`/status`로 활성 인증 확인 필수**.

## 3 인증 방식 비교 (V3 §2.2)

| 차원 | (A) `ANTHROPIC_API_KEY` | (B) `~/.claude` OAuth | (C) `CLAUDE_CODE_OAUTH_TOKEN` |
|---|---|---|---|
| 토큰 prefix | `sk-ant-api03-...` | `sk-ant-oat01-...` | `sk-ant-oat01-...` (1년) |
| 자격 저장 | 환경변수만 | macOS Keychain / Linux·Win `~/.claude/.credentials.json` | 환경변수만 |
| 만료 | 무기한 | access ≈ 8h, refresh 자동 | **1년 고정** |
| 과금 | Console PAYG | Pro/Max 쿼터 | Pro/Max 쿼터 |
| 5h/주간 한도 | ❌ (API rate limit만) | ✅ | ✅ |
| Docker 헤드리스 | ★★★★★ | ★★ (Issue #22066 6h 동기화) | ★★★★ |

## kormarc-auto 적용 (Windows PO 환경)

### 현재 (Phase 1 = Plan B Cycle 22~42)
- PO 로컬 환경 = Claude Code 데스크톱 앱 + `/login` OAuth (Pro/Max)
- 야간 Docker = 미운영 (po_loop.sh 로컬 실행만)
- 비용 모니터링 = `src/kormarc_auto/budget/tracker.py` (Cycle 19A)

### Phase 2 (사업자 등록 + Anthropic API 키 발급 후)
- night workspace 신설 (Console·spend cap $50/월·Anthropic API)
- `.env`: `ANTHROPIC_API_KEY=sk-ant-api03-NIGHT_xxx`
- po_loop.sh = `cost_supervisor.py` 래핑 (V3 §3 3-Layer Guard)

### Phase 3 (Docker 격리·v1.0+)
- Dockerfile.claude-overnight (V3 §2.4 참조)
- docker-compose.overnight.yml + .env.night
- workspace 분리: dev / night / prod (cap $50 / $300 / $1,000)

## 보안 (V3 §2.8)

### 워크스페이스 분리
```
console.anthropic.com → Workspaces
├─ dev    sk-ant-api03-DEV_…    cap $50/월
├─ night  sk-ant-api03-NIGHT_…  cap $300/월   (자율 루프)
└─ prod   sk-ant-api03-PROD_…   cap $1000/월
```

### 절대 금지
- API 키 git commit (헌법 §3 + scan-secrets.sh hook)
- `~/.ssh`·`~/.aws`·`~/.gnupg` Docker 마운트
- `~/.claude` 마운트 (Issue #22066 6시간 동기화 깨짐)

## 5 디버깅 케이스 (V3 §2.6)

| Case | 원인 | 해결 |
|---|---|---|
| `Invalid API key` | Console에서 revoked | `unset ANTHROPIC_API_KEY && claude /login` 또는 새 키 |
| `401 OAuth expired` | OAuth 8h 만료·refresh 실패 | `claude setup-token`으로 1년 토큰 재발급 |
| `429 rate_limit_error` | 5h 윈도우 또는 #40085 동기화 | `/usage` 잔여·extra usage 활성 |
| `Unable to open browser` | Docker/SSH 헤드리스 | `CLAUDE_CODE_OAUTH_TOKEN` env 또는 ssh -L 포트 포워딩 |
| `OAuth not persisting` | `~/.claude` 마운트·Issue #22066 | setup-token + env로 우회 |

## 참조

- 공식 `code.claude.com/docs/en/authentication`
- 공식 `code.claude.com/docs/en/devcontainer` — managed-settings
- GitHub `anthropics/claude-code#22066` — Docker OAuth 영속성
- GitHub `anthropics/claude-code/plugins/ralph-wiggum` — Ralph 패턴
- ghuntley.com/ralph — Geoffrey Huntley Ralph Wiggum 패턴
- V3 마스터 가이드 §2 (외부 256 출처·2026-05-06)
