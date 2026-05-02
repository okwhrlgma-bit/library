# Part 56 — Anthropic 권장사항 전수 조사·선별 적용 (2026-05-02)

> PO 명령: "엔트로픽 권장사항 전부 조사 + 좋은 것만 적용"

---

## 0. Anthropic 공식 권장사항 12 영역

| # | 영역 | 출처 | 현재 상태 |
|---|------|------|---------|
| 1 | CLAUDE.md (프로젝트 헌법) | Best Practices | ✅ 적용 |
| 2 | Hooks (deterministic 100%) | Hooks Guide | ✅ 적용 (irreversible·stop) |
| 3 | Subagents (격리 컨텍스트) | Subagents Doc | ✅ 16종 적용 |
| 4 | Skills (모듈화) | Skills Doc | ✅ 일부 적용 |
| 5 | MCP (외부 도구) | MCP Doc | ✅ data4library 등 적용 |
| 6 | Plan Mode (분리 실행) | Best Practices | ✅ 적용 |
| 7 | Memory (~/.claude/...) | Memory Doc | ✅ 17+ 메모리 |
| 8 | Prompt Caching | Caching Doc | ✅ 모듈 적용 (Part 47) |
| 9 | Extended Thinking | Extended Thinking | ✅ 일부 적용 |
| 10 | Test 피드백 루프 (2-3x 품질) | Best Practices | ✅ binary_assertions 38건 |
| 11 | Files API (대용량) | Files API | ✅ cc-automation §21 |
| 12 | Tool Use (구조화 출력) | Tool Use | ✅ 적용 |

→ **12 핵심 영역 모두 이미 적용** (kormarc-auto 성숙도 ★)

---

## 1. 신규 발견·좋은 것만 선별 (5건)

### A. 컨텍스트 윈도우 30% 임계값 ⭐ (Anthropic 공식)
> "신규 40% 이하·경험자 30% 이하·생각 60%"

현재 헌법 §컨텍스트 관리 명시 X.
**적용**: CLAUDE.md 헌법에 임계값 추가 + /compact 자동 트리거 hook

### B. 20K+ longform 데이터 = 위에 배치 (+30% 성능) ⭐
> "Long documents top, queries/instructions bottom"

영업 자료 시스템 프롬프트 구조 갱신 필요.
**적용**: prompt_cache_helper.py에 longform-first 정책 명시

### C. LSP 플러그인 활성화 ⭐ (단일 최고 영향)
> "Single highest-impact plugin"

현재 ruff·mypy 있음. LSP 모드 활성화 X.
**적용**: pyright LSP 또는 mypy --watch 활성화

### D. Citations API ⭐⭐ (영업 자료 신뢰 직결)
> "Built-in source attribution"

영업 자료 30+ = 출처 표시 수동.
**적용**: Citations API로 자동 출처 (E1·E3·E4 권위 인용 자동화)

### E. Skills 우선 시작 (Anthropic 권장)
> "Start with skills (easiest, highest immediate value)"

현재 .claude/skills/ 활용 부족.
**적용**: 자주 쓰는 작업 5종 → skill 변환:
- KORMARC 880 한자 자동 (vernacular)
- 자관 prefix 검출 (sanity-check)
- 권당 시간 측정·차트 (time_tracker)
- 영업 자료 작성 (sales-specialist 트리거)
- 페르소나 시뮬 호출 (persona/devil/expert)

---

## 2. 적용 X — 부적합 (PO 결정 영역)

| Anthropic 권장 | kormarc-auto 부적합 사유 |
|---------------|-----------------------|
| **Opus 4.7 default** | 비용 ↑ (Sonnet 4.6 충분, 1인 SaaS) — PO 결정 |
| **Managed Agents** (호스팅) | 대규모 기업용·월 $XXX | 가능성 낮음 |
| **Agent Teams 본격** | Opus 4.6+ 전용 = 비용 폭증 |
| **swarm 패턴** | "research only" — production X (Anthropic 권고) |

