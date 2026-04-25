---
description: ruff 자동 수정 + import 정렬 + 포맷
---

```powershell
.\.venv\Scripts\Activate.ps1
ruff check --fix src tests
ruff format src tests
```

수정된 파일 목록과 변경 내용을 요약 (Level 1 — 자율 실행).
