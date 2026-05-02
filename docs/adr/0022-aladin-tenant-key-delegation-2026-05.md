# ADR 0022 — 알라딘 OpenAPI 자체 키 위임 모델 (2026-05-03)

## Status
Accepted (긴급)

## Context
알라딘 OpenAPI 약관 (blog.aladin.co.kr/openapi/5353304):
> "도서 판매 또는 도서 정보 기반 영리 서비스 이용 불가"

kormarc-auto = 상용 SaaS = **자체 TTBKey 호출 시 약관 위반 위험 (50%+)**.

Part 87 deep research (200+ 소스) 검증 결과 = 즉시 해결 필요.

## Decision
**Tenant-Owned Key (자체 키 위임) 모델로 즉시 전환:**

1. kormarc-auto = **도구 제공자**
2. 각 도서관 = **알라딘 TTBKey 자체 보유** (직접 발급·무료·1~2일)
3. 우리 서버는 도서관 키로 **위임 호출**만 수행 (kormarc-auto 자체 키 X)
4. 환경변수: `ALADIN_TTBKEY_PER_TENANT`
5. 또는 도서관 config (per-tenant DB)에 키 저장

## Consequences

### 긍정
- 약관 위반 리스크 0
- 도서관 일일 5,000회 한도 = 자관 호출만 사용 → 실질 한도 ↑
- 도서관 = 자기 데이터 통제권 보유 (lock-in 보강)

### 부정
- 도서관 신규 가입 시 알라딘 키 발급 단계 추가 (1~2일 대기)
- 키 미발급 도서관 = 알라딘 보강 정보 (505·520) 사용 불가 → 폴백 SEOJI/data4library 정합

### 후속
- `src/kormarc_auto/api/aladin.py` docstring 경고 추가 ✅
- 환경변수 `ALADIN_TTBKEY_PER_TENANT` 도입 (M3 시점)
- `docs/legal/aladin_compliance.md` 작성 (M9)
- 영업 자료 정정: "알라딘 키 = 도서관 직접 발급" 명시

## References
- 알라딘 약관: blog.aladin.co.kr/openapi/5353304
- Part 87 §4.3 (알라딘 위임 모델)
- Part 87 §11 위험 매트릭스 #3 (즉시·확률 50%+·영향 4/5)
