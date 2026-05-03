# 도서관 정보나루 (data4library.kr) 가입·API 발급 가이드 (2026-05-03 조사)

> PO 명령: data4library.kr/joinPage 조사
> 출처: data4library.kr/joinPage·apiUtilization (직접 검증 2026-05-03)
> Part 87 §4.1 폭포수 2단계 (KDC 보강) 활성화 prerequisite

---

## 0. 한 줄 결론

> **PO 외부 작업 U-API-4 = 즉시 가능·무료·필수 입력 5개·1일 500건+ 시 서버 IP 등록 필요.**
> SaaS 상용 이용 = "도서관 사전 승낙" 필요·자체 키 1차 + 도서관 자체 키 위임 (알라딘 모델) 권장.

---

## 1. 가입 절차 (4단계)

1. **약관 동의** (이용약관 + 개인정보 수집·이용)
2. **회원가입 양식 작성**
3. **서비스 이용 신청**
4. **도서관 승낙 → 계약 성립**

---

## 2. 필수 입력 5개

| 항목 | 형식 | 비고 |
|---|---|---|
| 아이디 | 5~20자·영문 소문자·숫자·`_·-` | 소문자만 |
| 비밀번호 | 9~20자·영문/숫자/특수 조합 | 강함 |
| 이름 | 한국어 | PO 본인 |
| 이메일 | 표준 | 인증·발급 통보 채널 |
| 전화번호 | 휴대폰 | SMS 인증 가능성 |

## 3. 선택 입력 (호출 한도 따라 필수화)

| 항목 | 조건 |
|---|---|
| **서버 IP** | **1일 500건 이상 호출 시 등록 필수** |
| 사용기관명 | SaaS·도서관·기관 운영자 권장 |

→ kormarc-auto = SaaS 운영 시 IP 등록 권장 (서버 fixed IP 또는 VPC NAT)

---

## 4. API 발급 절차

```
회원가입 → 인증키 신청 → 인증키 발급 → API 활용
(4단계·정확한 승인 시간 명시 X·사례적 1일 이내)
```

---

## 5. 제공 API 종류 (kormarc-auto 활용)

| API | kormarc-auto 적용 |
|---|---|
| 도서관별 장서·대출 데이터 조회 | 자관 검수·중복 알림 |
| **인기대출도서 조회** | 사서 A 수서 결정 보조 |
| **추천도서 조회** (마니아·다독자) | 자치구 영업 자료·자료개발지침 §2 |
| **도서 상세 조회 + 키워드 목록** | KDC 056·650 보강·KDC waterfall §2 |
| 정보공개 도서관 조회 | 자관별 정책 자동 (library_specificity) |
| 대출반납 추이 분석 | 사서 C 통계 (annual_statistics) |

→ Part 87 §4.1 폭포수 2단계 (SEOJI → **data4library** → 부가기호 → 알라딘 → AI)
→ kormarc_auto/api/data4library.py 이미 구현·키만 입력하면 즉시 활성화

응답 형식: **XML**

---

## 6. 비용·한도

- **무료** (회원가입·키 발급·API 호출 모두)
- 일일 호출 한도 = 명시 X·**500건 이상 = IP 등록 필수**
- 한도 초과 정책 = 명시 X (libdata@korea.kr 문의)

---

## 7. 상업적 이용·SaaS 약관

| 항목 | 내용 |
|---|---|
| 상업적 이용 | "도서관의 **사전 승낙 없이** 정보를 상업 목적 사용 금지" |
| SaaS 가능성 | 약관 명시 X·사전 승낙 필요 (libdata@korea.kr) |
| 출처 표시 | 권장·약관 명시 X (관행적 "도서관 정보나루" 표기) |
| 재배포 | 약관 검증 필요 |

