# Part 1 — Vibe Coding & Claude Code: 비개발자 PO를 위한 종합 매뉴얼

> **kormarc-auto 종합 매뉴얼 시리즈 1/4**
> **작성일**: 2026-04-29 · **대상**: PO(사서 출신 1인 비개발자) + Claude Code(자율 야간 작업 시 그대로 참조 가능)
> **언어**: 한국어 본문 + 영어 헤더 (한국어 BPE 1.5~2× 토큰 비용 절감 정책)
> **분량**: 약 8,500자 · **PO 정점 정책**: 토큰·시간 고려 X, 깊이 우선

---

## 0. 30초 요약 (PO 화면 첫 줄)

- **바이브 코딩** = "코드를 잊고 결과만 보며 AI에 맡기는 개발 방식" (Karpathy 2025.2 명명). 비개발자 PO에게 최적이지만, **검증·헌법·안전망 없이 하면 청구서·보안·매출이 모두 무너진다**.
- **2026-04 기준 PO 최적 스택** = **Claude Code (Max 5x $100/월) + VS Code + Streamlit + .venv**. Cursor·Windsurf·Antigravity는 모두 보조 후보지만 **CLAUDE.md 헌법 + Hooks + Subagent 생태계가 가장 성숙한 Claude Code가 1순위**.
- **kormarc-auto는 이미 자율 모드 4단**으로 운영 중 (CLAUDE.md 320줄 + hooks 6종 + subagent 9종). Part 1은 이 setup이 왜 정답인지·어떻게 더 강화할지 설명.

---

## 1. 바이브 코딩이란? — 정의·역사·입문자 적합도

### 1.1 정의 (Karpathy 원문)

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists. It's possible because the LLMs are getting too good." — Andrej Karpathy, 2025.2 ([X 원문](https://x.com/karpathy/status/1886192184808149383))

**핵심 3 요소**:
1. **자연어로 의도 표현** (코드가 아니라 "로그인 폼 만들어")
2. **AI가 코드 생성·실행·디버깅** (사람은 결과만 평가)
3. **작은 사이클 반복** ("이건 안 돼, 저건 돼, 이렇게 바꿔")

### 1.2 역사 (2023~2026)

| 시기 | 사건 |
|---|---|
| 2023.5 | Karpathy "the hottest new programming language is English" — 영어가 새 프로그래밍 언어 |
| 2024.6 | Cursor 출시 (Composer 모드) — 첫 본격 vibe coding IDE |
| 2025.2 | Karpathy "vibe coding" 용어 명명 (Cursor + SuperWhisper 음성 입력) |
| 2025.5 | Anthropic Claude Code 정식 출시 (CLI 우선) |
| 2025.7 | Windsurf (Codeium 리브랜딩) — Cascade 모드 |
| 2025.11 | Google Antigravity 출시 (Gemini 3 + 병렬 에이전트) |
| 2026.1 | Claude Code 2.0 (Skills + Subagent + Worktree) |
| 2026.3 | Karpathy "vibe coding is passé" → 새 용어 모색 (코드 검토·테스트 강조 회귀) |

### 1.3 왜 비개발자 PO에게 적합한가?

| 전통 개발 | 바이브 코딩 |
|---|---|
| Python 문법 6개월 학습 → 첫 줄 작성 | "ISBN 입력하면 KORMARC 출력해" → 30초 후 동작 |
| 디버그·스택트레이스·StackOverflow 검색 1시간 | 에러 붙여넣기 → AI가 원인 진단 30초 |
| 라이브러리 비교 1주일 | "pymarc·dataclass·pydantic 중 뭐가 적합?" → 즉답 |
| 학습 곡선 = 절벽 | 학습 곡선 = 완만한 경사 (도메인 지식이 자산) |

**PO의 강점은 사서 도메인 25년**. 코드 생성을 AI에 위임하면 **"사서가 매일 8분 마크 작업하는 고통"을 가장 잘 아는 사람이 SaaS를 만들 수 있다**. 이게 kormarc-auto의 본질적 경쟁력이다.

### 1.4 한계 (Karpathy 본인이 2026.3 인정)

1. **이해 없는 코드 누적** → 6개월 후 본인도 못 고침
2. **보안 구멍** (`.env` 노출·SQL 인젝션·CORS open)
3. **테스트 없는 자신감** ("동작하니까 됐다" → 운영에서 폭발)
4. **비용 폭주** (Claude API 청구서 월 $500+ 사례 다수)
5. **벤더 락인** (특정 도구 의존 → 도구 가격 인상 시 종속)

→ **회피 전략**: 헌법(CLAUDE.md) + 자동 검증(hooks) + 비용 게이트(권당 비용 측정) + 다중 도구 알기. **kormarc-auto는 이 5개를 모두 갖춰 둔 모범 사례** (자세한 §3·§5·§6).

