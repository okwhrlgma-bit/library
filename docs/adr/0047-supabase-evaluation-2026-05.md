# ADR 0047 — Supabase 도입 검토 (Cycle 64)

- 상태: **Accepted (Cycle 64·옵션 A 채택·Supabase 미도입)**
- 일자: 2026-05-06
- 트리거: PO Supabase 토큰 발급 + "자동 도입 검토" + "다른게 더 좋나?"
- 결정: **자동 검토 결과 Supabase 모든 Phase에서 차순위·미도입 권장**

## Context

PO가 Supabase Personal Access Token (`sbp_*`) 발급·채팅 노출 → 즉시 폐기·재발급 권고.
Supabase = BaaS (Backend-as-a-Service)·Auth + DB + Storage + Edge + Realtime.

**현재 stack** (Cycle 63·ADR 0026·0044):
- GitHub Pages (정적·도메인 X·₩0)
- Streamlit Community Cloud (앱·₩0·secrets 박스)
- GitHub Actions (cron·₩0)
- 자관 .mrc = 로컬·git X (영구 invariant 2)

**Supabase 불필요 영역**:
- DB = 현재 자관 .mrc = 로컬 → Supabase = 불필요
- Realtime = Streamlit auto-rerun = 충분
- Storage = `.mrc` = 자관 누설 게이트 (헌법 §3·invariant 2) = **금지**

**Supabase 잠재 사용 영역**:
- Auth (사용자 로그인) = 현재 streamlit-authenticator 대체 가능 (50K MAU 무료)
- Edge Functions = GitHub Actions로 대체 가능
- 사업자 등록 후 = 다중 자관 PILOT 시 = DB 필요 가능성 ↑

## Decision (Draft·PO 결정 대기)

### 옵션 A: Supabase 미사용·토큰 폐기
- 현재 stack 충분·DB·Auth 모두 무료 대안 보유
- 권장 (Phase 1)

### 옵션 B: Supabase Auth만 도입 (50K MAU 무료)
- 사용자 로그인 무료·streamlit-authenticator 대체
- PIPA §28의8 = 6수신자 갱신 필요 (현재 5: Anthropic·AWS·PortOne·Google·Cloudflare → +Supabase)
- 사업자 등록·privacy-policy v2 발행 의무
- ADR 0026 §F (영업 채널) 와 통합 필요

### 옵션 C: Supabase 전면 도입
- DB + Auth + Storage + Edge
- ❌ Storage = 자관 누설 위험 (invariant 2)
- ❌ DB = PIPA §28의8 + 자관 데이터 외부 호스팅 = 거부
- **거부**

## Alternatives (현재 stack 유지 시)

1. **streamlit-authenticator** = Auth (이미 일부 박제·Cycle 21+)
2. **GitHub OAuth** = Streamlit Cloud 자동 통합·무료
3. **로컬 SQLite** = DB 필요 시 (PILOT 5관 미만)
4. **PostgreSQL on AWS Lightsail** = 매출 후 (외부 858 §E)

## Consequences

### Positive (옵션 B 채택 시)
- 50K MAU 무료 = 사서 수만 명 가능
- Auth + JWT + RLS = 무료
- Edge Functions = GitHub Actions 대체

### Negative
- PIPA §28의8 6수신자 갱신 필요 (privacy-policy v2)
- Supabase = 미국 호스팅·국외이전 추가 (PIPC 시정 위험·외부 858 보고서)
- 토큰 관리 = .env + Streamlit Cloud secrets 동시 = 중복 위험
- 자관 데이터 절대 X (invariant 2)

### Neutral
- 토큰 = .env에만·env override 표준
- 실 통합 = PO 결정 후·현재는 scaffold만

## scaffold (PO 결정 X 시 = env read만)

```python
# src/kormarc_auto/auth/supabase_client.py (Cycle 64+ 권장)
import os
from typing import Optional

def get_supabase_token() -> Optional[str]:
    """Supabase token = .env 또는 Streamlit Cloud secrets에서 read.

    채팅·코드·git 절대 노출 X (헌법 §3·invariant).
    PO 결정 = 옵션 B 채택 시만 활성·현재는 None 반환 = 통합 X.
    """
    return os.getenv("SUPABASE_ACCESS_TOKEN")
```

## 영구 invariant 추가 후보 (12번째)

> **"Supabase Storage·DB에 자관 .mrc·사서 PII 저장 절대 금지. 외부 BaaS = Auth만 한정 (옵션 B)·Storage·DB = AWS Lightsail Seoul (Phase 2 외부 858 §E 정합)."**

→ Phase 2 (사업자 등록 후) 박제 권장.

## 자동 결정 (Cycle 64·BaaS 10 옵션 비교 결과)

→ `docs/automation/baas-comparison-2026-05.md` 매트릭스 정합.

**채택**: **옵션 A (Supabase 미도입)** + Phase별 stack:
- Phase 1 (현재): **streamlit-authenticator + yaml** (★★★★★·자관 100% 로컬)
- Phase 2 (사용자 100+·사업자 등록 후): **AWS Cognito + Lightsail Seoul** (★★★★·PIPA 정합·한국 호스팅)
- Phase 3 (자치구·공공 진입): **NCP Cloud + CSAP** (★★★·CSAP 인증 필수)

**거부**: 옵션 B (Supabase Auth Phase 2)·옵션 C (Supabase 전면).

**이유**:
- Supabase = 미국 호스팅·PIPA §28의8 6수신자 추가·privacy v2 의무
- AWS Cognito + Lightsail Seoul = 동일 무료 50K MAU + 한국 호스팅 = **Supabase 대비 우위**
- 자치구·공공 진입 = CSAP 필수 = NCP/NHN = Supabase 부적합
- 도서관 시장 인지도 = AWS·NCP > Supabase

## 즉시 보안 (PO 1분·필수)

- 노출 토큰 즉시 revoke (https://supabase.com/dashboard/account/tokens)
- 새 토큰 = .env에만 저장 (채팅·코드 X)

## 결정 시점

- Phase 1 (현재·인터뷰 0건·매출 0): **옵션 A 권장**
- Phase 2 (사업자 등록 + 인터뷰 5명 후): 옵션 B 검토 가능