---

## 3. 즉시 적용 (5 신규 권장)

### A. 헌법 §컨텍스트 임계값 추가
```markdown
## §15 컨텍스트 관리 (Anthropic 권장 정합)
- 본 세션 컨텍스트 30% 초과 시 /compact 자동
- 60% 초과 = 강제 /clear 또는 분리 세션
- 신규 사용자: 40% 이하
```

### B. prompt_cache_helper.py longform 정책
```python
# 시스템 프롬프트 구조 (Anthropic +30% 검증)
system = [
    {"text": LONGFORM_DATA, "cache_control": "ephemeral"},  # ★ 위
    {"text": QUERIES_AND_INSTRUCTIONS},  # 아래
]
```

### C. mypy LSP 활성화 (개발 효율)
- pyproject.toml dev-extras에 `mypy[d]` 추가
- VS Code Pylance + mypy 동시
- 매 편집 후 자동 진단

### D. Citations API ADR-0072
- 영업 자료 30+ → 출처 자동 인용
- E1 KORMARC 권위·E3 마케팅 사례·E4 도서관 운영 정책
- 신뢰 ↑ (Anthropic 검증 패턴)

### E. Skills 5종 신규 ADR-0073
- `.claude/skills/kormarc-880-vernacular/SKILL.md`
- `.claude/skills/sanity-check-prefix/SKILL.md`
- `.claude/skills/time-tracker-chart/SKILL.md`
- `.claude/skills/sales-write/SKILL.md`
- `.claude/skills/persona-simulate/SKILL.md`

---

## 4. AUTONOMOUS_BACKLOG 신규 (Part 56)

- [ ] **CLAUDE.md §15 컨텍스트 임계값 추가** (10분·L2)
- [ ] **prompt_cache_helper.py longform 정책 갱신** (15분·L2)
- [ ] **mypy LSP 활성화** (30분·L2 ADR-0073)
- [ ] **Citations API 통합 ADR-0072** (2시간·L3)
- [ ] **Skills 5종 신규** (3시간·L2)
- [ ] **/compact 자동 트리거 hook** (1시간·L3)

---

## 5. 누적 효과 예상

| 영역 | 현재 | Part 56 적용 후 |
|------|------|---------------|
| 컨텍스트 효율 | 자율 관리 | 30% 임계값 자동 (Anthropic 정합) |
| longform 처리 | (배치 임의) | +30% 성능 (Anthropic 검증) |
| 코드 품질 | 348 tests | + LSP 자동 진단 |
| 영업 신뢰 | 수동 출처 | Citations API 자동 |
| 작업 모듈화 | subagent 위주 | Skills 5종 추가 |

---

## 6. 적용 X 결정 근거 (좋은 것만 선별 정합)

PO 명령 "좋은 것만 적용" 정합:
- Opus 4.7 default = 비용 폭증 (월 $XX → $XXX)
- Managed Agents = 대규모 기업용 (1인 SaaS 부적합)
- swarm 패턴 = Anthropic 자체 "production X" 권고

→ kormarc-auto 1인 SaaS·캐시카우 도달 우선 = **Sonnet 4.6 메인 + Haiku 라우팅 + Opus 한정** 유지

---

## 7. 검증 사례 매핑 (Part 35 정합)

| Anthropic 권장 | 검증 사례 |
|---------------|----------|
| 컨텍스트 30% | Best Practices 공식 + 경험자 권고 |
| longform top | "+30% 성능 in tests" (Anthropic) |
| LSP | "Single highest-impact plugin" |
| Citations | Anthropic Citations API blog |
| Skills first | "Start with skills (easiest)" |

---

> **이 파일 위치**: `kormarc-auto/docs/research/part56-anthropic-best-practices-cherry-pick-2026-05.md`
> **종합**: 12 영역 이미 적용 + 5 신규 좋은 것만 선별 + 4 부적합 결정 기록
> **PO 정합**: "좋은 것만 적용" ✅
