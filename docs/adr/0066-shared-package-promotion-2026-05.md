# ADR 0066 — _shared 정식 패키지 승격 (Sandi Metz AHA·Cycle 104)

- 상태: Accepted
- 결정자: Claude (자율·ADR 0064 정합·5 사용처 도달)
- 일자: 2026-05-09 (Cycle 104~105)

## 배경

Sandi Metz AHA: "3번째 사용처 등장 시 packages/ 승격 시점".

우리 사용처:
- #1 kormarc-auto (kormarc-auto/)
- #4 librarian-overtime (30-apps/04/)
- #31 freelancer-tax-helper (30-apps/31/)
- #32 sidehustle-tracker (30-apps/32/)
- (예정) #2 kdc-classify·향후 모든 앱

→ **5 사용처 도달·정식 패키지 승격 시점**.

## 결정

`30-apps/_shared/` = 정식 Python 패키지로 승격.

### 산출

- `30-apps/_shared/__init__.py` (top-level marker)
- `30-apps/_shared/pyproject.toml` (정식 패키지·Apache-2.0)
- `30-apps/_shared/email/` → `30-apps/_shared/email_helper/` (Python 표준 충돌 회피)
- `30-apps/_shared/tests/test_shared_smoke.py` (9 tests passing)

## 메타

| 항목 | 값 |
|---|---|
| Name | `30apps-shared` |
| Version | 0.1.0 |
| License | **Apache-2.0** |
| Python | 3.11+ |

## 모듈 (4 정식 + 2 docs)

- `payments/` (PortOne·Stripe·LS 3 wrapper)
- `auth/` (Better Auth·CSRF·PIPA 동의)
- `email_helper/` (Resend·전자상거래법 §13/§17)
- `landing/` (Streamlit FAQ·면책 컴포넌트)
- `legal_templates/` (PIPA 처리방침 markdown)
- `AUTOMATIC_REVENUE_FLOW.md` (8 단계)
- `STARTUP_ROADMAP.md` (6 Phase·3년 ₩3,000만/월)

## email → email_helper rename 이유

- Python 표준 `email` = pytest·dataclasses 의존
- sys.path 등록 시 충돌 = pytest 깨짐
- **rename = email_helper** = 충돌 회피·import 정상

## 사용 패턴 (다른 앱에서)

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "_shared"))

from landing import LandingConfig, default_faqs
from payments import PaymentConfig, select_provider
from auth import generate_csrf_token
from email_helper import build_welcome_message  # ← email X (충돌)
```

## tests 회귀 (9건)

- 패키지 metadata
- 4 모듈 import (payments·auth·email_helper·landing)
- 헌법 §3 (env only) 정합
- 전자상거래법 §17 (7일 환불) 정합

## ROI

- 코드 재사용 = 30 앱 누적 시 코드 단축 30~50%
- 일관성 = 결제·인증·이메일·랜딩 표준화
- 캐시카우 가속 = 새 앱 = _shared import 1줄

## 다음 단계

- pip install 정식 (`pip install -e ../_shared`) = 다른 앱
- packages 통합 시 = `pyproject.toml` workspaces (pnpm/Turborepo 정합·Cycle 외부 research)
