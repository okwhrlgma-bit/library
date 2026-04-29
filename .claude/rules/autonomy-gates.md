# 자율 운영 게이트

> 자율 commit이 안전하게 닫히기 위한 종료 조건·블래스트 반경.
> **2026-04-28 갱신**: 야간 자율 28 task / 26 신규 docs / 84 ADR / 자료 100% + D 100% 흡수 완료. 사업 5질문 rules 추가 (`business-impact-axes.md`).

## 야간 모드 품질 정책 (PO 정점 — 토큰·시간 고려 X)

**최우선 = 품질**. 토큰·소요 시간은 평가축 X.

| 항목 | 정책 |
|---|---|
| Opus 호출 | 평가축 부합하면 자유 (architect-deep·planner) |
| ADR 작성 | L3 이상이면 토큰·시간 고려 X, 무조건 작성 |
| code-reviewer 자문 | diff 50줄+이거나 외부 영향 시 매번 호출 |
| 작은 commit | 항상 우선 (큰 PR로 묶지 말 것) |
| 검증 | pytest·어셔션·골든·hook 모두 통과 후에만 commit |
| "충분" 자족 금지 | architect-deep·code-reviewer 자문 → 평가축 더 양수면 추가 작업 |

**사고·자기 비판 충분히** — 토큰 아끼는 응답·commit은 PO 평가에서 음수.

## 캐시카우 평가축 (PO 정점 목표)

**목표**: 사서 대상 자동화 앱 → **두면 계속 돈 버는 캐시카우**.

매 자율 commit은 다음 둘 중 하나 이상에 양수 영향이어야 함:
- §0 **사서 마크 시간 단축** (권당 8분 → 2분)
- §12 **사서 본인 예산 결제 의향 ↑** (캐시카우 직결)

평가축 음수면 commit 거부. 흥미·완성도·기술 호기심은 평가축 X.

캐시카우 측정:
- `scripts/aggregate_revenue.py` — 월별 매출·베타 사서·LOI 자동
- 200관 × 3.3만원 ≈ 월 660만원 = 캐시카우 도달 (Phase 3 목표)
- "두면 자동 결제" = 월정액 자동 차감 + PG 자동 결제 + PO 시간 0

## 종료 게이트 (이중)

매 자율 commit 직전 **둘 다 충족**해야 commit:

1. `pytest -q` 종료 코드 0 (전체 테스트 통과)
2. `scripts/binary_assertions.py --strict` 종료 코드 0 (현재 23/23)
3. **평가축 §0 또는 §12 양수 영향 (commit 메시지에 명시)**

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

## 5대 멈춤 패턴 사전 차단 (야간 자율 핵심)

| 패턴 | 미리 정의된 회피 행동 |
|---|---|
| 모호한 결정 (A vs B) | **더 안전·보수적 옵션 선택** + `DECISIONS.md` 기록 |
| 테스트 3회 실패 | `SKIPPED.md` 기록 + 다음 작업 |
| 자가 디버그 루프 | 작업당 30 iter 한계, 초과 시 다음 |
| 컨텍스트 한계·compact | 핵심 규칙은 CLAUDE.md (매 세션 로드) |
| 의존성 네트워크 실패 | 새 의존성 금지 + 오프라인 모드 우선 |

**원칙**: 자율성은 "막혔을 때 무엇을 할지"가 80%. 권한 0회보다 회피 정책이 더 중요.

## 사업 5질문 셀프 오딧 통합 (ADR 0013 PO 결정 후 active)

PO 사업 마스터 (2026-04-28) 흡수 → `.claude/rules/business-impact-axes.md` 작성 완료.

| 질문 | Beta 단계 가중치 |
|---|---:|
| Q1 결제 의향 | 40 |
| Q2 비용 | 25 |
| Q3 자산 | 15 |
| Q4 락인 | 10 |
| Q5 컴플 (별도 게이트) | 10 |

→ Q5 = FAIL → 즉시 폐기 (Q1·Q2·Q3·Q4 점수 무관). 컴플은 ARR이 아닌 **생존(survival) 조건**.

## 자료·D 드라이브 흡수율 게이트 (영업 신뢰성)

자관 PILOT 영업 시 인용 가능 자료:

| 자료 | 흡수 |
|---|---:|
| 자료 폴더 (PO 제공 + 자작 66) | **100% ✅** |
| D 드라이브 자관 87 항목 | **100% ✅** |
| .mrc 174 (자관 직접) | 4단 검증 정합 ≥99% 예상 |
| 6년 NPS (2018~2023) | 영업 신뢰성 ★ |
| 자관 사서 8명 페르소나 | 4 페르소나 자관 검증 가능 |

## 참조

- `learnings.md` — 누적 학습 (이번 세션 30+ 사실 active)
- `docs/adr/` — 큰 결정 84건 (이번 세션 0027~0084 = 58 신규)
- `docs/adr-priority-matrix-2026-04-28.md` — PO 결정 7 영역 차단점
- `docs/night-autonomous-session-2026-04-28-summary.md` — 종합 보고서
- `자료/MASTER_SYNTHESIS.md` — 8 source 통합 매트릭스
- `~/.claude/projects/.../memory/feedback_max_autonomy.md` — PO 자율성 지침
