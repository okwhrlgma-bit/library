# Cloud Routine 모니터링 가이드 (PO 매주 1회 점검)

> **목적**: Cloud routine 3개가 정상 동작하는지 PO가 매주 1번 5분 점검. 문제 발생 시 즉시 재등록·재개.
> **자동화 정점**: Cloud (3) + GitHub Actions (2) = 5중 자동화. 매주 1번 점검으로 충분.

---

## 1. 등록된 Cloud Routine 3개

| # | Routine | ID | Cron | 다음 fire |
|---|---|---|---|---|
| 1 | **kormarc-auto 무한 자율 1h** | `trig_01THW9GZG6G4sorCtwgJaR77` | 매시 정각 UTC | 매시간 |
| 2 | **주간 매출 리뷰** | `trig_01Yb5Ze4eAwn4Z6srKDDu2Ma` | `0 0 * * 1` (월 09:00 KST) | 매주 월요일 |
| 3 | **월간 매출 보고서** | `trig_01JGajzBSdRhMnS8KQPz5H8q` | `0 0 1 * *` (1일 09:00 KST) | 매월 1일 |

---

## 2. 매주 점검 5분 (월요일 또는 자유 시점)

### 2-1. GitHub commit 확인 (1분)

https://github.com/okwhrlgma-bit/library/commits/main 접속:

- 지난 주 commit 수 (예: 168 commit/주 = 1h × 24h × 7일 = 168 fire)
- 실제는 cloud agent가 작업 못 할 때도 있어서 50~150 commit/주 정상 범위
- 0 commit/주 = ★ 문제 발생 (다음 §3 참조)

### 2-2. routine 상태 확인 (2분)

각 routine 관리 URL 접속:

- https://claude.ai/code/routines/trig_01THW9GZG6G4sorCtwgJaR77
- https://claude.ai/code/routines/trig_01Yb5Ze4eAwn4Z6srKDDu2Ma
- https://claude.ai/code/routines/trig_01JGajzBSdRhMnS8KQPz5H8q

각 페이지에서 확인:
- ☐ "Enabled: Yes" (활성 상태)
- ☐ "Last run" 시각 (최근 1~2시간 내·1h routine)
- ☐ "Next run" 시각 (다음 fire)
- ☐ 최근 실행 결과 (성공/실패)

### 2-3. 영업 funnel 확인 (1분)

```powershell
cd "C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto"
git pull origin main
.\.venv\Scripts\python.exe scripts\sales_funnel.py
```

→ 신규 가입·활성·결제·이탈 즉시 출력.

### 2-4. 주간 보고서 확인 (1분)

지난 주 월요일 routine이 자동 생성한 `docs/weekly-report-YYYY-MM-DD.md` 확인:

- ☐ 지난 주 commit·funnel·이벤트
- ☐ 이번 주 자율 작업 5건
- ☐ PO 결정 대기 사항

---

## 3. 문제 발생 시 대응

### 3-1. routine fire 안 됨 (0 commit/주)

가능 원인:
1. Anthropic 클라우드 장애 (https://status.anthropic.com 확인)
2. routine `Enabled: No` 상태 (관리 URL에서 enable 토글)
3. GitHub repo 접근 fail (private 전환 후 인증 끊김)

해결:
1. 장애면 회복 대기 (보통 1~24h)
2. Enable 토글 ON
3. routine 재등록 (claude.ai/code/routines · "+ New routine"·`docs/cloud-routine-monitoring-guide.md` §4 참조)

### 3-2. commit 있는데 평가축 음수 commit

가능 원인:
1. Cloud agent가 평가축 오해 (CLAUDE.md 갱신 안 읽음)

해결:
1. PO가 직접 git revert 또는 reset 후 평가축 명문화
2. AUTONOMOUS_BACKLOG.md 우선순위 재조정
3. 다음 routine fire 시 자동 정합

### 3-3. pytest·ruff·assertions fail

가능 원인:
1. Cloud agent가 큰 변경 시도하다 깨뜨림
2. 외부 의존성 (NL Korea·alaadin API) 일시 fail

해결:
1. GitHub Actions ci.yml workflow가 자동 검증·차단 (이미 적용)
2. PO가 직접 git log·diff로 문제 commit 식별·revert

---

## 4. routine 신규 등록 (필요 시)

### Web UI

1. https://claude.ai/code/routines 접속
2. "+ New routine" 클릭
3. 입력:
   - Name: 한국어 가능
   - Cron: 매시간 `0 * * * *`·매주 월 `0 0 * * 1`·매월 1일 `0 0 1 * *`
   - Repository: https://github.com/okwhrlgma-bit/library
   - Model: claude-sonnet-4-6
   - Prompt: 자율 작업 가이드 (CLAUDE.md·INDEX·BACKLOG 참조 + 평가축)
4. Create

### API (자동)

```python
from anthropic_api import RemoteTrigger
RemoteTrigger.create(body={...})
```

(현재 세션에서 등록 가능 — Claude Code RemoteTrigger 도구)

---

## 5. routine 영구 종료 (필요 시)

routine 삭제는 Web UI로만 가능 (API 미지원):

1. https://claude.ai/code/routines 접속
2. 각 routine → "..." → "Delete routine"

또는 `Enabled: No`로 토글만 (재등록 불필요).

---

## 6. 비용 (참고)

- Cloud routine 3개 = 사용자 Claude 계정의 사용량에 합산
- Sonnet 4.6 사용량: 1h routine 약 30K~50K tokens × 24h × 30일 ≈ 월 30M tokens
- 사용자 Claude Pro·Max·Team 플랜에 따라 한도 다름
- 한도 초과 시 routine fire 일시 중단 → 한도 회복 후 자동 재개

---

## Sources

- `AUTONOMOUS_BACKLOG.md` (cloud agent 자율 작업 큐)
- `~/.claude/projects/.../memory/project_session_2026_04_29.md` (routine 등록 정보)
- claude.ai/code/routines (관리 UI)
- https://status.anthropic.com (장애 점검)
