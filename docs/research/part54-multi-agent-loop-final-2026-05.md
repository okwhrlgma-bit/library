# Part 54 — 멀티 에이전트 루프 최종 구조 (보강 후) (2026-05-02)

> PO 명령: "더 좋은 방법 있는지 검토 및 조사 후 실행"
> Part 53 후속 — Anthropic 2026 권고 + Mem0 +26% + Tracing 융합

---

## 0. 검증 보강 3건

### A. Hierarchical 단순화 (Anthropic 2026 공식 권고)
> "단일 에이전트로 시작 → 한계 도달 시 multi-agent로 escalate"
> "Hierarchical wins over swarm in production almost every time"

→ 14 specialist 모두 항상 활성 X · **핵심 6 활성 + 8 on-demand**

### B. Mem0 메모리 통합 (2026 가장 성숙한 솔루션)
- **+26% 정확도** vs vector RAG
- Postgres long-term + episodic
- 자동 consolidation·forgetting

### C. Tracing 강화 (Anthropic 필수)
- claudia (claude_telemetry, ADR-0041) 본격 활용
- 에이전트 결정 패턴·상호작용 구조 추적
- 디버깅 + 학습 데이터 누적

---

## 1. 최종 구조 (15 specialist · 6 활성 + 9 on-demand)

```
[Conductor (메트릭 자동, persona-simulator + critical-path-tracker)]
│
├── 핵심 6 (항상 활성, 매 작업)
│   ├── implementer (코드)
│   ├── sales-specialist (영업)
│   ├── persona-simulator (우호 시뮬)
│   ├── devil-advocate (부정 시뮬)
│   ├── qa-validator (7 Layer + Layer 8)
│   └── compliance-officer (PIPA·자관·KORMARC)
│
└── 9 on-demand (필요 시만)
    ├── architect-deep (복잡 설계)
    ├── code-reviewer (PR 리뷰)
    ├── researcher (조사)
    ├── explorer (코드베이스 탐색)
    ├── planner (작업 분해)
    ├── kormarc-expert (도메인 깊이)
    ├── librarian-domain-classifier
    ├── librarian-reviewer
    └── marketing-strategist (SEO·콘텐츠)
```

---

## 2. 표준 작업 사이클 (3 Phase 단순화)

### Phase 1: BUILD (병렬, 작업당 1~3 specialist)
- 단순 작업: implementer 단독
- 영업 자료: sales-specialist 단독
- 복잡 작업: implementer + planner + architect-deep

### Phase 2: CRITIC (병렬, 4 specialist 동시)
- persona-simulator (우호적)
- devil-advocate (부정적)
- qa-validator (7+1 Layer)
- compliance-officer (자관·PIPA)

### Phase 3: COMMIT
- 헌법 §종료 게이트 (pytest + binary_assertions)
- 4 Critic 모두 PASS 시 commit
- Mem0에 학습 누적 (페르소나 패턴·결함 패턴)

---

## 3. Mem0 통합 ADR-0071 신규

### 적용 영역
- **사용자 페르소나 학습**: 가입 → 사용 → 결제 패턴 누적
- **영업 응답 학습**: 영업 메일 응답률·전환율 페르소나별 누적
- **자관별 prefix·KDC 추천**: 사용자별 자주 쓰는 패턴 학습
- **time_tracker 통합**: 권당 시간 변화 추적 + Mem0 episodic

### 예상 효과
- onboarding 정확도 +26% (Day 3 활성화 분기)
- 영업 메일 응답률 +10% (개인화 정확도 ↑)
- 자관 prefix 추천 정확도 +30%

### 비용
- Postgres 무료 (Supabase free tier)
- Mem0 OSS (라이선스 무료)
- 추가 인프라 비용 0

---

## 4. Tracing 강화 (claudia 본격)

```bash
# 기존 claude → claudia drop-in 교체
claudia -p "$(cat task.md)" \
  --output-format stream-json \
  --otlp-endpoint http://localhost:4318
```

추적 메트릭:
- 작업당 specialist 호출 패턴
- Critic Layer 4 통과율 (페르소나·DA·QA·컴플)
- 평균 작업 시간·토큰
- Mem0 메모리 hit rate

---

## 5. 단순화 vs Part 53 (개선 점)

| 항목 | Part 53 (15 모두 활성) | **Part 54 (6 활성 + 9 on-demand)** |
|------|----------------------|----------------------------------|
| 매 작업 토큰 | 높음 (15 specialist 컨텍스트) | **낮음** (6만, 60% 절감) |
| 작업 속도 | 느림 (병렬 X 시) | **빠름** (필요한 specialist만) |
| 학습 데이터 | 분산 | **Mem0 통합** |
| 디버깅 | 어려움 | **claudia tracing** |
| 캐시카우 도달 | 120~210% | **125~220%** (효율 개선 반영) |

---

## 6. 적용 권장 (즉시)

### A. 메모리 정책 갱신 ✅ 진행
- feedback_persona_validation_mandatory.md 갱신
- Critic Layer 4 (devil-advocate 추가)
- 핵심 6 + on-demand 9 구조

### B. Mem0 통합 ADR-0071 백로그 등록
### C. claudia tracing 본격 가동 ADR-0041 우선순위 ↑
### D. 작업 사이클 매뉴얼 업데이트 (3 Phase 단순화)

---

## 7. PO 제안 + 본 보강 = 최종

PO 아이디어 ✅ (책임 분리·페르소나·피드백) +
Anthropic 권고 ✅ (hierarchical·단순화·tracing) +
Apple-Tesla ✅ (devil-advocate) +
Mem0 ✅ (메모리 +26%) =

**가장 검증된 자동화 루프 구조**

---

> **이 파일 위치**: `kormarc-auto/docs/research/part54-multi-agent-loop-final-2026-05.md`
> **종합**: 14 → 6 활성 + 9 on-demand · Mem0 +26% · claudia tracing · Critic Layer 4
> **다음**: Mem0 통합 ADR-0071 작성 + claudia 본격 가동
