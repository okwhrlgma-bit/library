# ADR 0010 — 야간 자율 운영 셋업 (Auto Mode + git worktree + 격리)

**상태**: accepted
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

자율 commit 누적 28건+ 도달. PO가 잠든 사이 안전하게 디벨롭 계속하려면 권한 모드·격리·로깅·시스템 슬립 4축 결정 필요.

PO 가이드(2026-04 신규):
1. Auto mode (Team+) — 분류기 자동 위험도 평가, 가장 안전한 자율 모드
2. acceptEdits (Pro) — 현재 적용
3. YOLO (`--dangerously-skip-permissions`) — Docker/git worktree 격리 필수

## 결정

**3단 운영 모드**:

| 시나리오 | 모드 | 위치 |
|---|---|---|
| 일반 작업 (현재) | `acceptEdits` | 메인 트리 (Pro 호환) |
| 야간 PILOT 자율 | `--enable-auto-mode` | git worktree `../kormarc-auto-night` |
| 위험 실험 | `--dangerously-skip-permissions` | Docker 컨테이너 + worktree 둘 다 |

### 야간 표준 셋업

```powershell
# Windows PowerShell (Win11)
git worktree add ../kormarc-auto-night night-work
cd ../kormarc-auto-night
# 전원옵션 → 절전 안 함 (1회 설정)
claude --enable-auto-mode "야간 작업 지시 (구체적 + 종료 조건 + read-only 영역)" 2>&1 | Tee-Object -FilePath "night-$(Get-Date -Format yyyyMMdd).log"
```

### 야간 작업 지시 표준

> "tests/ 폴더 실패 테스트를 한 번에 하나씩 통과시켜라.
> 매번 작은 commit + CHANGELOG_NIGHT.md 기록.
> 새 의존성 추가 금지, src/legacy/ 절대 수정 금지.
> `binary_assertions.py 16/16` + `pytest 통과`가 모두 충족되면 종료."

## 결과

- PO 잠든 사이 commit 5~20건 자동 누적 (Phase 7 RSI 패턴 정합)
- 메인 트리 절대 안전 (worktree 격리)
- 아침 검토 3분 (`git diff main` + `cat night.log` + `cat CHANGELOG_NIGHT.md`)

## 트레이드오프

✅ **장점**
- Pro 플랜에서도 acceptEdits로 90% 자율
- worktree 격리로 메인 트리 회귀 0%
- 매 commit 어셔션 자동 → 회귀 즉시 검출
- 시스템 슬립 차단 (Windows 전원옵션 / macOS caffeinate / Linux systemd-inhibit)

❌ **단점**
- Auto mode는 Team 플랜+ 필수 (Pro면 acceptEdits 또는 YOLO+Docker)
- worktree 충돌: 동일 브랜치 동시 체크아웃 불가 → 별도 브랜치 필수
- 야간 토큰 비용 누적 (50회 반복 ≈ $50~100)

## 완화 조치

- `--max-iterations 30` (Ralph 패턴) + 토큰 예산 환경변수
- `night.log`에 `caffeinate`/`systemd-inhibit` 사용 여부 명시
- worktree 정기 정리: `git worktree prune` 매주
- Routines (Anthropic 클라우드)는 정기 작업에만, 인터랙티브 야간 X

## 6개월 후 되돌릴 수 있는가?

**Y** — 모드 변경 즉시 효력. PG 도입·결제 처리 시작 시 `default`로 회귀해 매 prompt 받기 가능.

## 관련 자료

- `learnings.md` "야간 자율 운영 권한 모드" 섹션
- `~/.claude/settings.json` defaultMode (현재 acceptEdits)
- `.claude/rules/autonomy-gates.md` 종료 게이트
- PO 가이드 `compass_artifact_*.md` (Phase 4-7 매핑)
