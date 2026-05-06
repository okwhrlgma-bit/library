---
name: a11y-audit
description: KWCAG 2.2 Level AA 회귀 + 헌법 §12 invariants 자동 검증
allowed-tools: Read, Grep, Glob, Bash(python:*), Bash(pytest:*)
---

# a11y-audit — UI/UX 헌법 §12 회귀 (Cycle 61)

KWCAG 2.2 Level AA + KRDS + Pretendard + 사서 친화 어휘 정합 자동 검증.

## 트리거

- `src/kormarc_auto/ui/**` 변경 시
- `src/kormarc_auto/a11y/**` 변경 시
- `.streamlit/config.toml` 변경 시
- 매 release 직전

## 1. 정적 검증 (LLM 호출 0)

```bash
python -m pytest tests/test_a11y_inject.py tests/test_kwcag22.py -v
```

게이트:
- TestA11yGlobalCSS = 7 KWCAG 항목 (1.3.1·1.4.3·1.4.4·1.4.13·2.3.3·2.4.1·2.4.7·2.5.5)
- TestConfidenceChip = 헌법 §11 (raw % 금지)
- TestAIGhost = 헌법 §10 (인공지능 기본법 §31)
- TestConstitutionInvariants = §10·§11·§12

## 2. 코드 invariant 검증

```python
from kormarc_auto.ui.a11y_inject import A11Y_GLOBAL_CSS

# 헌법 §12 5 핵심 invariants
required = ['pretendard', 'skip-link', 'focus-visible', '44px', 'prefers-reduced-motion']
for r in required:
    assert r in A11Y_GLOBAL_CSS.lower(), f'{r} missing'
```

## 3. 사서 친화 어휘 검증

```python
from kormarc_auto.ui.librarian_ux import LIBRARIAN_DAILY_CYCLE, LIBRARIAN_VOCABULARY

assert len(LIBRARIAN_DAILY_CYCLE) == 5  # Part 49
assert '반입' in LIBRARIAN_VOCABULARY.values()  # IT → 사서
```

## 4. 모든 페이지 inject 적용 검증

```bash
grep -L "inject_global_a11y" src/kormarc_auto/ui/*.py | grep -v __pycache__
```

→ 출력 0 = 모든 페이지에 inject 적용됨.

## 위반 시 액션

1. `learnings.md`에 "a11y 회귀 패턴" 추가
2. PR 생성 (자동 머지 X·헌법 §12 = invariant)
3. PO 알림 (Slack 또는 채팅)

## 영구 게이트

CI `.github/workflows/a11y-ci.yml`이 PR + main push 시 동일 검증 자동 실행.
