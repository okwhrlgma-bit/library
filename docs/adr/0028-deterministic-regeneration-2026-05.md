# ADR 0028 — 결정론적 재생성 (갈래 A Cycle 8 / P12 / T4-1)

- 상태: Accepted (2026-05-04·갈래 A 헤더 §0 정합)
- 일자: 2026-05-04
- 트리거: 갈래 A 헤더 P2 = "결정론적 재생성"·v0.7.0 종착 7건 중 #2

## Context

KORMARC 자동 생성에서 사서 신뢰 = 동일 입력 = 동일 출력. LLM 호출 시:
- temperature > 0 = 매번 다른 출력 = 사서 검토 의미 없음
- 모델 string 미pinning = 모델 자동 업데이트 시 회귀 발생
- 호출 메타 부재 = 재생성·진단·diff 검증 불가

기존 `kormarc/provenance.py`는 588 stamp + audit log 담당.
Cycle 8 = call-time 결정론 강제 + record metadata 부착 = 별도 모듈.

## Decision

### A. `src/kormarc_auto/llm/deterministic.py` 신설
- `DETERMINISTIC_TEMPERATURE = 0.0`·`DETERMINISTIC_TOP_P = 1.0` 상수 (변경 = ADR 필수)
- `get_pinned_model(tier)` = ENV override (`ANTHROPIC_MODEL_HAIKU/SONNET/OPUS`) + default
- `compute_input_hash(payload)` = SHA-256·dict 키 정렬 정규화
- `DeterministicCallParams` dataclass = `to_anthropic_kwargs()` + `attach_record_metadata()`
- `assert_deterministic_kwargs()` = 위반 즉시 ValueError (CI·hook 검증)

### B. `src/kormarc_auto/kormarc/record_metadata.py` 신설
- `build_record_metadata(input_payload, tier, deterministic_seed, extra)` = 메타 dict 빌드
- `attach_metadata_to_record_dict(record_dict, ...)` = `_meta` 키로 부착
- `verify_deterministic_consistency(meta_a, meta_b)` = 두 메타 비교 (model·input_hash·deterministic 동일성)

### C. 기본 모델 pinning
- HAIKU: `claude-haiku-4-5-20251001`
- SONNET: `claude-sonnet-4-6`
- OPUS: `claude-opus-4-7`
- ENV override 가능·default 변경 = ADR 필수

### D. 헌법 §9 추가 (CLAUDE.md)
> 9. 동일 입력 = 동일 출력 보장 (모델 pinning + temperature=0·top_p=1)

### E. tests/test_deterministic.py 회귀 게이트
- 29 tests passing (5 클래스 + Hypothesis property 3건)
- 입력 hash 안정성·모델 pinning·assert 위반 차단

## Consequences

### Positive
- 사서 검토 의미 회복 (동일 ISBN = 동일 KORMARC)
- 재생성 diff (Cycle 12 P16) = 모델 변경 vs 입력 변경 분리 가능
- prompt caching (T2-4) 효율 ↑
- 진단·debug = input_hash로 추적

### Negative / Trade-off
- 창의성 0 = 서지 생성에는 무관 (정확성·재현성 우선)
- 모델 자동 업데이트 X = ADR 사이클 필요 (의도적 friction)
- record dict에 `_meta` 키 추가 = downstream consumer 정합 필요

### Risk Mitigation
- `assert_deterministic_kwargs` = 위반 시 즉시 ValueError = silent fail 차단
- ENV override = 운영 중 모델 hotfix 가능
- existing `provenance.py` (588 stamp) 분리 보존 = 기능 중복 X

## Alternatives Considered

### Alt 1: temperature 0.3 default (소량 variability)
- Reject: 사서 신뢰 회복 = 정확한 재현성·variability = 검토 의미 상실

### Alt 2: 기존 provenance.py 확장
- Reject: provenance = 588 stamp + audit·deterministic = call-time 강제·관심사 분리 우월

### Alt 3: 모델 string hardcode (ENV override X)
- Reject: 운영 중 모델 hotfix 불가·ENV override = 보수적 default + 운영 유연성

## References

- 갈래 A 헤더 §0 P2 (Cycle 8)
- 헌법 §3 (외부 API timeout 10s 정합)
- 기존 ADR 0023 (LLM Provider Router)
- 기존 ADR 0025 (Plan B 무중단·결정성 invariant)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-04 · 갈래 A Cycle 8 · 자율
