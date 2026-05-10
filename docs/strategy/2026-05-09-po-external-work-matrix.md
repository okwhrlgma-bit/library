# PO 외부 작업 자동화 의무 매트릭스 (Cycle 735·PO #84 산출물 #10)

> **목적**: PO가 직접 해야 하는 작업 vs Claude 자동 가능 명확 구분.

---

## 매트릭스 (작업 X 자동화 가능 여부)

### 🤖 Claude 100% 자동 (PO 작업 0)

| 작업 | 도구·근거 |
|---|---|
| 코드 시드·tests | Python·git·Claude Code |
| GitHub repo 생성·push | gh CLI (Cycle 695~728·12건 자동 검증) |
| Vercel project 생성·배포 | Vercel REST API (Cycle 685~732·10건) |
| Vercel SSO 자동 해제 | PATCH /v9/projects/{id}·Cycle 686 검증 |
| Polar 제품 등록·수정 | Polar API (Cycle 695·LS 한계 100% 우회) |
| Polar 영구 buy URL | create_checkout_link·29건 자동 |
| landing 디자인·HTML | Cycle 685·686·dynamic·다중 SaaS |
| SEO·robots·sitemap·llms.txt | Cycle 686·707·24 URL 자동 |
| webhook receiver | Vercel function·HMAC SHA256·Cycle 698~708 |
| 자동 health check | _shared/observability/deployment·매 cycle |
| Dashboard 자동 생성 | _shared/portfolio_dashboard·HTML 매주 |
| FAQ·terms 페이지 | cs_helper.faq_html·Cycle 700 |
| 메모리 박제·docs | Cycle 700~733·14 영구 정책·docs/strategy |

### 👤 PO 외부 작업 의무 (Claude 차단 X·법적·계정 권한)

| 작업 | 시간 | 차단 이유 |
|---|---:|---|
| Polar 가입·OAT 발급 | 5분 | 본인 인증·법적 |
| LemonSqueezy 가입·키 발급 | 5분 | 본인 인증 |
| Vercel 가입·토큰 발급 | 5분 | 본인 인증 |
| MongoDB Atlas 가입·credential | 5분 | 본인 결제 |
| Streamlit Cloud 가입·첫 Deploy | 5분 | OAuth + Web UI |
| **Polar 제품 publish** | **15분** | **Web Dashboard 의무·draft → published** |
| **Streamlit Secrets 입력** | **2~5분** | **Web UI·secrets 직접** |
| Polar webhook 등록·secret | 3분/건 | Web Dashboard·secret 발급 |
| Custom Domain 구매·연결 | 5분 | 본인 결제·도메인 등록자 |
| 검색엔진 등록 (Google·네이버) | 5분/건 | 본인 사이트 인증 |
| 사업자 등록 + VAT | 1주 | 법적 의무·홈택스·정부24 |
| 정부 자금 신청 | 1주 | 본인 사업자 신청 |
| ProductHunt·HN·X 발사 | 1일 | ADR 0052·PO 명시 후 |
| 사서 인터뷰·MOU·자관 PILOT | 변동 | ADR 0052·외부 활동 차단 |

### ⚠ Claude 자동 시도·실패 가능 (재시도·우회 권장)

| 작업 | 결과 | 우회 |
|---|---|---|
| LemonSqueezy 제품 등록 | ❌ HTTP 405 (Cycle 676·696) | Polar 채택 (Cycle 695) |
| Streamlit Cloud REST API | ❌ 미공개 | Web UI 1회 click 의무 |
| Polar 제품 publish | ❌ Web 의무 | PO 외부 작업 |

---

## PO 외부 작업 vs Claude 자동 합계

```
✅ Claude 자동: 13 작업 (코드·배포·SEO·monitoring 등)
👤 PO 외부 의무: 14 작업 (가입·publish·secret·발사·법적)
⚠ Claude 시도·실패: 3 작업 (LS 제품·Streamlit Cloud·publish)
```

---

## 우선순위 (시급도)

### Day 1 (최소 30분·매출 활성 시작점)
```
1. Polar 29 제품 publish (15분·💰 시급)
2. Streamlit Cloud Deploy (3분·💰 시급)
3. Streamlit Secrets 입력 (2분·💰 시급)
4. 자관 dogfooding 결제 (5분·💰 critical_lockup 해소·시그널)
5. Polar webhook secret 공유 (5분·자동 매출 흐름)
```

### Week 1 (선택)
```
6. 검색엔진 등록 6 SaaS × 3 (90분·SEO 활성)
7. (Vercel env vars POLAR_WEBHOOK_SECRET 추가·Claude 자동)
8. (선택) Custom Domain (5분·연 ₩1만)
```

### Month 1 (매출 ₩100K+ 후)
```
9. 사업자 등록 + VAT (1주·정부 자금 게이트)
10. PortOne v2 (한국 KRW 직접)
11. PyPI 패키지 (4 SaaS)
```

### Month 2~3 (PO 명시 후)
```
12. ProductHunt·HN·X 발사 (ADR 0052 해제 시)
13. 사서 인터뷰 (5명·자관 PILOT)
14. KOLAS·NLK MOU
```

---

## 결론

PO Day 1 = 30분·이후 거의 모든 작업 = Claude 자동.
Polar publish·Streamlit Deploy·자관 dogfooding 5건 = 매출 활성 핵심.

매트릭스 매월 갱신 (Cycle별·신규 작업 추가).
