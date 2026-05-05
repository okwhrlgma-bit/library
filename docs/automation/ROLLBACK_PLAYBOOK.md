# Rollback Playbook — 🚨 Claude가 잘못된 일을 했을 때

자율 시스템을 굴리다 보면 반드시 일어납니다. 패닉하지 마세요. 절차가 있습니다.

## 0. 즉시 정지 (10초 안에)

```bash
make stop
# 또는
./scripts/emergency-stop.sh
```

이게 하는 일:
1. 모든 `claude` 프로세스 즉시 종료 (SIGKILL)
2. Python 자동화 스크립트 종료
3. `crontab`을 비우고 백업 (복구는 `crontab <백업파일>`)
4. 진행 중인 git 작업 상태 보고
5. 슬랙/디스코드 웹훅으로 알림 (설정돼있으면)

**먼저 이걸 실행한 다음에 다음 단계로**.

---

## 1. 무엇이 잘못됐는지 파악

### 1-A. 최근 커밋 보기

```bash
git log -20 --oneline
```

`auto/...` 브랜치나 자동 커밋 메시지(`feat: ...(PAVR)`, `chore: auto-update ...`)를 찾으세요.

### 1-B. 최근 파일 변경

```bash
git diff HEAD~5 HEAD --stat
```

어느 파일들이 만져졌는지 한눈에.

### 1-C. Audit 로그

```bash
make audit
```

최근 7일 자율 실행 이력. 비용·시간·작업 디렉터리 확인.

### 1-D. PROGRESS.md 최근 항목

```bash
tail -50 PROGRESS.md
```

자동 생성된 작업 요약.

---

## 2. 시나리오별 대응

### 시나리오 A: 잘못된 코드가 main에 머지됨

```bash
# Step 1: 어떤 커밋인지 확인
git log -10 --oneline

# Step 2: 안전하게 revert
./scripts/rollback.sh --commits 1
# 또는 여러 개:
./scripts/rollback.sh --commits 3

# Step 3: 검토 후 원격에 반영
git diff main rollback/...
git push origin rollback/...
gh pr create --fill
```

⚠️ `git reset --hard`는 권한이 막혀있고, 그게 정상입니다. 항상 revert 사용.

### 시나리오 B: 실수로 푸시된 시크릿

이건 시간이 중요합니다. 시크릿이 한 번이라도 푸시되면 **로테이션 필수**입니다.

```bash
# Step 1: 즉시 로테이션
# - Anthropic API key: console.anthropic.com에서 키 비활성화 + 새 키 발급
# - Stripe: dashboard에서 restricted key 회전
# - DB: 비밀번호 변경 + 마이그레이션
# - GitHub PAT: settings/tokens에서 폐기

# Step 2: 히스토리에서 제거 (BFG 또는 git-filter-repo)
git filter-repo --path .env --invert-paths
git push --force origin main
# (협업 중이면 팀에 알림 필수)

# Step 3: scan-secrets.sh가 왜 못 잡았는지 확인
./scripts/hooks/scan-secrets.sh < <(echo '{"tool_input":{"content":"누설된패턴","file_path":"src/x.ts"}}')

# Step 4: scan-secrets.sh의 PATTERNS 배열에 패턴 추가
${EDITOR:-vi} scripts/hooks/scan-secrets.sh
make test-hooks
```

### 시나리오 C: Claude가 잘못된 파일을 잔뜩 지움

```bash
# Step 1: stash가 있는지 확인
git stash list

# Step 2: reflog에서 직전 상태 찾기
git reflog --date=iso | head -20

# Step 3: 직전 좋은 상태로 복귀
git reset --hard HEAD@{N}  # N은 reflog에서 본 인덱스
# 또는 특정 SHA로
git reset --hard <sha>

# Step 4: 푸시 안 했다면 여기서 끝.
# 푸시했다면 force push 전에 협업자 확인.
```

### 시나리오 D: 비용 폭주 (한 작업이 수만 토큰)

```bash
# Step 1: 즉시 정지
make stop

# Step 2: 비용 확인
make cost

# Step 3: audit 보면서 어떤 작업이 폭주했는지
./scripts/audit-query.sh --days 1

# Step 4: 폭주 원인 후보:
#   1) max-turns가 안 걸림 — 라우터 설정 확인
#   2) Opus를 trivial 작업에 씀 — 분류기가 잘못 분류
#   3) 무한 루프에 가까운 행동 — verify hook이 비결정적
#   4) 컨텍스트가 너무 큼 — .claudeignore 더 좁게

# Step 5: 일일 예산 더 좁게
${EDITOR:-vi} .env
# DAILY_BUDGET_USD=5 같은 작은 값으로
```

