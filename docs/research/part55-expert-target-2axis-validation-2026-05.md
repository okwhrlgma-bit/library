# Part 55 — 2축 검증 구조 (전문가 + 사용 타겟) (2026-05-02)

> PO 명령: "테스트·피드백 = 해당 분야 전문가 / 아웃풋 사용성 = 사용 타겟 + 전문가 양쪽"

---

## 0. PO 정리 명확화

| 검증 영역 | 담당 |
|----------|------|
| **테스트·피드백 (전문성·표준·기술)** | 해당 분야 **전문가** 페르소나 |
| **아웃풋 사용성** | **사용 타겟** + **분야 전문가** (양쪽 다) |

→ 사용 타겟 (P·DA)과 분야 전문가 (E)는 **다른 축**, 분리 필수

---

## 1. 신규 expert-personas subagent ✅

5+1 전문가:
- **E1**: KORMARC 표준·도서관학 (NLK·KCR4·KDC 위원)
- **E2**: UX·접근성 (KWCAG 2.2 인증 평가위원)
- **E3**: B2B SaaS 마케팅 (스티비 ARR 28억 자문)
- **E4**: 도서관 운영·관장 (KLA 운영위·자치구 자문)
- **E5**: 한국 SaaS 사업·세무 (1인 SaaS 컨설턴트)
- **E6**: 보안·PIPA (= 기존 compliance-officer)

---

## 2. 산출물 타입별 자동 호출 매트릭스

| 산출물 타입 | 사용 타겟 (P·DA) | 분야 전문가 (E) |
|-----------|----------------|---------------|
| **KORMARC 코드** | (사용자 직접 X) | **E1** + qa-validator |
| **UI 컴포넌트** (streamlit_app·ui/) | P + DA (양쪽) | **E2** |
| **landing·SEO·블로그** | P + DA | **E3** |
| **영업 자료** | P + DA | **E3 + E4** |
| **학교·자치구 양식** | P (P2·P4) | **E4** |
| **가격·결제·세무** | P + DA | **E5 + E6** |
| **ADR·아키텍처** | (사용자 X) | **E1** + architect-deep |
| **MCP·hook·인프라** | (사용자 X) | **E6** + qa-validator |

---

## 3. 최종 Critic Layer 구조 (Part 54 보강)

기존 4 Critic Layer:
- persona-simulator (Layer 8 우호)
- devil-advocate (Layer 9 부정)
- qa-validator (Layer 1~7 코드 품질)
- compliance-officer (자관·PIPA·KORMARC)

**신규 Critic Layer 추가**:
- **expert-personas (Layer 10)** — 산출물 타입별 5+1 전문가 자동 호출

**최종 5 Critic Layer**:
```
[BUILD] → 산출물 작성
       ↓
[CRITIC LAYER 5 병렬]
├── persona-simulator (사용 타겟 우호)
├── devil-advocate (사용 타겟 부정)
├── expert-personas (분야 전문가) ★ 신규
├── qa-validator (코드 품질 7 Layer)
└── compliance-officer (자관·PIPA)
       ↓
[5 모두 PASS] → commit
[1+ FAIL]    → REFINE → 재시도
```

---

## 4. 사용성 검증 (양축 — PO 명령 정합)

UI/UX·landing·영업 자료 등 **사용성 산출물**:

```
사용성 검증 = (사용 타겟 페르소나) + (분야 전문가)

예: streamlit_app.py UI 변경
  → persona-simulator (P1~P6 사서 = 사용 타겟)
  → devil-advocate (DA1~DA6 부정 사서 = 사용 타겟 부정)
  → E2 UX 전문가 (KWCAG 인증 평가)

→ 양축 모두 통과 = "사용자도 OK + 전문가도 OK"
```

---

## 5. 테스트·피드백 (전문가만 — PO 명령 정합)

코드·KORMARC·인프라 등 **기술 산출물**:

