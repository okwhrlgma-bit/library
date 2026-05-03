# 알라딘 OpenAPI 컴플라이언스 정책 (2026-05-03)

> **출처**: 알라딘 OpenAPI 약관 (blog.aladin.co.kr/openapi/5353304)
> **결정**: ADR 0022 — Tenant-Owned Key (자체 키 위임) 모델
> **연관 분석**: Part 87 §4.3, §11 위험 매트릭스 #3

---

## 1. 약관 핵심 (인용)

알라딘 OpenAPI 이용 안내:
> "도서 판매 또는 도서 정보 기반 영리 서비스 이용 불가."

→ kormarc-auto = 상용 SaaS = **자체 TTBKey로 직접 호출 시 약관 위반 위험 (50%+)**.

---

## 2. 우리 솔루션: Tenant-Owned Key 모델

### 2.1 역할 분리

| 주체 | 역할 |
|---|---|
| **kormarc-auto (당사)** | 도구 제공자 (Tool Provider) |
| **도서관 (고객)** | 알라딘 TTBKey 자체 보유자 (Key Owner) |

### 2.2 작동 메커니즘

1. 도서관은 **알라딘에 직접 회원 가입** → TTBKey 발급 (1~2일·무료)
2. 도서관이 발급받은 키를 kormarc-auto에 등록 (per-tenant DB)
3. kormarc-auto 서버는 **도서관 키로 위임 호출**만 수행
4. kormarc-auto **자체 TTBKey는 보유·사용 X**

→ 알라딘 약관상 "도서관이 자기 데이터에 접근하는 도구를 사용"하는 정상 use case.

### 2.3 환경변수·설정

```bash
# kormarc-auto 자체 키 사용 X
ALADIN_TTBKEY_DEFAULT=  # 빈 값 (의도적)

# 도서관별 키 (per-tenant DB 또는 환경변수)
ALADIN_TTBKEY_PER_TENANT=true
```

도서관 등록 페이지에서 TTBKey 입력 → 자관 DB에 암호화 저장 → 호출 시 위임.

---

## 3. 폴백 우선순위 (Part 87 §4.1)

알라딘은 보강 옵션이며 **백본은 무료 공공 API**:

```
SCAN(EAN-13)
  → SEOJI API (1차·무료·공공누리) — 12 필드
  → data4library (KDC 056 보강·무료)
  → NL Open API (레거시 폴백)
  → 알라딘 (도서관 자체 키 위임만·505/520 보강)
  → Naver/Kakao (이중화)
  → 사진 OCR + LLM (모두 미스 시)
```

→ 알라딘 키 미발급 도서관도 **SEOJI/data4library만으로 12 필드 자동 채움 가능**.

---

## 4. 출처 표시 의무

알라딘 데이터 사용 시 **반드시** 다음 문구 표시:

> "도서 DB 제공 : 알라딘 인터넷서점(www.aladin.co.kr)"

위치:
- KORMARC 040 ▾c 또는 588 출처주기
- UI: 메타데이터 패널 하단
- export CSV/JSON: `attributions` 필드

코드 위치: `src/kormarc_auto/constants.py:ALADIN_ATTRIBUTION`.

---

## 5. 호출 한도 관리

| 항목 | 정책 |
|---|---|
| 일일 한도 | 5,000회 (도서관 키별 알라딘 정책) |
| 캐시 | `cached_get` HTTP cache (TTL 24h) → 실 호출 1/n |
| 폴링 X | KOLIS-NET 카피 카탈로깅 매칭 시 알라딘 호출 skip |
| 백오프 | 429 응답 시 즉시 폴백 (data4library) |

---

## 6. 영업·도서관 안내 카피

### 6.1 도서관 가입 step
1. 알라딘 OpenAPI 회원 가입 (https://blog.aladin.co.kr/openapi/popup/6695306)
2. TTBKey 발급 (블로그 등록 → 1~2일 승인)
3. kormarc-auto 자관 설정에 TTBKey 입력
4. 즉시 활성화

### 6.2 영업 메시지
> "kormarc-auto는 도서관님이 직접 발급받은 알라딘 TTBKey를 사용합니다.
> 따라서 도서관님이 알라딘 약관·일일 한도를 직접 통제하시며, kormarc-auto는 도구로만 동작합니다."

---

## 7. 위반 위험 vs 본 모델

| 시나리오 | 기존 (자체 키) | **본 모델 (위임)** |
|---|---|---|
| 알라딘 약관 위반 위험 | 50%+ | **0** ✅ |
| 알라딘 차단 시 영향 | 전 고객 동시 차단 | 해당 도서관만 영향 |
| 일일 한도 5,000회 | 전 고객 합산 (즉시 한도 초과) | **도서관별 5,000회 (실질 한도 ↑)** |
| 도서관 데이터 통제권 | kormarc-auto 보유 | **도서관 자체 보유** (lock-in 보강) |

---

## 8. 후속 작업

- [x] ADR 0022 작성 (2026-05-03)
- [x] `src/kormarc_auto/api/aladin.py` docstring 경고
- [x] 본 컴플라이언스 문서 작성
- [ ] 도서관 등록 UI에 TTBKey 입력 필드 추가 (M3 후속)
- [ ] per-tenant DB 스키마 (M5 멀티테넌시 시)
- [ ] 영업 자료 (`docs/sales/`) 정정 — "kormarc-auto 자체 키" 표현 제거

---

## 9. 출처

- 알라딘 OpenAPI 안내: https://blog.aladin.co.kr/openapi/5353304
- 알라딘 OpenAPI 신청: https://blog.aladin.co.kr/openapi/popup/6695306
- ADR 0022: `docs/adr/0022-aladin-tenant-key-delegation-2026-05.md`
- Part 87: `docs/research/part87-strategic-pivot-barcode-first-2026-05.md` §4.3
