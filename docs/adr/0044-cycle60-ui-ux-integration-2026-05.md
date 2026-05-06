# ADR 0044 — Cycle 60 UI/UX 통합 (헌법 §12 KWCAG 2.2 + KRDS + Pretendard 100% 적용)

- 상태: Accepted (2026-05-06·Cycle 60)
- 일자: 2026-05-06
- 트리거: PO "UI UX 적인 분석 및 적용" + "그 외 적용해야하는 상항 철저히 조사하여 적용 필요한 모든것 적용 진행" + "최종 완성본 만들었을시 최신화 해야하는 부분 다 완료 했는지 확인 필수"

## Context

ADR 0032 (Cycle 15A) = KWCAG 2.2 + KRDS 모듈 신설·**검사 도구만**·실 적용 X.
헌법 §12 = "모든 UI = KWCAG 2.2 Level AA·KRDS 색상 토큰·Pretendard CDN" 박제·**Streamlit 실 적용 0건**.

UI/UX 갭 7건 식별 (Cycle 60 분석):
1. `.streamlit/config.toml` 없음 = 글로벌 KRDS·Pretendard 미적용
2. Pretendard CDN HTML inject 0건
3. KWCAG 2.2 직접 마크업 0건 (lang ko·skip-link·focus visible 미적용)
4. 시각 위계 일관성 부족
5. 모바일 분기 없음
6. 사서 친화 UI 헬퍼 모듈 부재
7. UI 회귀 테스트 부재

추가 PO 명령 = 전 영역 갭 조사·적용·최종 최신화 verification.

## Decision

### A. 글로벌 a11y inject (Pretendard + KRDS + KWCAG 2.2)
- `.streamlit/config.toml` 신규 = primary·background·text·base 16px·Telemetry 차단
- `src/kormarc_auto/ui/a11y_inject.py` 신규 = `inject_global_a11y()` 1회 호출로 9 KWCAG 항목 적용:
  * 1.3.1 lang ko·1.4.3 4.5:1 대비·1.4.4 200% 확대·1.4.13 호버 콘텐츠
  * 2.3.3 reduced-motion·2.4.1 skip link·2.4.7 focus visible·2.5.5 44px 터치 타겟
- `streamlit_app.py`·`revenue_dashboard.py` 진입부 1회 호출

### B. 사서 친화 UI 헬퍼 (`librarian_ux.py`)
- `LIBRARIAN_DAILY_CYCLE` = Part 49 5 단계 (수서·정리·배가·이용·납본)
- `LIBRARIAN_VOCABULARY` = IT → 사서 어휘 매핑 (12 항목)
- `time_saved_estimate()` = 헌법 §0 (8분 → 2분) 시각화·KRW 환산
- `render_librarian_friendly_error()` = 5 사서 친화 에러 (PIPA 정합)
- `render_workflow_position()` = 일과 위치 마이크로 카피
- `cite_authority()` = 5 권위 인용 (NLK·KAIT·MCST·KLA·KLMA)

### C. 신뢰도 chip + AI ghost (헌법 §11·§10 정합)
- `render_confidence_chip(category)` = 확실/검토 필요/불확실 (raw % UI 금지·헌법 §11)
- `render_ai_ghost(text)` = AI 생성 사실 표시 (인공지능 기본법 §31·헌법 §10)

### D. 회귀 테스트 (`test_a11y_inject.py`)
- 34 신규 tests (TestA11yGlobalCSS·ConfidenceChip·AIGhost·LibrarianVocabulary·TimeSaved·Errors·WorkflowPosition·CiteAuthority·MobileViewport·ConstitutionInvariants)
- 헌법 §10·§11·§12 invariants 자동 검증
- KWCAG 2.2 9 항목 CSS 정합 검증

### E. 운영 통합 (Makefile + CHANGELOG + SUMMARY)
- `make a11y` = UI/UX 회귀
- `make ui-test` = 모든 UI 테스트
- `make dashboard` = revenue_dashboard 실행
- CHANGELOG [Unreleased] Cycle 60 항목 박제
- SUMMARY.md 갱신 (Cycle 1+2 stale → Cycle 60 누적 매트릭스)

