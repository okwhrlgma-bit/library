# ADR 0006 — Claude Code 권한 정책 (acceptEdits + ask + deny 3단)

**상태**: accepted
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

자율 디벨롭 루프에서 Claude Code 권한 prompt가 매번 뜨면:
- PO 시간 낭비 (매번 "y" 입력)
- 야간 자율 운영 불가 (PO 없으면 멈춤)
- 사서 영업 시연 중 prompt 노출 시 불신

옵션:
1. `defaultMode: "default"` — 매번 prompt (가장 안전, 매출 속도 ↓)
2. `defaultMode: "acceptEdits"` — 편집 자동, Bash·기타는 prompt
3. `defaultMode: "dontAsk"` — 모든 권한 prompt 스킵 (deny만 작동)
4. `defaultMode: "bypassPermissions"` — 검사 자체 스킵 (위험)

## 결정

**`defaultMode: "acceptEdits"`** + **3단 분류**:
- `allow` 32종 — 일상 안전 작업 (Read·Edit·Write·Glob·Grep + git/npm/python/pytest 등)
- `ask` 5종 — 외부 영향·비가역 (`git push *`·`git tag *`·`npm publish *`·`pip install *`·`winget install *`)
- `deny` 87종 — 절대 금지 (`rm -rf *`·`sudo *`·`force push`·`.env 읽기`·SSH 키 등)

## 결과

- 매 세션 prompt 횟수 **약 90% 감소** (편집·일반 Bash 자동)
- 위험·비가역 액션은 그대로 PO 확인 (ask)
- deny는 hook + settings 이중 차단 (config 우회 불가)
- 야간 자율 루프 가능 (claude-auto-retry + tmux 조합)

## 트레이드오프

✅ **장점**
- 자율 commit 흐름 차단 0회
- 사서 시연 중 prompt 노출 0회 (편집·git·python 모두 자동)
- 위험 액션은 100% 정책 차단 — 우회 불가

❌ **단점**
- `acceptEdits`는 잘못된 편집도 자동 적용 → fileCheckpointing(`/rewind`) 필수
- Bash 패턴은 `&&`·`;`·`|` 우회 가능 (공식 문서 경고) — 샌드박스 보강 필요
- `pip install *`은 ask인데 의존성이 자주 추가되면 흐름 끊김

## 완화 조치

- `fileCheckpointingEnabled: true` (~/.claude/settings.json) — 편집 전 snapshot 자동
- PostToolUse hook에서 매 commit 후 `binary_assertions.py` 자동 평가 → 회귀 즉시 검출
- WebFetch deny에 `localhost`·`127.0.0.1`·`0.0.0.0`·`169.254.169.254` (메타데이터 서비스 우회 차단)
- 의존성 추가는 일괄 처리 (PILOT 진입 후 `pip install -e .[ocr,labels]` 한 번)

## 우선순위 (공식 문서 기준)

managed > local > project > user (높음 → 낮음)
**deny 절대 우선** — allow에 같은 패턴 있어도 deny가 이김.

## 6개월 후 되돌릴 수 있는가?

**Y** — defaultMode 변경 즉시 효력. 베타 50명 도달·외부 결제 처리 시작 시 `default`로 회귀해 매 prompt 받기 가능.

## 관련 자료

- `~/.claude/settings.json` — 사용자 전역 권한 (이 ADR의 적용 위치)
- `.claude/settings.json` — 프로젝트 권한 (기본 PO 작업 폴더만 허용)
- `.claude/settings.local.json` — 향후 PO 개인 오버라이드 (gitignore)
- 공식 문서: https://code.claude.com/docs/en/iam
