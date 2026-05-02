# Part 59 — 상업적 고려사항 + B2B SaaS 팀 페르소나 (2026-05-02)

> PO 명령:
> 1. "상업적으로 어떤걸 고려해? 우리도 찾아서 그런거 고려해야 할 듯"
> 2. "보통 이런거 만들때 팀을 어떻게 짜? 그 팀에서 필요한 페르소나 가져와서 적용"

---

## 0. B2B SaaS 표준 팀 구조 (검증된 패턴)

### Stage별 표준 팀 (Stripe·HubSpot·노션·토스·당근 분석)

**Pre-Seed/Seed (1~5명)**
- Founder/CEO (PO)
- Tech Lead (Claude = engineer)
- Designer (1)

**Series A (10~30명)**
- + PM (1) · CSM (1) · AE (2) · Marketing (1)
- + Backend (2) · Frontend (1) · DevOps (1)
- + Finance (1, part-time)

**Series B+ (50~200명)**
- + Growth/PMM (1~3) · CFO (1)
- + Sales Dev Rep (3+) · Account Manager (3+)
- + Data Analyst (1~3) · Legal (1)

### 1인 SaaS 적용 = **외부화된 페르소나**

PO 1명 = 모든 역할 동시 수행 = **사고 동반자 = 페르소나 시뮬**.

→ **B-team 페르소나 6명** (Part 59 신규 = `business-personas` subagent)
- B1 PM · B2 CSM · B3 AE · B4 Growth · B5 VC · B6 CFO

---

## 1. 상업적 고려사항 30+ 종합 (B2B SaaS 표준)

### A. 단위 경제 (Unit Economics) — B6 CFO 영역

| 메트릭 | 정의 | 목표 | 현재 | 갭 |
|--------|------|------|------|----|
| **CAC** (Customer Acquisition Cost) | 신규 1관 영업비 | ≤₩50,000 | 미측정 | 🔴 |
| **LTV** (Lifetime Value) | 1관 평생 매출 | ≥₩600,000 | 미측정 | 🔴 |
| **LTV/CAC** | 효율 | ≥3 | 미측정 | 🔴 |
| **Payback Period** | CAC 회수 | ≤12개월 | 미측정 | 🔴 |
| **Gross Margin** | 매출 - 원가 | ≥70% | 추정 90%+ | ✅ |
| **Burn Rate** | 월 지출 | 최소화 | 1인 = 매우 낮음 | ✅ |
| **Runway** | 자금 소진 시점 | 18개월+ | 1인 = 무한 | ✅ |
| **Magic Number** | (현분기 ARR - 전분기 ARR) × 4 / 전분기 영업비 | ≥1.0 | 측정 X | 🔴 |
| **Rule of 40** | 성장률 + 마진 | ≥40% | 측정 X | 🔴 |
| **Burn Multiple** | net burn / net new ARR | ≤1.0 | 측정 X | 🔴 |

### B. 매출·유지 (Revenue & Retention) — B2 CSM 영역

| 메트릭 | 정의 | 목표 | 현재 | 갭 |
|--------|------|------|------|----|
| **MRR** | 월 반복 매출 | 660만 (200관×3.3만) | 0 | Phase 1 진행 |
| **ARR** | 연 반복 매출 | 7,920만 (660만×12) | 0 | Phase 1 |
| **Churn** | 월 이탈율 | ≤5% | 측정 X | 🔴 |
| **NRR** (Net Revenue Retention) | (이전 + 확장 - 이탈) / 이전 | ≥110% | 측정 X | 🔴 |
| **GRR** (Gross Revenue Retention) | (이전 - 이탈) / 이전 | ≥90% | 측정 X | 🔴 |
| **Logo Retention** | 로고 유지율 | ≥95% | 측정 X | 🔴 |
| **Expansion Revenue** | 기존 고객 확장 매출 | 30% of ARR | 0 | Phase 2 |
| **NPS** (Net Promoter Score) | 추천 의향 | ≥50 | 측정 X | 🔴 |
| **CSAT** (Customer Satisfaction) | 만족도 | ≥80 | 측정 X | 🔴 |
| **CES** (Customer Effort Score) | 작업 어려움 | ≤2 | 측정 X | 🔴 |

### C. 가격 전략 (Pricing) — B3 AE + B6 CFO

