# business-impact-check hook 설계 (ADR 0014 후보)

> **목적**: 모든 commit·ADR·새 의존성·새 화면·새 hook 생성 시 사업 5질문 점수 자동 검증.
> **현재 상태**: docs only 설계 (ADR 0014 under_review).
> **헌법 정합**: `docs/business-evaluation-criteria-2026-04-28.md` (통합 평가 헌법) + `.claude/rules/business-impact-axes.md`.

---

## 0. 정합 배경

| 영역 | 현황 |
|---|---|
| autonomy-gates 캐시카우 평가축 | 현재: §0 §12 양수 영향만 commit message에 명시 |
| 사업 5질문 (ADR 0013 under_review) | 현재: 자동 검증 X·수동 평가만 |
| 업그레이드 후 | hook 자동 검증 + 임계값 미달 차단 |

→ business-impact-check.py = autonomy-gates의 §0/§12 양수 영향 검증을 5 차원 정밀화.

---

## 1. Hook 명세

### 1.1 위치

```
.claude/hooks/business-impact-check.py
```

### 1.2 트리거

PreToolUse hook — `Bash(git commit *)` 또는 `Edit·Write` (ADR·rules·src/ 변경 시).

### 1.3 검증 단계 (3 게이트)

```
Gate 1: 변경 영역 분류
  - 자료 폴더·docs/audit·README → skip (commit message 불필요)
  - src/·ADR·rules·hooks → 5질문 점수 강제

Gate 2: commit message 패턴 매처
  - "Q1 = N" or "결제 의향: N" 명시 검색
  - "Q2 = N", "Q3 = N", "Q4 = N", "Q5 = PASS|FAIL"
  - "종합 = N" 또는 자동 계산

Gate 3: 임계값
  - Q5 = FAIL → 즉시 deny (다른 점수 무관)
  - 종합 < 60 → deny
  - 60 ≤ 종합 < 75 → warn (PO 결정 영역)
  - 종합 ≥ 75 → allow
```

### 1.4 강제 commit message 형식

```
feat(영역): <설명>

Q1 결제 의향: <0~100>
Q2 비용: <0~100>
Q3 자산: <0~100>
Q4 락인: <0~100>
Q5 컴플: PASS|FAIL
6dim: <-9~+9>
종합: <0~100>

근거:
- Q1: <시간 절감 분 + 결제 트리거>
- Q2: <권당 비용 ₩>
- Q3: <재사용성·영업·차별화>
- Q4: <락인 메커니즘>
- Q5: <PIPA 5대 패턴 정합>
- 6dim: <OS·데이터·보안·의존성·롤백·관측>

자율성: L1|L2|L3|L4 (rules/autonomy-gates.md)
캐시카우: §0 +N | §12 +N

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

### 1.5 자동 계산 (옵션)

commit 작성 시 hook이 자동 보강:

```python
def auto_calculate_total(q1, q2, q3, q4, q5_pass, six_dim):
    """Beta 단계 가중치 기반 종합 점수."""
    if not q5_pass:
        return 0  # FAIL
    business = q1*0.4 + q2*0.25 + q3*0.15 + q4*0.10 + 100*0.10
    tech = (six_dim + 9) / 18 * 100  # -9~+9 → 0~100
    return round(business * 0.6 + tech * 0.4)
```

---

## 2. 차단 케이스 (Beta 단계)

| 케이스 | 결과 |
|---|---|
| Q5 = FAIL | 🔴 즉시 deny (점수 무관) |
| 종합 < 60 | 🔴 deny |
| 60 ≤ 종합 < 75 | 🟡 warn + PO 결정 |
| 종합 ≥ 75 | 🟢 allow |
| commit message 패턴 누락 | 🔴 deny (강제) |

---

## 3. 출력 형식 (Claude Code v2.1.x PreToolUse 표준)

### 3.1 deny

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "permissionDecisionReason": "사업 5질문 점수 누락. commit message에 Q1·Q2·Q3·Q4·Q5·종합 점수 명시 필수. 참조: docs/business-evaluation-criteria-2026-04-28.md"
  }
}
```

