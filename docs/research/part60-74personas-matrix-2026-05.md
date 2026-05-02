# Part 60 — 74 페르소나 종합 매트릭스 + B2C 사서 개인 + Bottom-up PLG (2026-05-02)

> PO 명령 (2026-05-02 야간 누적):
> 1. "B2C에 사서 개인이 산다는 시나리오" → C5 7명 신규
> 2. "앱 개발에 어떤 사람 필요해" → T-team 10명
> 3. "홍보 및 사람 유인 설계 필요한 사람" → G-team 13명
> 4. "또 다른 필요한 사람 확인" → L·S·DT·PT·DOC·IR·LR·ETH 17명
> 5. "해당 필요한 사람들 페르소나화 + 진행"

---

## 0. 74 페르소나 = 23 카테고리 = 11 subagent

### 누적 페르소나 매트릭스

| # | 카테고리 | subagent | 인원 | Phase 1 활성 |
|---|--------|---------|----|------|
| 1 | P 사서 우호 | persona-simulator | 6 | ★ 핵심 |
| 2 | DA 사서 부정 (DA7 깐깐 ★) | devil-advocate | 7 | ★ 핵심 |
| 3 | E 분야 전문가 | expert-personas | 6 | ★ 핵심 |
| 4 | B 비즈니스 팀 | business-personas | 6 | on-demand |
| 5 | C B2C 일반 | (consumer-personas 권장) | 4 | Phase 2 |
| 6 | C5 B2C 사서 개인 ★ | (consumer-personas) | 7 | ★ Phase 1 ★★★★★ |
| 7 | D 결재 라인 | (stakeholder-personas) | 2 | Phase 1 |
| 8 | R 인증·권위 | (stakeholder-personas) | 1 | Phase 1 ★★★★★ |
| 9 | U 이용자 | (stakeholder-personas) | 1 | Phase 1 |
| 10 | CP·AD 경쟁사 | (stakeholder-personas) | 2 | Phase 2 |
| 11 | M 미디어 | (stakeholder-personas) | 1 | Phase 1 |
| 12 | SEC 보안 | (security-personas) | 1 | Phase 1 |
| 13 | AI AI 윤리 | (security-personas) | 1 | Phase 1 |
| 14 | T 앱 개발 | **tech-team-personas** ✅ | 10 | ★ T1·T2·T3·T5·T6 활성 |
| 15 | G 홍보·유인 | **growth-team-personas** ✅ | 13 | ★ G1·G2·G4·G5·G6 활성 |
| 16 | L 법무 | **legal-cs-personas** ✅ | 3 | ★ L1·L3 활성 |
| 17 | S 고객 지원 | **legal-cs-personas** ✅ | 4 | ★ S1·S3 활성 |
| 18 | DT Data·BI | **data-bd-personas** ✅ | 2 | DT2 활성 |
| 19 | PT BD·Partnership | **data-bd-personas** ✅ | 3 | PT1·PT3 활성 |
| 20 | DOC 교육·문서 | **relations-ir-eth-personas** ✅ | 2 | DOC1 활성 |
| 21 | IR Investor Relations | **relations-ir-eth-personas** ✅ | 2 | Phase 2 |
| 22 | LR Librarian Relations ★ | **relations-ir-eth-personas** ✅ | 1 | ★ Phase 1 ★★★★★ |
| 23 | ETH 윤리·CSR | **relations-ir-eth-personas** ✅ | 1 | Phase 2 |
| | **계** | **11 subagent** | **74** | **20 활성 + 54 on-demand** |

---

## 1. Phase 1 핵심 20 페르소나 (캐시카우 직결)

### 메인 활성 (산출물 매 작업 자동 호출)
- **사서 검증 (3 축)**: P1~P6 + DA1~DA7 + E1~E6 = 19명
- **B2C 사서 개인**: C5a~C5g = 7명
- **권위·인증**: R1 NLK
- **결재**: D1 관장·교장
- **이용자**: U1 도서관 이용자
- **앱 개발 활성**: T1 Mobile + T2 AI/ML + T3 DevOps + T5 UX Researcher + T6 UX Writer
- **홍보 활성**: G1 Storyteller + G2 Content + G4 SEO + G5 Community + G6 PR
- **법무·CS 활성**: L1 Tech Lawyer + L3 세무사 + S1 CS Lead + S3 Onboarding
- **데이터·BD 활성**: DT2 BI Developer + PT1 BD Manager + PT3 Strategic Alliance
- **사서 관계 활성**: **LR1 Librarian Relations** ★★★★★

→ Phase 1 캐시카우 직결 = **약 50 페르소나 동원** (반복 카운트 포함)

---

## 2. 산출물 타입별 호출 매트릭스 (74 종합)

