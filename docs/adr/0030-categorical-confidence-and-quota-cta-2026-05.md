# ADR 0030 — 카테고리형 신뢰 + 한도 알림·CTA

- 상태: Accepted (2026-05-05·갈래 A Cycle 13A + 갈래 B Cycle 13B 통합)
- 일자: 2026-05-05
- 트리거: 갈래 A 헤더 P5 (카테고리형 신뢰) + 외부 매출 보고서 P15·P33

## Context

### A. raw % 표시의 함정 (P15)
- 92.3% 같은 정량 = 거짓 정밀성·사서 혼란·표시광고법 실증 부담
- Hamel Husain eval principle = "binary > 1-5 scale > raw %"
- Anthropic 2025 evals research = 카테고리가 신뢰도 표현에 우월

### B. 한도 알림 부재 = 전환 손실 (P33)
- Mixpanel A/B = 가치 실현 순간 업그레이드 +32%
- Pendo 2025 = 행동 트리거가 시간 트리거 3.4x
- Knock+Orb 75% pre-warning + 100% block 표준
- 한국 학교·공공 = 결재선 24h grace 필수 (즉시 차단 시 거래 손실)

## Decision

### 1. `src/kormarc_auto/llm/confidence.py` 신설 (P15)
- `SIGNAL_WEIGHTS` 10건 (isbn_grounded·external_api_match·model_self_confidence·field_rule_based 등)
- `calculate_confidence(signals)` → `ConfidenceResult(category, top_signals=2)`
- 3 카테고리 = "확실" / "검토 필요" / "불확실"
- `to_chip_dict()` = UI 렌더링 (color: green/amber/red·icon: ✓/ⓘ/⚠)
- raw 점수는 내부 산정만·UI 노출 X
- `is_raw_percentage_in_text(text)` 게이트 헬퍼 = CI sweep용

### 2. CLAUDE.md 헌법 §11 추가
> 신뢰도 = 카테고리 (확실/검토 필요/불확실)·raw % UI/API/CLI 모두 금지

### 3. `src/kormarc_auto/quota/` 신설 (P33)
- `tracker.py`
  * `QuotaTracker(user_id·plan·monthly_limit·current_count)` 멱등 record_id
  * `state()` = normal / pre_warning(80%) / at_limit(100%) / grace(24h) / blocked
  * `start_grace()` / `reset_for_new_month()` / `usage_pct()` / `remaining_records()`
- `cta.py`
  * `personalized_upgrade_cta()` = 사용자 본인 데이터 기반·1.5배 안전마진 추천 플랜
  * `quota_warning_message()` / `quota_block_message()`
  * 다른 도서관 데이터 노출 X (CTA 게이트)

### 4. 임계값
- pre-warning = 80% (40/50건·외부 보고서 P33 표준)
- block = 100% (50/50건)
- grace = 24h (학교 행정실 결재 시간·즉시 차단 X)
- 다음달 1일 자동 reset
- 작은도서관 평균 신착 30-40권/월 = 50건 freemium 적정

## Consequences

### Positive
- 사서 정량 혼란 ↓ (확실/검토/불확실 = 즉시 판단)
- 표시광고법 정량 주장 회피 (raw % X = 실증 부담 X)
- Mixpanel +32% 패턴 = 한도 도달 시 전환 가능
- 24h grace = 학교 결재 시간 정합 = 거래 손실 차단

### Negative
- raw % 활용 사용 케이스 X (개발자 debug 시 SCORE 내부만)
- 24h grace = 100% 도달 후 추가 처리 = 정확한 손익 계산 어려움
- 카테고리 3종 = 미세 구분 불가 (의도적 단순화)

### Risk Mitigation
- `is_raw_percentage_in_text` regex sweep = CI에서 회귀 차단
- CTA 다른 도서관 데이터 노출 = 게이트 (`test_cta_does_not_leak_other_libraries`)
- ENV override = 운영 중 임계값 hotfix·default 변경 = ADR 필수

## Alternatives Considered

### Alt 1: 5 카테고리 (매우 확실/확실/검토/불확실/매우 불확실)
- Reject: 카테고리 3종 = 인지 부담 최소·Hamel binary 원칙 정합

### Alt 2: 100% 즉시 차단 (grace 0)
- Reject: 학교 행정실 결재 24h+ 필요·즉시 차단 = 거래 손실

### Alt 3: 한도 = 30건/월 (작은도서관 신착 평균)
- Reject: 50건이 작은도서관 + 학교 1주차 안전마진·30건은 너무 빡빡

### Alt 4: 60% pre-warning (더 일찍)
- Reject: Knock+Orb·Pendo 표준 = 80% (사서 알림 피로 회피)

## References

- 외부 매출 성장 보고서 (2026-05-05) P15·P33
- Mixpanel A/B (가치 실현 +32%)
- Pendo 2025 (행동 트리거 3.4x)
- Knock+Orb (75% pre-warning + 100% block)
- Slack 10K·Dropbox 2GB→4%·Spotify 26.6% 한도 설계
- Hamel Husain "Your AI Product Needs Evals" (binary 우월)
- ADR 0029 (audit log·588 stamp 정합)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-05 · 갈래 A+B 병행 사이클
