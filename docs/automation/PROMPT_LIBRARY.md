# Prompt Library

> 자주 쓰는 프롬프트 모음. 복붙해서 `claude -p`나 `router.py`로 실행.
> 새로운 프롬프트가 안정화되면 `.claude/skills/`로 승격하세요.

---

## 1. 코드 작성

### 새 기능 구현 (PAVR로)

```
/pavr <기능 설명. 한 문장으로. 예: "사용자 프로필 페이지에 아바타 업로드 추가">
```

### 작은 수정 (라우터에 맡기기)

```bash
python automation/router.py "<수정 내용>"
# 라우터가 자동으로 code-edit 또는 refactor로 분류
```

### TypeScript any 제거

```
src/ 의 `any` 타입 사용처를 찾아 정확한 타입으로 교체.
복잡한 케이스(unknown 캐스팅 필요)는 PR 본문에 별도 섹션으로 보고.
파일당 5개 이하만 수정해 PR을 작게 유지.
```

### deprecated API 마이그레이션

```
codebase에서 <이전 API>를 <새 API>로 마이그레이션.
파일 단위로 작은 PR 여러 개로 쪼개. 각 PR은 5파일 이내.
각 PR마다 검증: npm test 통과 확인.
```

---

## 2. 테스트

### 커버리지 갭 메우기

```
코드 커버리지 보고서를 보고 (`npm run coverage`),
커버리지 가장 낮은 함수 5개에 대해 test-writer 서브에이전트로 테스트 작성.
```

### 회귀 테스트 추가

```
어제 발생한 버그(<버그 설명>)에 대한 회귀 테스트를 추가.
같은 시나리오가 다시 통과하면 테스트가 fail해야 함.
테스트 추가 후 일부러 코드를 망가뜨려 테스트가 실패하는지 확인.
```

### Mutation testing

```
src/utils/ 디렉터리에 Stryker로 mutation testing 실행.
mutation score 60% 미만인 함수에 대해 테스트 보강 PR 생성.
```

---

## 3. 리뷰·디버깅

### PR 자동 리뷰 (GitHub Action 외 즉석)

```
@<PR URL> 의 변경사항을 보고 코드리뷰어 서브에이전트로 리뷰.
보안·테스트 누락·성능 위주로. 한국어로.
```

### Sentry 에러 진단

```
@<Sentry 에러 URL 또는 스택트레이스 텍스트>

debugger 서브에이전트로 진단:
1. 재현 단계 찾기
2. 가설→검증
3. 가장 작은 fix
4. 회귀 테스트 추가
```

### 성능 회귀 진단

```
지난 N커밋 동안 npm run build 시간이 30s → 90s로 늘었음.
어떤 커밋부터 느려졌는지 git bisect로 찾고 원인 분석.
```

---

## 4. 마케팅·콘텐츠

### 블로그 포스트 초안

```
'<주제>'에 대한 블로그 포스트 작성.
- 타겟: <누구>
- 톤: <캐주얼/전문적/...>
- 길이: 800~1200자
- 구조: 문제→솔루션→사례→CTA
- SEO 키워드: <키워드 3개>

decisions.md의 우리 입장과 일치하게. 거짓 사실 금지.
content/blog/<slug>.md 로 저장.
```

### Changelog 생성

```
git log v1.2.0..HEAD 를 보고 사용자 친화적 changelog 작성.
- Added / Changed / Fixed / Removed로 분류
- 내부 변경(refactor, test 등)은 생략
- 한국어/영어 둘 다
CHANGELOG.md 상단에 추가.
```

### Tweet 시리즈

```
이번 주 출시한 기능을 트위터 스레드로.
- 5~7 트윗
- 각 280자 이내
- 첫 트윗은 후크
- 마지막은 CTA (가입/체험)
- 자랑 90%, 자조 10% (사람냄새)
```

---

## 5. 분석·KPI

### 주간 KPI 리포트