---

## 2. AI 코딩 도구 6종 비교 (2026-04 기준)

### 2.1 한눈 비교표

| 도구 | 가격 (개인) | 모델 | 인터페이스 | 강점 | 약점 | PO 적합도 |
|---|---|---|---|---|---|---:|
| **Claude Code** | Pro $20·Max5x $100·Max20x $200 | Opus 4.7·Sonnet 4.6·Haiku 4.5 (1M ctx) | CLI·VS Code 확장·JetBrains·웹 | 헌법(CLAUDE.md)·hooks·subagent·자율 모드·1M 컨텍스트 | Windows 한글 경로 가끔 hiccup·CLI 친숙 필요 | ★★★★★ |
| **Cursor** | Pro $20·Ultra $200 | Sonnet/Opus·GPT·Gemini 다중 | VS Code 포크 | Composer 멀티파일·Tab 자동완성·UI 친숙 | CLAUDE.md 같은 헌법 시스템 약함·고급 자동화 부족 | ★★★★ |
| **Windsurf** | Pro $20·Max $200 | 동일 다중 | VS Code 포크 | Cascade 에이전트·가성비 | 2026.3 가격 인상 후 Cursor와 차별점 ↓ | ★★★ |
| **Antigravity (Google)** | 무료 preview·AI Ultra $249.99 | Gemini 3·Claude Opus 4.6 | VS Code 포크 (Manager View) | 5 병렬 에이전트·무료 (현재) | 2026.3 무료 한도 92% 삭감 (250→20 RPD)·미성숙 | ★★ |
| **GitHub Copilot** | Free·Pro $10·Pro+ $39·Bus $19·Ent $39 | GPT-5·Claude·Gemini | VS Code·JetBrains·CLI | 가장 저렴·자동완성 1위 | 에이전트 약함·자율 모드 X | ★★★ (보조용) |
| **Cody (Sourcegraph)** | Free·Pro $9·Ent | 다중 | VS Code·JetBrains·웹 | 코드베이스 전체 검색·엔터프라이즈 | 1인 PO 오버킬 | ★★ |

### 2.2 도구별 PO 의사결정 매트릭스

#### Claude Code — 1순위 (현재 PO 사용 중) ✅

| 평가축 | 점수 | 근거 |
|---|---:|---|
| 한국어 친화 | 95 | 시스템 프롬프트·CLAUDE.md 한국어 완전 지원 |
| 자율 모드 | 100 | hooks·subagent·permissions 가장 성숙 |
| 1인 비개발자 적합 | 95 | "/init" 한 번으로 헌법 자동 생성 |
| 가격 (Max 5x) | 85 | $100/월 = ₩140K. **kormarc-auto 비용 회수 = 사서 5명 결제하면 본전** |
| Windows 호환 | 80 | 한글 경로 가끔 이슈, 대체로 안정 |
| **합계** | **91** | **즉시 채택 (현재 PO setup)** |

**PO 상황 추천**: ★★★★★ Max 5x ($100/월) 사용 권장. 야간 자율 모드 = Opus 호출 자유 정책일 때 5x 한도 안정적.

#### Cursor — 2순위 (보조용)

| 평가축 | 점수 | 근거 |
|---|---:|---|
| UI 친숙성 | 95 | VS Code 그대로 + Tab 자동완성 자연 |
| Composer (멀티파일) | 90 | 수정 범위 시각화 우수 |
| 자동화·hooks | 50 | Claude Code 대비 미성숙 |
| 가격 | 80 | Pro $20 동일 |
| **합계** | **75** | **타이핑 작업 보조용으로 병행 가능** |

**PO 상황 추천**: ★★★ Streamlit UI 작업처럼 즉각 시각 피드백이 필요한 부분만 Cursor 보조 (Tab 자동완성 + Cmd+K). 메인은 Claude Code.

#### Windsurf — 보류

2026.3 가격 인상($15→$20)·할인 폭 축소 후 Cursor 대비 차별점 약화. **현재 채택 이유 없음**.

#### Antigravity — 호기심 수준

Google이 무료 한도를 92% 삭감(2026.3, 250→20 RPD). **신뢰성 낮음**. 실험만 권장.

#### GitHub Copilot — 빠진 도구

현재 Pro $10/월로 Tab 자동완성만 쓰면 가성비 최고. 단 **에이전트·자율 모드 부재** → kormarc-auto의 자율 야간 작업에 부적합. **PO는 사용 안 해도 됨**.

#### Cody — Skip

엔터프라이즈 (수십~수백 개발자) 시나리오. 1인 PO에게 오버킬.

### 2.3 결론 (PO 단일 추천)