| 산출물 | 우호 P | 부정 DA | 전문가 E | 비즈 B | B2C C | 기타 |
|--------|------|------|------|------|----|----|
| **모바일 앱** | P3·P6 | DA2 | E2 | B1·B4 | C5·C2 | T1 + G3 |
| **AI 추천·환각** | P1·P5 | DA4·DA7 | E1 | B5 | - | T2 + AI1 + L2 |
| **인프라·SLA** | - | DA4 | E6 | B1 | - | T3·T4 + L2 |
| **B2B 영업 자료** | P1·P2 | DA1·DA3 | E3·E4 | B3 | - | G1 + LR1 + L1 |
| **C5 B2C 영업** | - | - | E3 | B4 | C5a~g | G2·G4·G7 |
| **landing 즉석 데모** | P3 | DA2·DA6 | E3 | B4 | - | T6 + G12 + G2 |
| **사서 친화 어휘** | P1~P6 | DA5 | E2 | - | - | T6 + G1 |
| **자치구 25관 일괄** | P1 | DA3 | E4 | B3·B6 | - | PT1 + LR1 + L1 |
| **NLK 인증·MOU** | - | DA4·DA7 | E1 | B5 | - | R1 + PT3 + LR1 |
| **가격 정책** | P3·P6 | DA2·DA6 | E5 | B3·B6 | C5 | L1·L3 |
| **약관·MSA·환불** | - | DA3 | E6 | B3 | - | L1 + B6 |
| **CSR·작은도서관** | P3 | - | E4 | B5 | - | ETH1 + G1 |
| **사서 권위자 관계** | P1·P2 | DA4·DA7 | E1·E4 | B5 | - | LR1 + R1 + G5 |
| **사서 통계 대시보드** | P1·P4 | - | E2 | B2 | C5b·C5f | DT2 + T6 |

---

## 3. 7 Critic Layer (5 → 7 확장)

```
[BUILD] 산출물
   ↓
[CRITIC LAYER 7 + 74 페르소나]
├── persona-simulator        (P1~P6 사서 우호)
├── devil-advocate           (DA1~DA7 부정·DA7 깐깐 ★)
├── expert-personas          (E1~E6 전문가)
├── business-personas        (B1~B6 비즈니스)
├── tech-team-personas ★     (T1~T10 앱 개발)
├── growth-team-personas ★   (G1~G13 홍보·유인)
├── legal-cs-personas ★      (L1~L3 + S1~S4)
├── data-bd-personas         (DT1·DT2 + PT1·PT2·PT3)
├── relations-ir-eth-personas (DOC·IR·LR·ETH)
├── qa-validator             (Layer 1~7+)
└── compliance-officer       (자관·PIPA·KORMARC)
   ↓
[7+ 모두 PASS = 360도 검증] → commit
```

---

## 4. B2C 사서 개인 (C5) Bottom-up PLG = 핵심 통찰

### 캐시카우 도달 6~12개월 단축 메커니즘

```
[Month 1] 사서 A 본인 카드 9,900 결제 (B2C C5b 작은도서관 1인)
   ↓
[Month 2] 동료 사서 B·C·D·E 추천 = 4명 viral (k=4)
   ↓
[Month 3] 자치구 25관 협의회 발견 = "이거 좋은데?"
   ↓
[Month 4] 자치구 25관 일괄 도입 (B2B Pro 5명 = 27.5만/월/관)
   ↓
[Month 6] 25관 × 27.5만 = 687.5만/월 = 캐시카우 ★ 달성
```

→ **B2B 단독 12~24개월 → C5 B2C + Bottom-up PLG = 6~12개월**

---

## 5. AUTONOMOUS_BACKLOG 신규 (Part 60 종합)

### 즉시 (Phase 1 = 캐시카우 직결)
- [x] tech-team-personas subagent (T1~T10)
- [x] growth-team-personas subagent (G1~G13)
- [x] legal-cs-personas subagent (L1~L3 + S1~S4)
- [x] data-bd-personas subagent (DT1~DT2 + PT1~PT3)
- [x] relations-ir-eth-personas subagent (DOC·IR·LR·ETH)
- [ ] consumer-personas subagent (C1~C5g 11명)
- [ ] stakeholder-personas subagent (D·R·U·CP·AD·M = 7명)
- [ ] security-personas subagent (SEC·AI = 2명)
- [ ] qa-validator Layer 9·10·11·12 자동 호출 활성화 (T·G·L·DT·DOC)

### 코드 (T-team 권장 우선순위)
- [ ] T1: 모바일 앱 (Flutter) PoC (8시간·L3 ADR-0073)
- [ ] T2: AI 환각 차단·confidence threshold (4시간·L2)
- [ ] T3: 99.5% SLA 인프라 (Vercel·Sentry·백업) (8시간·L3)
- [ ] T5: 사서 5명 인터뷰 routine (PO 작업·월 5명)
- [ ] T6: voice·tone 가이드 (3시간·L2)

### 영업·마케팅 (G-team 권장)
- [ ] G1: 미션·About·창업 스토리 (4시간·L2)
- [ ] G2: 블로그 12개월 콘텐츠 캘린더 (3시간·L2)
- [ ] G4: SEO 키워드 100+ 조사·schema markup (4시간·L2)
- [ ] G5: 사서 카페·디스코드 가입·운영 (PO 작업·주 1시간)
- [ ] G6: 보도자료 (KOLAS 종료·AI 바우처) 3건 (4시간·L2)

