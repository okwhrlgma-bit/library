# Part 5 — 외부 편의 도구·자동화 종합 추천 (2026-04-29)

> **목적**: PO (사서 출신 1인 비개발자) 워크플로우에 즉시 도움되는 외부 도구 큐레이션. 4-Part 매뉴얼 (`part1-vibe-coding`·`part2-kormarc-implementation`·`part3-librarian-workflows`·`part4-uiux-seo-marketing-deployment`) 보강.
> **단일 진실**: 매출 직결 + 무료 진입 가능 + 한국·1인 운영 정합 도구만.

---

## 0. 추천 12종 우선순위 매트릭스

| # | 도구 | 카테고리 | 우선순위 | 무료 한도 | §0 / §12 영향 |
|---|---|---|---|---|---|
| 1 | **GitHub** | 코드 백업·협업 | ★★★ 1순위 | 무료 (private 무제한) | §12 +5 (cloud agent·CI 활성) |
| 2 | **GitHub Actions** | CI/CD 자동 | ★★★ 1순위 | 월 2,000분 | §12 +3 (push 시 자동 검증) |
| 3 | **Vercel** | 호스팅·배포 | ★★ 2순위 | 월 100GB | §12 +2 (Streamlit·FastAPI 5분 배포) |
| 4 | **Supabase** | DB·Auth·Storage | ★★ 2순위 | DB 500MB·월 5GB | §12 +2 (SQLite 한계 시) |
| 5 | **포트원** | 결제 PG (한국) | ★★★ 1순위 (ADR 0007) | 거래 1.7~3% | §12 +5 (정식 결제·세금계산서 자동) |
| 6 | **PostHog** | 분석·세션 녹화 | ★★ 2순위 | 월 1M 이벤트 | §0 +2 (사서 막히는 지점 측정) |
| 7 | **Sentry** | 에러 추적 | ★★ 2순위 | 월 5K 에러 | §0 +1 (5xx 즉시 알림) |
| 8 | **Resend** | 이메일 발송 | ★★ 2순위 | 월 3K (3,000 이메일) | §12 +3 (영업·청구·NPS) |
| 9 | **Cal.com** | 일정 예약 자동 | ★★ 2순위 | 무료 (오픈소스 self-host) | §12 +2 (PILOT 시연 자동 예약) |
| 10 | **Notion** | 문서·KPI 추적 | ★ 3순위 | 무료 (개인) | §12 +1 (PILOT 결과 누적) |
| 11 | **Cursor/Windsurf** | IDE 비교 | ★ 3순위 (선택) | $20/월 | §0 +0 (Claude Code 보완) |
| 12 | **Linear** | PR·이슈 (추후) | ☆ 4순위 (Phase 3) | 무료 (10명) | §12 +0 (1인 운영엔 과대) |

→ **즉시 도입 5종**: GitHub (1) → GitHub Actions (2) → Resend (8) → Cal.com (9) → PostHog (6)
→ **사업자 등록 후**: 포트원 (5)
→ **트래픽 증가 시**: Vercel (3)·Supabase (4)·Sentry (7)

---

## 1. GitHub (★ 1순위)

### 왜 즉시 필요한가

- 33+ commit이 PC 로컬에만 = PC 고장 시 모두 잃음
- Cloud Claude routine은 GitHub URL로 clone → GitHub push 안 하면 자동 진행 불가
- `kormarc-auto prefix-discover` 같은 사서 도구 = GitHub repo로 배포 → 사서가 `git clone` 1줄로 받기

### 셋업 5분

```powershell
# 1. GitHub 가입 (이메일 본인 인증, 5분)
#    https://github.com/signup

# 2. 새 repository 만들기 (Web UI)
#    Repository name: kormarc-auto
#    Public 또는 Private (PO 결정·private도 무료)
#    README·LICENSE 추가는 우리 이미 있어서 X

# 3. 로컬에서 push (PowerShell)
cd kormarc-auto
git remote add origin https://github.com/[YourUsername]/kormarc-auto.git
git branch -M main
git push -u origin main
```

### 비용

- **Public·Private 모두 무료** (개인 무제한)
- LFS (큰 바이너리): 1GB 무료
- Actions (CI): 월 2,000분 무료

### 보안 주의

- `.env` 파일 push 금지 (`.gitignore` 이미 적용)
- API 키 노출 시 즉시 재발급 (1회 push되면 history에 영구)
- private repo로 시작 → 정식 release 시 public 검토

---

## 2. GitHub Actions (CI/CD ★ 1순위)

### 왜 필요한가

- 매 push마다 pytest·ruff·binary_assertions 자동 실행 = 회귀 즉시 검출
- PR 생성 시 자동 검증 → 안전한 merge
- 골든 데이터셋 회귀·정확도 측정 자동 알림

### 셋업 (다음 commit으로 진행)

`.github/workflows/ci.yml` 생성 후 push:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest -q
      - run: python scripts/binary_assertions.py --strict
