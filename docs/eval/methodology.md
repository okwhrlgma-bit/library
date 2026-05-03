# Eval Methodology — kormarc-auto v0.6.0+ (B안 Cycle 1)

> 작성: 2026-05-04 (Plan B Cycle 1·ADR 0025)
> 목적: 단일 "99.82%" 폐기 → MARC 블록별 분리 정합표 + per-record round-trip 재현 가능 명세

## 1. 코퍼스

| 항목 | 값 |
|---|---|
| 코퍼스 ID | `PILOT-자관-2024` |
| 도서관 수 | 1관 (자관 PILOT) |
| 파일 수 | 174 .mrc files |
| 레코드 수 | 3,383 |
| 데이터 경로 | `D:\○○도서관\수서\2024\2024_마크파일\**\*.mrc` |
| 측정일 | 2026-05-03 (block coverage) + 2026-05-04 (per-record round-trip) |
| Git 등재 | X (.gitignore·자관 식별자 보호·익명 corpus는 v1 대체) |

### 익명 eval-corpus v1 (참고)
- 빌드: `scripts/build_eval_corpus_v1.py`
- 출력: `tests/fixtures/eval_corpus/v1/records.jsonl`
- 익명화: SHA-256 12-char (020 ISBN → `978+hash`·049 → `EVAL-CORPUS-1-{hash}`·9XX → `EVAL-LOCAL-{hash}`)
- 자관 식별자 leak: 0건 검증

## 2. 측정 지표

### 2.1 Block coverage (presence)
- 파일: `docs/eval/results/2026-05-03/per-block.json`
- 정의: 각 MARC 블록의 record 단위 presence 비율 (records_with_block / total_records × 100)
- 비고: 정확도 X·"있는가" 측정 (자관 정책 반영·1XX 0% = 자관 = 700 부출만)

### 2.2 Per-record round-trip exact-match
- 파일: `docs/eval/results/2026-05-04/per-record.json`
- 하니스: `scripts/eval_per_record_roundtrip.py`
- 정의: `bytes(rec.as_marc()) == bytes(MARCReader(decode).as_marc())` — encode → decode → re-encode 바이트 동일
- 단위: 레코드 1건 = 1 boolean (pass / fail with reason)
- 결과: 3,383 / 3,383 = **100.00% pass** (fail_reasons = `{}`)
- 의미: 파서·builder 무손실 입증 (입력 .mrc → 우리 modeling → 동일 .mrc 복원)

### 2.3 Regression baseline
- 파일: `docs/eval/results/2026-05-04/regression_baseline.json`
- 임계값: 다음 사이클 회귀 ≤ 1pp = PR 머지 통과·> 1pp = P0 격상

## 3. exact-match 정의 (subfield 단위)

본 측정에서 exact-match는 다음을 의미:
- subfield code + value (공백 양끝 strip 후 비교)
- indicator1 + indicator2 (공백 = " " 정규화)
- field tag (3-char ASCII)
- leader (24-char raw string)

normalization:
- 양끝 공백 strip (`(value or "").strip()`)
- 빈 indicator → " " (single space)
- 그 외 padding·encoding·field 순서 = 원본 유지

## 4. 정답 출처

본 measurement에서 "정답"은 자관 사서가 KOLAS·KORMARC KS X 6006-0:2023.12 정합으로 작성한 174 .mrc 파일 자체.
- AI 생성 ↔ 정답 비교 X (현 측정 = round-trip 무손실만)
- LLM extraction 정합률은 NL_CERT_KEY 발급 후 별도 측정 (P23·eval-corpus-v1 1,000건)

## 5. 재현 명령

```bash
# 자관 사이트 (D:\ 접근 환경)
python scripts/eval_real_disaggregation.py     # block coverage
python scripts/eval_per_record_roundtrip.py    # per-record round-trip

# 익명 corpus 사이트 (Git 안전·아무 환경)
python scripts/build_eval_corpus_v1.py
# → tests/fixtures/eval_corpus/v1/records.jsonl
```

## 6. 측정 환경

- Python 3.12.10 (Windows 11)
- pymarc (PyPI 최신)
- pytest 9.0.3
- ruff 검증 통과
- binary_assertions 39/39 (2026-05-03)

## 7. 한계 (정직 명시)

- **N=1**: 자관 1관 PILOT만 = 전국 일반화 X
- **자관 정책 반영**: 1XX 0% / 880 0% = 자관 = 700 부출 + 한자 자료 X (정상)
- **Round-trip ≠ extraction accuracy**: 무손실 직렬화는 입증·LLM 생성 정합률 X
- **외부 API 매칭 X**: NL_CERT_KEY·SEOJI 미발급 = 외부 정답 비교 보류
- **Cross-library X**: v0.7 = `kormarc-eval-corpus-v1` 1,000건 공개 예정 (P23 사이클 24+)

## 8. 단일 헤드라인 (가장 보수적 대표값)

> **자관 PILOT 1관·174 파일·3,383 레코드 round-trip 100.00% (B안 baseline)**

99.82% 단일 표시 = 모든 surface (README·landing·Streamlit·FastAPI·CLI·badges)에서 폐기.

## 9. 변경 이력

- 2026-05-03 c4914e2: 11-block coverage 첫 측정
- 2026-05-04 (Cycle 1): per-record round-trip + regression baseline + methodology
- 차기: 사이클 2 = offline demo 30초 회귀 + sample 5건 정답 비교

## 10. 참조

- ADR 0025 Plan B 무중단 자율
- B안 §1 Cycle 1 강제 산출물
- Hamel Husain "Your AI Product Needs Evals" (Level 1 binary assertions)
- Eugene Yan "Product Evals in Three Simple Steps"
- pymarc round-trip 패턴 = bytes equality

---

**작성**: Claude Opus 4.7 (1M context) · Plan B Cycle 1 · 자율
