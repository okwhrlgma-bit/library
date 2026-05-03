# 알라딘 OpenAPI = 도서관 자체 키 발급 안내 (영업 자료)

> **U-87-1 응답** (PO 위임 자율 진행 2026-05-03)
> 알라딘 약관 = 상업 SaaS 자체 키 호출 금지 → 도서관별 자체 발급 모델

---

## 1. 도서관님께 (영업 카피)

**kormarc-auto는 도서관님이 직접 발급받은 알라딘 OpenAPI 키를 사용합니다.**

### 왜?
- 알라딘 약관: "도서 정보 기반 영리 서비스 사용 불가"
- kormarc-auto = 상용 SaaS = **도서관 자체 키 위임만 가능**
- 도서관 = 자기 알라딘 일일 한도 5,000회 통제권 100% 보유

### 도서관 입장 장점
- **약관 위반 리스크 0** = 도서관 직접 발급 = 정상 사용
- **일일 한도 ↑** = 다른 도서관과 합산 X = 자관 5,000회 단독
- **데이터 통제** = 알라딘 ↔ 도서관 직접 (kormarc-auto는 통과만)

---

## 2. 도서관 가입 step (5분)

### Step 1: 알라딘 회원 가입
- https://blog.aladin.co.kr/openapi/popup/6695306 접속
- 도서관 이메일·도서관명으로 가입
- 1~2일 승인 대기 (블로그 등록 필수)

### Step 2: TTBKey 발급
- 승인 후 OpenAPI 페이지 → "TTBKey" 발급
- 발급 키 복사 (예: `ttbXXXXXXXXX001`)
- 일일 한도 = 5,000회 (자관 단독)

### Step 3: kormarc-auto에 등록
- kormarc-auto 자관 설정 → "알라딘 TTBKey" 입력 → 저장
- 즉시 활성화 (재시작 불필요)
- 키는 자관 DB에 암호화 저장 (PIPA 정합)

### Step 4: 검증
- ISBN 1권 입력 → 알라딘 데이터 (505 목차·520 요약·표지) 자동 보강 확인
- 출처 표시: "도서 DB 제공 : 알라딘 인터넷서점(www.aladin.co.kr)" 자동

---

## 3. 도서관별 권장 시나리오

### 페르소나 02 (작은도서관 1인)
- TTBKey 발급 = 30분 (블로그 등록 1일 + 발급 5분)
- 일일 한도 5,000회 = 자관 신간 100~500권/월에 충분
- ROI: 권당 200원·연간 200만원·payback 1.2개월

### 페르소나 01 (사립 중학교 사서교사)
- 학교 행정실장 결재 = 30분
- TTBKey 발급 = 30분
- DLS 521 자동 분류 (BK/SR/NB/LR/ET) 활성화

### 페르소나 04 (사립대 분관)
- TTBKey 발급 = 본관 IT 부서 위임 가능
- Alma MARCXML 출력 (의학분관 holdings 852)
- DDC + MeSH + LCSH 3중 분류

### 페르소나 03 (P15 순회사서) — Phase 2-B
- 학교별 TTBKey 발급 (15~37개교 × 발급)
- 모바일 sync_api 통해 자관별 위임

---

## 4. 알라딘 키 미발급 도서관 옵션

알라딘 키 발급 X 도서관도 **kormarc-auto 정상 사용 가능**:
- SEOJI (NL Korea) = 1차 (12 필드 자동)
- data4library = KDC 보강
- 부가기호 디코더 = 0 API 호출 KDC 추출
- 알라딘 보강 (505·520) = 옵션 (필수 X)

→ 알라딘 키 = **선택**·없어도 KORMARC 12+ 필드 자동.

---

## 5. 약관 정합 (영업 신뢰)

### 우리 정합
- ADR 0022 = Tenant-Owned Key 모델 영구 결정
- 코드: `src/kormarc_auto/api/aladin.py` docstring 경고
- 법무: `docs/legal/aladin-compliance-2026-05.md`
- 자체 TTBKey 보유 X (검증 가능)

### 도서관 안전
- 약관 위반 시 알라딘 차단 = 우리 자체 키 X = 영향 0
- 도서관별 키 = 도서관 단독 차단 (다른 도서관 영향 X)

---

## 6. FAQ

### Q1. 도서관이 알라딘 키 없으면?
A. SEOJI·data4library·NL Open API만으로 12+ 필드 자동. 알라딘 = 옵션.

### Q2. 알라딘 키 발급 비용?
A. **무료**. 단 블로그 등록 + 1~2일 승인 대기.

### Q3. 도서관 직원이 비전공자라 어려우면?
A. kormarc-auto가 step-by-step 가이드 제공 (본 문서 + 화면 캡처).

### Q4. 일일 한도 5,000회 초과 시?
A. 알라딘 다음 날 자동 reset. 또는 알라딘 유료 플랜 (도서관 직접 결정).

### Q5. 키 분실 시?
A. 알라딘 OpenAPI 재발급 → kormarc-auto 자관 설정 갱신.

---

## 7. 영업 메시지 (콜드 메일·KLA 부스)

> "kormarc-auto는 도서관님의 알라딘 키로만 동작합니다.
> 우리는 도서관님의 데이터·키·예산을 절대 통제하지 않습니다.
> 알라딘 약관도 도서관님이 직접 준수하시며, kormarc-auto는 도구로만 동작합니다.
> 이 모델 = 약관 위반 리스크 0·도서관 데이터 통제권 100%."

---

## 출처

- ADR 0022 (`docs/adr/0022-aladin-tenant-key-delegation-2026-05.md`)
- 법무 (`docs/legal/aladin-compliance-2026-05.md`)
- 알라딘 약관 (https://blog.aladin.co.kr/openapi/5353304)
- Part 87 §4.3 (Tenant-Owned Key 모델)
