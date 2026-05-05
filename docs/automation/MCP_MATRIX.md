# MCP Servers 통합 매트릭스 (Cycle 22 P45·V2 §6)

> 외부 시스템 연결 지도 + PreToolUse hook 게이트.
> ⚠️ MCP 활성화 = PreToolUse 화이트리스트 + 금액·횟수 캡 필수 (V2 §9 Defense in Depth).

## 활성 우선순위

| MCP | 영역 | 활성 시점 | 의존성 | 캡 필수 |
|---|---|---|---|---|
| Stripe (PortOne 대체) | 결제 | P30 사업자 등록 후 | PortOne v2 통합 | 환불 일일 5건·100만원 초과 사람 |
| Gmail (이메일) | 마케팅 | Cycle 23+ | 사업자 등록 | 발송 일일 100건·BCC 차단 |
| Slack | 알림 | 즉시 | webhook URL | rate limit 분당 1건 |
| Google Sheets | 영업 CRM | Cycle 24+ | 사업자 등록 | 읽기만·write 사람 |
| Notion | 문서 | 즉시 가능 | 토큰 발급 | write 화이트리스트 |
| GA4 / PostHog | 분석 | Cycle 23+ | 사업자 등록 | 읽기만 |
| Postgres / Supabase | DB | Cycle 24+ | DB 셋업 | SELECT만·write 사람 |

## 활성 절차 (V2 §6)

1. `.claude/settings.json` permissions.allow에 MCP 도구 추가 (Level 5 Progressive Trust 정합)
2. PreToolUse hook = MCP 호출별 화이트리스트
3. 비용·횟수 캡 hook 추가 (예: 환불 100만원 초과 = 사람 호출)
4. `decisions.md`에 MCP 추가 = 처리방침 §28의8 위탁자 6항목 동시 갱신 (PIPC 정합)

## STOP 조건

- PreToolUse 게이트 미설정 MCP 활성 = 즉시 정지
- 처리방침 §28의8 위탁자 누락 + MCP 활성 = PIPA 위반·자동 정지
- 환불·삭제·발송 MCP 호출 = audit log 필수 (audit/store.py 정합)

## kormarc-auto 현재 (Cycle 22)

| MCP | 상태 | 다음 단계 |
|---|---|---|
| Slack | ⏳ 대기 | webhook URL 발급 후 weekly-funnel-cron.sh 활성 |
| 나머지 | ⏳ 대기 | P30 PortOne 통합 후 (Cycle 23+) |

## 정합 ADR

- ADR 0026 한국 SaaS (PortOne primary)
- ADR 0029 audit log (MCP 호출 기록)
- ADR 0031 funnel + Plausible (PIPA 정합)
- ADR 0034 hooks (PreToolUse 화이트리스트)
- 외부 V2 §6·§9 Defense in Depth