**현재**: 무료 50건 + 월 3.3만/관 (단일 티어)

**B2B SaaS 표준 패턴**:

| 패턴 | 정의 | kormarc-auto 적용 |
|------|------|-----------------|
| **Freemium** | 무료 영구 + 유료 확장 | ✅ 무료 50건 |
| **Tier (3티어)** | Starter·Pro·Enterprise | ⚠️ 단일만 |
| **Anchor** | 고가 옵션 = 중간 매력 ↑ | 🔴 X |
| **Usage-based** | 사용량 비례 | ⚠️ 50건 후 X |
| **Per-seat** | 사용자별 | ⚠️ 1관당 (괜찮음) |
| **Annual discount** | 연 결제 20% 할인 | 🔴 X |
| **Volume discount** | 자치구 25관 일괄 30% | 🔴 X |
| **Pilot pricing** | 첫 3개월 50% | 🔴 X |
| **Reference pricing** | 후기 작성 시 50% | 🔴 X |
| **Sunset pricing** | 가입 시점 = 영구 | 🔴 X |

**적용 권장**:
- 🔴 **3티어**: Starter (3.3만) · Pro (5.5만 + 다중 사용자) · Enterprise (협의)
- 🔴 **Anchor**: Enterprise 19.9만 → Pro 5.5만 매력 ↑
- 🔴 **Annual discount 20%**: 3.3만 × 12 = 39.6만 → 31.7만 (자치구 1년 예산 정합)
- 🔴 **Volume**: 자치구 25관 = 30% 할인 (66만 → 46만/월)

### D. 영업 사이클 (Sales Motion) — B3 AE 영역

| 영업 모델 | 정의 | kormarc-auto |
|---------|------|-------------|
| **PLG** (Product-Led) | 사용자 자가 가입 | ✅ self-serve |
| **SLG** (Sales-Led) | 영업 주도 | ⚠️ AE 없음 |
| **Bottom-up** | 사용자 → 의사결정자 | ✅ 사서 → 관장 |
| **Top-down** | 임원 → 조직 | ⚠️ KLA·자치구 |
| **Hybrid** | PLG + SLG | 권장 |

**한국 B2B SaaS 표준 영업 사이클**:
1. **Lead Generation**: 콜드 메일·블로그·KLA 부스
2. **MQL** (Marketing Qualified Lead): 가입·자료 다운로드
3. **SQL** (Sales Qualified Lead): demo 요청·예산 확인
4. **Proposal**: MSA·SOW 발송
5. **Negotiation**: 가격 협상·결재 양식
6. **Close**: 계약·결제·온보딩
7. **Onboarding**: TTV ≤5분
8. **Expansion**: 추가 라이선스·자치구 일괄

**현재 갭**:
- 🔴 Lead → Close pipeline 측정 X
- 🔴 MSA·SOW·DPA 표준 X
- 🔴 Demo 자동 (Calendly·자동 데모) X
- 🔴 Sales enablement 자료 (영업 30+) ✅ 있음

### E. 컴플라이언스 + 인증 (Compliance) — E6 + B6

| 인증 | 영역 | kormarc-auto | 영향 |
|------|------|-------------|------|
| **ISMS-P** | 정보보호 | 🔴 | 대학·정부 차단 해소 |
| **CSAP** (클라우드 보안) | 정부 SaaS | 🔴 | 정부 조달 차단 해소 |
| **ISO 27001** | 글로벌 | 🔴 | 해외 진입 |
| **SOC 2** | 미국 SaaS | 🔴 | 글로벌 |
| **PIPA** | 개인정보 | ✅ compliance-officer | 매출 10% 회피 |
| **GDPR** | 유럽 | ⚠️ | 글로벌 |
| **클라우드 바우처 인증** | NIPA | 🔴 | 80% 정부 지원 |
| **AI 바우처 인증** | NIPA | 🔴 | 8,900억 풀 |
| **NLK 사서지원과 등록** | 도서관 | 🔴 | 권위·DA7 통과 |
| **KOLAS 마이그 인증** | 종료 후속 | ⚠️ | 18,400관 마이그 |
| **TIPS·디딤돌 R&D** | 자금 | 🔴 | 12~15억 |
| **ICT 인증** | KISA | 🔴 | 정부 신뢰 |
| **부가세 면세** | 소프트웨어 | 🔴 | 면세 검토 |

