---
description: 정답 데이터셋 자동 수집 + 정확도 측정 (NL Korea·KOLIS-NET 기반)
---

## Step 1 — 골든 수집 (1회, 또는 분기 1회)

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\build_golden_dataset.py
```

`tests/samples/golden/`에 `{ISBN}.mrc` + `{ISBN}.json` + `_index.csv` 자동 생성.
시드 ISBN 50건이 다양한 KDC 분포로 들어있음. 직접 ISBN 목록 쓰려면:

```powershell
python scripts\build_golden_dataset.py --isbns my_list.txt --limit 100
```

## Step 2 — 정확도 측정 (배포 전·코드 변경 후)

```powershell
python scripts\accuracy_compare.py --output reports\accuracy.json
```

각 ISBN을 우리 풀 파이프라인(aggregator + AI)으로 다시 만들어
NL Korea 직답(골든)과 필드별 비교.

기호:
- `✓` exact 일치
- `≈` partial (한쪽이 다른쪽 포함 — 공백·구두점 차이)
- `✗` 다름
- `○` 한쪽만 비어있음
- `·` 둘 다 비어있음 (정상 — 옵션 필드)

## 예상 출력

```
📊 필드별 일치율 (총 35건)
필드           exact  partial  mismatch  one_empty   both_empty
ISBN              35        0         0          0           0   (100%)
본표제            33        2         0          0           0   (97%)
저자              30        4         1          0           0   (91%)
출판사            34        1         0          0           0   (99%)
KDC               28        0         3          4           0   (80%)
```

KDC는 NL Korea 미부여 → 우리 AI 추천 → 차이가 정상적으로 발생.
사서 베타 시연 시 이 표를 보여주면 신뢰 입증.
