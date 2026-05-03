# Release Process (B안 P4)

> CLAUDE.md slim 정합 = 릴리스 절차 상세는 본 파일.
> Plan B 무중단 자율 = Cycle 종료 시 자동 트리거 (게이트 통과 시).

## 사이클 종료 = 자동 PR + 자동 머지 (Plan B §0)

### 머지 차단 게이트 6건 (영구·invariants)
1. `ruff check .` = 0 errors
2. `pytest -q` = 전수 통과
3. `python scripts/binary_assertions.py --strict` = 39/39
4. 자관 174 파일 round-trip = 회귀 ≤ 1pp (regression_baseline.json 비교)
5. `kormarc-auto demo` = 30초 5건 round-trip 100% (Cycle 2 게이트)
6. CLAUDE.md 헌법 위반 = 0건 (raw 확률·100% 자동·본문 송신·검토 우회)

### Conventional Commits
- `feat(scope):` 신규 기능
- `fix(scope):` 버그 수정
- `docs(scope):` 문서
- `refactor(scope):` 리팩토링
- `test(scope):` 테스트
- `chore(scope):` 잡무
- 매 메시지 마지막: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

## 메이저 버전 cut (Cycle 2 / 28 / 등)

### v0.6.0 cut (2026-05-04·Cycle 2)
1. `pyproject.toml version = "0.6.0"`
2. `src/kormarc_auto/__init__.py __version__ = "0.6.0"`
3. `CHANGELOG_NIGHT.md` v0.6.0 항목
4. `git tag -a v0.6.0 -m "..."` + `git push origin v0.6.0`
5. GitHub Release 생성:
   - PO 환경 = `gh release create v0.6.0` 자동
   - PO 환경 = gh CLI 미설치 → 웹 수동 (https://github.com/.../releases/new?tag=v0.6.0)

## 사이클 종료 시 산출물 (B안 §0)
- `SUMMARY.md` 갱신 (지난 7일·commit·blockers·다음 사이클)
- `PROGRESS.md` 또는 `learnings.md` 갱신
- `CHANGELOG_NIGHT.md` 항목

## SKIPPED 처리
- 항목 모호 → `SKIPPED.md` 기록 → 다음 항목
- 외부 의존성 차단 → `SKIPPED.md` "PO 결정 필요" 기록
- 동일 P 3 사이클 연속 SKIPPED → STOP 조건

## STOP 조건 (영구·B안 §5)
1. 회귀 게이트 5 사이클 연속 위반
2. 자관 데이터 git 누설 시도
3. 본문 LLM 송신 시도
4. API 키 commit 시도
5. 우선순위 큐 모든 항목 SKIPPED
6. PO "STOP" / "PAUSE" 입력
7. 동일 P 3 사이클 연속 SKIPPED

## 7 사이클마다 META_REVIEW.md
- SUMMARY 7개 통합 분석
- 패턴·blocker·속도 회고
- 다음 7 사이클 전략

## v1.0.0 release gate (Cycle 28·B안 P28)
- 462 + 신규 테스트 0 fail
- eval-corpus-v1 회귀 ≤ 1pp
- mutation score builder/validator ≥ 85%
- librarian-judge advisory critical 0
- manual smoke (T2-1 demo) 30초
- v1.0.0 + 외부 학술지 1건 acceptance/게재

## 참조
- ADR 0025: Plan B 채택
- B안 §0~§5: 헤더·사이클 1·2·3+·invariants·STOP
- `learnings.md`: 사이클 사실 누적