```

### 비용

- 월 2,000분 무료 (1개 workflow ~3분 = 약 660 push 가능)
- 사적 repo도 무료

---

## 3. Vercel (호스팅 ★ 2순위)

### 왜 필요한가

- Streamlit·FastAPI 5분 배포 (PowerShell 1줄)
- Phase 0 MVP 외부 노출 (지금은 cloudflared 단발 터널)
- 사서가 PILOT 시 Wi-Fi·hotspot 없이 https URL 접속

### 셋업

```powershell
npm i -g vercel
cd kormarc-auto
vercel  # 로그인 → 자동 배포
```

### 비용

- Hobby (개인): 무료 (월 100GB 대역폭·서버리스 함수 무제한 invocation·24h serverless 한도)
- Streamlit은 별도 hosting (Vercel은 Streamlit 직접 지원 X) → **Streamlit Community Cloud** 또는 **Render** 권장

→ 우리 케이스: **Render** (Streamlit·FastAPI 둘 다 지원) 또는 **Fly.io** (Cloudflare Tunnel 대체) 고려.

---

## 4. Supabase (DB·Auth ★ 2순위)

### 왜 필요한가

- 현재 SQLite (단일 PC) → 사서 100명 동시 접속 시 한계
- Postgres + Auth + Storage 매니지드 (백업 자동·무중단)
- DSAR (개인정보보호법 §35-3) Postgres SQL 직접 조회 가능

### 셋업

```powershell
# 1. https://supabase.com 가입 (GitHub 로그인)
# 2. 새 프로젝트 (서울 리전 선택·한국 사서 지연 ↓)
# 3. .env에 DATABASE_URL 추가
# 4. SQLAlchemy로 SQLite → Postgres 마이그레이션
```

### 비용

- 무료: DB 500MB·Storage 1GB·월 5GB 대역폭·인증 사용자 무제한
- Pro $25/월: DB 8GB·일일 백업·24h 지원 (사서 200관 도달 시)

→ 우리 케이스: **Phase 2 (12~24개월·100관) 도달 시 마이그레이션** 고려.

---

## 5. 포트원 (결제 PG ★ 1순위 ADR 0007)

### 왜 필요한가

- 정식 결제 자동 (월정액·자동 차감·환불·세금계산서)
- PG 어댑터 + webhook stub 이미 정합 (`server/payment_adapter.py`·`portone_webhook.py`)

### 셋업 (사업자 등록 후)

```powershell
# 1. 사업자 등록증 + 통신판매 신고 (홈택스·5분·무료)
# 2. 포트원 가입 (https://portone.io)
# 3. .env에 KORMARC_PORTONE_API_KEY·SECRET·CHANNEL_KEY·BIZ_NO 채움
# 4. KORMARC_PG_PROVIDER=portone
# 5. 포트원 콘솔에서 webhook URL 등록 (https://[우리서버]/webhook/portone)
```

### 비용

- 거래액 기준 1.7~3% (PG사 수수료)
- 무월비
- 세금계산서 자동·환불 자동·정기결제 자동

---

## 6. PostHog (분석·세션 녹화 ★ 2순위)

### 왜 필요한가

- 사서가 우리 UI에서 어디 막히는지 화면 녹화로 직접 확인
- A/B 테스트 (가격 표기·UI 흐름)
- 사서 funnel (가입 → 50건 무료 → 결제 전환률) 측정

### 셋업

```powershell
# 1. https://posthog.com 가입 (US·EU·자체호스팅 선택)
# 2. Streamlit에 1줄 추가
import posthog
posthog.identify(user_id, properties={"plan": "free"})
posthog.capture(user_id, "kormarc_generated", {"isbn": isbn})
```

### 비용

- 무료: 월 1M 이벤트·세션 녹화 5K
- Cloud (Pro) $0~ + 사용량
- 자체 호스팅 (오픈소스): 무료

---

## 7. Sentry (에러 추적 ★ 2순위)

### 왜 필요한가

- 5xx 발생 시 PO 폰에 즉시 알림 (Discord·Slack·Email·SMS)
- Stack trace + 사용자 행동 + 환경 자동 캡처
- 디버깅 시간 ↓

### 셋업

```powershell
# 1. https://sentry.io 가입 (무료)
# 2. pip install sentry-sdk[fastapi,sqlalchemy]
# 3. server/__init__.py 추가
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=0.1)
```

### 비용

- 개발자 1명·월 5K 에러 무료
- Team $26/월 (5K → 50K 에러)

---

## 8. Resend (이메일 발송 ★ 2순위)

### 왜 필요한가

- 사서 영업 메일 (4 페르소나별·`docs/sales/pilot-package` §2)
- NPS 자동 발송 (PILOT 1주차 종료 후)
- 영수증 자동 발송 (포트원 webhook 이후)

### 셋업

```powershell
# 1. https://resend.com 가입 (GitHub 로그인)
# 2. 도메인 인증 (kormarc-auto.kr 또는 PO 도메인)
# 3. pip install resend
import resend
resend.api_key = os.getenv("RESEND_API_KEY")
resend.Emails.send({
    "from": "PO <po@kormarc-auto.kr>",
    "to": "사서@자관.or.kr",
    "subject": "kormarc-auto PILOT 제안",
    "html": "<p>...</p>",
})
```

### 비용

- 무료: 월 3,000 이메일·1 도메인
- Pro $20/월: 50,000 이메일·도메인 무제한

---

## 9. Cal.com (일정 예약 ★ 2순위)

### 왜 필요한가

- 사서가 카카오 채널 안내 본 후 → "5월 PILOT 시연 신청 클릭" → Cal.com에서 자동 30분 예약
- PO 캘린더 (구글·네이버) 통합 → 충돌 자동 회피
- 사서에게 자동 확인·알림 메일

### 셋업

```powershell
# 1. https://cal.com 가입 (또는 self-host)
# 2. PILOT 시연 30분 이벤트 생성 (월·화·목 18:00~20:00 가능)
# 3. 카카오 채널·README에 "PILOT 시연 예약" 링크 노출
```

### 비용

- 무료: 1 이벤트·연동 1개
- Pro $15/월: 무제한 이벤트·연동
- 자체 호스팅 (오픈소스): 무료 (Vercel 호스팅 추천)

---

## 10. Notion (문서·KPI 추적 ★ 3순위)

### 왜 필요한가

- PILOT 4주 KPI 누적 (조기흠 1주·박지수 2주·종합 3주·통합 4주)
- 사서 인터뷰 누적 → `aggregate_interviews.py` import
- 영업 funnel (메일 발송·시연·결제) 시각화

### 셋업

```powershell
# 1. https://notion.so 가입 (개인 무료)
# 2. PILOT 데이터베이스 생성 (사서·페르소나·NPS·Q1·날짜·코멘트)
# 3. Notion API 키 → server/notion_sync.py로 자동 export
```

### 비용

- 개인: 무료
- Plus $10/월 (팀 협업 시)

---

## 11. Cursor / Windsurf (IDE 비교 ★ 3순위 선택)

### 왜 검토하는가

- Claude Code 외에 다른 AI IDE 검토 가치
- 자세한 비교: `docs/research/part1-vibe-coding-and-claude-code.md` §2

### 결론

- 우리는 **Claude Code 1순위 유지** (이미 hooks·agents·메모리 정합)
- Cursor·Windsurf는 보조 도구로 IDE 비교 검토만 (실 도입 X·시간 비효율)

---

## 12. Linear (PR·이슈 관리 ☆ 4순위 — Phase 3)

### 왜 추후

- 1인 운영 = GitHub Issues로 충분
- 팀 확장 (Phase 3·24~36개월·캐시카우 도달) 후 도입 검토
- 그 전엔 Notion + GitHub Issues 충분

---

## 13. 즉시 도입 5종 일정

| 순서 | 도구 | 시간 | PO 액션 |
|---|---|---|---|
| 1 | GitHub | 5분 | 가입 + repo + push |
| 2 | GitHub Actions | 5분 | `.github/workflows/ci.yml` (자율 진행) |
| 3 | Resend | 10분 | 가입 + 도메인 인증 + API 키 |
| 4 | Cal.com | 5분 | 가입 + 이벤트 생성 + 카카오 링크 |
| 5 | PostHog | 5분 | 가입 + Streamlit 1줄 추가 |

→ **30분 안에 5종 모두 셋업** = 자관 PILOT 시작 전 운영 인프라 정점.

---

## 14. 후속 도입 (사업자 등록 후 또는 트래픽 증가 시)

| 도구 | 트리거 |
|---|---|
| 포트원 | 사업자 등록 + 통신판매 신고 (5월 中) |
| Vercel / Render | Streamlit·FastAPI 외부 노출 (cloudflared 한계 시) |
| Supabase | 사서 100관+ 동시 접속 |
| Sentry | 정식 결제 시작 후 (장애 0% 보장) |
| Linear | 팀 확장 (Phase 3·24~36개월) |

---

## Sources

- `docs/research/part1-vibe-coding-and-claude-code.md` (Cursor·Windsurf 비교)
- `docs/research/part4-uiux-seo-marketing-deployment.md` (배포·마케팅)
- `docs/sales/pilot-package-2026-04-29.md` (영업 채널)
- `docs/sales/kakao-channel-content-2026-04-29.md` (카카오 콘텐츠)
- `src/kormarc_auto/server/payment_adapter.py`·`portone_webhook.py` (포트원 stub)
- ADR 0007 (포트원 채택)·ADR 0011 (매니지드 스택)
- 2026년 1월 기준 가격·기능 (각 공식 사이트 확인 권장)
