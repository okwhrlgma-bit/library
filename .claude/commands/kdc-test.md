---
description: KDC AI 분류 테스트 — NL Korea가 KDC 미부여한 ISBN
---

## 사용

KDC 미부여(또는 모호한) ISBN으로 호출:
```powershell
kormarc-auto isbn $ARGUMENTS --verbose
```

`[2/5] KDC 분류 추천...` 단계의 출력 확인.

## 기대 동작

1순위: NL Korea KDC 있으면 → 신뢰도 0.95 사용
2순위: ISBN 부가기호 매핑 → 신뢰도 0.40
3순위: Claude AI 호출 → 후보 1~3개 + 신뢰도 (0.0~0.85)

## 예시 ISBN

- `9788932020789` (김영하 작별인사 — KDC 있음)
- `9788936434120` (한강 작별하지 않는다)
- 자비출판/소규모 ISBN — AI 폴백 트리거

## 비용

- 캐시 히트: 0원
- 캐시 미스: 약 0.5원/건 (Sonnet 4.6 + prompt caching)
