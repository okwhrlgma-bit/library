# 모바일에서 Claude Code 쓰기 — "한번만 허용" 한계 우회

## 핵심 한계

**모바일 Claude 앱은 "항상 허용" 옵션을 보여주지 않습니다.** "한번만 허용" 또는 "거부"만 가능. 이건 앱의 UI 한계라서 우회만 가능.

## 우회 방법: 사전 등록

권한 요청이 뜨기 전에 `settings.json`에 미리 등록해두면 **아예 묻지 않고 자동 통과**합니다.

### 적용된 두 위치

| 위치 | 파일 | 적용 범위 |
|---|---|---|
| 전역 | `C:\Users\kormarc-auto\.claude\settings.json` | 모든 프로젝트 |
| 프로젝트 | `kormarc-auto\.claude\settings.json` | 이 프로젝트만 |

전역에는 **읽기 전용·정보 조회 명령**(`git status`, `ls`, `grep`, `python --version` 등)만 깔았습니다.
프로젝트에는 **개발에 필요한 모든 안전 명령**(`pip install`, `pytest`, `pnpm dev`, `git add/commit` 등)을 깔았습니다.

### 절대 차단 (deny) 목록

다음은 자동 차단되어 모바일에서 아예 실행 못합니다 — 안전을 위해:
- `rm -rf` / `Remove-Item -Recurse -Force` / `format`
- `git push --force` / `git reset --hard`
- `npm publish` / `pnpm publish`
- `.env` 파일 읽기·쓰기 (시크릿 보호)
- `curl ... | sh` (원격 스크립트 직접 실행)

## 모바일 사용 권장 흐름

1. **PC에서 시작**: 새 작업·복잡한 결정은 PC Claude Code로 시작 (Plan Mode 사용 권장)
2. **모바일은 모니터링·간단 응답**: 자리 비울 때 권한 프롬프트 응답용
3. **모바일에서 새 명령 막힘**: 그 명령을 PC에서 한 번 실행하면서 "Always allow"로 추가 → 다음부터 모바일에서도 자동 통과

## 새 명령이 자주 막히면

PC에서 `.claude/settings.json` 직접 편집하거나, Claude에게 다음과 같이 부탁:
> "방금 차단된 `XXX` 명령을 settings.json allow에 추가해줘"

## 모바일에서 절대 하지 말 것

- 큰 리팩토링 (UI에서 검토하기 어려움)
- 운영 배포 (Level 4 — PO가 PC에서 직접)
- API 키 입력 (모바일 키보드는 오타 위험)
- 결제 설정 변경
