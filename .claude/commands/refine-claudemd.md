---
name: refine-claudemd
description: 최근 30일 학습 패턴 분석 후 CLAUDE.md 개선 PR (자동 머지 절대 금지·사람 검토 필수)
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash(git:*), Bash(gh:*)
---

# refine-claudemd — V2 §6.1 자기 수정 (P50)

CLAUDE.md 자기 개선 워크플로우. **사람 명시 트리거만**·자동 cron 호출 금지.
시스템이 자기 안전장치를 풀게 두지 마라.

## 1. 분석

- `learnings.md` 최근 30일 항목 모두 읽기 (Stop hook이 자동 적재)
- 같은 패턴 3회 이상 반복 = 헌법 후보
- 현재 `CLAUDE.md` 헌법 §1~§12 검토
- 사문화된 규칙 = 최근 60일 위반·참조 0건 = 제거 후보

## 2. 제안 생성

```bash
git checkout -b auto/refine-claudemd-$(date +%s)
```

- `CLAUDE.md`에 추가할 규칙 작성 (3회+ 반복 패턴 기반)
- 사문화된 규칙 제거 (있다면)
- 커밋 메시지에 사유 명확히 (Conventional Commits = `docs(claude): refine §X·반복 패턴 N건 흡수`)

## 3. PR 생성

```bash
gh pr create --title "refine(claude): CLAUDE.md 자기 개선 (refine-claudemd)" --body "$(cat <<'EOF'
## 분석

- 분석 기간: 최근 30일
- 분석한 learnings 항목 = N개
- 반복 패턴 (3회+) = M개
- 사문화 규칙 후보 = K개

## 변경

### 추가
- §X (사유: 패턴 반복)

### 제거
- §Y (사유: 60일 미참조)

## 사람 검토 요청 포인트

1. <검토 포인트 1>
2. <검토 포인트 2>
3. <검토 포인트 3>

## 머지 방침

⚠️ **자동 머지 절대 금지**·PO 명시 승인 필수.
시스템이 자기 안전장치 (헌법) 를 풀게 두지 않는 V2 §6.1 정합.

EOF
)"
```

## 4. 보고

- PR URL 출력
- 사람이 검토 시 봐야 할 핵심 포인트 3줄

## STOP 조건

- 자동 cron 호출 시 = 즉시 중단 (V2 §6.1 핵심 원칙)
- 헌법 §0~§3 (정체성·헌법·평가축·HARD RULES) 변경 시 = PR 라벨 `critical` + 멘션 필수
- 영구 invariants (헌법 0·자관 누설 0) 변경 시 = STOP·PO 직접 ADR

## 정합

- ADR 0036 (PAVR + Failure Replay·learnings 정합)
- 외부 자동화 V2 §6.1 자기 수정 PR만
