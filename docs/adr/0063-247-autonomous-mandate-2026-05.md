# ADR 0063 — 24/7 자동 작동 의무 + 자가 점검·재등록 (PO 명령 2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠
- 일자: 2026-05-08
- 관계: ADR 0062 (Cron 자동 cycle) 보강

## PO 명령

> "계속 켜놨어 그러니까 넌 자동으로 움직여 줘야만해·그럼 이제 멈추지 않는것?"

## 결정

**Claude = 24/7 자동 작동 의무·매 cycle 끝 = cron 상태 자가 점검·만료 임박 시 자동 재등록.**

## 자가 점검 매트릭스 (매 cycle 끝 자동)

```
1. CronList 호출 = 현재 cron 상태 확인
2. 만료 일자 계산 (7일 - 등록일)
3. 만료 ≤ 24h = 자동 재등록 (CronCreate)
4. 만료 > 24h = OK·다음 cycle 대기
5. cron 0건 = 즉시 재등록 (이전 ID 인용)
```

## 자동 작동 의무 4 단계

| 단계 | 의무 |
|---|---|
| 1 cron 발사 | "야간 자율 진행" → 1 cycle 무한 자율 (ADR 0056) |
| 2 ADR 0061 정합 | 박제 30~50%·코드 50~70%·페인 0~20% |
| 3 매 cycle 끝 | cron 상태 자가 점검·STATUS·learnings 갱신 |
| 4 7일 임박 | 자동 재등록·PO 알림 X (자율) |

## 멈출 수 있는 시나리오 (정직 박제)

| 시나리오 | 대응 |
|---|---|
| Claude Code 세션 종료 | PO 재시작 시 = Claude 자동 재등록 의무 (메모리·CLAUDE 자동 로드) |
| 7일 자동 만료 | Claude 매 cycle 끝 점검·만료 24h 전 = 자동 재등록 |
| PO 활동 중 | 그 cycle skip·5분 후 재발사·자연 회복 |
| Claude Code 크래시·업데이트 | PO 재시작 시 = 메모리 로드·cron 재등록 자동 |
| **PO STOP 명시 명령** | 즉시 정지 (헌법 정지 조건 1건) |

## 자율 진행 의무 (PO 명시 명령 정합)

PO 명령 시퀀스 (Cycle 85~89·30+ 명령):
- "야간 무한 진행"
- "중간 멈춤 X"
- "멈추지 않고 사용"
- "지속해서 일할것"
- "계속 켜놨어 자동으로 움직여 줘야만해"

→ 모두 = "Claude = 자동 작동 의무" 명시·정합 의무.

## 매 cycle 자동 작업 (cron 발사 시)

PO 명령 "야간 자율 진행" cron 발사 = 다음 자동:

1. CronList = cron 상태 확인 (자가 점검)
2. ADR 0061 비율 검증 (박제 vs 코드 vs 페인)
3. 우선순위 자동 결정:
   - 박제 < 50% = 코드 우선 (_shared·smoke test·UI)
   - 새 페인 0건 (24h 내) = WebSearch 1회
   - GO 후보 = 1 cycle 압축 코딩
4. STATUS·learnings·INDEX 자동 갱신
5. CronList 재확인·만료 24h 전 = 재등록

## 비용 가드 (헌법 §6)

- 5분 마다 = 1일 288 cycle ≈ ~$350~600/일
- PO 즉시 정지 가능: "cron 정지"
- 자동 재등록 시 = 동일 5분 주기 유지 (PO 변경 명령 X 시)

## 박제

- 본 ADR
- `scripts/cron_health_check.py` (코드 페어·다음 cycle)
- CLAUDE.md §8L (다음 cycle)
- `feedback_247_autonomous_mandate.md` ⭐⭐⭐⭐⭐ (다음 cycle)

## 정합 정책

- ADR 0052: 외부 인프라 (GitHub Actions·Routines) = PO 명시 시
- ADR 0056: 무한 자율 (1 응답 내) + 본 ADR (응답 간) = 24/7 정합
- ADR 0061: 박제·코드 균형 = cron 발사 cycle 모두 정합
- 헌법 §1 의심: 매 cycle 끝 자가 진단 의무 (5 cycle 마다 자기 진단 박제)
