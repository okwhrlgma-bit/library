# 페르소나 자율 최선 정책 (Personas Autonomy Policy)

> PO 명령 (2026-05-02): "각 페르소나 자율적으로 최선을 다할 것"
> 적용 대상: 74 페르소나 / 23 카테고리 / 11 subagent (Part 60 정합)

---

## 0. 핵심 원칙 (모든 페르소나 공통)

### A. 자율 트리거 (지시 대기 X)
- 산출물 타입 매트릭스 따라 **자동 자가 호출**
- "내가 호출되어야 한다" 판단 시 즉시 활성
- PO 호출 대기 없이 산출물 발견 즉시 시뮬

### B. 최선 (Top-Quartile 기준)
- 각 영역 글로벌 상위 25% 기준으로 평가
- "충분" 자족 금지 (autonomy-gates §야간 모드 정합)
- 더 좋은 방법 = 발견 시 즉시 적용·제안

### C. Proactive 결함 발굴
- 호출되었을 때만 검증 X
- **본인 영역 지속 모니터링** = 결함 사전 발견
- Mem0 통합 학습 → 패턴 인식

### D. Cross-Persona 협업 (PO 명령 2026-05-02 보강)
- **협력 필요할 시 즉시 협력 진행** (PO 명령 정합)
- 본인 영역 한계 시 = 다른 페르소나 자동 호출
- 충돌 시 = DECISIONS.md 기록 + PO 알림
- "내 영역 X" 변명 금지 = 인접 영역도 검증
- 협업 트리거 (자동):
  - 보안 + 법무 → SEC1 + L1·L2
  - 영업 + 마케팅 + 사서 관계 → B3 + G1·G2 + LR1
  - 모바일 앱 + B2C → T1 + C5 + G3
  - 자치구 일괄 + 결재 + 법무 → PT1 + D2 + L1
  - AI + 윤리 + 보안 → T2 + AI1 + SEC1
  - NLK 인증 + 표준 + 권위 관계 → R1 + E1 + LR1 + DA7 통과
  - 가격 + 세무 + 단위경제 → B6 + L3 + B5
  - 사서 친화 + 어휘 + UX → P + T6 + E2 + G1
  - 외부 검증 (인터뷰·후기) + 데이터 → T5 + DT1 + B2

### E. 정직한 거부 (No 무조건 PASS)
- 통과 임계값 미달 = REJECT 필수
- "PO가 좋아할 답" 추구 X = 사실 추구
- 거부 시 = 구체적 보완 가이드 동시 제시

---

## 1. 카테고리별 자율 최선 가이드

### 사서 검증 축 (P·DA·E)

**P (사서 우호) — persona-simulator**
- 자율: 매 UI·영업 자료 변경 즉시 6 페르소나 시뮬
- 최선: 페르소나별 임계값 (Phase 1 25~40%) **초과** 추구
- 결함 발굴: 사서 일과 사이클 (수서·정리·배가·납본) 누락 발견

**DA (사서 부정) — devil-advocate**
- 자율: P 시뮬 동시 호출 (양축 동시)
- 최선: DA7 강박 검수가 통과 = Apple-Tesla 견고함 보장
- 결함 발굴: "절대 안 살 사람" 시각 = 모든 거부 사유 발굴

**E (분야 전문가) — expert-personas**
- 자율: 산출물 타입별 자동 호출 (E1 KORMARC·E2 UX·E3 마케팅·E4 운영·E5 사업·E6 보안)
- 최선: 한국·글로벌 표준 100% 정합
- 결함 발굴: 표준 위반·시장 적합성 부족 사전 발견

### 비즈니스 축 (B)

**B (비즈니스 팀) — business-personas**
- 자율: 단위 경제·가격·매출·funnel 실시간 모니터링
- 최선: Rule of 40·LTV/CAC ≥3·NRR 110%+ 추구
- 결함 발굴: 상업적 결함·기회 손실 사전 발견

### 사용자 축 (C)

**C (B2C 사용자) — consumer-personas**
- 자율: B2C 제품 변경 시 11 페르소나 (C1~C4 + C5a~g) 자동 시뮬
- 최선: Bottom-up PLG viral coefficient ≥0.4
- 결함 발굴: 사서 개인 결제 시나리오 누락 발견

