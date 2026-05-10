# ADR 0062 — Cron 자동 cycle 발사 (PO 명령 2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠
- 일자: 2026-05-08
- 관계: ADR 0056 (무한 자율) 보강·"사용자 입력 없이 자동 다음 자율"

## PO 명령

> "사용자 입력 없이 다음 자율이였으면 해"

## 결정

**Claude Code `CronCreate` tool 활용·매시간 자동 cycle 발사.**

## 활성 등록

```
cron: "17 * * * *"  (매시간 17분 KST)
prompt: "야간 자율 진행"
recurring: true
durable: true
job_id: d4660119
```

## 한계 (정직 박제)

| 항목 | 한계 |
|---|---|
| 세션 종료 | Claude exits 시 cron 사라짐·재등록 필요 |
| 7일 자동 만료 | 7일 후 마지막 1회 발사 후 삭제·재등록 의무 |
| Idle 시만 발사 | PO 활동 중 = 발사 X·자연스러운 jitter |
| 1 cycle = 1 응답 | 응답 종료 후 = 다음 cron까지 정지·1시간 단위 |

## 24/7 진정 자율 (다음 단계·PO 외부)

본 cron = 세션 한정·완전 24/7 = 외부 인프라 필요:

| 옵션 | 셋업 | 비용 |
|---|---|---|
| **A. GitHub Actions schedule** | yaml 1회·30분 | API 키만·무료 |
| **B. Anthropic Routines** | 가입·routine 등록 | API 사용량 |
| **C. Windows 작업 스케줄러 + claude --print** | 1회·노트북 켜둠 | API 사용량 |

→ ADR 0052 정합·PO 명시 시 즉시 셋업.

## 매 cycle 자동 작업 (cron 발사 시)

PO 명령 "야간 자율 진행" = 다음 자동 진행:
1. ADR 0061 정합 검증 (박제 ≤ 50%·코드 ≥ 50%)
2. _shared 인프라 강화 (auth·email·landing·billing)
3. 30 앱 깊이 (UI·smoke test·tests)
4. 새 페인 발굴 (WebSearch·ADR 0055)
5. STATUS·learnings·INDEX 자동 갱신

## 비용 가드 (헌법 §6·overhead)

- 1 cycle 평균 = 토큰 ~50K (관측치)
- 매시간 24회/일 = 1,200K/일 ≈ $30~50/일 (API direct 기준 가설)

## PO Plan 정합 (2026-05-08 PO 확인)

**PO = Claude Max plan 사용 (확정·2026-05-08).**

| Plan | 5분 cron | 비용 |
|---|---|---|
| Free | ❌ rate limit | - |
| Pro $20/월 | ⚠ 5h reset overflow | 월정액 |
| **Max** | ✅ **5x~20x usage·5분 OK** | **월정액·별도 API X** |
| API direct | ✅ 무제한 | $350~/일 |

→ **Max plan 사용 시 = 별도 API 청구 X·plan 월정액에 포함**.
→ **5분 cron 유지·정합** (PO 결정 2026-05-08).
→ 이전 비용 가드 ($350/일) = API direct 기준·Max 사용 시 무관.

## 즉시 정지 (PO 변경 시)

`CronDelete ac6a2cd4` 명령 → 즉시 삭제.

## 정합 정책

- ADR 0052: 외부 인프라 = PO 명시 시
- ADR 0056: 무한 자율 = 1 응답 내 + cron = 응답 간
- ADR 0061: 박제·코드 균형 = cron 발사 cycle도 정합
- 헌법 §6: 비용 ↑ = 50K/cycle 모니터·이상 = PO 알림

## 메모리 영속

- `feedback_cron_autonomous.md` ⭐⭐⭐⭐⭐ (다음 cycle 박제)
- CLAUDE.md §8L (다음 cycle)
- 매 7일 = 재등록 의무 (PO 또는 Claude 자동·세션 유지 시)
