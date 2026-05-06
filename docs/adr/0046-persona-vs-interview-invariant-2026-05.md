# ADR 0046 — 영구 invariant 11: 페르소나 시뮬 ≠ 실 사서 인터뷰

- 상태: Accepted (2026-05-06·Cycle 61 마무리)
- 일자: 2026-05-06
- 트리거: PO "더 조사할거" + Cycle 61 정직 진단 정합

## Context

Cycle 1~61 누적:
- 74 페르소나 (Part 60)·8 ICP 깊이 (Part 96·Cycle 61)
- 페르소나 시뮬 56% 전환 (Part 51)·92.5점 PMF (Champion 4/4)
- **사서 5명 인터뷰 (`SALES-1`) = 0건**

외부 901 보고서 진단 (메모리 박제):
- identity fusion·productive avoidance·agent pace inflation·domain expert curse
- **시뮬 ≠ 실 검증** = 패턴 재발 방지 영구 invariant 필요

## Decision

### 영구 invariant 11 박제

> **"페르소나 시뮬 결과는 영업 메시지 후보·인터뷰 가설 우선순위로만 사용. PMF 결정·가격 확정·기능 우선순위 변경 = 사서 5명 이상 실 인터뷰 후. 시뮬 결과 인용 시 = 정직 헤더 (시뮬·가설·인터뷰 N건) 명시 의무."**

### 적용 범위

1. 모든 페르소나 시뮬 코드 (`src/kormarc_auto/personas/`)
   - `render_persona_summary()` = "⚠ 가설·시뮬·인터뷰 0건" 헤더 영구
   - 외부 인용 시 = "Cycle 61 시뮬·실 검증 X" 명시
2. 모든 페르소나 doc (`docs/research/part*persona*`)
   - 첫 줄 = 정직 헤더 의무
3. 영업 메시지 (`docs/sales/persona-message-matrix-*`)
   - "메시지 후보·인터뷰 후 검증" 헤더 영구
4. PMF 결정 (가격·기능 우선순위)
   - 인터뷰 0건 = 결정 X·후보만
   - 인터뷰 5+건 = 결정 가능·인터뷰 N 명시

### 인용 표준 형식

```markdown
> **정직 헤더**: 본 문서 = Cycle 61 페르소나 시뮬·인터뷰 N건·실 검증 [완료/진행중/미진행].
> PMF 결정 = SALES-1 사서 5명 인터뷰 후.
```

## Alternatives

1. **invariant 박제 X·문서 권장만** — 거부. 외부 901 보고서 4중 패턴 = 영구 위반 위험
2. **시뮬 결과 사용 금지** — 거부. 가설 우선순위 도구로는 유용
3. **인터뷰 1명 후 활성** — 거부. 통계 의미 부족 (n≥5 표준)

## Consequences

### Positive
- 외부 901 보고서 4중 패턴 재발 방지·**영구 게이트**
- 페르소나 시뮬 = 가설·인터뷰 = 검증·역할 분리 명시
- PO·미래 사이클 자동 방어 (시뮬 단독 결정 X)

### Negative
- 모든 페르소나 doc·코드 = 정직 헤더 추가 의무 (1회 박제 후 유지)
- PMF 결정 지연 = 사서 5명 인터뷰 = 1주 시간

### Neutral
- ADRs: 0045 → 0046
- 영구 invariants: 10 → **11**
- Cycle 61 정직 진단 영구화

## Related ADRs

- ADR 0024 솔로 PO 가드레일 (외부 901 출처)
- ADR 0025 Plan B 무중단 자율 (가드레일 supersede)
- ADR 0030 카테고리형 신뢰 (raw % 금지·정직 표시)
- ADR 0044 UI/UX 통합 (헌법 §12)
- ADR 0045 12 추가 고려 영역

## 영구 invariants 매트릭스 갱신 (11건)

1. 헌법 위반 0건
2. 자관 데이터 git 누설 0건
3. 결정론 (ADR 0028)
4. AI 출처 표시 (ADR 0029)
5. 카테고리형 신뢰 (ADR 0030)
6. KWCAG 2.2 (ADR 0032)
7. KOLAS3 종료일 = 2026-12-31 (ADR 0026)
8. 야간 자율 = cost_supervisor 래핑 (ADR 0041)
9. budget-cap-precheck.sh exit 2 우회 금지 (ADR 0041)
10. audit.jsonl append-only·직접 편집·삭제 금지 (ADR 0041)
11. **페르소나 시뮬 ≠ 실 인터뷰·정직 헤더 명시 의무 (ADR 0046·이번)**

## 게이트 (Cycle 62+ 강제)

매 페르소나 관련 문서·코드 = 다음 검증 통과 필수:
1. "시뮬"·"가설"·"인터뷰" 키워드 1+ 포함 (정직 헤더)
2. PMF·가격·기능 결정 = 인터뷰 N건 명시
3. tests/test_deep_personas.py `TestConstitutionInvariants` 정합

## STOP 조건 추가 (V2 §11)

페르소나 시뮬 단독으로 PMF 결정 시도 = 즉시 STOP·PO 알림.
