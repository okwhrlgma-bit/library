# 자율 운영 게이트

> 자율 commit이 안전하게 닫히기 위한 종료 조건·블래스트 반경.

## 종료 게이트 (이중)

매 자율 commit 직전 **둘 다 충족**해야 commit:

1. `pytest -q` 종료 코드 0 (전체 테스트 통과)
2. `scripts/binary_assertions.py --strict` 종료 코드 0 (16/16)

**완료 마커**: commit 메시지에 `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` 포함.

## 자율 액션 등급

| 등급 | 행동 | 게이트 |
|---|---|---|
| L1 | 오타·린트·docstring | 즉시 자율 |
| L2 | 새 모듈 + 테스트 | 이중 게이트 통과 |
| L3 | DB 스키마·외부 API 추가 | architect-deep 자문 + ADR 작성 후 |
| L4 | 결제·인증·운영 키 | **PO 수동 확인** — 자율 금지 |

## 비가역 액션 차단

`~/.claude/settings.json` deny 87종 + `.claude/hooks/irreversible-guard.sh` (PreToolUse) 정규식 이중 차단:

- `mkfs\.`·`dd if=.+of=/dev/`·`DROP (TABLE|DATABASE)`·`db\.dropDatabase\(`
- `git push.*--force`·`git reset --hard`·`git filter-branch`
- `rm -rf /`·`rm -rf ~`·`rm -rf \*`

## ADR 0009 §33 트리거 미충족 시

- `marc21_east_asian.py` ACTIVATED=False 유지
- 어셔션 §16이 회귀 즉시 검출
- 활성화는 PO 수동 PR + ADR 0009 트리거 3/3 충족 시에만

## 위험 신호 (자율 즉시 중단)

- 어셔션 통과율 80% 미만
- ruff 위반 누적
- git log에 `--no-verify`·`--force` 등장
- 사용자 PROMPT가 "stop"·"중단"·"멈춰"

## 참조

- `learnings.md` — 누적 학습
- `docs/adr/` — 큰 결정 9건
- `~/.claude/projects/.../memory/feedback_max_autonomy.md` — PO 자율성 지침
