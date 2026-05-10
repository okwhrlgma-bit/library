# 24~72h 첫 매출 ₩1 작전 (Cycle 733·PO #84·#85 산출물 #1)

> **목표**: critical_lockup 619 cycle 해소·시그널 = 매출 ₩1 (자관 dogfooding·외부 발사 X)
> **헌법**: ADR 0052 외부 발사 차단·PO 자관 사서 자기 결제 = 자율 정합·법적 X

---

## 🎯 24h 작전 (PO 외부 작업 = 30분)

### Step 1: Polar 26 제품 publish (15분)
```
URL: https://polar.sh/dashboard/kormarc-auto/products
9 SaaS × 3 = 27 제품 + Bundle 2 = 29 제품
- kormarc-auto: $5/$37/$112
- general-docs: $2/$4/$40
- group-member: $10/$7/$70
- receipt-ocr: $8/$6/$60
- simple-budget: $1.5/$15/$30
- ai-writer: $6/$5/$50
- simple-todo: $1.5/$15/$25
- diet-workout: $2/$20/$35
- medication: $1.5/$15/$20
- All-Access Bundle: $25/$250

각 제품 → "Publish" 버튼·draft → published 활성
```

### Step 2: PO 자관 사서 자기 결제 (5분·시그널)
```
PO 자관 도서관 = kormarc-auto 사용자 1명
→ kormarc-auto Pro (월정액·소) 50건 패키지 = $5 (≈₩7,000) 결제
→ Polar checkout URL: https://buy.polar.sh/polar_cl_Ys08mrzNseYOtG2ldptcfE25llGDGW7KDOsWN1wDkig
→ 매출 ₩1 = ₩7,000·critical_lockup 해소·첫 매출 시그널

근거 (헌법 §13·DA7·dogfooding 정합):
- PO 자관 = 8명 사서 운영 1관
- KORMARC 자관 매월 50~100권·실 사용자
- PO 자기 결제 = 단순 dogfooding·법적 X·법인 결제 X·개인 카드
- 시그널 = "첫 사용자 = founder·검증 시작점"
```

### Step 3: 자기 검증 흐름 (10분)
```
1. 결제 완료 → Polar webhook → /api/webhook
2. license_key 자동 발송 (이메일·Polar)
3. 라이선스 키 = .env LEMONSQUEEZY_VARIANT_ID 갱신 (Claude 자동)
4. 자관 KORMARC 1건 처리 (실 ISBN·실 자료) → 시간 측정
5. PO 매월 50권 사용 시뮬·MRR ₩7,000·12개월 = ₩84,000 확인
```

---

## 🎯 24~72h 작전 (Claude 자율·외부 발사 X)

### Day 1 (24h 후)
```
Claude:
- 자동 health check (10 SaaS·Vercel·Polar)
- 매출 dashboard 갱신 (PO #82·#84 정합)
- _meta·사용자_TODO·메모리 박제

PO:
- (선택) 자관 dogfooding 1건 결제 (Step 2)
- (선택) Streamlit Cloud Deploy 1회 click (3분)
- (선택) Polar webhook secret 공유
```

### Day 2~3 (24~72h)
```
Claude 자동 (외부 발사 X):
- SEO 보강 (구조화 데이터·robots·sitemap·llms.txt)
- 콘텐츠 자동 (#87 SNS 컨텐츠·blog·매주 1회 자동)
- Bundle CTA cross-link 검증 (모든 SaaS 일관성)
- Polar webhook secret 등록 후 = MongoDB 로그 자동
- 30일 매출 데이터 수집 시작

PO:
- (선택) 검색엔진 등록 (Google·네이버·다음·90분)
- (선택) ProductHunt·HN·X 발사 = ❌ 차단 (ADR 0052)
- 사업자 등록 = 매출 ₩100K+ 후 (3순위·1주 작업)
```

---

## ⚠ 위험 요소 (정직)

```
🔴 PO 자관 dogfooding = 1건 매출만·시그널 부족 (실 사용자 ≠ founder)
🔴 외부 발사 X = 트래픽 0·30일 후 매출 데이터 부족 가능
🔴 9 SaaS 분산 = 어느 하나도 깊이 X·sunk cost 우려
🔴 Streamlit Cloud Deploy = PO 미진행 시 = 본 앱 사용 X·결제만 활성
```

---

## 📊 시그널 측정 (24~72h 후)

| 지표 | 목표 | 측정 |
|---|---|---|
| 매출 ₩1 | ✅ ₩7,000+ | Polar webhook |
| Vercel HTTP 200 | 10/10 SaaS | _shared/observability/deployment |
| Bundle CTA cross-link | 9 SaaS | landing/index.html grep |
| Dashboard 활성 | HTTP 200 | all-access-bundle.vercel.app/dashboard/ |
| 자기 진단 | 117+ | docs/self-assessment/ |

---

## 🎯 결론

**24h = PO 30분 외부 작업 (Polar publish 15분 + 자기 결제 5분 + Streamlit Deploy 3분 + Secrets 2분 + dogfooding 5분)**·
이후 100% Claude 자동·30일 매출 데이터 수집 → Top 3 결정.

PO 결정 = "자관 dogfooding 진행" 명시 시 즉시 실행·외부 발사는 PO 명시 후만.
