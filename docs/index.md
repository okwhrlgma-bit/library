# docs/ 다층 인덱스 (kormarc-auto v0.5.0+)

> 92 Part 연구·44 영업·5 페르소나·24 ADR·7 법무 = **268 .md** 다층 진입.
> 페르소나·역할별 맞춤 경로 우선.
> 기존 인덱스 = `INDEX-legacy.md`

---

## 0. 가장 먼저 (5분 시작)

- **PO**: `사용자_TODO.txt` (외부 작업 14건·우선순위 4단계)
- **신규 사서**: `README.md` 빠른 시작 + `docs/quickstart-librarian.md`
- **개발자**: `CLAUDE.md` 헌법 + `docs/spec.md`
- **투자자**: `docs/research/part88-strategy-v2-2026-05.md` (Executive Summary)
- **학자**: `docs/research/part86-similar-automation-papers-2026-05.md` (학술 비교)

---

## 1. 페르소나별 진입 경로 (Champion 4 + Rejecter 1)

| # | 페르소나 | Phase | 점수 | 핵심 모듈 |
|---|---|---|---:|---|
| 01 | 사립 중학교 사서교사 | 1 ICP | 95 | dls_521_classifier·decision_maker_pdf |
| 02 | 작은도서관 관장 | 1 ICP | 98 | volunteer_onboarding·aladin tenant key |
| 03 | P15 순회사서 | 2-B | 85 | mobile/{offline_queue·bluetooth·sync} |
| 04 | 사립대 의과대학 분관 | 2 | 92 | ddc·mesh·lcsh·alma_xml·pubmed |
| 05 | Rejecter (25년차) | ICP 외 | 60 | (영업 자원 X) |

페르소나 카드: `docs/personas/01~05-*.md`

---

## 2. 92 Part 연구 — 5 클러스터

### Cluster A: 바이브 코딩·Claude Code (Part 1)
### Cluster B: KORMARC·KOLAS·DLS 표준 (Part 2)
### Cluster C: 사서 워크플로우·페르소나 (Part 3, 45~91)
- part45~51: 페르소나 시뮬·12%→56% 전환율
- part52~60: 멀티 에이전트·74 페르소나·B-team
- part66~75: 사서 페인 발굴
- part76~82: 웹 검증 사서 페인 54건
- part83~85: PASS audit·아웃풋 시뮬·마스터 플랜
- **part87·88**: 전략 피벗 (바코드·외주·결제자 깔때기)
- **part89·90·91**: 5 페르소나 검증·회복·100점 로드맵

### Cluster D: UI·UX·SEO·마케팅 (Part 4, 15~20, 35~44)
### Cluster E: 학술·비교·전략 (Part 86·88a)

---

## 3. 영업 자료 — 44건

### 시기별
- **5월 골든타임**: docs/sales/{31~40}-*
- **무기한**: docs/sales/kolas-termination-response-2026-12.md
- **9월 기고**: docs/sales/school-library-journal-2026-09-pitch.md

### 핵심 신규 (자율 결정)
- `pricing-decision-2026-05.md` (권당 200원 1차)
- `pilot-icp-priority-2026-05.md` (Champion 02+01 우선)
- `aladin-tenant-key-onboarding.md` (자체 키 위임)
- `kla-2026-presentation-{outline,guardrails}.md`

---

## 4. 법무·약관 — 7건

- dpa·sla·refund-policy
- aladin-compliance·privacy-policy·incident-response·data-retention

---

## 5. ADR 24건 (영구 결정)

- 0021 바코드 우선 피벗
- 0022 알라딘 자체 키 위임
- 0023 LLM Provider 추상화 (Proposed)
- 그 외 = `docs/adr/README.md`

---

## 6. Audit·Reality Check

- `docs/audits/2026-05-03-reality-check.md` (8/10 일치)

---

## 7. 핵심 코드 모듈

### classification/
budgaeho_decoder·kdc_waterfall·copy_cataloging·ddc_classifier·mesh_mapper·lcsh_mapper

### mobile/ (페르소나 03 Phase 2-B)
offline_queue·bluetooth_scanner·sync_api·sync_router

### output/
dls_521_classifier·alma_xml_writer·decision_maker_pdf

### security·observability·evaluation
tenant_isolation·redaction·slo_metrics·cross_library_simulation·load_test·billing_e2e·onboarding_smoke

### api/
nl_korea (SEOJI)·aladin (자체 키 위임)·pubmed·kolisnet_compare·data4library·kakao

### intelligence/
volunteer_onboarding·librarian_agent·pmf_validator

---

## 8. 단일 진실원

1. `CLAUDE.md` (헌법)
2. `README.md` (배지·Phase·페르소나 ICP)
3. `사용자_TODO.txt` (PO 외부 작업)
4. `learnings.md` (세션 누적 학습)
5. `CHANGELOG_NIGHT.md` (변경 이력)
6. `AUTONOMOUS_BACKLOG.md` (P0 큐)
7. 본 docs/INDEX.md (다층 진입)

---

## 9. 통계 (2026-05-03 기준)

| 카테고리 | 누적 |
|---|---:|
| docs/research | **92** Part |
| docs/sales | **44** |
| docs/personas | **5** |
| docs/legal | **7** |
| docs/adr | **24** |
| docs/audits | **1** |
| 총 docs/.md | **268** |
| src/.py 모듈 | **170+** |
| pytest | **563+** |

---

> **갱신 정책**: 매 자율 사이클 = 신규 Part·sales·legal 추가 시 본 INDEX 자동 갱신 (영구).
