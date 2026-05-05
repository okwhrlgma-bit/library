# ADR 0036 — PAVR 슬래시 (P47) + Failure Replay (P48)

- 상태: Accepted (2026-05-06·Cycle 20A + 20B 통합)
- 일자: 2026-05-06
- 트리거: V2 §2 PAVR + §4 3-Tier Memory + §4.3 Failure Replay

## Context

### A. 모델 자체 검증 거짓 통과 (P47)
- V2 §2 PAVR = Plan→Act→Verify→Reflect 4단계
- "다 했어요" 거짓말 = Verify 결정론 셸 외부에서만 잡을 수 있음
- worktree 격리 + 결정론 verify + learnings 자동

### B. 실패 회귀 미검증 (P48)
- 새 모델 자동 업데이트 = 옛 실패가 다시 발생할 수 있음
- replay 디렉토리 = 재현 가능한 input·output·context
- 모든 replay = 새 모델/프롬프트 변경 시 자동 회귀 검사 (V2 §4.3)

## Decision

### 1. `.claude/commands/pavr.md` (P47)
- 슬래시 커맨드 = `/pavr <작업 설명>` 진입점
- Plan = 수용 기준 + 영향 파일 + 롤백 + verify 명령 목록
- Act = `git checkout -b pavr/<timestamp>` 격리
- Verify = ruff + pytest + binary_assertions + 자관 회귀 (eval_per_record_roundtrip --sample 50) + leak gate
- Reflect = 성공 시 PROGRESS (Stop hook 자동)·실패 시 learnings.md top-of-file 추가
- STOP 5건 (5회 verify 연속 실패·자관 누설·본문 송신·키 commit·사람 STOP)

### 2. `src/kormarc_auto/replay/` (P48·V2 §4.3)
- `store.py`
  * `FailureReplay` frozen dataclass (slug·title·failure_kind·failed_at·prompt·expected·actual·model·options·note·fixed_at·fix_commit)
  * `create_replay()` = 디스크 저장 (`{YYYY-MM-DD}-{slug}/input.json·expected.txt·actual.txt`)
  * `load_replay(slug)`·`iter_replays(since=date)` 순회
  * `run_regression(replay, actual_now)` → `ReplayResult` (exact match·substring match·diff)
- 4 failure_kind 권장 = regression / crash / wrong_output / injection
- ENV: `KORMARC_REPLAYS_DIR` (default = `~/.kormarc-auto/replays`)
- 17 tests passing

### 3. learnings.md 헤더 갱신 (V2 §4 정합)
- Warm Tier 명시·PAVR 실패 자동 추가
- Failure Replay 회귀 검증 안내
- 사실 9 (PAVR) + 사실 10 (Replay) 추가

### 4. STOP 조건 (V2 §11)
- KOLAS3 종료일 (2026-12-31) replay 등록 후 회귀 발생 = 즉시 STOP
- replay 디렉토리 손상 (input.json 누락) = 그 replay만 skip·log warning
- replay 자체에 시크릿 평문 = create_replay에서 차단 (Cycle 18A scan-secrets 정합)

## Consequences

### Positive
- 큰 작업 (refactor·migration) = `/pavr` 진입점으로 안전 자동화
- 자관 회귀 ≤ 1pp = 모든 PAVR commit 게이트
- KOLAS3 사실 (2026-12-31·1,296·확장형 별도) = replay 등록 후 영원히 회귀 차단
- 새 모델 출시 = 모든 replay 회귀 자동 = 침묵의 모델 변경 차단

### Negative
- PAVR 슬래시 = 작은 작업 overkill (1-2 파일 변경 = 직접)
- replay 디스크 = 1년 누적 시 수십 MB (ENV path로 분리 가능)
- 사람 검토 단계 = 5회 실패 후 = 빠른 사이클 저해 (의도적)

### Risk Mitigation
- create_replay = title 한국어 slug 안전 (pytest 통과)
- iter_replays = since=date 필터 (오래된 replay 제외)
- run_regression = exact / substring 2 통과 패턴 (false positive 차단)
- replay 디렉토리 손상 = JSON skip·log only (silent fail X = 명시 log)

## V2 정합 매트릭스

| V2 § | 본 ADR 적용 |
|---|---|
| §2 PAVR 4 단계 | ✅ `.claude/commands/pavr.md` |
| §2.4 결정론 verify | ✅ ruff·pytest·assertions·자관 회귀·leak |
| §2.5 Reflect 자동 학습 | ✅ learnings.md 자동 추가 (Stop hook 정합) |
| §4 3-Tier Memory | Hot=CLAUDE.md·Warm=learnings.md·Cold=replays/ |
| §4.3 Failure Replay | ✅ src/kormarc_auto/replay/store.py |
| §11 안전 체크리스트 | PAVR STOP 5 + replay 손상 silent skip |

## Alternatives Considered

### Alt 1: PAVR = Python script (CLI)
- Reject: 슬래시 커맨드 = Claude Code 자연 진입·Bash 호출 통합

### Alt 2: replay = SQLite
- Reject: 디렉토리 = git diff·인간 검토·복잡도 X

### Alt 3: run_regression = LLM judge
- Reject: 결정론 substring/exact match = 비용 0·V2 §2.4 결정론 정합

### Alt 4: replay TTL (90일 후 자동 삭제)
- Reject: KOLAS3 사실 등 영구 invariant = TTL X·필요 시 PO 수동 정리

## References

- 외부 자동화 V2 §2 PAVR + §4 3-Tier + §4.3 Failure Replay
- ADR 0028 결정론 (Verify 정합)
- ADR 0029 audit log (Reflect 정합)
- ADR 0034 hooks (Cycle 18A scan-secrets·post-format)
- ADR 0035 budget (회귀 진단 V2 §8.3 정합)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 20A+B 병행
