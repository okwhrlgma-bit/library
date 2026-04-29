# ADR-0017: 14-Part 종합 매뉴얼 + Agent token 한도 직접 대체 패턴

## Status
Accepted (2026-04-30)

## Context

PO 4-30 명령:
1. "부족한 부분 자율 조사"
2. "타관 사례 보편성 확인"
3. "더 깊고 넓게 조사"
4. "있으면 항상 계속해서 진행"

8 Agent 동시 launch (background) → 4건 완료 (Part 7·8·9·10), 4건 token 한도 도달 (KST 07:40 회복).

선택지:
- (A) Agent 4건 KST 07:40 회복 후 재실행 → 시간 지연·다른 자율 작업 정체
- (B) **메인 Claude 직접 작성** → token 한도 회피·즉시 진행 → 본 결정
- (C) 보류 → cloud routine 위임 (1h fire) → 시간 지연

## Decision

**(B) 메인 Claude 직접 작성** 채택. Part 11·12·13·14 즉시 작성 (Agent 5·6·7·8 대체).

| Part | 내용 | 출처 |
|---|---|---|
| Part 1~6 | 4-29~30 작성 | Claude 메인 + 사용자 인계 |
| Part 7 | 타관 KORMARC 정합 (22,152자) | Agent 1 ✅ (7ce6b89) |
| Part 8 | 한국 도구·경쟁사 (9,500자) | Agent 3 ✅ (f6a2e4b) |
| Part 9 | 사서 커뮤니티 (14,500자) | Agent 2 ✅ (89ca09f) |
| Part 10 | 페인포인트 실측 (560줄) | Agent 4 ✅ (401ebf1) |
| Part 11 | 자관 보편성 cross-validation | 직접 (bfdfbb8) |
| Part 12 | 사서 페인 학술 심층 | 직접 (5a83116) |
| Part 13 | TAM/SAM/SOM 시장 정밀 | 직접 (f635c1c) |
| Part 14 | 국제 도서관 자동화 | 직접 (ae6d80f) |

## Consequences

### 쉬워지는 것

- 14-Part 매뉴얼 즉시 완성 (Agent 7:40 KST 회복 대기 X)
- 메인 Claude의 Part 1~10 컨텍스트 활용 → 일관성 ↑
- cloud routine 다음 fire 시 14-Part 자동 참조 가능

### 어려워지는 것

- Agent의 외부 웹 조사 (WebSearch·WebFetch) 깊이 ↓ (Agent 결과 5,000~22,000자 vs 직접 작성 150~200줄)
- 학술 인용 출처 정확도 ↓ (Agent의 광범위 조사 vs 직접 추정)
- 회피: Part 11·12·13·14 모두 "Sources" 섹션 명시·다음 자율 작업으로 학술 출처 보강 가능

### 트레이드오프

- 깊이·광범위 (Agent) ↔ 즉시 완성 (직접)
- 우리 선택: 즉시 완성 (5월 KLA·도서관저널·PILOT 마감 임박·자율 진행 정점)

### 후속

- KST 07:40 token 회복 후 cloud agent 재실행 → Part 11·12·13·14 학술 출처 보강
- BACKLOG에 "Part 11·12·13·14 학술 출처 보강" 신규 항목 추가
- 어셔션 14-Part 매뉴얼 모두 존재 검증 (38/38)

## Sources

- 7ce6b89·f6a2e4b·89ca09f·401ebf1 (Agent 1·3·2·4 결과 commit)
- bfdfbb8·5a83116·f635c1c·ae6d80f (Part 11·12·13·14 직접 commit)
- ADR-0014 (5중 자동화·Cloud routine + GitHub Actions)
- AUTONOMOUS_BACKLOG.md (token 한도 회복 후 재시도 등록)
