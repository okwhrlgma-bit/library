# Onboarding — Clone 후 첫 10분

## 0. 사전 준비

다음이 설치돼있어야 합니다:
- `git`, `node` (>= 20), `npm`, `jq`
- (선택) `python3`, `pip3` — Python 자동화 스크립트용
- (선택) `gh` — GitHub Actions 디버깅용

## 1. Bootstrap (1분)

```bash
./bootstrap.sh
```

이 스크립트는:
- 모든 `.sh` 파일에 실행 권한 부여
- `.env.example` → `.env` 복사
- `claude` CLI 설치 (없으면)
- Python 의존성 설치 (선택)
- `git init` (안 됐으면)

## 2. 환경변수 (1분)

```bash
${EDITOR:-vi} .env
```

최소 채워야 하는 것:
- `ANTHROPIC_API_KEY` — https://console.anthropic.com/ 에서 발급
- `DAILY_BUDGET_USD` — 일일 한도. 처음엔 5~10불 추천

선택:
- `EMERGENCY_CONTACT_WEBHOOK` — 사고 시 슬랙/디스코드 알림
- 사용하는 MCP 서버 키들

## 3. 헬스체크 (30초)

```bash
make health
```

모든 ✅이어야 합니다. 빨간 ❌이 있으면:
- 필수 파일 누락 → README의 디렉터리 구조 참고
- Hook 실행 권한 없음 → `chmod +x scripts/hooks/*.sh`
- `ANTHROPIC_API_KEY` 누락 → `.env` 다시 확인

## 4. Hook 자가 테스트 (30초)

```bash
make test-hooks
```

이건 매우 중요합니다. Hook이 조용히 깨져있으면 시크릿이나 위험 명령이 통과합니다.
모두 PASS여야 합니다.

## 5. 프로젝트 정보 채우기 (3분)

`CLAUDE.md` 편집:
- 한 줄 설명
- 스택 (Next.js? FastAPI?)
- 코딩 컨벤션 (이미 있는 컨벤션 그대로)
- 절대 금지 사항 (이건 신중히 — 너무 좁으면 자율성이 죽고, 너무 넓으면 사고)

`goals/current.md` 편집:
- 분기 목표 (예: "MRR $1k 달성")
- 이번 주 집중 영역

`decisions.md`에 이미 내린 큰 결정 1~2개 추가 (예: 왜 X 라이브러리 골랐는가)

## 6. 첫 자율 작업 (2분)

가장 안전한 첫 작업: **README 오타 수정**.

```bash
python automation/router.py "현재 README의 오타를 잡아 PR 만들어"
```

기대 결과:
- `[ROUTED] kind=code-edit model=claude-sonnet-4-6` 같은 라우팅 로그
- Claude가 README 읽고, 오타 찾고, 수정하고, 새 브랜치에서 커밋
- 수동으로 PR 푸시는 직접 (자동 푸시는 차단됨)

작동 안 하면:
- 토큰 부족 → `make audit --cost`로 사용량 확인
- 권한 거부 → `.claude/settings.json`의 `permissions.allow` 확인

## 7. GitHub Actions 셋업 (선택, 5분)

자동 PR 리뷰를 원하면:

1. GitHub repo 생성 + push
2. Repo 설정 → Secrets and variables → Actions
3. `ANTHROPIC_API_KEY` 시크릿 추가
4. PR을 하나 만들어보기 — `claude-pr-review.yml`이 자동 코멘트

## 8. 자율 시스템 첫 가동 (선택, 5분)

cron으로 일일 루프 돌리기:

```bash
# 매일 아침 9시
crontab -e
# 추가:
0 9 * * * cd /path/to/your/saas && ./automation/daily-autonomy.sh
```

⚠️ **처음 일주일은 수동으로 `make daily`를 돌려보고 결과를 확인한 다음에 cron 등록하세요.** 자율 시스템이 무엇을 하는지 모르고 등록하면 위험합니다.

## 9. 사고 났을 때

`make stop`이 모든 걸 멈춥니다. 외워두세요.

이후 절차는 [`docs/ROLLBACK_PLAYBOOK.md`](ROLLBACK_PLAYBOOK.md).

## 10. 다음에 읽을 것

- [`docs/PROMPT_LIBRARY.md`](PROMPT_LIBRARY.md) — 자주 쓰는 프롬프트 모음
- [`docs/ROLLBACK_PLAYBOOK.md`](ROLLBACK_PLAYBOOK.md) — 사고 대응
- V1/V2 마스터 가이드 — 왜 이렇게 설계됐는지

---

**막혔을 때**: V1 마스터 가이드의 §11(실수 방지 체크리스트)부터 다시 보세요. 자율 시스템 깔기 전에 갖춰야 할 것들이 있습니다.