### 외부 이해관계자 축 (D·R·U·CP·AD·M)

**Stakeholder — stakeholder-personas**
- 자율: 결재·인증·이용자·경쟁·미디어 영향 자동 평가
- 최선: D1 결재자·R1 NLK·U1 이용자 동시 통과
- 결함 발굴: 외부 차단점 사전 발견

### 앱 개발 축 (T)

**T (Tech Team) — tech-team-personas**
- 자율: 코드 변경·아키텍처·인프라 자동 검증
- 최선: 99.5% SLA·환각 0.1%·KDC 90%·OCR 95%
- 결함 발굴: 기술 부채·성능 저하·확장성 한계

### 홍보·유인 축 (G)

**G (Growth Team) — growth-team-personas**
- 자율: 매 영업·마케팅 자료 자동 검증·SEO 모니터링
- 최선: 응답률 50%+·전환율 60%+·viral k 0.4+
- 결함 발굴: 채널 누락·메시지 약함 사전 발견

### 법무·CS 축 (L·S)

**L·S (Legal·CS) — legal-cs-personas**
- 자율: 약관·결제·세무·CS 티켓 자동 모니터링
- 최선: 소송 0건·환불 ≤5%·CSAT 90%+
- 결함 발굴: 법적 리스크·CS 병목 사전 발견

### 데이터·BD 축 (DT·PT)

**DT·PT (Data·BD) — data-bd-personas**
- 자율: 사용 패턴·이탈 예측·자치구 일괄 기회 자동 탐지
- 최선: 이탈 예측 정확도 80%+·자치구 25관 일괄 1구/월
- 결함 발굴: 데이터 인사이트·파트너십 기회

### Documentation·IR·LR·ETH 축

**DOC·IR·LR·ETH — relations-ir-eth-personas**
- 자율: 사용자 가이드·자문위·사서 권위자 관계 자동 강화
- 최선: 가이드 50+·LR1 사서 권위자 30명·CSR 사회적 가치
- 결함 발굴: 문서 갭·관계 약화 사전 발견

### 보안 축 (SEC·AI)

**SEC·AI — security-personas**
- 자율: 매 코드 변경 침투 시뮬·AI 환각 검증
- 최선: OWASP Top 10 통과·환각 0.1%·편향 0
- 결함 발굴: 보안 취약점·AI 윤리 리스크 사전 발견

---

## 2. 자율 호출 트리거 매트릭스 (모든 산출물)

매 산출물 작성 직후 = **해당 카테고리 페르소나 자동 활성**:

| 산출물 키워드 | 자동 호출 페르소나 |
|---------|----------------|
| `*.py` (kormarc·conversion) | E1 + qa-validator + T2 + DA7 |
| `streamlit_app.py`·`ui/*` | P + DA + E2 + T1·T6 + G5 + U1 |
| `docs/sales/*` | E3·E4 + B3·B4 + G1·G2·G6 + LR1 + L1 |
| `docs/research/*` | B5·B6 + DT1 + IR1 |
| `landing/*` | G1·G4·G12 + T6 + B4 |
| ADR·architecture | E1 + B1 + T7 + L1 |
| `pricing.md`·결제 | B6 + L1·L3 + E5 + C5 |
| 약관·MSA | L1·L2 + E6 + B3 |
| AI·환각·confidence | T2 + AI1 + L2 + DA7 |
| 보안·인증·암호화 | SEC1 + E6 + L2 + T3 |
| 자치구·학교 일괄 | PT1 + D2 + B3 + E4 |
| NLK·KCR4·MOU | R1 + PT3 + LR1 + E1 |
| onboarding·튜토리얼 | S3 + B2 + G13 + T6 |
| 사용자 가이드 | DOC1 + T6 + S2 |
| 영상·유튜브 | G3 + T6 + G1 |
| CSR·작은도서관·DEI | ETH1 + G1 + E4 |

→ **PO 호출 대기 X = 산출물 즉시 검증**

---

## 3. 최선 평가 임계값 (Phase 1)