→ **kormarc-auto SaaS 권장 모델 = 알라딘과 동일 = Tenant-Owned Key 위임**:
- kormarc-auto = 자체 키 1차 (개발·체험)
- 도서관 = 자체 발급 키로 위임 호출 (상용 안전)
- ADR 0022 Aladin Tenant-Owned Key 모델과 정합

---

## 8. 가입 거부 사유

- 허위 정보 기재
- 타인 명의 도용
- 기타 가입 요건 미비

→ PO 본인 명의 가입 = 거부 위험 0

---

## 9. PO 작업 가이드 (5분)

### Step 1: 가입
1. https://data4library.kr/joinPage 접속
2. 약관 동의 (이용약관 + 개인정보)
3. 5개 필수 입력 (아이디·비밀번호·이름·이메일·전화)
4. 가입 완료

### Step 2: 인증키 신청
5. 로그인 후 → 마이페이지 → "인증키 신청"
6. 사용기관명 = "kormarc-auto SaaS (사서 출신 1인 PO)"
7. 사용 목적 = "한국 도서관 KORMARC 자동 생성·KDC 056·650 보강"
8. (서버 IP = 추후 배포 후 등록)

### Step 3: 발급 후
9. 발급된 키 = `.env`에 `DATA4LIBRARY_AUTH_KEY=<키>` 추가
10. 즉시 활성화 (kormarc_auto/api/data4library.py 자동 호출)

### Step 4: 상용 운영 시
11. libdata@korea.kr 메일로 SaaS 사전 승낙 요청 (선제적 정합)
12. 양식: "kormarc-auto SaaS·도서관 KORMARC 자동·도서관별 자체 키 위임 모델·출처 표기 의무 준수"
13. 응답 후 → 도서관 가입 시 자체 키 발급 안내 첨부

---

## 10. SaaS 영업 카피 (도서관 안내)

> "kormarc-auto는 도서관 정보나루 키를 도서관님이 직접 발급받아 사용합니다.
> 도서관님이 직접 가입(5분·무료) → 인증키 → kormarc-auto에 입력 → 즉시 활성화.
> 도서관님은 정보나루 약관·일일 한도를 직접 통제하며, kormarc-auto는 도구로만 동작합니다."

---

## 11. 위험·대응

| 위험 | 대응 |
|---|---|
| 일일 한도 초과 | 캐시 (TTL 24h)·로컬 DB 1차·정보나루 호출 최소화 |
| SaaS 약관 위반 | libdata@korea.kr 사전 승낙·도서관 자체 키 위임 모델 |
| 키 노출 | redaction middleware 자동 마스킹 (security/redaction) |
| 서비스 다운 | aggregator 폭포수 = NL Korea·알라딘 폴백 자동 |

---

## 12. kormarc-auto 통합 상태

- ✅ `src/kormarc_auto/api/data4library.py` 구현 완료
- ✅ `src/kormarc_auto/api/aggregator.py` 폭포수 2단계 통합
- ✅ `src/kormarc_auto/classification/kdc_waterfall.py` 정합
- 🚧 `.env` `DATA4LIBRARY_AUTH_KEY` = **PO 발급 대기**

---

## 13. 사용자_TODO 갱신

- ✅ U-API-4 (data4library AUTH_KEY) = 본 가이드로 5분 발급 가능
- 추가: U-API-4-LIC = libdata@korea.kr 상용 SaaS 사전 승낙 요청 (선택·영업 안전)

---

## 14. 출처

- https://data4library.kr/joinPage (회원가입 폼·약관 검증)
- https://www.data4library.kr/apiUtilization (API 활용 안내)
- libdata@korea.kr (고객센터·약관 문의)
- API 매뉴얼 다운로드: https://www.data4library.kr/downloadApiManual
- Part 87 §4.1 폭포수 정합

> **이 파일 위치**: `kormarc-auto/docs/sales/data4library-onboarding-2026-05.md`
> **다음**: PO 가입 → DATA4LIBRARY_AUTH_KEY 발급 → .env 입력 → kdc_waterfall 즉시 활성화
