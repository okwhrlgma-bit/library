# 야간 SKIPPED 항목

> Plan B §0 — 외부 의존성 부재·동일 P 3 사이클 연속 SKIPPED → STOP 조건

## Cycle 6 (P5 부분) — vhs GIF 생성 (2026-05-04)

- 항목: T2-5 vhs (charmbracelet/vhs) GIF 생성·.tape 작성
- 차단 사유: vhs 외부 도구 PO 환경 미설치 (`which vhs` = not found)
- 영향: README headline GIF 임베드 X·기능 영향 0
- 자동 복구: PO가 `winget install charmbracelet.vhs` 또는 `brew install vhs` 후 재시도
- 다음 사이클 = P5 잔여 (README.en.md) 진행 + vhs는 PO 외부 작업 등록

## Cycle 2 — GitHub Release 자동 생성 (2026-05-04)

- 항목: B안 §2 v0.6.0 release notes 자동 push
- 차단 사유: gh CLI PO 환경 미설치 (`which gh.exe` = not found)
- 영향: tag v0.6.0은 push 완료·release notes만 PO 수동
- PO 작업: https://github.com/kormarc-auto/library/releases/new?tag=v0.6.0
