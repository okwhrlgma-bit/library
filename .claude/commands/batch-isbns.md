---
description: ISBN 목록 파일 일괄 처리
---

파일: $ARGUMENTS (기본값: examples/sample_isbns.txt)

```powershell
.\.venv\Scripts\Activate.ps1
kormarc-auto batch $ARGUMENTS
```

결과를 docs/test_results.md 표로 추가:
- 총 건수
- 성공 / 실패 / 부분 성공
- 평균 신뢰도
- 자동 승인 가능 비율 (신뢰도 0.95 이상)
- 실패 ISBN 별도 섹션 (원인 분석)

문제 발견 시 (예: 특정 출판사 데이터가 일관되게 부족) 별도 이슈로 docs/known-issues.md에 추가.