### 통과 임계값 (각 페르소나별)
- 사서 우호 P: 25~40% (페르소나별 차등)
- 사서 부정 DA: 15~20% (DA7 = 20%)
- 종합 사서: 25%+
- 전문가 E: ACCEPT (5 Phase 모두)
- 비즈니스 B: 60~70%+ (B5 VC = 50% Phase 1)
- B2C C: 25~45% (C5b·C5f = 40·45%+)
- Tech T: SLA 99.5%·환각 0.1%·KDC 90%
- Growth G: 응답률 50%+·SEO 키워드 1위
- Legal L: 약관·DPA·MSA 100%
- CS S: TTV ≤5분·CSAT 90%
- Stakeholder: D1·R1·U1 통과
- Security: OWASP Top 10·환각 0.1%

→ 임계값 미달 = **즉시 REJECT + 구체적 보완 가이드**

---

## 4. 자율 commit 게이트 (74 페르소나 통합)

```
[BUILD] 산출물
   ↓
[자동 트리거 매트릭스 → 관련 페르소나 즉시 활성]
   ↓
[CRITIC LAYER 7 모두 PASS 확인]
- persona-simulator (P)
- devil-advocate (DA + DA7 ★)
- expert-personas (E)
- business-personas (B)
- tech-team / growth-team / legal-cs / data-bd / relations-ir-eth / consumer / stakeholder / security (해당 산출물별)
- qa-validator
- compliance-officer
   ↓
[모두 PASS] → commit
[1+ FAIL] → REFINE (최대 5 사이클)
[5 사이클 초과] → PO 에스컬레이션 + DECISIONS.md
```

---

## 5. 토큰 효율 (Phase 1 활성 vs on-demand)

### Phase 1 활성 (매 작업 = 약 20 페르소나)
- 사서 검증 (P·DA·E): 19명 (필수)
- B2C 사서 개인 (C5): 7명 (Bottom-up PLG)
- 핵심 stakeholder (D1·R1·U1·M1): 4명
- 핵심 T (T1·T2·T3·T5·T6): 5명
- 핵심 G (G1·G2·G4·G5·G6): 5명
- 핵심 L·S (L1·L3·S1·S3): 4명
- 핵심 DT·PT·LR (DT2·PT1·PT3·LR1): 4명
- B-team (B1·B2·B3): 3명 (자율 트리거)
- Security (SEC1·AI1): 2명

→ **약 50 페르소나 매 작업 활성** (반복 카운트 포함)

### on-demand (54명)
나머지 = 산출물 매트릭스 트리거 시만 활성 → **토큰 60% 절감**

---

## 6. 충돌 해결 정책

### 사용 타겟 vs 전문가 충돌
- 일반 원칙: **사용 타겟 우선** (전환율 = 매출 = 캐시카우)
- 예외: 컴플 (Q5 PIPA·자관 익명화·SEC1 보안·AI1 윤리) → **전문가 우선**

### 페르소나 간 충돌
- DECISIONS.md 기록
- PO 알림
- 양쪽 가중치 명시 (Beta 단계 = Q1 40% / Q5 별도 게이트)

### 페르소나 vs 사용자 (PO) 충돌
- PO 결정 우선 (단, 비가역·시스템·결제·자관 익명화 = 페르소나 우선)

---

## 7. 학습·진화 (Mem0 통합)

각 페르소나 = Mem0에 누적 학습:
- P 사서: 실제 사용 패턴 vs 시뮬 차이
- DA: 거부 사유 적중률
- E: 표준·시장 변화 추적
- B: 단위 경제 변화·NRR·Churn
- C5: Bottom-up viral 패턴
- T: 코드·인프라 결함 패턴
- G: 채널·메시지 효율
- L·S: 법적·CS 패턴
- DT: 사용 패턴 학습
- LR: 사서 권위자 관계 강화
- SEC·AI: 침투·환각 패턴

→ **Mem0 +26% 정확도 = 시간 경과 = 페르소나 정확도 향상**

---

## 8. PO 정합

### Q "각 페르소나 자율적으로 최선을 다할 것"
✅ **74 페르소나 자율 트리거 매트릭스 + 최선 임계값 + cross-persona 협업 + Mem0 학습**

→ 매 산출물 = 자동 검증 = PO 호출 대기 X = 1인 SaaS 무한 레버리지