**Claude Code Max 5x ($100/월) 단독 사용**. 비용은 사서 3.4명만 ₩30K/월 결제하면 본전. **현재 setup 유지가 정답**.

---

## 3. Claude Code 깊이 가이드

### 3.1 CLAUDE.md 작성법 (헌법화)

**원칙**: 매 세션 자동 로드되는 파일. **150~200줄 권장** (짧을수록 자주 읽힘, 너무 짧으면 컨텍스트 손실).

**kormarc-auto 현재**: 320줄 — 약간 길다. 하지만 §0~§5는 헌법, §6~§13은 참조성이라 **분리 후보**: §6 이후를 `.claude/rules/*.md`로 이동 → CLAUDE.md는 헌법 200줄로 슬림화.

**필수 13 섹션** (kormarc-auto가 표준):
1. 프로젝트 정체성 (1줄로 미션)
2. 의심·검증·정제 3원칙
3. 도메인 용어 (PO 도메인은 사서 → KORMARC·KOLAS·KDC 정의 필수)
4. 외부 API 단일 진실 소스
5. 코딩 규칙 HARD RULES (절대 X / 반드시 O)
6. 도메인 빌드 핵심 규칙
7. 자율성 4단계 + 종료 규약
8. 자기 비판 체크리스트 (커밋 전)
9. 참조 문서 인덱스
10. 슬래시 명령 + 서브에이전트 인덱스
11. 핵심 모듈 인덱스
12. 변경 이력
13. 수익 모델 (헌법) — **PO 미션 정합 핵심**

> **Claude Code에 던질 프롬프트 1**:
> ```
> CLAUDE.md를 읽고 320줄 → 헌법 200줄(§0~§5+§7+§12)과 참조 120줄(.claude/rules/index.md)로 분리해.
> 각 섹션 어디로 이동했는지 표로 매핑.
> ```

### 3.2 Memory 시스템 (4 타입)

Claude Code는 **세션 간 자동 메모리**를 4 위치에 저장:

| 타입 | 위치 | 용도 | kormarc-auto 사례 |
|---|---|---|---|
| **user** | `~/.claude/projects/.../memory/user_profile.md` | PO 정체성 | "사서 출신 1인 비개발자 창업자" |
| **feedback** | `feedback_*.md` | PO 지시 영구화 | `feedback_max_autonomy.md` (자율 모드 정책) |
| **project** | `project_*.md` | 프로젝트 상태 | `project_kormarc_auto.md` (v0.4.36 / 222 tests) |
| **reference** | `reference_*.md` | 참조 정보 | `reference_paths.md` (작업 폴더 경로) |

**갱신 트리거**: PO가 "이걸 기억해"·"앞으로는 ~"·"매번 ~"·"~할 때마다" 발화 시.

> **Claude Code에 던질 프롬프트 2**:
> ```
> ~/.claude/projects/.../memory/MEMORY.md를 읽고, 6개월 안 갱신된 항목을 표로 보여줘. 각 항목별로 (a) 폐기 (b) 갱신 (c) 유지 추천.
> ```

### 3.3 Hooks (자동화 핵심)

