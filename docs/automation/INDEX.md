# docs/automation/ — 통합 색인 (Cycle 30·V2 자동화 문서 단일 진입점)

> 자동화 인프라 6 영역 색인. 각 문서 = 운영·디버깅·롤백·온보딩·프롬프트·보안 표준.

## 핵심 6 문서

| 문서 | 영역 | 핵심 |
|---|---|---|
| [DEBUGGING.md](DEBUGGING.md) | 디버깅 | 자율 작업 실패 시 root cause·로그·진단 |
| [NON_CODE_AUTOMATION.md](NON_CODE_AUTOMATION.md) | 비-코드 | 마케팅·영업·문서·고객 지원 자동화 |
| [ONBOARDING.md](ONBOARDING.md) | 온보딩 | 새 SaaS 부팅·CLAUDE.md·hooks·subagents 셋업 |
| [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md) | 프롬프트 | 검증된 명령 템플릿 (배포·리뷰·리팩터·디버그) |
| [ROLLBACK_PLAYBOOK.md](ROLLBACK_PLAYBOOK.md) | 응급 | 시크릿 누설·코드 머지·비용 폭주·무한 루프 6 시나리오 |
| [MCP_MATRIX.md](MCP_MATRIX.md) | 외부 통합 | 7 MCP 우선순위·PreToolUse 게이트·STOP 조건 |

## 운영 cadence (operations.md 정합)

- 매일: `make blocker`·`make cost`
- 매주 월: `make funnel` (weekly-funnel-cron.sh 자동)
- 매월: learnings.md 검토·`/refine-claudemd` 슬래시
- 매 commit: hooks 자동 (validate-bash·scan-secrets·post-format·append-progress)
- 매 7 사이클: META_REVIEW.md (V2 §6.1 자기 수정)

## 응급 entry point

```bash
make stop            # 🚨 모든 자율 프로세스 즉시 정지
make rollback        # 최근 1 commit revert
bash scripts/automation/emergency-stop.sh
```

자세한 시나리오 = `ROLLBACK_PLAYBOOK.md`.

## V2 §11 안전 체크리스트 정합

본 색인 = V2 §11 정합:
- ✅ 모든 변경 = 브랜치/worktree (PAVR 슬래시)
- ✅ 결정론 verify (셸 외부)
- ✅ 시크릿 스캔 hook (scan-secrets.sh)
- ✅ 일일 토큰 예산 알람 (budget-guard.sh + Cycle 19A tracker)
- ✅ 자율 실행 audit log (Cycle 9 audit_log)
- ✅ PreToolUse 화이트/블랙리스트 (validate-bash.sh)
- ✅ git revert + 롤백 절차 (rollback.sh)
- ✅ 자기 수정 PR만 (refine-claudemd 슬래시)

## 정합 ADR

- ADR 0028~0038 (Cycle 8~28 누적)
- ADR 0033 블로그 + bundle 영업
- ADR 0034 hooks + LLM GEO
- ADR 0035 budget + onboarding
- ADR 0036 PAVR + Failure Replay
- ADR 0037 Progressive Trust + Goals
- ADR 0038 Cycle 22~28 통합

## 자동화 인프라 코드 (참고)

- `automation/router.py` — 메타 라우터 (V2 §1·8 TaskKind)
- `automation/proposer_critic.py` — Sonnet 제안 + Opus 비평 (V2 §3.1)
- `automation/supervisor.py` — 멀티 SaaS 큐 (V2 §7)
- `automation/po_loop.sh` — PO 무중단 자율 루프
- `scripts/automation/` — 5 운영 스크립트 (audit·cost·emergency·health·rollback)
- `scripts/regression_check.py` — 자관 baseline 자동 비교
- `scripts/next_blocker.py` — 매출 차단점 자동 감지
- `src/kormarc_auto/budget/` — 일일 USD 추적 + 회귀 진단 (Cycle 19A)
- `src/kormarc_auto/replay/` — Failure Replay (Cycle 20B)
- `src/kormarc_auto/trust/` — Progressive Trust 5 Level (Cycle 22)
- `src/kormarc_auto/goals/` — Goal Decomposer 5계층 (Cycle 22)
