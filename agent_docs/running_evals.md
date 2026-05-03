# Running Evals (B안 P4)

> CLAUDE.md slim 정합 = 평가 측정 절차 상세는 본 파일.
> 핵심 인용: Hamel Husain "60-80% of dev time = error analysis + evals"·Eugene Yan 3-step.

## 1. 자관 174 파일 disaggregation (Cycle 1·매월·옵션)

### Block coverage
```bash
python scripts/eval_real_disaggregation.py
# → docs/eval/results/{YYYY-MM-DD}/per-block.json
```

### Per-record round-trip exact-match
```bash
python scripts/eval_per_record_roundtrip.py
# → docs/eval/results/{YYYY-MM-DD}/per-record.json + regression_baseline.json
```

### 결과 위치
- `docs/eval/results/2026-05-03/per-block.json` (block coverage)
- `docs/eval/results/2026-05-04/per-record.json` (3,383 / 100% pass)
- `docs/eval/results/2026-05-04/regression_baseline.json` (사이클 회귀 ≤ 1pp 게이트)

## 2. 익명 eval-corpus v1 빌드 (Git push 안전)

```bash
python scripts/build_eval_corpus_v1.py
# → tests/fixtures/eval_corpus/v1/records.jsonl
```

### 익명화 정책
- `020 ▾a` ISBN → `978+SHA-256[:12]`
- `049 ▾l` 등록 → `EVAL-CORPUS-1-{hash}`
- 9XX → `EVAL-LOCAL-{hash}`
- 자관 식별자 leak = 0건 (자동 검증)

## 3. Property-based tests (Cycle 4·B안 P3)

```bash
pip install -e .[dev]   # hypothesis 포함
python -m pytest tests/test_property_based.py tests/test_property_kormarc.py -q
```

### 12 invariants 검증
- Leader 24-char
- ISBN-13 EAN13 정합
- 부가기호 round-trip
- KDC ↔ DDC mapping
- Tenant scope consistency
- SLO p95 ≥ p50 (metamorphic)
- 008 = 정확히 40자리
- ISBN-13 020 ▾a 정합
- Builder 결정성 (동일 입력 = 동일 필드 수)
- pymarc bytes round-trip

## 4. Eval Level 분류 (Hamel Husain)

### Level 1 — Binary assertions (매 변경)
- `python scripts/binary_assertions.py --strict`
- 39/39 = 통과
- regex·JSON validity·구조 검사

### Level 2 — 인간 검토·LLM-as-judge (사이클·NL_CERT_KEY 발급 후)
- 자관 174 파일 + LLM 생성 비교
- 카테고리형 라벨 (확실/검토/불확실)·raw % X (헌법 #4)

### Level 3 — A/B in production (paid pilot 확보 후)
- v0.7+ = 사서 실 사용 데이터로 A/B
- privacy 우선·익명 corpus 우선

## 5. 회귀 게이트 (B안 §0)
- 자관 174 round-trip = ≤ 1pp 회귀 = PR 차단
- regression_baseline.json 비교 자동
- 5 사이클 연속 위반 = STOP 조건

## 6. v0.7+ eval-corpus v1 (B안 P23·1,000건 공개)
- 출처: NL Korea Open Catalog + KOLIS-NET 공개 + 정보나루 공개
- 장르·도서관 유형 stratify
- LICENSE: CC0 또는 NL Korea 정책
- arXiv preprint 초안 (B안 P28 v1.0 게이트 정합)

## 7. 한계 (정직 명시)
- N=1 자관 PILOT만 = 전국 일반화 X
- LLM extraction 정합 = NL_CERT_KEY 발급 후 별도 측정
- Cross-library = v0.7 eval-corpus-v1 1,000건 공개 후

## 참조
- `docs/eval/methodology.md` (Cycle 1 작성)
- `docs/research/part95-autonomous-cycle-summary-2026-05.md` (자율 사이클 요약)
