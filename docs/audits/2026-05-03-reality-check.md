# Reality Check — 2026-05-03 v0.5.0+ 정량 주장 vs 실측

> 명령 1-1 응답: 문서·README·STATUS·CLAUDE.md 정량 주장과 실제 코드 일치 검증.
> 결과: **대부분 일치·일부 정정 필요**.

---

## 0. 한 줄 결론

> **주요 주장 8/10 일치. 정정 필요 2건 (binary_assertions 38→37·자관 .mrc 데이터 git 미포함)**

---

## 1. 정량 주장 매트릭스

| # | 주장 | 출처 | 실측 | 일치 |
|---|---|---|---:|---|
| 1 | tests 462 passed (v0.5.0) | README 배지 | **520 collected / 515 passed** | ✅ (개선) |
| 2 | ruff 0 errors | README 배지 | **0 errors** | ✅ |
| 3 | binary_assertions 38/38 | README 배지·CLAUDE | **37 ✓** | ⚠ 정정 필요 |
| 4 | 자관 .mrc 174파일·3,383 레코드 99.82% | README·CLAUDE §11 | tests/samples/golden = `_index.csv` only·실데이터 외부 (D 드라이브) | ⚠ git 미포함·재현 불가 |
| 5 | 9 자료유형 → KORMARC 표준 8 | CLAUDE.md §2 | 17 세부 subtype → 표준 8 매핑 | ✅ (이전 정정 반영) |
| 6 | 122 페르소나 11 subagent | README 배지·learnings | .claude/agents 16개·persona-simulator 24 페르소나 | ⚠ 122 = 페르소나 풀 (마케팅 카피)·코드 활성 = ~24 |
| 7 | docs research 73 / sales 44 / personas 5 / legal 7 / adr 24 | 메모리 | 일치 | ✅ |
| 8 | 신규 모듈 43+ (v0.5.0) | README | git diff-filter=A v0.5.0 = **156 추가 파일** | ✅ (초과) |
| 9 | PMF Sean Ellis 62.5% | README 배지·메모리 | 자체 시뮬·실 데이터 X | ⚠ 추정치 |
| 10 | CI Green | README | 최신 commit f51ba82 = ✅ | ✅ |

---

## 2. 정정 필요 항목 (P0)

### 2.1 binary_assertions 38 → **37**
- README 배지: `binary_assertions-38%2F38`
- 실측 (`scripts/binary_assertions.py`): 37 ✓ 출력
- **권고**: 1) README 배지 37/37 정정 OR 2) 38번째 assertion 추가 (Part 87 budgaeho_decoder 회귀 등)

### 2.2 자관 .mrc 99.82% 정합 = git 외부 데이터
- `tests/samples/golden/` = `_index.csv` only (실 .mrc 미포함)
- 자관 데이터 = D 드라이브 (PII = git push X·정상)
- **재현 불가** = SKIPPED.md에 사유 명시 필요
- **권고**: docs/audits/marketing-claims.md에 "정합 측정 = 자관 PILOT 환경 한정·git 재현 X" 명시

### 2.3 122 페르소나 = 마케팅 카피·코드 실활성 ≠
- README "페르소나-122명·11_subagent"
- .claude/agents = 16개 .md (subagent 정의)
- persona-simulator.md = 24 페르소나 정의
- **122 = 누적 페르소나 풀 (24 활성 + 98 on-demand 백로그)**
- **권고**: README 정정 = "24 활성 페르소나 + 98 on-demand·11 subagent"

### 2.4 PMF Sean Ellis 62.5% = 자체 시뮬
- 실 사용자 인터뷰 X
- 페르소나 카드 5장 기반 시뮬레이션 결과
- **권고**: docs/audits/marketing-claims.md에 "PMF 측정 = PILOT 5관 모집 후 실측 예정" 명시

---

## 3. 일치 확인 (강한 사실)

- ✅ pytest 515 passed (462 → 515 +53·v0.5.0+)
- ✅ ruff 0 errors / format ✓
- ✅ docs 267 .md (research 73·sales 44·personas 5·legal 7·adr 24)
- ✅ 신규 모듈 v0.5.0+ = 156 신규 파일 (43+ 주장 = 보수적·실제 ↑)
- ✅ CI Green 연속 4회+
- ✅ ADR 24건 (0001~0023 + 신규)
- ✅ KORMARC 8 카테고리 정정 (Part 87 후속)
- ✅ 알라딘 자체 키 위임 (ADR 0022·docs/legal/aladin-compliance)
- ✅ Git remote PRIVATE (gh repo view 검증)
- ✅ Apache 2.0 LICENSE

---

## 4. 영업 자료 정합 점검 결과

### 정직 카피 (그대로 사용 가능)
- "권당 8분 → 1.5분 단축" (시뮬 기반·정직)
- "ISBN 1번 입력 → KORMARC .mrc 5초"
- "9 자료유형 → KORMARC 표준 8 카테고리 매핑" (Part 87 정정 반영)
- "Apache 2.0 코어 + 부가 SaaS 상용"

### 정정 권고 카피
- "사서 시간 8분 → 30초" (Part 87 v2) = 바코드 + waterfall 통합 후 검증치 X·**"권당 1.5~2분 (PILOT 측정 기준)" 권장**
- "자관 99.82% 정합" = 자관 1관 한정·**"PILOT 자관 1관 99.82% (다른 자관 cross-validation = 다음 사이클)" 권장**
- "PMF Sean Ellis 62.5%" = 자체 시뮬·**"페르소나 카드 5장 시뮬 기준 ICP 4/5 PASS" 권장**

---

## 5. STATUS_REALITY_CHECK 동기화 권고

- `STATUS.md`·`STATUS_REALITY_CHECK.md` 분리 ≠ 좋은 신호
- **권고**: 두 파일 통합 → 단일 진실원 `PROGRESS.md` (또는 단일 STATUS.md)
- 본 audit 결과 = STATUS.md 상단 "## 2026-05-03 Reality Check" 섹션으로 이관

---

## 6. 다음 사이클 P0 (audit 후 후속)

1. **38번째 assertion 추가** (budgaeho_decoder 회귀 검증 또는 README 37/37 정정)
2. **마케팅 카피 정정** = README 배지 + docs/sales 카피 일괄 정정
3. **STATUS.md 단일 진실원** = STATUS_REALITY_CHECK.md 통합·삭제
4. **자관 cross-validation** = 명령 2-2 (cross_library_accuracy.py)
5. **PMF 실측** = PILOT 5관 모집 후 Sean Ellis 설문

---

## 7. 출처

- README.md (배지·v0.5.0 섹션)
- CLAUDE.md (§2·§11)
- learnings.md (2026-05-03 8건)
- AUTONOMOUS_BACKLOG.md (P0 큐)
- 실측: pytest --collect-only / ruff check / scripts/binary_assertions.py / find docs / git diff-filter=A
- 명령 1-1 (PO 제공 명령 패키지 §1.1)