```
지난 7일 GA4·Stripe·PostHog 지표를 종합해 주간 리포트.
- MRR/ARR 변동
- 신규 가입 vs 이탈
- 활성 사용자
- 전환 funnel 어디서 가장 많이 새는가

reports/weekly-$(date +%Y%m%d).md 로 저장.
숫자만 나열하지 말고 '왜?'를 추정. 근거 약하면 약하다고 명시.
```

### A/B 테스트 결과 분석

```
PostHog의 <실험 이름> 결과를 분석:
- 통계적 유의성 (95% CI)
- 효과 크기
- 세그먼트별 차이
- 다음 액션 추천

decisions.md에 결과 + 결정 추가 제안 (사람 승인 후 적재).
```

---

## 6. 운영·인프라

### 의존성 업데이트 (안전한 것만)

```
npm audit + npm outdated를 보고:
- patch 업데이트(0.1.x → 0.1.y): 자동 PR 생성
- minor 업데이트(0.x.0 → 0.y.0): 이슈로 보고만
- major 업데이트: 본문에 breaking change 분석 포함한 이슈

PR마다 별도 — 한 번에 전부 머지 금지.
```

### Lighthouse 점수 개선

```
production URL로 Lighthouse 실행.
점수 90 미만 카테고리에 대해 가장 영향 큰 fix 3개를 PR로.
이미지 최적화·번들 사이즈는 우선순위 높게.
```

### Database 인덱스 점검

```
@db/schema.sql 과 @src/api/ 의 쿼리 패턴을 비교.
WHERE 절에 자주 쓰이는데 인덱스 없는 컬럼 찾기.
EXPLAIN ANALYZE 결과를 첨부한 마이그레이션 PR 작성.

⚠️ 절대 마이그레이션 자동 실행 금지. PR로만.
```

---

## 7. 메타 (시스템 자체 개선)

### CLAUDE.md 정제

```
/refine-claudemd
```

### 사문화된 규칙 찾기

```
지난 60일 git log와 PROGRESS.md를 보고,
CLAUDE.md의 규칙 중 한 번도 언급/위반/적용되지 않은 것을 찾아.
제거 후보 PR로 제안.
```

### Hook 자동 생성

```
learnings.md에서 같은 패턴이 3회 이상 반복되는 실수를 찾아.
이를 막을 수 있는 PreToolUse hook의 초안을 .claude/hooks/proposed/ 에 작성.

⚠️ 사람 검토 후에만 .claude/settings.json에 등록.
```

---

## 8. 응급 상황

### "오 안 돼, Claude가 X를 했어"

```bash
# Step 1: 일단 멈춰
make stop

# Step 2: 무엇을 했는지 파악
git log -10 --oneline
make audit

# Step 3: docs/ROLLBACK_PLAYBOOK.md 보고 시나리오 매칭
```

### 비용이 갑자기 폭주

```bash
make cost
./scripts/audit-query.sh --days 1 --cost
# 폭주 작업 식별 → DAILY_BUDGET_USD를 더 낮추고 ANTHROPIC_API_KEY 회전 고려
```

---

## 9. 프롬프트 작성 팁 (이 라이브러리에 추가할 때)

좋은 프롬프트의 5가지:

1. **명확한 목표**: "X를 해" 보다 "X를 해서 Y가 되게"
2. **출력 형식 명시**: "마크다운으로", "JSON으로", "PR로"
3. **제약 명시**: 토큰/시간/파일 수 한도
4. **금지 명시**: "절대 X 하지 마"
5. **검증 가능한 종료 조건**: "테스트 통과", "lint 0 에러", "PR URL 출력"

피해야 할 것:
- "잘 해줘" → 무엇이 "잘"인지 모름
- "최대한 많이" → 비용 폭주 + 노이즈
- "알아서" → 라우터에 맡길 거면 router.py로 호출. 그 외엔 명확히

---

## 새 프롬프트 추가 시

이 라이브러리에 한 번만 잘 정리해 추가. `.claude/skills/`로 승격할 만큼 안정화되면 skill로 만들기.