### 시나리오 E: 자동 PR이 너무 많이 쌓임

```bash
# 모두 닫기
gh pr list --label "auto-generated" --json number --jq '.[].number' | \
  xargs -I {} gh pr close {} --comment "수동 정리: 자동 PR 일괄 종료"

# nightly-autonomy.yml의 빈도를 낮추기 (매일 → 주 1회)
${EDITOR:-vi} .github/workflows/nightly-autonomy.yml
# cron: '0 18 * * *' → '0 18 * * 0'  (일요일만)
```

### 시나리오 F: 무한 루프 (cron이 폭주)

```bash
# Step 1: cron 비활성화 (emergency-stop이 이미 했지만 재확인)
crontab -l   # 비어야 함

# Step 2: 백그라운드 프로세스 확인
ps aux | grep -E "claude|router\.py|supervisor\.py"
# 보이면 추가로 kill

# Step 3: 실행 중이던 작업의 git 상태
git status
git stash  # 안전하게 보존

# Step 4: cron 복구는 천천히 — 원인 분석 후
ls -lt ~/.claude/crontab-backup-*.txt | head -1
# 검토 후 crontab <백업파일>
```

---

## 3. 사고 후 처리 (꼭 하기)

### 3-A. learnings.md 업데이트

```markdown
## YYYY-MM-DD — <사고 한 줄 제목>
**작업**: 무엇을 시켰는가
**증상**: 어떻게 잘못됐나
**원인**: 진짜 이유 (추측 아님)
**예방**: 무엇을 바꿔야 같은 사고 안 나는가
**관련**: 추가/수정한 hook, CLAUDE.md 규칙
```

### 3-B. 시스템 강화

원인에 따라:

| 원인 | 강화 |
|------|------|
| 위험한 명령이 통과 | `validate-bash.sh`의 DENY_PATTERNS에 추가 + `make test-hooks` 통과 확인 |
| 시크릿 통과 | `scan-secrets.sh`의 PATTERNS에 추가 |
| 잘못된 카테고리 분류 | `router.py`의 CLASSIFIER_PROMPT에 예시 추가 |
| max-turns 부족/과다 | `ROUTING_TABLE` 조정 |
| 너무 많은 자율 권한 | `.claude/settings.json`의 `permissions.deny` 추가 |
| CLAUDE.md 부족한 가이드 | "절대 금지 사항"에 한 줄 추가 |

### 3-C. 회귀 테스트 추가

`replays/<날짜-제목>/` 디렉터리 만들고:
- `input.json` — 사고 시 입력
- `repro.sh` — 어떻게 재현하는가
- `expected.txt` — 어떤 행동이어야 했는가
- `actual.txt` — 실제 무엇을 했는가

다음에 모델/프롬프트 변경 시 이 replay를 한 번 돌려서 회귀 검사.

---

## 4. 절대 하지 말 것

- ❌ **시크릿이 노출됐는데 "그냥 보지 못했을 거야" 넘기기** — 반드시 로테이션
- ❌ **`git push --force`로 흔적 지우기** — 머지 전에 revert로 처리. 푸시 후엔 사고 자체를 인정하고 새 PR로 fix
- ❌ **사고 원인 분석 없이 cron 즉시 재가동** — 같은 사고 반복
- ❌ **혼자 패닉으로 결정** — 결제·DB·도메인 사고는 5분 멈추고 차분히

---

## 5. 사람을 부를 때

자율 시스템이 다음 중 하나라도 했으면 즉시 사람 검토:

- 결제 로직 (`src/lib/stripe/`, `src/api/webhook/`) 변경
- DB 스키마 변경 (마이그레이션 파일)
- 환경변수 변경 (특히 production)
- 도메인·라우팅 변경
- 가격 페이지 변경
- 사용자 PII 처리 코드 변경

이 영역들은 **router가 unsafe로 분류해서 자동 차단**돼야 정상입니다. 통과했다면 라우터 분류가 잘못된 것 — `router.py`의 분류 프롬프트 강화하세요.

---

## 6. 빠른 참조

```bash
make stop              # 🚨 모든 거 정지
make audit             # 최근 7일 audit
make cost              # 최근 7일 비용
make rollback          # 최근 1개 커밋 revert
./scripts/rollback.sh --commits 5  # 5개 revert
./scripts/rollback.sh --branch auto/123  # 특정 브랜치 삭제
git reflog --date=iso  # 모든 git 상태 변화 이력
```