> **결정적 차이**: CLAUDE.md = 80% 권고 (Claude가 읽고 따름) vs Hooks = **100% 결정적** (시스템이 강제 실행).
> **격언** ([Anthropic Best Practices](https://code.claude.com/docs/en/best-practices)): "포맷팅·린팅·보안 검사처럼 매번 예외 없이 실행되어야 한다면 hook으로 만들어라."

**kormarc-auto 현재 6 hooks**:

| 시점 | hook | 역할 |
|---|---|---|
| **PreToolUse (Bash)** | `irreversible-guard.sh` | `rm -rf /`·`mkfs`·`git push --force` 등 87 패턴 차단 |
| **PostToolUse (Write/Edit)** | `ruff --fix` 자동 | Python 파일 저장 즉시 린트 자동 수정 |
| **PostToolUse (Bash git commit)** | `binary_assertions.py` | 커밋 후 어셔션 23종 자동 평가 |
| **PostToolUse (모든)** | `post-trust.py` | 트러스트 점수 누적 |
| **Stop** | `binary_assertions.py --json` | 세션 종료 시 어셔션 누적 → `logs/evals/` |
| **PostCompact** | `postcompact-reinject.py` | 컨텍스트 압축 후 핵심 룰 재주입 ★ |
| **PermissionDenied** | `permission-denied-log.py` | 거부 패턴 누적 → 권한 정책 개선 |

**활용 패턴 5종**:
1. 저장 시 자동 포맷 (Black/Ruff/Prettier)
2. 커밋 전 자동 테스트 (`pytest -q`)
3. 위험 명령 차단 (deny 정규식)
4. 컨텍스트 압축 후 헌법 재주입 (kormarc-auto 사례)
5. 세션 종료 시 어셔션 누적 (PO 정점 정책 = 야간 자율 품질 검증)

> **Claude Code에 던질 프롬프트 3**:
> ```
> .claude/settings.json의 PostToolUse hooks 보고, "저장 즉시 mypy --strict 실행" hook 추가해줘.
> 30초 timeout, async true, 실패해도 세션 안 멈추게.
> ```

### 3.4 Slash Commands + Custom Subagents

**Slash commands** (`.claude/commands/*.md`): PO가 자주 쓰는 워크플로 단축. kormarc-auto = 17개.

**Custom subagents** (`.claude/agents/*.md`): **별도 컨텍스트 윈도우**로 작업하는 전문가. kormarc-auto = 9개.

| 에이전트 | 호출 트리거 |
|---|---|
| `researcher` | 코드 30곳 이상 grep 필요 시 |
| `kormarc-expert` | 새 KORMARC 필드 처리 추가 시 |
| `librarian-reviewer` | 빌더 결과를 PO에게 보여주기 전 |
| `architect-deep` | L3 의사결정 시 (DB 스키마·API 추가) |
| `code-reviewer` | diff 50줄+ 또는 외부 영향 시 |
| `planner` | 새 모듈·기능 설계 시 |
| `implementer` | 계획 → 코드 변환 |
| `explorer` | 미지의 영역 정찰 |
| `librarian-domain-classifier` | 사서 도메인 분류 |

**서브에이전트의 진짜 가치**: 메인 컨텍스트가 200K로 제한될 때, 서브가 **자기만의 200K 컨텍스트**를 가짐. → 1M 토큰 = 2개 동시 풀가동 가능.

### 3.5 Permissions (allow/deny/ask + 3 모드)

**3 운영 모드**:
| 모드 | 키 | 설명 | PO 사용 |
|---|---|---|---|
| **default** | `--permission-mode default` | 위험 시 매번 묻기 | 학습 단계 |
| **acceptEdits** | `--permission-mode acceptEdits` | 파일 편집은 자동 승인 | 평일 작업 권장 |
| **plan** | `/plan` 입력 또는 `--permission-mode plan` | 계획만 수립, 변경 X | L3 결정 전 |
| **bypassPermissions** | `--permission-mode bypassPermissions` ⚠️ | 모든 권한 묻지 않음 | 야간 자율 모드 (격리 환경에서만) |

**kormarc-auto 현재**: `.claude/settings.json` allow 30+ / deny 87+. 모바일·자율 모드 권한 사전 등록 완료.

> **Claude Code에 던질 프롬프트 4**:
> ```
> .claude/settings.json의 deny 87 패턴을 (1) 파일 시스템 (2) git (3) 패키지 게시 (4) 셧다운 (5) 시크릿으로 카테고리 분류해 표로 보여줘. 누락된 위험 패턴 5개 제안도 함께.
> ```

### 3.6 Plan 모드·Background Agents·Worktree

**Plan 모드** (Shift+Tab 두 번): Claude가 **변경 없이** 계획만 수립. PO 승인 후 실행. **L3 결정 시 필수**.

**Background Agents** (Claude Code 2.0+): subagent가 백그라운드에서 진행. 메인 에이전트는 다른 작업. **Monitor 도구**로 백그라운드 stdout 실시간 tail.

**Git Worktree** (v2.1.49 부터, 2026.2.19 출시): subagent마다 **독립 git worktree**. 병렬 3~5 세션 가능.

> **PO 활용 시나리오**: 야간 자율 시 worktree 3개 = (1) 기능 구현 (2) 테스트 추가 (3) 문서 작성. PO 아침에 3 PR 검토.

> **Claude Code에 던질 프롬프트 5**:
> ```
> 오늘 밤 야간 자율 작업 3개를 worktree로 병렬 실행:
> (a) docs/research/part1 작성
> (b) docs/research/part2 작성
> (c) PIPA logging 마스킹 보강
> 각 worktree 이름은 wt-part1·wt-part2·wt-pipa. Plan 모드로 먼저 계획 보여주고, 내가 OK 하면 acceptEdits로 진행.
> ```

### 3.7 모델 라우팅 (Opus·Sonnet·Haiku 분기)

| 모델 | 가격 (입력/출력 per 1M tok) | 용도 | kormarc-auto 분기 |
|---|---|---|---|
| **Opus 4.7** | $15 / $75 | L3 결정·architect-deep·planner | ADR 작성·DB 스키마·외부 API 추가 |
| **Sonnet 4.6** | $3 / $15 | 일반 코딩·researcher·implementer | 평일 거의 모든 작업 |
| **Haiku 4.5** | $1 / $5 | 1차 분류·OCR pre-filter | Vision 입력 1단계·로그 분석 |

**kormarc-auto 정책**: Opus는 **평가축(§0 마크 시간 단축 + §12 결제 의향) 부합 시 자유 호출**. 토큰·시간 X. 단 일반 코드 생성은 Sonnet 기본.

---

## 4. 프롬프트 엔지니어링 (한국어 환경)

### 4.1 한국어 BPE 토큰 비용 (반드시 알아야 할 수치)

> **Aihola·token-calculator.net·GitHub Issue #26401 종합**: 같은 의미 표현 시 **한국어는 영어 대비 1.5~3× 토큰**. 평균 **2×**. Claude Pro $20 한도가 한국어 사용자에겐 실질 30~50%로 줄어드는 셈.

**원인**: BPE 토크나이저가 영어 단어 통째로 1 토큰 처리. 한국어는 교착어 + 음절 단위 → 자주 character-level fallback.

**대응 5 패턴** (kormarc-auto 적용):

| 전략 | 효과 | 적용 |
|---|---|---|
| **헤더는 영어** | 30% 절약 | CLAUDE.md §·Markdown ## |
| **식별자는 영어** | 50% 절약 | 함수명·파일명·git commit |
| **본문은 한국어 OK** | 가독성 우선 | 도메인 용어 (KORMARC·관제) |
| **한 단어 ≠ 한국 단어 X** | 혼용 금지 | `결제Service` 같은 식별자 X |
| **반복 정보는 코드로 인용** | 컨텍스트 절약 | "CLAUDE.md §4.2 참조" |

**측정 사례**: 본 Part 1 문서 한국어로 8,500자 ≈ **약 12,000~15,000 토큰** (영어 동일 의미라면 6,000~8,000). 1.5~2× 그대로.

### 4.2 한국어 프롬프트 4 패턴 (지시·예시·제약·출력 형식)

```
[지시] 무엇을 할지 (동사 + 목적)
[예시] 입력·출력 1~3개 (few-shot)
[제약] 하지 말아야 할 것·반드시 지킬 것
[출력 형식] 표·코드·JSON·markdown 명시
```

**좋은 예** (kormarc-auto 사례):
```
[지시] kormarc/serial.py에 022 필드 빌더 함수 추가.
[예시] 입력 ISSN="1234-5678" → 출력 022 ▾a1234-5678
[제약]
- 함수 30줄 이하
- timeout=10 명시
- 한국어 docstring
- ISSN 체크섬 검증 try/except
[출력] git diff 형식으로
```

**나쁜 예**: "022 필드 만들어줘" → 모호 → Claude가 추측 → 회귀 위험.

### 4.3 컨텍스트 압축 회피 (PreCompact·PostCompact)

Claude Code는 컨텍스트 200K 80% 도달 시 자동 압축. **압축 = 핵심 룰 망각 위험**.

**kormarc-auto 대응**: `PostCompact` hook으로 `postcompact-reinject.py` 실행 → CLAUDE.md §0·§4·§6 자동 재주입.

**PO 추가 가능**: PreCompact hook으로 압축 전 "지금 작업 중인 task ID·진행도" 별도 저장.

---

## 5. 개발 환경 도구 의사결정 (PO 상황)

### 5.1 VS Code 확장 추천 5종

| 확장 | 용도 | PO 적합도 |
|---|---|---:|
| **Python (Microsoft)** | 기본 Python 지원·디버거·인터프리터 선택 | ★★★★★ 필수 |
| **Ruff (Astral)** | 자동 포맷·린트 (kormarc-auto 표준) | ★★★★★ 필수 |
| **Pylance** | 타입 힌트·자동완성 (mypy 보조) | ★★★★★ 필수 |
| **GitLens** | git 히스토리 인라인 표시 | ★★★★ 강력 추천 |
| **Korean Language Pack** | UI 한국어화 | ★★★ PO 친숙도 ↑ |

**일부러 빠진 것**: Copilot (Claude Code와 충돌·중복). Black (Ruff와 중복).

### 5.2 터미널 (Windows)

| 옵션 | 장점 | 단점 | PO 추천 |
|---|---|---|---|
| **PowerShell** | Windows 네이티브·`.ps1` 자동화 | bash 문법 다름 | 보조 |
| **Git Bash** | Unix 명령 그대로 (`ls`·`grep`·`cat`)·Claude Code Hook 호환 | Windows 경로 변환 필요 | **★ 메인** |
| **WSL2 (Ubuntu)** | 진짜 Linux | 디스크·메모리 부담·OneDrive 동기화 충돌 | Skip |

**kormarc-auto 정합**: hooks 모두 `bash "/c/Users/.../path"` 형식 = Git Bash 전제. **PO는 Git Bash 메인 + PowerShell 보조** 권장.

### 5.3 디버깅 (Vibe Coding 시)

| 방법 | 시기 | PO 권장도 |
|---|---|---|
| `print()` | ❌ 절대 금지 (CLAUDE.md §4.1) | ☆ |
| `logging.info()` | ✅ 평일 디버깅 (시크릿 마스킹 자동) | ★★★★★ |
| `breakpoint()` | 가끔 (단계별 변수 확인) | ★★★ |
| VS Code 디버거 (F5) | 복잡한 버그 (스택 따라가기) | ★★★ |
| Claude Code에 에러 로그 붙여넣기 | 80% 케이스 | ★★★★★ |

**PO 패턴**: 에러 발생 → 전체 traceback 복사 → Claude Code에 "이 에러 원인·수정안 3개 비교"라고 prompt → 적용. 평균 30초.

### 5.4 의존성 관리

| 도구 | 속도 | 학습 비용 | PO 적합도 |
|---|---|---|---|
| **pip + .venv** | 보통 | 낮음 | ★★★ 익숙하면 유지 |
| **uv (Astral)** | **10~100×** 빠름 | 낮음 (pip 호환) | ★★★★★ **추천** |
| **poetry** | 느림 | 높음 (pyproject 학습) | ★★ 1인 개발 오버킬 |
| **conda** | 느림 | 중간 | ☆ Python only이면 불필요 |

**PO 즉시 액션**: `pip install uv` → `uv pip install -r requirements.txt`. 체감 5~50× 빨라짐. **kormarc-auto 향후 마이그 후보**.

---

## 6. 5대 멈춤 패턴 (자율 모드 운영 시)

> **kormarc-auto `.claude/rules/autonomy-gates.md`에 이미 명시된 정책**. 본 §은 이를 외부 컨텍스트와 통합.

### 6.1 5 패턴 표

| 패턴 | 증상 | 회피 행동 |
|---|---|---|
| **모호한 결정 (A vs B)** | "둘 다 가능, PO에게 물어볼까?" | **더 안전·보수적 옵션 선택** + `DECISIONS.md` 기록 |
| **테스트 3회 실패** | 같은 테스트 반복 실패 | `SKIPPED.md` 기록 + 다음 작업 |
| **자가 디버그 루프** | 같은 파일 30회 수정 반복 | **max-iterations 30 한계** → 다음 작업 |
| **컨텍스트 한계·compact** | 핵심 룰 망각 | **CLAUDE.md 매 세션 자동 로드** + PostCompact hook |
| **의존성 네트워크 실패** | `pip install` 타임아웃 | **새 의존성 금지** + 오프라인 모드 우선 |

**원칙**: 자율성의 80%는 "**막혔을 때 무엇을 할지**"가 결정. 권한 0회보다 회피 정책이 더 중요.

### 6.2 PO가 추가해야 할 6번째 패턴 (제안)

**비용 폭주 패턴**: Opus 호출이 한 세션 $5 초과 시 자동 Sonnet 강등. `~/.claude/settings.json`의 `model` 옵션 또는 `cost-budget` hook으로 가능 (기능 출시 시).

---

## 7. 학습 리소스 (한국어 우선)

### 7.1 한국 커뮤니티

| 채널 | URL/이름 | 특징 |
|---|---|---|
| 페이스북 「AI 개발자」 | (검색) | 한국어 질문·답변 활발 |
| 인프런 「Claude Code 실전」 | inflearn.com | 유료 강의 (₩99K 안팎) |
| 네이버 카페 「바이브 코딩 한국」 | (검색) | 입문자 친화 |
| 디스코드 「Anthropic Korea Builders」 | (검색) | 실시간 |

### 7.2 유튜브 (한국어)

- "노마드 코더" — 일반 개발 입문 (Claude Code 시리즈 있음)
- "코딩애플" — Python·웹 기초 (vibe coding 보조 학습)
- 영어지만 자동 자막 OK: "Anthropic" 공식 채널 (Claude Code 데모)

### 7.3 공식 문서 (영어, 우선순위)

1. **[Claude Code Docs](https://code.claude.com/docs/en/)** — 1순위 (가장 정확)
2. **[Best Practices](https://code.claude.com/docs/en/best-practices)** — 헌법·hooks·subagent 정석
3. **[Sub-agents 가이드](https://code.claude.com/docs/en/sub-agents)** — 자율 모드 핵심
4. **[Anthropic Skilljar 「Claude Code in Action」](https://anthropic.skilljar.com/claude-code-in-action)** — 무료 코스
5. **[How Anthropic teams use Claude Code (PDF)](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf)** — Anthropic 사내 활용

### 7.4 4주 입문 로드맵 (PO 맞춤)

| 주차 | 목표 | 산출물 |
|---|---|---|
| **1주** | Claude Code 설치 + Streamlit Hello World | 첫 commit |
| **2주** | CLAUDE.md 작성 + slash command 3개 | 헌법 + `/test`·`/lint`·`/daily` |
| **3주** | hook 2개 추가 (포맷 자동·테스트 자동) | `.claude/settings.json` 1차 완성 |
| **4주** | subagent 1개 + 야간 자율 1세션 | 다음날 PR 검토 |

**PO 현재 상태**: 이미 4주 로드맵 **모두 완료** (CLAUDE.md 320줄·hooks 6종·subagent 9종). **PO는 입문자 → 중급자 단계**.

---

## 8. kormarc-auto 적용 — 즉시 액션

### 8.1 PO가 오늘 30분 안에 할 일 (우선순위)

| # | 액션 | 시간 | 예상 효과 |
|---:|---|---|---|
| 1 | CLAUDE.md §6 이후를 `.claude/rules/`로 분리 (200줄 슬림화) | 10분 | 매 세션 토큰 30% 절감 |
| 2 | `pip install uv` → 의존성 설치 속도 10~50× | 5분 | 체감 즉시 |
| 3 | 본 Part 1 문서를 `~/.claude/projects/.../memory/reference_part1.md`로 추가 | 2분 | 다음 세션 자동 참조 |
| 4 | `~/.claude/settings.json` 글로벌 권한 점검 (Bash 31 allow 그대로?) | 5분 | 자율 모드 마찰 ↓ |
| 5 | `/loop 30m /daily` 시도 (kormarc-auto의 daily 명령 30분마다 자동 실행) | 1분 | 야간 자율 강화 |
| 6 | logs/evals/ 디렉토리 생성 (Stop hook 산출 저장) | 1분 | 어셔션 누적 |
| 7 | Plan 모드(`/plan`) 한 번 시도해보기 | 5분 | L3 결정 안전판 익숙화 |

### 8.2 「Claude Code가 자율로 야간 작업하게 만드는 setup 7단계」

**PO가 한 번 setup 후 매일 밤 그대로 작동**:

```
1. CLAUDE.md = 헌법 (200줄 이내·미션·HARD RULES·자율 4단)
   ✅ kormarc-auto 보유 (320줄, 슬림화 대기)

2. .claude/rules/ = 도메인·운영 게이트·평가축
   ✅ kormarc-auto 보유 (autonomy-gates·business-impact·kormarc-domain)

3. .claude/settings.json hooks
   - PreToolUse: irreversible-guard (위험 명령 차단)
   - PostToolUse: 자동 포맷·자동 테스트·어셔션 평가
   - Stop: 어셔션 누적 → JSON 저장
   - PostCompact: 헌법 재주입
   ✅ kormarc-auto 6 hooks 활성

4. .claude/agents/ = 전문 서브에이전트 (도메인·검토·계획·구현)
   ✅ kormarc-auto 9 agents

5. .claude/commands/ = 워크플로 단축 (/daily·/test·/quality-check)
   ✅ kormarc-auto 17 commands

6. permissions allow 사전 등록 (자주 쓰는 도구·서버 실행)
   ✅ kormarc-auto 30+ allow

7. 야간 자율 명령 1줄
   예: claude --permission-mode acceptEdits "오늘 밤 docs/po-master-action-plan-2026-04-28.md §1 9 ADR 결정 항목 중 5개를 자율 진행. 5대 멈춤 패턴 회피. 작은 commit. 평가축 §0·§12 양수만."
```

→ **kormarc-auto는 이미 7단계 모두 완비**. PO가 위 명령 한 줄 + Cloudflare Tunnel로 모바일 모니터링하면 **잠자는 동안 ADR 결정·문서 작성·테스트 추가·커밋이 자동으로 누적**.

### 8.3 5월 마감 정합 (PO 마스터 액션 플랜)

| 5월 활동 | 본 Part 1 활용 |
|---|---|
| 5.1~5.7 ADR 9 PO 결정 | §3.6 Plan 모드로 각 ADR 영향 시뮬레이션 |
| 5.8~5.31 자관 PILOT 4주 시연 | §3.4 librarian-reviewer 서브에이전트가 시연 슬라이드 검토 |
| 5.31 KLA 발표 신청 마감 | §3.6 Worktree 3 병렬 = 슬라이드·데모·발표문 |

---

## 9. Claude Code에 던질 프롬프트 추가 5선 (재사용 권장)

```
[프롬프트 6 — 헌법 점검]
CLAUDE.md를 읽고, 최근 7일 commit 90개와 비교해 (a) 위반 사례 (b) 모호한 룰 (c) 추가 필요 룰 표로.

[프롬프트 7 — 비용 게이트]
지난 30일 .claude/logs/cost.json 읽고 모델별·hook별·subagent별 토큰 소비를 표로. Opus 호출 중 §0·§12 평가축 부합 비율 산정.

[프롬프트 8 — 야간 자율 안전판]
오늘 밤 자율 commit 5건 진행. 각 commit 메시지에 Q1·Q2·Q3·Q4·Q5 점수 + 평가축 영향 명시. Q5=FAIL 즉시 중단 + 보고.

[프롬프트 9 — Worktree 병렬]
worktree 3개 만들어서 (a) docs/research/part2 작성 (b) PIPA 마스킹 보강 (c) tests/golden 5개 추가 병렬. 각 30분 한계, 초과 시 SKIPPED.md.

[프롬프트 10 — 학습 누적]
learnings.md 마지막 7일 항목 읽고, .claude/rules/*.md에 흡수할 수 있는 사실을 표로. PO 결정 후 흡수.
```

---

## 10. 다음 Part 미리보기

- **Part 2 — 사서 도메인 + KORMARC 기술 심화**: KS X 6006-0:2023.12 완전 해부·9 자료유형·880·049·KOLAS 호환·MODS XML·ISO 2709
- **Part 3 — kormarc-auto 아키텍처 + 비즈니스 모델**: 모듈 인덱스·외부 API 폴백 전략·BYOK·권당 비용·캐시카우 도달 경로·자관 PILOT 4주 시나리오
- **Part 4 — 자율 운영 + 컴플라이언스 + 영업 골든타임**: 야간 자율 모드 풀 가이드·PIPA 5대 패턴·KLA 5.31·작은도서관 ₩30K 월정액·매크로 사서 영업 1순위

---

## Sources

### Vibe Coding
- [Andrej Karpathy 원문 X 포스트 (2025.2)](https://x.com/karpathy/status/1886192184808149383)
- [Vibe coding — Wikipedia](https://en.wikipedia.org/wiki/Vibe_coding)
- [Karpathy "vibe coding is passé" — The New Stack (2026.3)](https://thenewstack.io/vibe-coding-is-passe/)
- [Simon Willison: Not all AI-assisted programming is vibe coding](https://simonwillison.net/2025/Mar/19/vibe-coding/)
- [What is Vibe Coding? — IBM](https://www.ibm.com/think/topics/vibe-coding)

### AI 도구 비교
- [AI Coding Agents 2026 Comparison — Lushbinary](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- [Agentic IDE Comparison — Codecademy](https://www.codecademy.com/article/agentic-ide-comparison-cursor-vs-windsurf-vs-antigravity)
- [I Compared Every Major AI Coding Tool — Eric Murphy (Medium)](https://murphye.medium.com/i-compared-every-major-ai-coding-tool-so-you-dont-have-to-f05a6915c0d4)
- [Cursor vs Claude Code vs Windsurf 2026 — Shareuhack](https://www.shareuhack.com/en/posts/cursor-vs-claude-code-vs-windsurf-2026)
- [GitHub Copilot Pricing 2026 — Costbench](https://costbench.com/software/ai-coding-assistants/github-copilot/)
- [Sourcegraph Cody vs GitHub Copilot — AISO Tools](https://aisotools.com/compare/cody-vs-github-copilot)

### Claude Code 공식·심화
- [Claude Code Best Practices — Anthropic](https://code.claude.com/docs/en/best-practices)
- [Claude Code Sub-agents Docs](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows)
- [Claude Code Hooks/Subagents/Skills Complete Guide — DEV/ofox.ai](https://dev.to/owen_fox/claude-code-hooks-subagents-and-skills-complete-guide-hjm)
- [Claude Code Pricing 2026 — Verdent Guides](https://www.verdent.ai/guides/claude-code-pricing-2026)
- [Everything Claude Has Shipped in 2026 — The AI Corner](https://www.the-ai-corner.com/p/everything-claude-shipped-2026-complete-guide)
- [Claude Code Worktree Setup Guide — Verdent](https://www.verdent.ai/guides/claude-code-worktree-setup-guide)
- [How Anthropic Teams Use Claude Code (PDF)](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf)

### 한국어 토큰 비용
- [Aihola — Claude Tokenizer Language Tax](https://aihola.com/article/claude-tokenizer-language-tax)
- [GitHub Issue #26401 — Korean/Japanese/CJK tokenization disadvantage](https://github.com/anthropics/claude-code/issues/26401)
- [Token Calculator & Cost Estimator (2026)](https://token-calculator.net/)
- [I Measured Claude 4.7's New Tokenizer — Claude Code Camp](https://www.claudecodecamp.com/p/i-measured-claude-4-7-s-new-tokenizer-here-s-what-it-costs-you)

---

> **Part 1 끝.** 본 문서는 PO 본인 학습용 + Claude Code 자율 모드 컨텍스트 자료 양용. `~/.claude/projects/.../memory/reference_part1.md`로도 추가 권장.