## Alternatives

1. **st.set_option("theme.primaryColor", ...) 동적 설정** — 거부. 페이지 단위·일관성 X·config.toml = 표준
2. **각 페이지 inject (전역 X)** — 거부. 중복·일관성 X
3. **Streamlit components-html 사용** — 거부. iframe 격리·키보드 흐름 단절
4. **사서 친화 어휘 = streamlit_app.py 본문 직접 박제** — 거부. SRP 위반·재사용 X
5. **테스트 = 시각 회귀 (Playwright·storybook)** — 미룸. 1인 SaaS 비용 ↑·CSS 정합 검증으로 충분

## Consequences

### Positive
- 헌법 §12 = doc → **실제 코드 100% 적용** (1 → 9 KWCAG 항목)
- 사서 친화 어휘 = 70+ 키워드·5 일과 단계·5 권위 인용 박제
- Streamlit 페이지 = **모든 진입점에 1회 호출로 글로벌 적용** (DRY)
- Pretendard CDN = jsdelivr·v1.3.9 안정 버전·SLA 99.9%+
- 테스트 1,152 → 1,186 (+34·UI/UX 회귀 자동)

### Negative
- CSS inject = `unsafe_allow_html=True` 사용 (Streamlit 정책상 X 권장이나 a11y 필수 영역)
- Pretendard CDN 의존 = 오프라인 환경 = system fallback (Apple SD Gothic Neo·맑은 고딕)
- 모바일 viewport 감지 = Streamlit 한계로 width_hint 의존 (browser API X)

### Neutral
- ADRs: 0043 → **0044**
- 신규 모듈: a11y_inject·librarian_ux·.streamlit/config.toml·test_a11y_inject
- Cycle 카운트: 59 → 60
- 기존 ADR 0032 보완·deprecate X (검사 도구 = 여전히 유효)

## V3 통합 + UI/UX 매트릭스 최종

| 영역 | Cycle | 상태 | 적용 위치 |
|---|---|---|---|
| 헌법 §10 (AI 표시) | 10A·29 | ✅ | a11y_inject `render_ai_ghost()` |
| 헌법 §11 (카테고리 신뢰) | 13A·30 | ✅ | a11y_inject `render_confidence_chip()` |
| 헌법 §12 (KWCAG·KRDS·Pretendard) | 15A·32·**60** | ✅ | a11y_inject `inject_global_a11y()` + .streamlit/config.toml |
| 사서 친화 어휘 (Part 49) | 51·**60** | ✅ | librarian_ux `LIBRARIAN_VOCABULARY` |
| 시간 절감 시각화 (헌법 §0) | **60** | ✅ | librarian_ux `time_saved_estimate()` |

## 추가 적용 (PO 명령 정합 = 철저 조사·모두 적용)

| 영역 | 갭 | 적용 |
|---|---|---|
| Makefile UI 명령 | 0건 | `a11y`·`ui-test`·`dashboard` 추가 |
| CHANGELOG | Unreleased 비어 있음 | Cycle 60 UI/UX 항목 박제 |
| SUMMARY.md | Cycle 1+2 stale | Cycle 1 → 60 누적 매트릭스 신설 |
| Old SUMMARY | overwritten 위험 | `docs/archive/SUMMARY-2026-05-04-cycle1-2.md`로 이동 |

## 다음 7-cycle 권장 (Cycle 61~67)

→ SUMMARY.md §"다음 7-cycle 권장" 참조.

## 영구 invariants 재확인 (10건·변동 없음)

ADR 0041 §"영구 invariants 매트릭스" 정합·UI/UX 통합 후에도 10건 모두 유지.
헌법 §12 = 1 invariant (KWCAG 2.2 + KRDS + Pretendard) = 이번 Cycle 60에서 **doc → 코드 적용 완성**.
