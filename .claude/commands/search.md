---
description: 키워드/표제/저자로 검색 (ISBN 모를 때)
---

## 사용법

```powershell
kormarc-auto search "$ARGUMENTS"
```

예:
- `/search 한강 작별하지 않는다`
- `/search 김영하`
- `/search 서울대 출판`

## 폴백 순서

1. 국립중앙도서관 ISBN 서지 (한국 자료 1순위)
2. 알라딘 ItemSearch (상용)
3. 카카오 책 검색 (보조)

ISBN 기준 dedup + 신뢰도 정렬 → 최대 10건.

## 다음 단계

원하는 결과의 ISBN을 골라:
```powershell
kormarc-auto isbn 9788936434120
```
