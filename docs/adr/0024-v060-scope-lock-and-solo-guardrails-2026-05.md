# ADR 0024 — v0.6.0 Scope Lock + Solo PO 가드레일 (외부 901 출처 진단 반영)

- 상태: Accepted (PO 자율 적용·2026-05-03)
- 일자: 2026-05-03
- 결정자: Claude Opus 4.7 (PO 자율 위임)
- 트리거: 외부 deep research 보고서 (901 출처)·"identity fusion + productive avoidance + agent pace inflation + domain expert curse" 4중 진단

## Context

v0.5.0 = **43 modules**·612 tests·자관 단일 (N=1) 검증·외부 협력 일시 중단.
외부 보고서 (Levels·Kahl·Welsh·Perri·Kua·Newport·Cunningham·Anthropic 등 901 출처) 진단:

1. **Identity fusion**: 43-module 출하 = 자아 = 프로젝트 융합 패턴 (MIT Sloan/Linville)
2. **Productive avoidance**: 코드 = 사서 인터뷰 회피 도구화 (Walling/Kahl/Solving Procrastination)
3. **Agent-induced pace inflation**: 야간 무중단 Claude Code = sphere of accountability 확장 (HBR/BCG 2026 "AI brain fry")
4. **Domain expert curse**: 사서 출신 = "정합 완성도" 추구 = 사용자 jobs 무시 (Kapur/Heath/Santos·Bob Moesta)

**MarcEdit 교훈**: 26년·25K users·143국·subscription 0원. 전 세계 KORMARC SaaS 부재.
**Volumetree 케이스**: 43-feature 솔로 = month 26 폐업 (구조적 동일).

## Decision

### A. v0.6.0 scope lock (2건만)
1. Per-MARC-block disaggregation publish (174 files / 3,383 records / 11 blocks)
2. T2-1 offline demo finish (50% → 100%)

### B. Deferred (parking lot·인터뷰 + wedge 1택 후 재개)
- T3 Anthropic optimization (prompt caching tuning·model routing)
- T4 trust UX (disaggregation table 외)
- T5 Korean sovereignty (sovereign cloud·on-prem)
- T6 eval/meta (disaggregation harness 외)
- 신규 Streamlit 탭 (현재 14개 = 충분)
- 모바일 앱 신규 (backend 기존)
- 가격·결제·signup flow (paying customer 확정 전)
- I18n (English UI)
- 사업자 등록·법인 (개인사업자 유지)

### C. Agent 가드레일 (CLAUDE.md §8B)
1. 신규 모듈 생성 = 금지 (refactor·tests·docs·publish 산출물만 허용)
2. Cycle 당 module 변경 = 5개 hard cap (3-week cycle 정합)
3. 야간 자율 = Mon~Thu only (금 18시 → 월 9시 dead air)
4. 24h hold on agent PR before merge
5. Morning agent review = 45분 kitchen timer
6. 일요일 = full no-laptop·notification off

### D. 인터뷰 우선 (코드보다 우선)
- 사서 5명 cold outreach 이번 주 (Mom Test rules)
- 인터뷰 3명 60분 진행 (week 2)
- wedge segment 1택 (week 3): 작은도서관 / 학교도서관 사서교사 / 출판사 metadata / 개인 도서수집가
- 회피: 공공도서관 (KOLAS 무료)

### E. 측정 변경
- 단일 "99.82%" = 폐기 (모든 surface에서 ripgrep 제거)
- 대체: per-block table (5XX 59% / 4XX 30% / round-trip 100% / 1XX 0% 자관 정책 / 880 0% 자관 한자 X)
- 정직 60-80% > 숨겨진 99% (Hamel Husain eval principle)

### F. PO 본인 운영 (CLAUDE 영역 X·TODO 등록)
- 17:30 shutdown ritual (Newport)
- 일요일 laptop off
- 청년 마음건강 신청 (서울 youth.seoul.go.kr / 보건복지부 bokjiro.go.kr)
- 1577-0199·1393 phone에 저장

## Consequences

### Positive
- v0.6.0 = v0.5.0보다 작아짐 = deletion test 통과
- 인터뷰 데이터 = 진짜 validation = wedge 확정 가능
- agent 가드레일 = burnout 회피 + 24h hold = sober second look
- per-block table = 사서 신뢰 (정직 > 과장)
- MarcEdit 교훈 흡수 = "edits KORMARC" wedge 회피 = AI 생성 wedge 강화

### Negative / Trade-off
- 5월 골든타임 (KLA·정부 자금) 일부 보류 = 단기 영업 기회 손실
  → 인터뷰·wedge 확정 후 6월 재개 = 더 강한 영업 자료 (per-block table·실 사서 인용)
- T3 Anthropic optimization 보류 = LLM 비용 일시 더 높음
  → paid pilot 확보 후 = 비용 최적화 정당화

### Risk Mitigation
- "신규 모듈 X" 룰을 agent CLAUDE.md §8B에 박제 = 자율 cycle 위반 차단
- per-block table 7일 내 publish = "fix 후 publish" 회피
- 인터뷰 5명 응답률 = expect 2/5 (cold outreach base rate) = 10건 발송으로 보강

### Reentry Triggers (외부 협력 재개)
- 인터뷰 5명 완료 + wedge 1택 후 = 사업자 등록·정부 자금 재평가
- paid pilot 1건 = T3 LLM 최적화 정당화
- paid pilot 5~10건 = 외부 PR·KLA 발표·LR1 권위자 관계 재개
- month 3 paid pilot 0 = wedge 잘못 = 인터뷰 재실행 (코드 추가 X)

## Alternatives Considered

### Alt 1: 6-tier 로드맵 그대로 진행
- Reject: Volumetree·MarcEdit·Perri build trap 패턴 = 알려진 실패 경로

### Alt 2: 99.82% 유지·6XX 100% fix 후 publish
- Reject: Hamel/Yan eval principle 위반·정직성 = buyer trust = 더 큰 자산

### Alt 3: agent 완전 정지
- Reject: refactor·tests·docs·publish 산출물 = 충분히 안전한 영역·완전 정지 = 과잉 반응

### Alt 4: PO 인터뷰 보류·"외부 협력 X" 절대 적용
- Partially Reject: PO 의지 존중하되·인터뷰 = "협력" 아님·"학습"임 = TODO 등록

## References

- 외부 보고서 (901 출처·deep research)
- Memory: `~/.claude/projects/.../memory/project_solo_founder_diagnosis_2026_05_03.md`
- Part 95 자율 사이클 종합: `docs/research/part95-autonomous-cycle-summary-2026-05.md`
- Perri "Escaping the Build Trap"
- Kua "The Builder's Trap"
- Cunningham 1992 + 2009 debt video
- Hamel Husain "Your AI Product Needs Evals"
- Anthropic "Claude Code Best Practices"
- MarcEdit 26년 케이스 (Terry Reese)
- Volumetree 43-feature 케이스
- Sifted 2025 (n=138)·CEREVITY 2025 (n=127)·디캠프 2022 (n=271 Korean)
- 강북삼성 2023 burnout → suicide ideation +77%
- HBR/BCG 2026 "AI brain fry"
- Cal Newport / Pang Rest = 4h/day deep work 상한

## Status Notes

- v0.5.0 lock = git tag·신규 commit = v0.6.0-rcN
- per-block table publish = 7일 내 (week 1 Friday·이번 주 D-3)
- agent 가드레일 = CLAUDE.md §8B 박제 (이번 commit)
- 인터뷰 5명 = PO 작업 (TODO PO-WEEK1-1)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-03 · ADR autonomy 위임 적용
