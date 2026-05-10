# Cross-SaaS 시너지 측정 (Cycle 736·PO #84 산출물 #9)

> **목적**: Bundle 효과·LTV·viral coefficient·cross-saas funnel 측정.
> **PO #76·#79·#80 정합**: 다중 SaaS 투망·cross-saas learning·growth 14.

---

## 4 핵심 측정 지표

### 1. Bundle Conversion Rate
```
Bundle 결제 / 단일 SaaS landing 진입 사용자
- 단일 SaaS 진입 → Bundle CTA 클릭률
- Bundle CTA 클릭 → Bundle 결제 완료율
- 목표: 10%+ (Bundle CTA 진입 → 결제)
```

### 2. LTV (Lifetime Value)
```
사용자당 누적 매출 (월별·12개월)
- 단일 SaaS LTV: 평균 $7.21/월 × 6개월 churn = $43
- Bundle LTV: $25/월 × 8개월 churn = $200 (4.6x)
- Bundle 효과 = LTV ↑ + churn ↓
```

### 3. Viral Coefficient (k)
```
신규 사용자 1명이 데려오는 평균 사용자 수
- Affiliate 1개월 무료 = k 0.2~0.4 목표
- 추천 link = Polar Referral Code 발급
- Bundle 추천 = "친구 가입 시 1개월 무료" 보너스
```

### 4. Cross-SaaS Funnel
```
사용자 진입 path 추적:
- SaaS A → Bundle 인지 → Bundle 결제 (B·C·D 동시 사용)
- SaaS A → SaaS B 직접 진입 (footer link 클릭)
- SaaS A 결제 → SaaS B 추천 노출 → 30일 후 추가 결제
```

---

## MongoDB 측정 schema (자동·Polar webhook)

```javascript
// collection: cross_saas_events
{
  _id: ObjectId,
  user_email: "...",
  saas: "kormarc-auto",  // 또는 "all-access-bundle"
  event_type: "checkout.completed" | "subscription.created" | ...,
  amount_krw: 7000,
  occurred_at: ISODate,
  funnel: {
    landing_referrer: "google.com" | "general-docs-auto.vercel.app",
    bundle_clicked: true,
    bundle_purchased: true,
    cross_saas_count: 3  // 가입 SaaS 수
  }
}

// collection: bundle_metrics_daily
{
  _id: "2026-05-09",
  total_revenue_usd: 250.50,
  bundle_revenue_usd: 175.00,  // 70%
  single_revenue_usd: 75.50,
  bundle_count: 7,
  single_count: 12,
  conversion: { bundle_view: 100, bundle_click: 25, bundle_paid: 7 },
  ltv_30d_usd: { bundle: 175.0, single: 21.5 }
}
```

---

## 사전 추정 (실 데이터 30일 후 검증)

```
시나리오 (월별·100명 가입 가정):
- 단일 SaaS만: 100 × $7.21 = $721/월
- Bundle 25%: 75 × $7.21 + 25 × $25 = $541 + $625 = $1,166/월 (1.6x ↑)
- Bundle 50%: 50 × $7.21 + 50 × $25 = $361 + $1,250 = $1,611/월 (2.2x ↑)
- Bundle 70%: 30 × $7.21 + 70 × $25 = $216 + $1,750 = $1,966/월 (2.7x ↑)

실 측정 = Polar webhook + cs_helper.match_faq (이메일 분석) + Vercel Analytics.
```

---

## 매주 자동 보고 (Cycle 자동)

```
매 7일 cycle:
1. MongoDB → revenues·conversions·LTV 집계
2. portfolio_dashboard.render_dashboard_html → HTML 갱신
3. Bundle 효과 metric 표시 (Top 3 + Bundle conversion + LTV)
4. PO 알림 (이메일·Slack·또는 dashboard URL)
```

---

## Cross-SaaS 학습 적용 (PO #79 정합)

```
한 SaaS 인사이트 → 모든 SaaS 적용:
- kormarc-auto Pro 구독자 = simple-budget·simple-todo 무료 추천
- general-docs Pro = receipt-ocr·simple-budget 자동 데이터 import
- Bundle = 9 SaaS 모두 활성·LTV 자동 ↑
```

---

## 결론

Cross-SaaS 시너지 = Bundle 매출 70%+ 달성 시 LTV 2.7x.
실 측정 = MongoDB + portfolio_dashboard 30일 자동.
PO 결정 = "매 7일 dashboard 확인 + 매출 데이터 기반 Top 3 결정".
