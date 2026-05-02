# ADR 0021 — 사진 OCR → ISBN 바코드 우선 피벗 (2026-05-03)

## Status
Accepted

## Context
Part 87 (deep research 200+ 소스) 결론:
- 사진 OCR 1차 = 권당 5~15초 + LLM 비용 + KORMARC ≤2 필드 자동
- ISBN 바코드 + SEOJI 폭포수 = 권당 0.5~1.5초 + 무료 + KORMARC 12~15 필드 자동

PO 헌법 §0 (사서 시간) + §12 (결제 의향) 양축에서 단일 최대 ROI.

## Decision
**사진 OCR을 보조로 강등, ISBN 바코드 + SEOJI/data4library API를 1차로 승격.**

폭포수 아키텍처:
```
Scan(EAN-13)
  → SEOJI API (1차·무료) → 12 필드
  → data4library (KDC 056 보강·무료)
  → NL Open API (레거시 폴백)
  → 알라딘 TTBKey (도서관 자체 키 위임만·505/520 보강)
  → Naver/Kakao (이중화)
  → 사진 OCR + LLM (모두 미스 시)
```

부가기호 5자리 디코더 추가:
- EAN-13 add-on → KDC 1.5자리 (0 API 호출·100% 정확)
- SEOJI KDC 공백 (2020-12-31 이후) 즉시 해소

## Consequences

### 긍정
- 사서 권당 시간 8분 → 30초 (10× 가속)
- Anthropic 추론 비용 -60~80% (월 150~250만원 절감 추정)
- 660만원/월 캐시카우 도달 경로 압축
- KORMARC 020 ISBN 정확도 100% (EAN-13 체크디지트)
- 외국서 (CJK OCR 약함) 우위

### 부정
- HID 바코드 스캐너 신규 도입 시 7~30만원/창구 (도서관 부담)
- SEOJI/data4library API 의존 (캐시 >70% 적중으로 완화)
- 사진 OCR 모듈 개발 우선순위 ↓ (M3 완료 후 polish 단계로)

### 후속
- M3 모듈 (SEOJI/data4library 백본): 우선순위 P0★
- M7 모듈 (KOLIS-NET 카피 카탈로깅): 우선순위 P0★
- 마케팅 카피 변경: "사진으로 5초" → "바코드로 1초"

## References
- Part 87 §2 (바코드 vs OCR 비교표)
- Part 87 §4.1 (백본 폭포수)
- Part 87 §4.2 (부가기호 디코더)
