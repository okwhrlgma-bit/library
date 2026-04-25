---
description: 단일 ISBN을 KORMARC로 변환
---

ISBN: $ARGUMENTS

```powershell
.\.venv\Scripts\Activate.ps1
kormarc-auto isbn $ARGUMENTS
```

또는 직접:
```powershell
python -m kormarc_auto.cli isbn $ARGUMENTS
```

결과 보고 형식:
- 사용된 데이터 소스 (NL Korea / 알라딘 / 카카오)
- 신뢰도 점수
- 채워진 필드 수
- 880 페어 개수
- 검증 통과 여부
- 저장 경로
- 출처 표시 의무 문구 (있다면)

캐시 히트면 그 사실도 명시 (비용 0원).
