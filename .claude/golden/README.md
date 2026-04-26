# Golden Dataset — KORMARC 회귀 테스트

> PO 자율성 가이드 §11 (골든 데이터셋과 회귀 벤치) 적용.
> 검증된 KORMARC 정답 케이스 누적 → 매 commit 회귀 검출.

## 구조

```
.claude/golden/
├── case-001/                # 한 케이스 = 한 폴더
│   ├── input.json           # ISBN 또는 입력
│   ├── expected.json        # 기대 결과 (필드별)
│   ├── assertions.json      # 바이너리 어셔션 (true/false)
│   └── notes.md             # 출처·도서관 검증·주의사항
├── case-002/...
└── README.md
```

## assertion 형식

```json
{
  "case_id": "001",
  "isbn": "9788936434120",
  "assertions": [
    {"name": "title_exact", "field": "title", "op": "equals", "value": "작별하지 않는다"},
    {"name": "kdc_prefix", "field": "kdc", "op": "starts_with", "value": "813"},
    {"name": "008_length", "field": "_kormarc_008", "op": "length_eq", "value": 40},
    {"name": "isbn_check_passed", "field": "isbn_valid", "op": "equals", "value": true}
  ]
}
```

`op` 종류: `equals`, `not_equals`, `contains`, `starts_with`, `length_eq`, `length_ge`, `confidence_ge`.

## 실행

```bash
python scripts/golden_check.py                # 전체 케이스 평가
python scripts/golden_check.py --case 001     # 단일 케이스
python scripts/golden_check.py --strict       # 1개 실패 시 exit 1 (CI용)
```

## 누적 정책

- 사서 PILOT에서 **검증된 정답 KORMARC만** 추가
- 자동 추가 금지 — 사서 1인 이상 검토 후 수동 commit
- 케이스 폐기 시 `notes.md`에 deprecated 명시 (파일 삭제 X)
- 모델 업그레이드·Anthropic SDK 변경 시 회귀 즉시 감지

## 케이스 인덱스

| ID | ISBN | 표제 | 사서 검증 | 추가일 |
|---|---|---|---|---|
| 001 | 9788936434120 | 작별하지 않는다 | NL Korea API | 2026-04-26 |
| 002 | 9788932473901 | 태백산맥 1 | NL Korea API | 2026-04-26 |
| 003 | 9788983927774 | 우리가 빛의 속도로 갈 수 없다면 | NL Korea API | 2026-04-26 |

PO·베타 사서 PILOT 진행하면서 30~50건까지 누적 목표.
