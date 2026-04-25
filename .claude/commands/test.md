---
description: pytest + ruff + mypy 일괄 실행
---

다음 명령을 순서대로 실행하고 결과를 보고해주세요.

```powershell
.\.venv\Scripts\Activate.ps1
ruff check src tests
mypy src
pytest -v --tb=short
```

각 단계 결과를 다음 형식으로:
- ruff: 통과/실패 (실패 시 위치)
- mypy: 통과/실패 (실패 시 위치)
- pytest: 통과 N개 / 실패 N개 (실패 시 케이스명)

마지막에 종합 판정. 실패가 있으면 우선 수정 제안 (Level 2).