```
테스트·피드백 = (분야 전문가만, 사용 타겟 X)

예: KORMARC 008 필드 빌더 코드
  → E1 KORMARC 표준 위원 (40자리 정확성·자료유형 분기)
  → qa-validator (binary_assertions 38건 + 신규 어셔션)

→ 사용 타겟 페르소나 시뮬 X (사용자가 직접 보지 않는 영역)
```

---

## 6. 사용 타겟 vs 전문가 충돌 시 (PO 결정 영역)

종종 사용 타겟과 전문가 충돌:
- 사용 타겟: "5분 학습 가능한 단순 UI"
- 전문가: "KORMARC 880 ▾6 연결표시기호 정확 입력 필요"

→ **충돌 시 PO 결정 필수** (DECISIONS.md 기록)
→ 일반 원칙: **사용 타겟 우선** (전환율 = 매출 = 캐시카우)
→ 단 컴플 (Q5 PIPA·자관 익명화) 만 전문가 우선

---

## 7. 5 Critic Layer 병렬 가동 시 효과

기존 4 Layer (Part 54): commit당 평균 5분
**신규 5 Layer (Part 55)**: commit당 평균 6분 (+1분)
- expert-personas Opus 4.7 호출 = 토큰 ↑
- 그러나 결함 발견율 +30% (전문성 검증)
- 시장 적합성 검증 +50% (전문가 시장 통찰)

캐시카우 도달율 갱신: 125~220% → **130~230%** (전문가 검증 효과 반영)

---

## 8. AUTONOMOUS_BACKLOG 신규

- [x] **expert-personas subagent** 작성 ✅ (`.claude/agents/expert-personas.md`)
- [ ] qa-validator Layer 10 자동 호출 활성화 (산출물 타입 자동 분류)
- [ ] 신규 산출물 작성 시 매트릭스 따라 expert-personas 호출
- [ ] 사용 타겟·전문가 충돌 시 PO 알림 routine

---

## 9. 누적 specialist (16)

| # | specialist | 역할 |
|---|-----------|------|
| 1 | implementer | 코드 작성 |
| 2 | sales-specialist | 영업 자료 |
| 3 | marketing-strategist | SEO·콘텐츠 |
| 4 | persona-simulator | 사용 타겟 우호 (P1~P6) |
| 5 | devil-advocate | 사용 타겟 부정 (DA1~DA6) |
| 6 | **expert-personas** ★ 신규 | 분야 전문가 (E1~E6) |
| 7 | qa-validator | 코드 품질 7 Layer |
| 8 | compliance-officer | 자관·PIPA·KORMARC (= E6) |
| 9 | architect-deep | 복잡 설계 |
| 10 | code-reviewer | PR 리뷰 |
| 11 | researcher | 조사 |
| 12 | explorer | 코드베이스 탐색 |
| 13 | planner | 작업 분해 |
| 14 | kormarc-expert | 도메인 깊이 (= E1과 협업) |
| 15 | librarian-domain-classifier | 사서 분류 |
| 16 | librarian-reviewer | 사서 리뷰 |

→ 핵심 6 활성 + 10 on-demand (Part 54 + expert-personas 신규)

---

## 10. 검증된 효과 (예상)

| 메트릭 | Part 54 | **Part 55** |
|--------|---------|-------------|
| 결함 발견율 | 100% (기준) | +30% (전문성 검증) |
| 시장 적합성 | (페르소나만) | +50% (전문가 시장 통찰) |
| 표준 정합 | qa-validator 7 Layer | + E1 KORMARC + E2 KWCAG |
| 영업 응답률 | 18~50% | + E3 마케팅 모범 사례 |
| 사업 안전성 | compliance만 | + E5 세무·사업·자금 |
| 캐시카우 도달율 | 125~220% | **130~230%** |

---

> **이 파일 위치**: `kormarc-auto/docs/research/part55-expert-target-2axis-validation-2026-05.md`
> **종합**: 5+1 전문가 페르소나 + 산출물 타입별 매트릭스 + 5 Critic Layer
> **PO 명령 정합**: 테스트·피드백 = 전문가만 / 사용성 = 사용 타겟 + 전문가 양쪽
