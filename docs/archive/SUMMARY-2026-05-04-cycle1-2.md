# SUMMARY — Plan B Cycle 1+2 (2026-05-03 → 2026-05-04)

> B안 §0 영구 헤더 적용·ADR 0025 채택 후 Cycle 1+2 종료
> 다음 = Cycle 3 자동 전환 (P2 = T2-2 .bat 제거 + uv tool install)

## Cycle 1 — Per-block disaggregation publish (B안 §1·강제·완료)

산출물:
- `scripts/eval_per_record_roundtrip.py` (script only·자관 누설 0)
- `docs/eval/results/2026-05-04/per-record.json` (3,383 / 100% pass)
- `docs/eval/results/2026-05-04/regression_baseline.json` (사이클 회귀 ≤ 1pp 게이트)
- `docs/eval/methodology.md` (재현 가능 명세·N=1 한계 명시)
- 5 surface 정정: README·Streamlit·FastAPI `/accuracy`·CLI `info`·prefix_discover_app
- "99.82%" 단일 = 모든 surface 폐기

ADR 0025: Plan B 무중단 자율 채택 (ADR 0024 supersede)·invariants 2건만 보존

## Cycle 2 — T2-1 Offline demo finish (B안 §2·강제·완료)

산출물:
- `aggregator` `KORMARC_DEMO_MODE=1` 분기 (외부 호출 0건)
- `cmd_demo` 5건 자동·30초 timing·round-trip 회귀
- `tests/test_offline_demo.py` (5 tests passing)
- 결과: 5/5 records · 0.00s · round-trip 100%
- pyproject 0.5.0 → 0.6.0·`__init__.py` 0.6.0 정정
- git tag v0.6.0 push 완료

GitHub Release: `gh` CLI 부재로 PO 수동 생성 필요 (TODO PO-WEEK1-NEW)

## 게이트 통과 (B안 §0·둘 다 사이클)
- ruff check . = All checks passed
- pytest -q = 650 passed / 7 skipped
- binary_assertions = 39/39 (100%)
- 자관 174 파일 round-trip = 100% baseline
- 헌법 위반 = 0건
- 자관 git 누설 = 0건
- demo 30초 게이트 = 0.00s 통과

## Commits (Cycle 1+2)
1. c94cc74 — T2-2 console_scripts + T2-4 prompt cache + Part 95 + 39/39
2. a4ab145 — ADR 0024 (가드레일·이후 supersede)
3. e7d74f6 — Cycle 1 per-record + ADR 0025 + 5 surface
4. c292b6d — Cycle 2 offline demo finish + v0.6.0 bump
5. tag v0.6.0 → origin

## 다음 사이클 (Cycle 3 — 자동 전환)
- B안 §3 P2: T2-2 .bat 제거 + uv tool install
- 일부 완료 (console_scripts·ka alias)·잔여:
  - init·serve 서브커맨드 신설
  - .bat deprecation stub
  - README "uv tool install" 섹션

## Cycle 3 — P2 .bat deprecation + init subcmd (완료)
- `kormarc-auto init` 신규 (B안 P2)
- 안전 가드: 기존 .env에 키 1건이라도 있으면 --force도 거부
- start-all.bat: deprecation 안내 (기능 유지·v0.7+ 제거)
- README "빠른 시작": 30초 데모 + uv tool install
- ⚠ 자가 사고: init --force가 PO 키 3건 덮어씀 → 즉시 사용자_TODO에서 복구·가드 강화·learnings 사실 6
- commit: 1a4c019

## Cycle 4 — P3 Hypothesis 정식 통합 (완료)
- pyproject [dev] hypothesis>=6.150
- tests/test_property_kormarc.py 4 신규 class (008·ISBN·결정성·round-trip)
- 12 property tests passing
- 발견: builder가 \x1f (MARC delimiter) 입력에 round-trip fail (v0.7 backlog)
- commit: d736864

## Cycle 5 — P4 agent_docs/ 분할 (완료)
- agent_docs/kormarc_field_reference.md (KS X 6006-0:2023.12 필드)
- agent_docs/running_evals.md (Hamel 3-level eval)
- agent_docs/release_process.md (사이클 종료·v1.0 게이트·STOP)
- CLAUDE.md §9 참조 갱신·85줄 (60 ceiling 초과·v0.7 추가 슬림 검토)
- commit: 4898711

## 누적 메트릭 (Cycle 1~5)
- Tests: 662 passing / 6 skipped
- ruff: 0 errors
- binary_assertions: 39/39
- 자관 round-trip: 100% baseline
- CLAUDE.md: 85줄 (60 ceiling)
- agent_docs/: 4 파일 (1 백업 + 3 신규)
- v0.6.0 tag push 완료

## 다음 사이클 (Cycle 6 — Plan B P5)
- T2-5 이중언어 README + vhs GIF
- vhs (charmbracelet) 외부 도구 의존 = 일부 SKIPPED 예상
- 가능한 잔여: README.en.md 신설·README.md 한국어 검증
- 또는 P6 (T2-6 STATUS 단일 진실원) 우선

## PO 외부 작업 (TODO 등록·이번 세션)
- GitHub v0.6.0 Release 수동 생성 (https://github.com/kormarc-auto/library/releases/new?tag=v0.6.0)
- 사서 5명 cold outreach (외부 보고서 진단·보존)
- 청년 마음건강 신청 (1577-0199·1393)
- NL_CERT_KEY·ANTHROPIC_API_KEY 발급

## SKIPPED (없음·Cycle 1+2 강제 산출물 모두 완료)

## Stop Reason
- 없음·다음 사이클 자동 트리거

## PO 외부 작업 (TODO 등록)
- GitHub v0.6.0 Release 수동 생성 (`gh` CLI 미설치 환경)
  - https://github.com/kormarc-auto/library/releases/new?tag=v0.6.0
  - 노트는 본 SUMMARY + CHANGELOG_NIGHT v0.6.0 항목 인용

---

작성: Claude Opus 4.7 (1M context) · 2026-05-04 · Plan B Cycle 1+2 종료 · 무중단 자율
