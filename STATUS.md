# STATUS — kormarc-auto 단일 진실원 (B안 P6)

> Plan B Cycle 7 (P6) — STATUS_REALITY_CHECK.md → `docs/archive/STATUS_REALITY_CHECK-2026-04-27.md`로 이동·이 파일이 단일 진실원

## 현재 상태 (2026-05-04 Cycle 7)

| 항목 | 값 |
|---|---|
| 버전 | v0.6.0 (tag push 완료) |
| Tests | 662 passing / 6 skipped |
| ruff | 0 errors |
| binary_assertions | 39/39 |
| 자관 174 round-trip | 100% baseline (regression ≤ 1pp 게이트) |
| CLAUDE.md | 85줄 (60 ceiling 초과·v0.7 추가 슬림) |
| agent_docs/ | 4 파일 (kormarc_field_reference·running_evals·release_process·CLAUDE-full 백업) |
| GitHub | 동기 (origin/main = 로컬·v0.6.0 tag pushed) |

## Plan B 사이클 진행 (B안 §0)

| Cycle | P | 상태 | commit |
|---|---|---|---|
| 1 | P1-(1) per-block disaggregation | ✅ | e7d74f6 |
| 2 | P1-(2) offline demo + v0.6.0 tag | ✅ | c292b6d |
| 3 | P2 init/serve subcmd + .bat 안내 | ✅ | 1a4c019 |
| 4 | P3 Hypothesis 정식 + 4 KORMARC property | ✅ | d736864 |
| 5 | P4 agent_docs/ 3 신규 reference | ✅ | 4898711 |
| 6 | P5 README.en.md + vhs SKIPPED | ✅ | cd7540f |
| **7** | **P6 STATUS 통합 + ADR 0026 + 익명화** | **진행 중** | (이 commit) |
| 8+ | P29 처리방침 / P30 PortOne v2 / P31 가격 페이지 (외부 858 출처 신설) | 대기 | - |
| 9~28 | P7~P28 (T3~T6) | 대기 | - |

## ADR 누적

- ADR 0024: 솔로 PO 가드레일 (외부 901 출처)
- **ADR 0025: Plan B 무중단 자율** (0024 supersede·active)
- **ADR 0026: 한국 SaaS 프로덕션 결정** (외부 858 출처·active)

## 영구 invariants (B안 §4)

1. 헌법 위반 0건 (raw 확률·100% 자동·본문 LLM 송신·사서 검토 우회)
2. 자관 데이터 git 누설 0건 (D:\ commit 시도 = 자율 정지)

## 자동 머지 차단 게이트 6건 (B안 §0)

1. ruff check . = 0 errors
2. pytest -q = 전수 통과
3. binary_assertions 39/39
4. 자관 174 회귀 ≤ 1pp
5. demo 30초 5건 round-trip 100%
6. CLAUDE.md 헌법 위반 0건

## STOP 조건 7건 (B안 §5)

1. 회귀 게이트 5 사이클 연속 위반
2. 자관 데이터 git 누설 시도
3. 본문 LLM 송신 시도
4. API 키 commit 시도
5. 우선순위 큐 모든 항목 SKIPPED
6. PO "STOP" / "PAUSE" 입력
7. 동일 P 항목 3 사이클 연속 SKIPPED

## SKIPPED 누적 (`SKIPPED.md`)

- vhs GIF 생성 (Cycle 6 P5 부분·외부 도구 미설치·PO 작업 등록)
- GitHub Release 자동 생성 (Cycle 2·gh CLI 미설치·PO 수동)

## 외부 보고서 흡수 (메모리 영속)

- 901 출처: 솔로 PO 진단 (4중 패턴·Plan B 채택 트리거)
- 858 출처: 한국 SaaS 프로덕션 (사업자·결제·영업·가격·인프라·법무 7 영역·ADR 0026)

## PO 외부 작업 (사용자_TODO P0 재배치 후)

1. 일반과세자 홈택스 등록 (722000·자택)
2. 통신판매업 신고 (PG 가입 → 구매안전서비스 → 정부24)
3. 사업자통장 (카뱅/토스 + 시중은행 1)
4. NL_CERT_KEY + ANTHROPIC_API_KEY 발급
5. 사서 5명 cold outreach (Mom Test)
6. GitHub v0.6.0 Release 수동 생성
7. 청년 마음건강 신청 (1577-0199·1393)

## 이전 STATUS_REALITY_CHECK (참조)

`docs/archive/STATUS_REALITY_CHECK-2026-04-27.md` — 2026-04-27 시점 회고. 이후 사이클 1~7에서 상당수 항목 해소·이 파일이 현행 진실원.

---

작성: Claude Opus 4.7 (1M context) · 2026-05-04 · Plan B Cycle 7 P6 STATUS 통합