### 3.2 warn (60 ≤ 종합 < 75)

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "ask",
    "permissionDecisionReason": "종합 점수 N (Beta 임계값 75 미달). PO 결정 영역. 진행하려면 ADR 작성 권장."
  }
}
```

---

## 4. 자율 commit 활성 매트릭스 (예시)

### 통과 케이스 (자동 allow)

| ADR | 종합 | 결과 |
|---|---:|---|
| 0021 (상호대차 띠지 자동 — 자관 양식 등록) | 89 | 🟢 allow |
| 0022 (양식 resolver 4단 fallback) | 89 | 🟢 |
| 0027 (KOLAS F12 자동 import) | 88 | 🟢 |
| 0049 (주제명표목 자동) | 85 | 🟢 |
| 0058 (xlsx 도서원부 자동) | 88 | 🟢 |
| 0070 (자관 .mrc PILOT) | 88 | 🟢 |

### 차단 케이스 (예시)

| 가상 변경 | 결과 |
|---|---|
| `class PatronManager` 신규 | Q5 = FAIL → 🔴 deny |
| `kormarc/random_module.py` (Q1=20·Q2=80·Q3=30·Q4=10·Q5=PASS) | 종합 ~ 36 → 🔴 deny |
| 외부 API 추가 (Q1=70·Q2=30·Q3=70·Q4=50·Q5=PASS) | 종합 ~ 56 → 🟡 warn |

---

## 5. PO 결정 영역 (자율 X)

ADR 0014 PO 승인 후 active.

### 후속 작업 (PO 승인 후)

```bash
# 1. hook 구현
# .claude/hooks/business-impact-check.py (이 docs 기반, 약 200줄)

# 2. settings.json 등록
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit *)",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PROJECT_DIR}/.claude/hooks/business-impact-check.py"
          }
        ]
      }
    ]
  }
}

# 3. 테스트
# tests/integration/test_business_impact_check.py
def test_commit_message_pattern_required(): ...
def test_q5_fail_blocks(): ...
def test_threshold_75_passes(): ...
def test_below_60_blocks(): ...
def test_60_75_warns(): ...
```

---

## 6. 자율 점수 기록 (ADR·docs)

ADR·docs에도 commit과 동일 형식 명시 권장:

```markdown
# ADR 0021 정정 — 「상호대차 띠지 자동 생성기」

## 평가
- Q1 결제 의향: 100 (자관 26~31분 → 6~7분 = 77% 단축)
- Q2 비용: 95 (python-hwpx 의존성만)
- Q3 자산: 80 (자관 양식 등록 → 정책 ③ 일반화)
- Q4 락인: 70 (자관 5년 책단비 历사 정합)
- Q5 컴플: PASS (PIPA 영역 X)
- 6dim: +7
- **종합: 89** 🟢 ACCEPT
```

---

## 7. Q5 자동 검증 (pii-guard.py 연동)

business-impact-check가 Q5 = PASS 자동 검증할 때 `pii-guard.py` 결과 활용:

```python
def check_q5(git_diff: str) -> bool:
    """PIPA 5대 패턴 자동 검증 (pii-guard.py 결과 활용)."""
    # 1. Reader entity 패턴 매처
    # 2. PII 5종 필드 매처
    # 3. 자관 PII 영역 매처
    # → 모두 통과 시 PASS
```

→ pii-guard와 business-impact-check 통합 = 사업 + 컴플 자동 검증.

---

## 8. 영업 메시지 (사업 5질문 자동)

> "우리 SaaS는 모든 코드 변경에서 사업 5질문 (Q1 결제·Q2 비용·Q3 자산·Q4 락인·Q5 컴플) 점수를 hook으로 자동 검증합니다.
>
> 종합 점수 75 미달 변경은 자동 차단 — '사서 결제 의향 ↑' 영역만 진입.
>
> Q5 (PIPA 컴플) FAIL은 즉시 차단 (회원 PII entity 절대 X)."

---

## 9. ADR 0014 PO 승인 트리거

PO 승인 후:
1. `business-impact-check.py` 구현 (이 docs 기반)
2. settings.json 등록 (Bash(git commit *) matcher)
3. 통합 테스트 5+ 케이스
4. CLAUDE.md §4 절대 규칙 추가: "commit message에 사업 5질문 점수 강제"
5. learnings.md `business-impact-check active` 갱신

---

## 10. 종합 점수 (ADR 0014 자체)

| 항목 | 점수 |
|---|---:|
| Q1 결제 | 50 (영업 메시지 — "사업 5질문 자동 검증") |
| Q2 비용 | 100 (hook 비용 0) |
| Q3 자산 | 95 (재사용성 ↑·차별화 ↑) |
| Q4 락인 | 70 (commit pattern 강제) |
| Q5 컴플 | PASS |
| 6dim | +6 |
| **사업 5질문** | (40·50 + 25·100 + 15·95 + 10·70 + 10·100)/100 = 73 |
| 6dim 정규화 | (6+9)/18×100 = 83 |
| **종합** | 73×0.6 + 83×0.4 = 76.6 | 🟢 ACCEPT |

---

## 11. Sources

- `docs/business-evaluation-criteria-2026-04-28.md` (통합 평가 헌법)
- `.claude/rules/business-impact-axes.md` (5질문 rules)
- `.claude/rules/autonomy-gates.md` (캐시카우 평가축)
- `docs/pii-guard-hook-design.md` (Q5 자동 검증 연동)
- ADR 0010 (6차원), 0013 (사업 5질문 — under_review), 0014 (commit hook — under_review), 0015 (pii-guard — under_review)
- Claude Code v2.1.119 PreToolUse hook spec