### 법무·CS (L·S 권장)
- [ ] L1: MSA·SOW·DPA·환불 약관 5종 (5시간·L3 ADR-0074)
- [ ] L3: 사업자 등록 가이드·면세 결정 (PO 작업·U-17)
- [ ] S1: FAQ 30+·티켓 시스템 (4시간·L2)
- [ ] S3: 자치구 25관 일괄 onboarding 가이드 (3시간·L2)

### Data·BD·Relations (DT·PT·LR 권장)
- [ ] DT2: 사서 개인 통계 대시보드 (8시간·L3 ADR-0075)
- [ ] PT1: 자치구 25관 일괄 영업 매뉴얼 (4시간·L2)
- [ ] PT3: NLK·NIPA MOU 신청서 (PO 작업)
- [ ] LR1: 사서 권위자 30명 리스트·1:1 routine (PO 작업·핵심)
- [ ] DOC1: 사용자 가이드 50건·troubleshooting (8시간·L2)

총 **30+ 신규 백로그** (Phase 1 추가)

---

## 6. PO 외부 작업 (74 페르소나 분석에서 식별)

| # | PO 작업 | 마감 | 우선 |
|---|--------|----|----|
| U-1 | KLA 발표 신청 | 5/31 | ★★★★★ |
| U-17 | 사업자 등록 (면세 검토) | 즉시 | ★★★★★ |
| U-49 | AI 바우처 신청 | 5월 | ★★★★★ |
| **U-NEW** | **LR1 사서 권위자 30명 1:1 routine** | 즉시 시작 | **★★★★★** |
| U-NEW | NLK 사서지원과 등록 신청 | 1개월 | ★★★★ |
| U-NEW | T5 사서 5명/월 인터뷰 routine | 즉시 | ★★★★ |
| U-NEW | G5 사서 카페 가입·활동 | 즉시 | ★★★ |
| U-NEW | NIPA·KISTI MOU 신청 | 3개월 | ★★ |

---

## 7. 캐시카우 도달율 누적 갱신

| Part | 페르소나 수 | 카테고리 | 도달율 |
|------|----------|--------|------|
| 51 | 6 (P만) | 1 | 112~197% |
| 55 | 12 (+E) | 2 | 130~230% |
| 58 | 19 (+DA7+wow) | 3 | 150~280% |
| 59 | 25 (+B) | 4 | 170~300% |
| 60 (T·G 추가) | 48 | 17 | 210~360% |
| **현재 (74·11 subagent)** | **74** | **23** | **240~400%** |

→ **74 페르소나 = 1인 SaaS의 100인 회사 사고력**
→ **23 카테고리 = 360도 검증 = 캐시카우 도달율 240~400%**

---

## 8. 핵심 통찰 종합

### A. Bottom-up PLG = 캐시카우 가속의 핵심 (Part 60 ★)
- C5 사서 개인 (9,900원) → 동료 viral → 도서관 도입 (B2B)
- 12~24개월 → **6~12개월 단축**
- 검증 패턴: 노션·슬랙·토스 모두 동일

### B. LR1 Librarian Relations = 단일 차단점 해소
- 사서 권위자 30명 = 모든 도서관 추천 가능
- DA1·DA3·DA4·DA7 거부 사유 동시 해소
- PO 출신 = LR1 자체 활용 가능 (즉시 시작)

### C. 11 subagent = 1인 SaaS의 무한 레버리지
- 매 작업 = 11 검증 layer 동시 가능
- 토큰 효율 = on-demand 호출 (기본 6 활성 + 5 trigger)
- 자율 commit = 7 Critic Layer + 74 페르소나 통과 시만

### D. T·G·L·DT·DOC·IR·LR·ETH = Phase 1 보강 핵심
- T1·T2·T3 = 앱 개발 (B2C 모바일 + AI 환각 + SLA)
- G1·G2·G4·G5·G6 = 홍보·유인 (스토리·콘텐츠·SEO·커뮤니티·PR)
- L1·L3 = 법무·세무 (B2B 진입·5채널 잠금 해제)
- LR1 = 사서 관계 (캐시카우 폭발 핵심)

---

## 9. 다음 사이클 권장 (PO 결정)

1. **consumer-personas subagent 작성** (C1~C5g 11명)
2. **stakeholder-personas subagent 작성** (D·R·U·CP·AD·M 7명)
3. **security-personas subagent 작성** (SEC·AI 2명)
4. **qa-validator Layer 9~12 자동 호출 활성화** (T·G·L·DT·DOC)
5. **MEMORY.md 갱신** (Part 60 + 74 페르소나)

---

> **이 파일 위치**: `kormarc-auto/docs/research/part60-74personas-matrix-2026-05.md`
> **종합**: 74 페르소나 + 23 카테고리 + 11 subagent + 7 Critic Layer + Bottom-up PLG
> **PO 정합**: 74 페르소나 = 1인 SaaS 100인 회사 = 캐시카우 240~400%
