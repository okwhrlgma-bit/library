# Part 93 — data4library-mcp 통합 검토 (2026-05-03)

> PO 제공: https://github.com/isnow890/data4library-mcp
> MIT·TypeScript·MCP 서버·도서관 정보나루 25+ tool wrapper

---

## 0. 한 줄 결론

> **kormarc-auto 자체 client (`api/data4library.py`) = 핵심 백본 유지**
> **data4library-mcp = Claude Code/Desktop 보조 + MCP Skill 옵션** (Phase 2 보강)

---

## 1. 무엇인가

| 항목 | 값 |
|---|---|
| 이름 | data4library-mcp (isnow890) |
| 라이선스 | MIT (자유 사용) |
| 언어 | TypeScript 92.7% |
| 활동 | 34 commits·★6·🍴2 (소규모·active) |
| 기능 | 도서관 정보나루 OpenAPI 25+ tool MCP wrapper |
| 인증 | `LIBRARY_API_KEY` 환경변수 |
| 한도 | 500~30,000/일 (data4library 정책 정합·IP 등록 시 30K) |

---

## 2. 25+ Tool 카테고리

| 카테고리 | 활용 (kormarc-auto) |
|---|---|
| **Library/Book Search** | aggregator 폭포수 보강 |
| **Trends** (인기·키워드·월간) | 페르소나 02 (작은도서관 수서) |
| **Statistics** (지역·반납 추이) | 사서 C 통계·annual_statistics |
| **Personalization** (마니아·다독자 추천) | 사서 A 수서·acquisition/decision_helper |
| **Location** (GPS 기반 인근 도서관) | 페르소나 03 (P15 순회·이동 중) |
| **Code Helpers** (도서관·지역·KDC 코드) | library_specificity·KDC waterfall |

---

## 3. 자체 client vs MCP 비교

| 차원 | `api/data4library.py` (자체) | data4library-mcp |
|---|---|---|
| 언어 | Python (uniform) | TypeScript (Node 추가 의존) |
| 통합 | aggregator·kdc_waterfall 직접 | MCP protocol 경유 |
| 성능 | 직접 HTTP·단일 프로세스 | npm/npx subprocess·overhead 약 50~100ms |
| 테스트 | pytest mock 즉시 | MCP 서버 mock 필요 |
| 결정성 | 직접 통제 | external server 응답 의존 |
| Claude Code 통합 | 코드 import | Claude Code MCP server 등록 |
| 활용 폭 | kormarc-auto SaaS 1축 | Claude Desktop·Cursor·Claude Code 모두 |

→ **결론: 자체 client = SaaS 백본 유지** + **MCP = 개발 보조 (Claude Code dev session)**

---

## 4. 권장 통합 패턴

### 4.1 SaaS 런타임 (kormarc-auto)
- `api/data4library.py` 직접 호출 = 1차 백본 (Part 87 §4.1)
- 이유: 결정성·성능·Python uniform·결제 흐름 통합

### 4.2 Claude Code 개발 세션 보조 (옵션)
- `.claude/mcp.json` 또는 `.claude/settings.json` MCP 등록
- 개발 중 Claude가 직접 도서관 정보나루 데이터 조회 가능
- 예: "○○도서관 인기대출 top 10 분석" 명령으로 시장 조사 자동

설정 예시 (`.claude/settings.json`):
```json
{
  "mcpServers": {
    "data4library": {
      "command": "npx",
      "args": ["-y", "@isnow890/data4library-mcp"],
      "env": {"LIBRARY_API_KEY": "${DATA4LIBRARY_AUTH_KEY}"}
    }
  }
}
```

→ Claude Code 세션 = 코드 작성 + 시장 데이터 조회 동시.

### 4.3 Agent Skill 패키징 (Part 92 권장)
- `.claude/skills/data4library/` 폴더 = MCP tool 사용법 + 예제 prompts
- kormarc-auto skill (kormarc-build) + data4library skill 동시 등록 = Claude 에이전트 시너지

---

## 5. 즉시 활용 시나리오 (kormarc-auto 영업·연구)

### 5.1 페르소나 02 (작은도서관) 영업 자료
- MCP tool 호출 = "○○구 작은도서관 인기 대출 top 30·KDC 분포" 자동 분석
- → 콜드메일 본문에 "귀 작은도서관 분야별 평균 대출은 ◯○입니다" 자동 삽입

### 5.2 페르소나 03 (P15 순회) GPS 기반
- MCP location tool = 학교 좌표 → 인근 5교 KOLAS 데이터 cross-check
- → 순회사서 워크플로우 자동화

### 5.3 시장 조사 (PO·Claude Code 자율)
- 매주 "전국 인기 대출 KDC 분포 변화" 자동 분석
- Part 88 v2 시장 보고서 데이터 갱신 자동

### 5.4 cross-library 시뮬 (2-2)
- MCP "도서관 코드 + 지역 코드" tool = 5 가상 자관 페르소나 ↔ 실제 도서관 매핑
- → cross_library_simulation.py 실제 데이터 검증

---

## 6. 위험·고려

| 위험 | 대응 |
|---|---|
| Node 의존 추가 | 개발 보조만·SaaS 런타임 X |
| 외부 maintainer (작은 프로젝트·★6) | fork 보존·우리 영구 사용 보장 |
| MCP 서버 응답 형식 변경 | 자체 client 백본·MCP = 보조 |
| API key 관리 | 동일 `DATA4LIBRARY_AUTH_KEY` 재사용 |

---

## 7. 결정·진행

### ✅ 즉시 적용 (Phase 1)
- Part 93 보고서 보존 (본 파일)
- 자체 `api/data4library.py` 백본 유지

### 🔶 Phase 2 (선택 적용·1주)
- `.claude/settings.json` MCP server 등록 (개발 세션 강화)
- `.claude/skills/data4library/` skill 폴더 생성

### ⏸ Phase 3 (보류)
- SaaS 런타임 MCP 전환 = X (성능·결정성 손실)

---

## 8. PO 작업 (옵션·5분)

`.claude/settings.json` MCP 등록:
1. 파일 열기 (없으면 신규)
2. 위 §4.2 JSON 추가
3. Claude Code 재시작
4. `/mcp` 슬래시 명령으로 활성 확인

→ Claude Code dev 세션 = data4library 데이터 직접 호출 가능 (시장 조사·페르소나 검증·콜드메일 자동화).

---

## 9. 출처
- https://github.com/isnow890/data4library-mcp (MIT·★6·34 commits)
- Smithery: https://smithery.ai/server/@isnow890/data4library-mcp
- 도서관 정보나루: https://data4library.kr (Part 92 docs/sales/data4library-onboarding 정합)
- MCP 표준: https://modelcontextprotocol.io
