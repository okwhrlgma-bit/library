# I-003 — Claude Skills Marketplace 활용 (30 앱 → SKILL.md 변환)

## PO 명령 (2026-05-08)

> "클로드 코드 수익화 조사하여 적용·더 조사할게 있나 꼼꼼히"

## 검색 결과 (외부)

- **Claude Code = $2.5B 실행률** (2026)·기업 구독 4배 성장
- **Skills Marketplace** = 2026 emerging economic layer
- 표준 `SKILL.md` 형식·VoltAgent 1000+ awesome-agent-skills (오픈)
- **Agent37** = "working locally" → "live product with payments" = 1일 발사·infra X·결제 자동
- **Composio**·**VoltAgent** = Skills 호스팅 플랫폼 다수

## 우리 적용 가능성

| 30 앱 | SKILL.md 변환 가능? | 활용 방법 |
|---|---|---|
| #1 kormarc-auto | ✅ "Generate KORMARC" Skill | Anthropic 공식 도서관 영역 |
| #2 kdc-classify | ✅ "Classify book by KDC" Skill | 한국 도서관 niche |
| #4 librarian-overtime | ⚠ (일정 추적 = state·Skill 적합 X) | API 활용 가능 |
| #31 freelancer-tax-helper | ✅ "Korean freelancer tax estimator" Skill | 글로벌 한국어 사용자 |
| #32 sidehustle-tracker | ⚠ (state 누적·Skill 적합 X) | API 활용 가능 |

→ **#1·#2·#31 = 즉시 SKILL.md 변환 가능** (다음 cycle 코드).

## 평가 (ADR 0055)

| 항목 | 점수 |
|---|---|
| 시장 = Anthropic 사용자 1억+ (2026)·Skills Marketplace 신생 | +25 |
| 경쟁 = Skills 1,000+·but 한국 niche 부족 | +15 |
| 인디 검증 = Agent37·VoltAgent 호스팅 사례 | +15 |
| 빈도 = Claude 사용자 매일 | +15 |
| 결제 의향 = $1~9/Skill 사용 (Anthropic 표준) | +10 |
| 한국·글로벌 양면 | +10 |
| Anthropic 공식 = 외부 마이그레이션 골든윈도우 | +5 |

**시장 점수: 95/100** ✅

## 캐시카우

| 항목 | 점수 |
|---|---|
| ARPU = Skills 사용 ₩100~1,000/실행 (Anthropic 사용량 정산) | +25 |
| COGS = 코드 자체·infra X (Anthropic 호스팅) | +25 |
| 자동 갱신 = Anthropic 사용자 = 자동 결제 | +20 |
| 락인 = Skill 사용 history 누적·Anthropic 결제 | +10 |
| 1인 PO 운영 = OK (코드만·인프라 X) | +10 |

**캐시카우 점수: 90/100** ✅

## ADR 0058 4 조건

| 조건 | 결과 |
|---|---|
| 시장 ≥ 75 | ✅ 95 |
| 캐시카우 ≥ 80 | ✅ 90 |
| 벤치마크 1+ | ✅ Agent37·VoltAgent·Composio |
| Q5 PASS | ✅ (Anthropic 정합·헌법 §3) |

→ **GO + 배포 가능 후보**·다음 cycle SKILL.md 변환 코드.

## 단일 기능 변환 예시

```yaml
# .claude/skills/generate-kormarc/SKILL.md
name: generate-kormarc
description: 한국 도서관 KORMARC (KS X 6006-0:2023.12) 자동 생성 — ISBN → .mrc
inputs:
  - isbn: ISBN-13 (필수)
  - source: nl_korea | aladin | byok (옵션)
outputs:
  - mrc_text: KORMARC 형식 (UTF-8)
  - confidence: high | medium | low
  - source_map: dict[field, source]
```

## 다음 cycle 작업 (코드 페어·ADR 0061 정합)

1. `.claude/skills/generate-kormarc/` SKILL.md + 코드
2. `.claude/skills/classify-kdc/` SKILL.md + 코드
3. `.claude/skills/freelancer-tax-helper/` SKILL.md + 코드
4. Agent37·VoltAgent 호스팅 검토 (PO 결정 시)

## 출처

- [Claude AI Statistics 2026 (Panto)](https://www.getpanto.ai/blog/claude-ai-statistics)
- [10 Must-Have Skills for Claude (Medium)](https://medium.com/@unicodeveloper/10-must-have-skills-for-claude-and-any-coding-agent-in-2026-b5451b013051)
- [Claude Skills Marketplace (Agent37)](https://www.agent37.com/blog/claude-skills-marketplace)
- [Claude Monetization Master Plan 2026 (Claude Lab)](https://claudelab.net/en/articles/cowork/claude-monetization-masterplan-2026)
- [Top 10 Claude Code Skills (Composio)](https://composio.dev/content/top-claude-skills)
- [VoltAgent awesome-agent-skills (1000+)](https://github.com/VoltAgent/awesome-agent-skills)
- [Building complete SaaS with only Claude Code (HEY)](https://world.hey.com/cpinto/building-a-complete-saas-product-with-only-claude-code-cca13895)
