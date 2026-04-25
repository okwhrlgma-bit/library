---
description: 품질 5축 종합 점검 (CLAUDE.md §6)
---

다음 5개 축을 각각 점검하고 종합 판정해주세요.

## 1. 정확성 (Correctness)
- `pytest -v` 통과 여부
- 골든 데이터셋과의 비교 (있다면)
- KORMARC 표준 준수 (008 길이 40, 245 필수, ISBN 체크섬)

## 2. 견고함 (Robustness)
- 모든 외부 API 호출에 try/except + timeout 있는가
- 부분 실패 시 다음 소스로 폴백되는가
- `tests/test_isbn.py`의 엣지케이스 (None, 빈 문자열, 잘못된 ISBN) 통과

## 3. 읽기 쉬움 (Readability)
- 함수 30줄 초과 없는가 (`grep -c def src/**/*.py`)
- 한국어 docstring 있는가
- `ruff check` 통과

## 4. 테스트 가능 (Testability)
- 외부 의존성 모킹 가능한 구조인가
- `src/kormarc_auto/kormarc/` 커버리지 80% 이상
- 결제 관련 코드 (해당 시) 90% 이상

## 5. 사업 적합성 (Business Fit) ★
- 이 변경이 사서가 실제 쓰는 기능에 기여하는가
- 권당 처리 시간 단축에 영향이 있는가
- KOLAS·DLS 호환을 깨뜨리지 않는가

각 축에 🟢/🟡/🔴 표시. 🔴 하나라도 있으면 종합 실패. 우선 수정 우선순위 1~3 제시.