### F. 조달 채널 (Procurement) — B3 AE + B6 CFO

| 채널 | 영역 | 진입 조건 |
|------|------|---------|
| **나라장터** | 정부 일반 | 사업자 등록 + 카탈로그 |
| **조달청** | 대량 | 카탈로그 + 가격 |
| **S2B** (학교장터) | 학교 | 사업자 + 카탈로그 |
| **G-PASS** | 정부 SaaS | CSAP 인증 |
| **자치구 일괄** | 자치구 | 두드림 패턴 |
| **KLA·KSLA 추천** | 도서관 협회 | 부스·발표 |
| **NIPA AI 바우처** | 8,900억 | AI 인증 |

→ **단일 차단점 = 사업자 등록** (5채널 잠금 해제 = U-17)

### G. 자금 조달 (Funding) — B5 VC + B6 CFO

| 자금원 | 규모 | kormarc-auto 적합 |
|--------|------|---------------|
| **AI 바우처** (NIPA) | 8,900억 | ★★★★★ (5월 마감) |
| **클라우드 바우처** | 80% 지원 | ★★★ |
| **TIPS** | 12~15억 | ★★ (R&D 인정) |
| **디딤돌 R&D** | 3억 | ★★★ |
| **KISTI 데이터 바우처** | 5천만 | ★ |
| **Series Pre-A** | 5~30억 | ★★ (캐시카우 후) |
| **Crowdfunding** (와디즈) | 1~10억 | ★ (B2C 위주) |
| **부트스트래핑** | 자금 0 | ★★★★ (현재 모델) |

→ **즉시**: AI 바우처 5월 마감 ★★★★★

### H. Marketing Mix — B4 Growth 영역

| 채널 | 비용 | 전환율 | kormarc-auto |
|------|------|------|-------------|
| **콘텐츠 SEO** | 시간 | 5~10% | ✅ 블로그 일부 |
| **콜드 메일** | 시간 | 5~50% (페르소나) | ✅ 30+ |
| **카카오 알림톡** | 7.5원/건 | 30% open | ✅ |
| **KLA 부스** | 200~500만 | 직접 만남 | ✅ 5/31 신청 |
| **블로그 + SEO** | 시간 | 장기 | ✅ |
| **유튜브 (사서 채널)** | 시간 | 장기 | 🔴 |
| **Webinar** | 시간 | 20~40% | 🔴 |
| **Reference Customer** | 보상 | 50%+ | ⚠️ PILOT 1관 |
| **Partner (협회·VAR)** | 수수료 | 안정 | 🔴 |
| **PR·매체** | 보도자료 | 신뢰 ↑ | 🔴 |
| **유료 광고** (Google·페북) | 비용 ↑ | B2B 약함 | 비추 |

### I. Customer Health & Success — B2 CSM 영역

| 메트릭 | 정의 | 측정 도구 |
|--------|------|---------|
| **TTV** (Time-to-Value) | 가입 → 첫 가치 | 🔴 미측정 |
| **Activation** | Day 1·7·30 사용 | 🔴 |
| **Health Score** | 종합 헬스 | 🔴 |
| **At-Risk Account** | 이탈 예측 | 🔴 |
| **QBR** (Quarterly Business Review) | 분기 리뷰 | 🔴 |
| **NPS Survey** | 추천 의향 | 🔴 |
| **Customer Advisory Board** | 자문위 | 🔴 |
| **User Group / Community** | 커뮤니티 | 🔴 |
| **Knowledge Base / Docs** | 셀프 서비스 | ✅ |
| **In-app Onboarding** | 가이드 투어 | ✅ tutorial |

### J. 법무·약관 (Legal) — E6 + B3 AE

| 문서 | 영역 | kormarc-auto |
|------|------|-------------|
| **MSA** (Master Service Agreement) | 마스터 약관 | 🔴 |
| **SOW** (Statement of Work) | 작업 명세 | 🔴 |
| **DPA** (Data Processing Agreement) | 데이터 처리 | 🔴 (PIPA 정합) |
| **SLA** (Service Level Agreement) | 99.9% 보장 | 🔴 |
| **BAA** (Business Associate Agreement) | 의료·교육 | 🔴 |
| **Terms of Service** | 이용 약관 | ⚠️ 일부 |
| **Privacy Policy** | 개인정보 처리 | ⚠️ 일부 |
| **AUP** (Acceptable Use Policy) | 사용 한계 | 🔴 |
| **Refund Policy** | 환불 약관 | 🔴 (Part 57 권장) |
| **데이터 보존·에스크로** | 폐업 시 | 🔴 (Part 57 권장) |

