# 야간 자율 실행 프로토콜 (PO 표준)

> 야간 무인 운영 시 표준 프롬프트. PO 가이드 (2026-04) 야간 셋업 즉시 사용.

## 모드 비교 (PO 가이드)

| 모드 | 권한 prompt | 자율 강도 | 비고 |
|---|---|---|---|
| `--enable-auto-mode` (Team+) | 위험 작업만 1~2회 | ⭐⭐⭐⭐ | 권장 — 분류기 자동 평가 |
| `--dangerously-skip-permissions` (YOLO) | 0회 | ⭐⭐⭐⭐⭐ | 끝까지 진행, 단 격리 필수 |
| `acceptEdits` (Pro, 현재) | 편집 자동·Bash prompt | ⭐⭐⭐ | 매일 작업용 |

**중요**: "권한 0회 = 잘함" 아님. YOLO여도 다음 5개 시나리오에서 멈추거나 망가짐.

## 5대 멈춤·고장 시나리오 + 회피

| # | 시나리오 | 회피 |
|---|---|---|
| 1 | **모호한 결정** ("A vs B 뭐가?") | 프롬프트에 "막히면 더 안전·보수적 쪽 + DECISIONS.md 기록" 명시 |
| 2 | **테스트 무한 실패** | "같은 테스트 3회 실패 → SKIPPED.md + 다음" 탈출 조건 |
| 3 | **자가 디버그 무한루프** | 작업당 최대 시도 횟수 명시 (예: 30 max-iterations) |
| 4 | **컨텍스트 한계 + auto-compaction** | 중요 규칙은 CLAUDE.md에 — 매 세션 자동 로드 |
| 5 | **외부 의존성 실패** (npm·pip 네트워크) | 의존성 추가 금지 + offline 모드 우선 |

## 표준 작업 지시 (PO 발급)

```
목표: [구체적이고 검증 가능한 완료 조건]
완료 기준: 모든 테스트 통과 + 커밋된 상태

작업 규칙:
- 한 번에 하나씩, 작은 단위로 커밋
- 매 커밋마다 CHANGELOG_NIGHT.md 에 변경 사유 기록
- 같은 문제 3회 시도 후 실패하면 SKIPPED.md 에 기록하고 다음으로
- 판단 필요한 지점에서는 더 안전/보수적인 선택을 하고 DECISIONS.md 에 기록
- 절대 묻지 말고 진행. 막히면 다른 작업으로 우회

금지:
- src/legacy/, .env, package.json/pyproject.toml 의 dependencies 수정
- 새 외부 라이브러리 설치
- git push, 브랜치 삭제

종료 조건:
- 모든 테스트 통과 → 최종 커밋 후 종료
- 더 이상 진행 불가 → STATUS.md 작성 후 종료
```

## 우리 프로젝트 야간 운영 매핑

### 산출물 4종 (yyyymmdd 단위)
- `CHANGELOG_NIGHT.md` — 매 commit 변경 사유 (3줄 이내)
- `SKIPPED.md` — 3회 실패 작업 + 다음 시도 제안
- `DECISIONS.md` — 보수적 선택 + 근거 (작은 ADR 후보)
- `STATUS.md` — 종료 시 최종 상태 + 다음 야간 인계

### 검증 게이트 (`.claude/rules/autonomy-gates.md`)
- `pytest -q` 종료 코드 0
- `python scripts/binary_assertions.py --strict` (18/18)
- 매 commit 메시지에 `Co-Authored-By` 트레일러

### 금지 영역 (kormarc-auto 특화)
- `src/kormarc_auto/conversion/marc21_east_asian.py` ACTIVATED 변경 금지 (ADR 0009)
- `pyproject.toml` 의존성 추가 금지 (pip install 금지와 일관)
- `~/.claude/settings.json` 권한 변경 금지 (블래스트 반경 통제)
- `.env`·`.env.local` 읽기·쓰기 금지 (이미 deny)
- `src/legacy/` 없음 — 대신 `kormarc/loss_damage.py` 등 583 처리 영역 read-only

### 우회 정책 (3회 실패 후)
1. SKIPPED.md에 ISBN/모듈/근본 원인 기록
2. 다른 미흡수 PO 자료 영역으로 전환 (자료/ 폴더 신규 발견)
3. ADR 미작성 큰 결정 → architect-deep 자문 → ADR 추가

### 종료 시 STATUS.md 양식
```markdown
# 야간 실행 상태 (yyyy-mm-dd)
- 시작: HH:MM KST
- 종료: HH:MM KST  (이유: [완료/한도 초과/막힘])
- commit 누적: N건
- 어셔션 통과율: M/18
- 다음 야간 시작 시 우선 처리할 항목:
  1. ...
  2. ...
```

## 실행 명령 (Windows PowerShell)

```powershell
git worktree add ../kormarc-auto-night night-work
cd ../kormarc-auto-night
# 위 표준 작업 지시를 NIGHT_TASK.txt로 저장
claude --enable-auto-mode (Get-Content NIGHT_TASK.txt -Raw) 2>&1 | Tee-Object -FilePath "logs/night-$(Get-Date -Format yyyyMMdd).log"
```

## 아침 검토 3분

```bash
git log --oneline night-work..main
cat CHANGELOG_NIGHT.md
cat STATUS.md
python scripts/binary_assertions.py
git diff main..night-work --stat
```

문제 없으면 `git merge night-work` (또는 PR), 문제 있으면 `git worktree remove ../kormarc-auto-night`.

---

## 관련

- ADR 0010 — 야간 자율 셋업
- `.claude/rules/autonomy-gates.md` — 자율 게이트 정의
- `learnings.md` — 매 야간 후 PO 가이드 흡수 갱신
