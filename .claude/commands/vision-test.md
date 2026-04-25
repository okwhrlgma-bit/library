---
description: Claude Vision으로 책 사진 → KORMARC 테스트
---

## 사전 점검

```powershell
echo $env:ANTHROPIC_API_KEY  # 설정돼 있어야 함
```

## 사용

샘플 표지 사진(또는 PO가 직접 촬영한 사진) 1~3장 준비:

```powershell
kormarc-auto photo cover.jpg copyright.jpg
```

## 흐름

1. **바코드** (pyzbar) → ISBN 시도 → 성공 시 외부 API 보강
2. **Vision Stage 1** (Haiku 4.5, 저렴) → 표지에서 ISBN 텍스트
3. **Vision Stage 2** (Sonnet 4.6) → ISBN조차 없으면 종합 메타데이터

## 결과 예시 (성공)

```
📷 1장 분석...
✓ output/9788936434120.mrc (123 bytes)
```

## 비용 안내

- 바코드 성공: 0원
- Vision Stage 1만: 약 0.1원/장 (Haiku)
- Stage 2까지: 약 1.5원/장 (Sonnet)
- 30일 캐시 → 같은 사진 재호출은 무료
