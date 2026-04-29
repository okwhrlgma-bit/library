# ADR 0012 — Always Night Mode 공식화

**Status**: Accepted (supersedes ADR 0010 §3 day/night toggle)
**Date**: 2026-04-27
**의사결정자**: PO
**6-Dim Scores**: os=+1 data=+2 security=+1 deps=0 rollback=+2 observability=+1 (TOTAL=+7)

## 컨텍스트

직전 21.5시간 단일 작업에서 commit 0건·실 산출물 0건 사고 발생 (`STATUS_REALITY_CHECK.md` 4번 항목). PO 1인 운영에서 "주간/야간" 토글은 PO 부재 감지 → 모드 전환 로직을 유발하며, 이는 PO 가이드 5대 멈춤 패턴 §1·§3과 충돌. 또한 야간 토글이 별도 개념으로 존재하면 효율·안전 가드를 야간 한정으로 적용하려는 유혹이 발생.

PO 마스터 명령서 (2026-04-27) §0.1·§0.4 명시 결정: 운영 모드는 단일 ALWAYS_NIGHT.

## 결정

운영 모드는 `ALWAYS_NIGHT` 하나로 단일화. 시간대·PO 재실/부재 무관하게 항상 활성.

### 제거되는 개념

- "주간 모드"·"야간 모드" 구분 (settings.json 키·CLI 토글·UI 모두)
- "PO 부재 감지" 트리거로 모드 전환하는 로직
- 야간 한정 위험 행동 게이트 (`logs/halt_reasons/`·night.log 등 야간 한정 명칭)
- ADR 0010 §3 day/night toggle 절 (supersede)

### 대체 가드 (모드 무관·상시 적용)

1. **효율 게이트 5종** (`.claude/rules/efficiency-gates.md`, Part M-4) — 토큰/커밋·시간당 커밋·어셔션 회귀·단일 작업 시간·의존성 추가 빈도
2. **6차원 안전 평가** (Part D) — 외부 도구·라이브러리·서비스 도입 시 점수 합계 ≥ +6
3. **ADR 사전심의** — L3 등급 결정은 ADR 발행 후만 진행
4. **비가역 행동 차단** — 결제·force push·DB drop·외부 송신은 모드 무관 항상 ADR + ask 권한
5. **Opus 4.7 토크나이저 인플레 보정** — effort=low 기본·캐시 활용·코드 생성 Sonnet 4.6 라우팅 (Part F)

## 결과

### 긍정

- 운영 모드 의사결정 단일화로 컨텍스트 오버헤드 감소
- 효율 게이트가 13시간 무한 작업 사고 자동 차단 (게이트 1: 분당 10토큰 미만 60분 누적 → 즉시 중단)
- ADR 0010의 야간/주간 분기 코드 제거 → SLOC 약 50줄 감축
- 효율 게이트가 모든 자율 commit에 일관 적용 → 사고 재발 방지

### 부정

- 야간 한정 보수 모드 (acceptEdits)에서 더 보수적 정책으로 자동 전환 옵션 손실 — 효율 게이트로 대체하지만 trade-off 존재
- 단일 모드라 PO가 명시 잡 휴식 시간이 없음 (효율 게이트는 시간 무관 — 의도)

### 위험

- 효율 게이트가 정상 작업도 차단 가능성 — 임계값 튜닝 1주 PILOT 필요
- "야간"이라는 명칭이 헌법·룰·코멘트에 잔존 시 혼란 → grep으로 삭제 의무

## 검증

- ADR 0010 §3 절 supersede 표기 (`docs/adr/0010-night-autonomous-setup.md`) 후 git grep으로 "주간"·"야간 토글"·"day/night" 키워드 0건 (헌법·룰 한정)
- `~/.claude/settings.json`에서 night_mode 관련 키 archive
- `.claude/rules/autonomy-gates.md`에 야간/주간 구분 절 모두 삭제 + supersedes ADR-0012 명시
- 효율 게이트 5종 (M-4) 도입 후 13시간 사고 시뮬레이션 — 60분 시점에 자동 중단 확인

## 롤백

본 ADR 폐기 시:

1. `docs/adr/0010-night-autonomous-setup.md` §3 day/night toggle 절 git revert
2. `~/.claude/settings.json` env에서 시간대 가드 (TZ 등) 복원
3. `.claude/rules/autonomy-gates.md` 야간/주간 분기 절 복원
4. 효율 게이트 5종은 보존 (모드 무관 가드)

폐기 트리거: 효율 게이트 false-positive 비율 > 20% 1개월 이상 지속 시 PO 검토.

## 참조

- `STATUS_REALITY_CHECK.md` (2026-04-27 21:30 KST) — 13h 사고 사후 분석
- PO 마스터 명령서 (2026-04-27) §0 항시 야간모드 + Part M-4 효율 게이트
- ADR 0010 (supersedes §3) — 3단 운영 모드 일부
- `learnings.md` 5대 멈춤 패턴 (PO 가이드)