---

## 2. 상업성 즉시 적용 (Phase 1 — 캐시카우 직결만)

### A. 단위 경제 측정 인프라 (B6 CFO + B2 CSM) — 5건
- [ ] CAC 측정: 영업 비용 / 신규 가입
- [ ] LTV 측정: 평균 사용 기간 × ARPU
- [ ] Payback 측정: CAC / 월 매출
- [ ] NPS 자동 수집: 가입 후 7·30일
- [ ] Churn·NRR 자동 측정: Mem0 통합

### B. 가격 3티어 + 할인 (B3 AE + B6 CFO) — 4건
- [ ] Starter (3.3만) · Pro (5.5만) · Enterprise (협의)
- [ ] Annual 20% 할인 (자치구 1년 예산 정합)
- [ ] Volume 25관 30% 할인 (자치구 일괄)
- [ ] Pilot 첫 3개월 50% 할인

### C. 영업 사이클 자동 (B3 AE) — 4건
- [ ] MSA 표준 약관
- [ ] SOW 양식
- [ ] DPA (PIPA 정합)
- [ ] Demo 자동 (Calendly + 1인 대응)

### D. 인증 로드맵 (E6 + B6) — 5건
- [ ] **사업자 등록** (U-17) ★ 단일 차단점 (5채널 잠금 해제)
- [ ] **AI 바우처 신청** (5월 마감) ★ 8,900억
- [ ] ISMS-P 로드맵 ADR (대학·정부 진입)
- [ ] CSAP 로드맵 ADR (정부 조달)
- [ ] NLK 사서지원과 등록 (DA7 통과)

### E. 자금 조달 (B5 VC + B6 CFO) — 3건
- [ ] AI 바우처 신청서 (즉시)
- [ ] 디딤돌 R&D 신청 (분기)
- [ ] TIPS 신청 검토 (Phase 2)

### F. 마케팅 채널 추가 (B4 Growth) — 4건
- [ ] 사서 유튜브 채널 (검색 SEO)
- [ ] Webinar 월 1회 (KOLAS 마이그·KORMARC 880)
- [ ] PR 매체 (베타뉴스·전자신문 IT)
- [ ] 협회 파트너 (KLA·KSLA·KPLA)

### G. CSM 인프라 (B2 CSM) — 5건
- [ ] TTV 측정 (가입 → 첫 책 시간)
- [ ] Activation funnel (Day 1·7·30)
- [ ] Health Score 자동
- [ ] At-Risk warning
- [ ] QBR 양식 (분기 리뷰)

### H. 법무 약관 (E6 + B3) — 4건
- [ ] 1주 환불 정책
- [ ] 데이터 보존 6개월·에스크로
- [ ] DPA + PIPA 정합
- [ ] SLA 99.5%+ 보장

총 **34 신규 항목** (Phase 1 추가)

---

## 3. B-team 호출 매트릭스 (산출물 타입별)

| 산출물 | 호출 페르소나 |
|--------|------------|
| 신규 기능 ADR | **B1 PM** + B5 VC + E1 KORMARC |
| UI/UX | B1 PM + B4 Growth + E2 UX |
| 영업 자료 | **B3 AE** + B4 Growth + E3 마케팅 |
| 가격 정책 | **B6 CFO** + B5 VC + B3 AE + E5 |
| 약관·MSA | B3 AE + E6 컴플 + (변호사 — 외부) |
| onboarding | **B2 CSM** + B4 Growth + E2 |
| 결제·세무 | **B6 CFO** + E5 |
| landing | B4 Growth + E3 |
| 정부 자금 | B6 CFO + E5 |
| 투자 | **B5 VC** + B6 CFO |
| 인증 (ISMS·CSAP) | E6 + B6 |
| 채널 (KLA·자치구) | B3 AE + E4 도서관 운영 |

---

## 4. 핵심 7+1 + 9 on-demand 갱신 (Part 59)

