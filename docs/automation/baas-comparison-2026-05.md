# BaaS·Auth·DB 10 옵션 비교 (Cycle 64·자동 도입 검토)

> PO 명령: "자동 도입 검토·다른게 더 좋나?"
> 기준: ₩0/월·자관 .mrc 안전·PIPA 정합·도서관 영업 친화·Phase 1 활성.

## 매트릭스 (10 옵션 × 7 기준)

| # | 옵션 | 비용 (Phase 1) | 자관 안전 | PIPA | 한국 호스팅 | 무료 한도 | 통합 시간 | 권장도 |
|---|---|---:|---|---|---|---:|---:|---|
| 1 | **streamlit-authenticator + yaml** | ₩0 | 🟢 (로컬) | 🟢 (외부 X) | 🟢 (PO 환경) | 무한 | 5분 | **★★★★★ Phase 1** |
| 2 | Supabase (Auth만) | ₩0 | 🟡 | 🟠 +6수신자 | 🔴 (US) | 50K MAU | 1시간 | ★★ Phase 2 |
| 3 | Supabase (전면) | ₩0 | 🔴 (자관 누설) | 🔴 | 🔴 | 500MB DB | 4시간 | ❌ 거부 |
| 4 | Firebase Auth | ₩0 | 🟢 | 🟠 +6수신자 | 🔴 (US) | 50K MAU | 2시간 | ★ Phase 2 |
| 5 | Auth0 | ₩0 | 🟢 | 🟠 +6수신자 | 🔴 (US) | 7K MAU | 2시간 | ★ Phase 2 |
| 6 | Clerk | ₩0 | 🟢 | 🟠 +6수신자 | 🔴 (US) | 10K MAU | 1시간 | ★ Phase 2 |
| 7 | AWS Cognito + Lightsail Seoul | ₩7K/월 | 🟢 | 🟢 (외부 858 §E) | 🟢 (Seoul) | 50K MAU | 4시간 | **★★★★ Phase 3 (자치구)** |
| 8 | NCP Cloud + Auth | ₩7K~/월 | 🟢 | 🟢 (CSAP 가능) | 🟢 (한국) | 다양 | 8시간 | ★★★ Phase 3 (공공) |
| 9 | PocketBase (self-host) | ₩7K/월 (Lightsail) | 🟢 | 🟢 | 🟢 (Seoul) | 무한 | 4시간 | ★★ Phase 2 (대안) |
| 10 | Appwrite (self-host) | ₩10K/월 | 🟢 | 🟢 | 🟢 (Seoul) | 무한 | 6시간 | ★★ Phase 2 (대안) |

## 자동 결정 (Cycle 64)

### Phase 1 (현재·사용자 0명·매출 0): **옵션 1 streamlit-authenticator + yaml**

```python
# 이미 일부 박제 (Cycle 21+)
import streamlit_authenticator as stauth
# 로컬 yaml = .streamlit/auth_config.yaml (gitignore)
# 비용 ₩0·자관 데이터 100% 로컬·외부 X
```

**이유**:
- 자관 PILOT 1관 = 사용자 = PO 본인 = Auth 단순 충분
- 외부 BaaS = PIPA §28의8 6수신자 추가 = privacy-policy v2 발행 의무
- 사용자 ≤ 5명 PILOT = 50K MAU 한도 의미 X
- Phase 2 (사용자 100+·사업자 등록 후) = Supabase Auth or AWS Cognito 검토

### Phase 2 (사용자 100~1,000·사업자 등록 후): **옵션 7 AWS Cognito + Lightsail Seoul**

**이유**:
- 한국 호스팅 = PIPA 정합·국외이전 6항목 추가 X
- 외부 858 §E (인프라) 정합·자치구 진입 시 CSAP 자체점검 가능
- AWS = 표준·도서관 RFP 통과 가능

**Supabase는 Phase 2에서 X 추천**:
- 미국 호스팅 = PIPA 정합 추가 비용 (privacy-policy v2·국외이전 6항목 박스)
- AWS = Lightsail Seoul + Cognito = 동일 무료 50K MAU + 한국 호스팅 = **Supabase 대비 우위**

### Phase 3 (자치구·공공 진입): **옵션 8 NCP Cloud + CSAP**

**이유**:
- 자치구·공공도서관 = CSAP 인증 필수 (외부 858 §I)
- NCP·NHN·KT·삼성SDS = 4 CSAP 사업자
- AWS Lightsail Seoul = CSAP 미적용·**자치구 진입 시 NCP로 마이그**

## 자동 결정 결과

```
Phase 1 (지금): streamlit-authenticator + yaml = ★★★★★
   ↓ (사용자 100+·사업자 등록 후)
Phase 2: AWS Cognito + Lightsail Seoul = ★★★★
   ↓ (자치구·공공 진입)
Phase 3: NCP Cloud + CSAP = ★★★
```

→ **Supabase = 모든 Phase에서 차순위·도입 X 권장**.

## 왜 Supabase가 차순위인가?

| 영역 | 우위 옵션 | Supabase 단점 |
|---|---|---|
| Phase 1 ₩0·자관 안전 | streamlit-authenticator | 외부 호스팅 = privacy v2 의무 |
| Phase 2 무료 + PIPA | AWS Cognito + Lightsail Seoul | 미국 호스팅 = 국외이전 6항목 |
| Phase 3 CSAP | NCP Cloud | CSAP 미적용·자치구 진입 X |
| 도서관 RFP | AWS·NCP | Supabase = 도서관 시장 인지도 ↓ |
| 설명 자료 | streamlit-auth (로컬) | 외부 SaaS = 도서관장 결재 부담 ↑ |

## 예외: Supabase가 적합한 경우

- 사서 개인 (B2C·Bottom-up PLG) = Phase 2 = 50K MAU 무료 = 사서 카페·SNS 통합 시
- 그러나 = 한국 도서관 본연 (학교·공공·자치구) = 한국 호스팅 우위

## 자동 진행 결과 (Cycle 64)

1. ✅ ADR 0047 = Draft → **Accepted (옵션 1 채택)**·Supabase = 미도입
2. ✅ Phase 1·2·3 stack 매트릭스 박제
3. ⏳ 토큰 폐기 권고 = PO 처리 (이미 "괜찮아" 답)
4. ⏳ Phase 2 = 사업자 등록 + 사용자 100명+ 시 = AWS Cognito 통합 검토 (Cycle 80+ 권장)

## 정직 헤더

본 비교 = **외부 자료 + 가격 표준** 종합·실 사용자 0명·인터뷰 0건.
Phase 2·3 결정 = 사업자 등록 + 인터뷰 5명 후 = 실 데이터로 재검증.

## 영구 invariant 12 후보 (V2 §11)

> **"자관 .mrc·사서 PII = 외부 BaaS Storage·DB 절대 X. Auth만 외부 BaaS 허용 (Phase 2+·PIPA §28의8 6수신자 갱신 의무). DB·Storage = AWS Lightsail Seoul (Phase 2) → NCP CSAP (Phase 3)."**

→ Cycle 65+ 박제 권장 (사업자 등록 후).
