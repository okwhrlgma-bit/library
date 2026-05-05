# ADR 0031 — Visible diff + Funnel 측정 (Plausible 호환)

- 상태: Accepted (2026-05-05·갈래 A Cycle 14A + 갈래 B Cycle 14B 통합)
- 일자: 2026-05-05
- 트리거: 갈래 A 헤더 P6 (visible diff) + 외부 매출 보고서 P34 (funnel)

## Context

### A. 재생성 시 무엇이 바뀌었는지 모름 = 사서 신뢰 저하 (P16)
- Cursor 2024-2025 forum 항의 = auto-apply 회귀 = per-field 표준화
- ADR 0028 결정론 = 동일 입력 → 동일 출력·이걸 검증하려면 diff 필요
- subfield 단위 diff = 사서가 정확히 어디 바뀌었는지 인지

### B. funnel 측정 부재 = 의사결정 인프라 0 (P34)
- ChartMogul·OpenView 2025 = 6단 funnel 표준
- Plausible self-hosted = no cookies·PIPA 정합
- 주간 리포트 자동 = PO 의사결정 5분 단축

## Decision

### 1. `src/kormarc_auto/diff/mrc_diff.py` 신설 (P16)
- `DiffEntry(diff_type, field_tag, subfield_code, before, after)` (frozen)
- `DiffSummary(entries)` + added/removed/changed 카운트 + to_api_dict()
- `diff_records(before, after)` = pymarc.Record 또는 dict 모두 지원
- `is_empty_diff(summary)` = ADR 0028 결정론 검증 게이트
- `format_diff_text(summary)` = CLI/email plain text (rich 없이도 동작)
- 12 tests passing (empty·added·removed·changed·control field·api dict·pymarc)

### 2. `src/kormarc_auto/analytics/` 신설 (P34)
- `events.py`
  * `EventName` Literal (10건)·`FunnelEvent` dataclass·`record_event` JSONL append
  * `_anon_id(email)` SHA-256 12자 hash·이메일 raw X·`@` 포함 X
  * 월별 파티션 (~/.kormarc-auto/analytics/{YYYY-MM}/events.jsonl)
  * EVENT_CATALOG 6단 = demo_start → signup → activation → quota_warning → upgrade_clicked → paid
- `funnel.py`
  * `FUNNEL_STEPS`·`FunnelMetrics`·`calculate_funnel(events, period)`
  * counts·unique_users·conversion % per step
  * `to_markdown()` = 표 형식
- `weekly_report.py`
  * `generate_weekly_report(events, now)` = 지난 7일 vs 직전 28일 평균
  * 자동 권고 (단순 규칙: demo_start=0 → SEO 점검·signup<10% → onboarding 점검 등)
- 18 tests passing (anon_id·event·calculation·weekly·PIPA compliance)

### 3. PIPA 호환 보장
- 이메일·이름·IP raw 송출 X
- 사용자 식별 = SHA-256 익명 hash
- 도서관부호 X·페르소나 ID X
- `test_event_no_email_in_jsonl` = 게이트
- `test_event_no_ip_field` = ip/user_agent 필드 자체 부재

### 4. 외부 매출 보고서 P34 STOP 조건 박제
- 사용자 식별자 (이메일·이름) 1건이라도 송출 = 즉시 STOP + 데이터 삭제
- GA4·Mixpanel 등 PIPA 처리방침 위탁자 추가 = P29 처리방침 동시 갱신 PR 없으면 STOP
- 본 모듈 = self-hosted JSONL only·외부 SaaS 송출 X (운영자 별도 추가 시 ADR)

## Consequences

### Positive
- 재생성 diff = 사서 통제감·결정론 검증·향후 모델 비교 가능
- funnel = 매출 의사결정 인프라·주간 5분 검토
- PIPA 정합 = §28의8 위탁자 추가 X = 처리방침 변경 부담 X
- self-hosted JSONL = 외부 SaaS 비용 X·라이선스 부담 X

### Negative
- 6단 funnel = 일부 미세 단계 누락 (예: photo_upload·feedback)
  → 필요 시 EventName Literal 확장 (ADR)
- 주간 리포트 자동 권고 = 단순 규칙·복잡한 코호트 분석 X
  → 추후 Plausible Stats API 통합 시 강화

### Risk Mitigation
- diff 비어있음 = 결정론 정합 = is_empty_diff 게이트
- funnel 익명화 = SHA-256·이메일·IP 송출 0건 회귀 테스트 박제
- record_event JSONL append-only·동시성 안전 (POSIX append)

## Alternatives Considered

### Alt 1: line-level diff (line_dict)
- Reject: subfield 단위가 KORMARC 도메인 자연스러운 단위·사서 인지 정합

### Alt 2: GA4 / Mixpanel SaaS
- Reject: PIPA 처리방침 위탁자 추가 부담·self-hosted JSONL 충분

### Alt 3: SQLite / PostgreSQL events
- Reject: append-only JSONL = 단순·diff 가능·복잡한 의존성 X·Cycle 9 audit store와 정합

### Alt 4: 12단 funnel (모든 이벤트)
- Reject: 6단 = ChartMogul/OpenView 표준·인지 부담 최소

## References

- 갈래 A 헤더 P6 visible diff
- 외부 매출 성장 보고서 (2026-05-05) P34 funnel·Plausible
- ADR 0028 결정론적 재생성 (diff 정합)
- ADR 0029 audit log·588 stamp (analytics와 분리: audit = 레코드 단위·analytics = 사용자 단위)
- ChartMogul 2026·OpenView 2025·Plausible self-hosted
- PIPC 결정 2024-010-184 (위탁자 누락 시정 선례 회피)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-05 · 갈래 A+B 병행 사이클