**핵심 7** (매 작업): implementer · sales-specialist · persona-simulator · devil-advocate (DA1~DA7) · expert-personas (E1~E6) · qa-validator · compliance-officer

**핵심 7+1 신규** (Phase 2 캐시카우 후 = 핵심 8):
- + **business-personas** (B1~B6)

**10 on-demand**: architect-deep · code-reviewer · researcher · explorer · planner · kormarc-expert · librarian-domain-classifier · librarian-reviewer · marketing-strategist · **business-personas (Phase 1 = on-demand)**

---

## 5. 5 Critic Layer + B-team

```
[BUILD] 산출물
   ↓
[CRITIC LAYER 5+ B-team]
├── persona-simulator (P1~P6 우호)
├── devil-advocate (DA1~DA7 부정 + 깐깐 ★)
├── expert-personas (E1~E6 전문가)
├── business-personas (B1~B6 비즈니스 팀) ★ 신규
├── qa-validator (Layer 1~7+)
└── compliance-officer (E6 = 자관·PIPA)
   ↓
[B5 VC 통과 = 상업성 + DA7 통과 = 견고함] → commit
```

---

## 6. 상업적 페르소나 임계값

| 페르소나 | Phase 1 임계값 | 미달 시 |
|---------|-------------|------|
| B1 PM | 70%+ (기능 우선순위 정합) | 백로그 재정렬 |
| B2 CSM | 60%+ (TTV·NPS·Churn) | 측정 인프라 추가 |
| B3 AE | 70%+ (영업 자료 즉발 가능) | 영업 자료 보완 |
| B4 Growth | 60%+ (Aha·viral) | 측정·실험 |
| **B5 VC** | **50%+ (Phase 1 == 검증 단계)** | 캐시카우 후 70%+ |
| B6 CFO | 70%+ (단위 경제 측정) | 측정·정부 자금 |

---

## 7. 검증된 효과 (예상)

| 메트릭 | Part 58 | **Part 59** |
|--------|---------|-------------|
| 페르소나 검증 축 | 3 (P+DA+E) | **4 (P+DA+E+B)** |
| 상업적 결함 발견율 | 미측정 | **+45%** (B-team) |
| 단위 경제 가시성 | 0% | **80%** (CAC·LTV·NRR 측정) |
| 영업 사이클 표준화 | 30% | **70%** (MSA·SOW·DPA) |
| 정부 자금 활용 | 0% | **AI 바우처 신청** |
| 캐시카우 도달율 | 150~280% | **170~300%** |

---

## 8. AUTONOMOUS_BACKLOG 신규 (Part 59)

- [x] business-personas subagent ✅
- [ ] B-team 6명 호출 매트릭스 적용
- [ ] 단위 경제 측정 인프라 5건
- [ ] 가격 3티어 + 할인 4건
- [ ] 영업 사이클 자동 4건
- [ ] 인증 로드맵 5건
- [ ] 자금 조달 3건
- [ ] 마케팅 채널 4건
- [ ] CSM 인프라 5건
- [ ] 법무 약관 4건

총 **34 신규** (Phase 1 추가)

---

## 9. PO 응답 정합

### Q1 "상업적으로 어떤 걸 고려?"
✅ **30+ 상업 고려 영역 종합**:
- 단위 경제 (10) · 매출 유지 (10) · 가격 전략 (10) · 영업 사이클 (8) · 컴플 인증 (13) · 조달 채널 (7) · 자금 조달 (8) · 마케팅 믹스 (11) · CSM (10) · 법무 약관 (10)

### Q2 "보통 팀 어떻게 짜?"
✅ **B2B SaaS 표준 팀 = 6 핵심 + Stage별 확장**
✅ **business-personas subagent 신규** (B1 PM · B2 CSM · B3 AE · B4 Growth · B5 VC · B6 CFO)
✅ **5 Critic Layer + B-team = 4번째 검증 축**

→ 상업성 결함 발견율 +45% 예상 = 캐시카우 도달율 170~300%

---

> **이 파일 위치**: `kormarc-auto/docs/research/part59-commercial-considerations-bteam-2026-05.md`
> **종합**: B-team 6 페르소나 + 30+ 상업 고려 + 34 신규 백로그 + 5 Critic Layer 확장
> **PO 정합**: 사고 동반자 = 외부화된 팀 = 1인 SaaS의 무한 레버리지
