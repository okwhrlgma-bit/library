# DEBUGGING — Claude Code가 잘못 갔을 때

자율 시스템은 반드시 잘못 갑니다. 이 문서는 그때 무엇을 보고 어떻게 진단할지 정리합니다.

## 진단 우선순위 (순서대로)

```
1. 멈춰라 (make stop)        ← 더 망가지기 전에
2. 무엇이 일어났는지 파악     ← 로그·git·audit
3. 가설 세우고 재현            ← replays/
4. 고치고 학습 기록            ← learnings.md
```

## 1. 흔한 실패 모드 카탈로그

### 모드 A: 무한 루프

**증상**: 프로세스가 계속 돌고 비용은 쌓이는데 진척이 없음.

**원인**:
- 같은 테스트가 계속 실패해서 같은 fix를 반복
- PostToolUse hook이 파일을 다시 변경 → Claude가 또 변경 → 무한 반복

**진단**:
```bash
ps aux | grep -E "claude|automation" | head
tail -100 ~/.claude-orchestrator/queue.log
git log --oneline -20  # 같은 메시지 반복?
```

**처방**:
1. `make stop` (즉시 정지)
2. PostToolUse hook이 입력 파일을 변경하지 않는지 확인 (auto-format은 변경하지만 멱등이어야 함)
3. `learnings.md`에 "이 패턴은 재시도 한도 5회"로 기록

---

### 모드 B: 잘못된 파일 대량 수정

**증상**: `git diff`에 수백 파일이 변경됨. 의도한 작업과 무관.

**원인**:
- 와일드카드 명령 (`find -exec sed`)
- 잘못된 working directory
- "전체 코드베이스를 리팩터링" 같은 모호한 지시

**진단**:
```bash
git diff --stat HEAD~1  # 변경 규모
git log --oneline -5    # 어느 커밋부터?
```

**처방**:
1. `make rollback` (안전하게 새 브랜치에 revert)
2. 절대 `git reset --hard` 쓰지 마세요. revert 사용.
3. `decisions.md`에 "전 코드베이스 변경은 사람 승인 필수"

---

### 모드 C: 비용 폭주

**증상**: 일별 비용이 평소의 10배.

**원인**:
- Opus를 분류·요약 같은 가벼운 작업에 사용
- 컨텍스트가 너무 커서 매 호출마다 입력 토큰이 누적
- 캐시 무효화 (system prompt가 매번 바뀜)

**진단**:
```bash
make cost                          # 일별 비용
./scripts/audit-query.sh --cost 1  # 어제 비용 상세
./scripts/audit-query.sh --days 7  # 최근 7일 작업 목록
```

**처방**:
1. `~/.claude-orchestrator/usage.json` 확인 — 어느 작업이 비쌌나
2. 라우터 분류표 점검 — Haiku로 갈 작업이 Opus로 갔는지
3. `CLAUDE.md` 길이 확인 (200줄 넘으면 캐싱 효율 떨어짐)
4. `.claudeignore`에 큰 파일/폴더 추가

---

### 모드 D: 시크릿 노출

**증상**: 푸시한 코드에 API 키, `.env` 내용이 들어감.

**원인**:
- `scan-secrets.sh` hook이 비활성화됐거나 누락
- 새로운 키 패턴이 hook에 등록 안 됨 (예: 새 SaaS API)

**진단**:
```bash
git log --all --full-history -p | grep -E "sk-|pk_|API_KEY" | head
./tests/test-hooks.sh  # hook이 실제로 막는지
```

**처방** — `docs/ROLLBACK_PLAYBOOK.md` §시나리오 2 참고. 핵심:
1. **즉시 키 회전** (Stripe/Anthropic 대시보드에서)
2. `git filter-repo`로 히스토리에서 제거
3. force push (협업 중이면 팀에 사전 공지)
4. `scan-secrets.sh`에 새 패턴 추가 + `tests/test-hooks.sh`에 케이스 추가

---

### 모드 E: 폭주 PR

**증상**: GitHub에 자동 생성된 PR이 50개 쌓임. 머지도 안 되고 닫히지도 않음.

**원인**:
- nightly-autonomy가 같은 작업을 매일 새 PR로 만듦 (중복 감지 누락)
- 사람 리뷰 캐파를 초과한 자동 생성

**처방**:
```bash
gh pr list --author @me --state open --limit 100 \
  | awk '{print $1}' | xargs -I{} gh pr close {} --delete-branch
```
이후 `automation/supervisor.py`에 동일 작업 중복 감지 로직 추가:
- 매일 작업 시작 전 `gh pr list --search "in:title <task-name>"`로 기존 PR 확인.

---

### 모드 F: Hook이 조용히 실패

**증상**: `validate-bash.sh`가 `rm -rf /`를 막아야 하는데 안 막음.

**원인**:
- chmod +x 안 됨
- `.claude/settings.json`에서 경로 오타
- hook 스크립트 자체 버그 (정규식 오류)

**진단**:
```bash
./tests/test-hooks.sh   # 모든 hook 회귀 테스트
ls -l scripts/hooks/    # 실행 권한 (rwx)
```

**처방**:
1. `chmod +x scripts/hooks/*.sh`
2. `tests/test-hooks.sh`가 통과하는지 확인
3. 통과 안 하면 실패 케이스를 보고 hook 로직 수정

---

### 모드 G: Cron 작업 폭주 (같은 스크립트 다중 실행)

**증상**: `automation/daily-autonomy.sh`가 동시에 5개 떠있음.

**원인**: 작업이 24시간 안에 끝나지 않아서 다음 cron이 쌓임.

**진단**:
```bash
ps aux | grep daily-autonomy
crontab -l
```

**처방**: cron 명령에 `flock` 추가:
```cron
0 18 * * * /usr/bin/flock -n /tmp/daily.lock /home/me/myapp/automation/daily-autonomy.sh
```

---

## 2. 진단 도구

| 도구 | 용도 |
|---|---|
| `make health` | 모든 hook·권한·환경변수 검증 |
| `make audit` | audit.jsonl 최근 작업 조회 |
| `make cost` | 일별 비용 |
| `make stop` | **🚨 모든 자동화 즉시 정지** |
| `tests/test-hooks.sh` | hook이 실제로 차단하는지 회귀 테스트 |
| `git log --oneline -20` | 최근 자동 커밋 패턴 |
| `tail -100 ~/.claude-orchestrator/queue.log` | 라우터 결정 로그 |

## 3. 학습 회로

실패할 때마다:
1. `replays/<YYYY-MM-DD>-<short-name>.md`에 재현 가능한 케이스 저장 (입력·기대출력·실제출력)
2. `learnings.md`에 한 줄로 교훈 추가
3. 가능하면 hook이나 라우터 분류표에 가드 추가 → 같은 실패가 다시 안 나오도록

> "같은 실패는 두 번 일어나면 시스템 결함이다." — 한 번은 사고, 두 번은 자동화의 결함.

## 4. 사람 호출 기준 (이 중 하나라도 해당하면 즉시 멈추고 사람에게)

- 일별 비용이 예산의 200% 초과
- 같은 작업이 5회 이상 실패
- production 배포 후 5분 안에 에러율 3% 초과
- 시크릿 의심 패턴이 git에 들어감
- 한 번에 100개 이상 파일 변경
- 결제·인증·DB 마이그레이션 자동 실행 시도
