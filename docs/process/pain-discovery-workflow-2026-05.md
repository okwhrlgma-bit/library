# 페인 발굴 + 시장성·캐시카우 조사 워크플로우 (PO 명령 2026-05-08)

> ADR 0055 (신설)·ADR 0052·0053·0054 정합·**모든 신규 앱 = 본 워크플로우 통과 후만 진행**
> PO 명령: "인터넷 검색으로 사람들 페인포인트를 찾아내서 해결하는 간단 앱·시작 전 시장성과 캐시카우화 조사 후 시행"

## 0. 핵심 원칙

| 원칙 | 적용 |
|---|---|
| 페인 = 출발점 | 기능 X·사용자 페인 X·시장 → 페인 발굴 |
| 시장성 X = 폐기 | 통과 임계값 미달 = 0 시간 투자 (sunk cost 회피) |
| 캐시카우 X = 폐기 | 1회성 매출 X·반복 매출 가능성 |
| 조사 1시간·앱 1주 | 시간 투자 비율 = 1:7 (Pieter Levels 5% 적중률 정합) |
| ADR 0052 정합 | WebSearch + 공개 자료 OK·인터뷰·외부 발신 = X |

## 1. 4 단계 워크플로우

```
[1] PAIN DISCOVERY (WebSearch·1시간)
        ↓
[2] MARKET SIZE ASSESSMENT (자료 분석·30분)
        ↓
[3] CASH COW POTENTIAL (단위 경제·30분)
        ↓
[4] GO/NO-GO DECISION (자동 룰)
        ↓
   GO  →  ADR 0053 1주 1앱 사이클 진행
   NO  →  영구 폐기·다음 페인 (sunk cost 0)
```

## 2. STAGE 1 — PAIN DISCOVERY (페인 발굴)

### 2-1. 검색 채널 우선순위

| 채널 | URL/검색어 패턴 | 신뢰도 |
|---|---|---|
| **Reddit r/SideProject·r/Entrepreneur** | "pain point" + niche keyword | ★★★★★ |
| **Hacker News Ask HN** | "Ask HN: What problem are you solving" | ★★★★★ |
| **Indie Hackers Forum** | site:indiehackers.com "pain" | ★★★★ |
| **한국 사이드 프로젝트** | "사이드 프로젝트 한국·디스콰이엇·GeekNews" | ★★★ |
| **Twitter/X** | #buildinpublic + niche | ★★★ |
| **Quora·Stack Exchange** | "How to" + 반복 질문 | ★★★ |
| **유튜브 댓글** | 인기 영상 unmet need | ★★ |
| **앱스토어 리뷰** | 1~3 별점 = "X 안 되어요" 페인 | ★★★★ |
| **블로그·브런치** | 한국 직군 토로글 | ★★★★ |

### 2-2. 페인 검색 템플릿

```
[일반]    "[direction] biggest frustration 2026"
          "what tool is missing in [industry] 2026"
          "Reddit pain point [niche] 2026"

[한국]    "한국 [직군] 시간 낭비 2026"
          "한국 [직군] 자동화 필요 2026"
          "[직군] 답답한 일 2026"

[검증]    "[페인 키워드] 해결 도구 가격"  → 경쟁사 가격
          "[페인 키워드] startup MRR"      → 검증 사례
          "[페인 키워드] indie hacker"      → 1인 가능 검증
```

### 2-3. 페인 박제 형식

```yaml
pain_id: P-2026-XXX
discovered_date: 2026-MM-DD
source: <URL>
direct_quote: "<사용자 직접 발언>"
audience: <누구가 겪음>
frequency: daily | weekly | monthly | yearly
current_workaround: <지금 어떻게 해결>
willingness_to_pay_signal: <"$X 내겠다" 직접 언급 or 추정>
```

## 3. STAGE 2 — MARKET SIZE ASSESSMENT (시장성)

### 3-1. TAM·SAM·SOM 추정

| 영역 | 추정 방법 | 통과 임계값 |
|---|---|---|
| **TAM** (전체) | 구글 트렌드·통계청·해당 산업 보고서 | ≥ 10만명 (한국) or ≥ 100만 (글로벌) |
| **SAM** (도달 가능) | TAM × 인터넷·SNS 도달 가능 비율 | ≥ 1만명 (한국) or ≥ 10만 (글로벌) |
| **SOM** (1년 점유) | SAM × 1~3% (인디 적중률 정합) | ≥ 100명 결제 가능 (Pieter Levels 5% 적중률 보정) |

### 3-2. 시장 신호 점수 (0~100·룰 기반)

```
+25 → 검색량 ≥ 1,000/월 (글로벌) or ≥ 100/월 (한국)
+20 → 경쟁사 1+ 존재 (시장 검증) but ≤ 5 (포화 X)
+15 → 인디 검증 사례 1+ ($1K MRR+)
+15 → 주 1회+ 페인 발생 (사용 빈도)
+10 → 결제 의향 직접 발언 1+
+10 → 한국·글로벌 양면 가능
+5  → KOLAS III 등 외부 마이그레이션 골든윈도우

총 100점·통과 = ≥ 60
```

## 4. STAGE 3 — CASH COW POTENTIAL (캐시카우 가능성)

### 4-1. 단위 경제 (5 질문 정합·`.claude/rules/business-impact-axes.md`)

| 질문 | 임계값 |
|---|---|
| Q1 결제 의향 | HIGH/MID (직접 발언 또는 유사 직군 결제) |
| Q2 비용 | 권당 ₩100 이하 or LLM 미사용 (offline 우선) |
| Q3 자산 | 재사용 ≥ 50% (다른 앱 재활용) |
| Q4 락인 | MID 이상 (사용자 데이터 누적·전환 비용) |
| Q5 컴플 | PASS (PIPA·자관 익명화·헌법 §3·§14) |

### 4-2. 캐시카우 점수 (0~100)

```
+30 → ARPU ≥ ₩4,900/월 (사서 자비 한도 정합) or ≥ $9.99/월 (글로벌)
+25 → COGS 권당 ≤ ₩100 (마진 90%+)
+20 → 자동 갱신 가능 (월정액 PG 자동 차감)
+15 → 락인 메커니즘 1+ (자관 양식·routine·통계 history)
+10 → 1인 PO 운영 가능 (지원 = 자동·CSAT 90%+)

총 100점·통과 = ≥ 60
```

## 5. STAGE 4 — GO/NO-GO 결정

### 5-1. 자동 룰

```python
def go_or_no_go(market_score: int, cashcow_score: int, q5_compliance: bool) -> str:
    if not q5_compliance:
        return "NO_GO"  # 컴플 = 별도 게이트·다른 점수 무관
    if market_score >= 60 and cashcow_score >= 60:
        return "GO"
    if market_score >= 50 and cashcow_score >= 50:
        return "MAYBE"  # PO 결정
    return "NO_GO"  # 영구 폐기
```

### 5-2. GO 시 다음 단계

1. ADR 0053 1주 1앱 사이클 진행 (Mon spec → Sun docs)
2. 30 앱 매트릭스에 추가 (`docs/portfolio/30-apps-roadmap-2026-05.md`)
3. 발사·홍보 = ADR 0052 정합 = 보류

### 5-3. NO_GO 시

1. 영구 폐기 박제 (`docs/pain-discovery/rejected/`)
2. 폐기 이유·점수 기록
3. 동일 페인 재검토 = 6개월 후 (시장 변화 시)

## 6. 박제 위치

```
kormarc-auto/docs/
├── process/
│   └── pain-discovery-workflow-2026-05.md  (이 파일)
├── pain-discovery/
│   ├── candidates/
│   │   ├── P-2026-001-<pain-name>.md
│   │   └── P-2026-002-<pain-name>.md
│   ├── approved/  (GO 통과)
│   └── rejected/  (NO_GO)
└── adr/
    └── 0055-pain-discovery-mandate-2026-05.md
```

## 7. ADR 0052 정합

- ✅ WebSearch 사용 (외부 공개 자료 분석 = 허용)
- ✅ 페인 박제·시장성 보고·캐시카우 평가 = docs 작성
- ❌ 사용자 직접 인터뷰 X
- ❌ cold email·SNS 글 X
- ❌ 외부 베타 모집 X
- ❌ 발사·홍보 X (PO 결정 시)

## 8. 1인 PO 효율

- 페인 발굴 1시간 + 시장성 30분 + 캐시카우 30분 = **2시간 조사**
- 조사 통과 = 7일 1앱 = **2시간 : 7일 = 1:84 시간 비율**
- Pieter Levels 5% 적중률 = 평균 20 페인 검토 → 1 GO
- 즉, 40시간 조사 → 7일 앱 1개 = 47시간 = ROI 정합

## 9. 7 핵심 점수 카드 (자동 출력)

```markdown
# 페인 P-2026-XXX 평가 카드

## 페인
- ID: P-2026-XXX
- 직접 인용: "..."
- 출처: <URL>
- 발생 빈도: <daily|weekly|monthly>
- 결제 의향 시그널: <강|중|약>

## 시장성
- TAM: <N명>
- SAM: <N명>
- SOM (1년): <N명>
- 시장 점수: <0~100>

## 캐시카우
- ARPU 가설: <₩X/월>
- COGS 가설: <₩Y/월>
- LTV (3년): <₩Z>
- 캐시카우 점수: <0~100>

## 컴플
- Q5: <PASS|FAIL>
- 근거: <...>

## 결정
- 자동: <GO|MAYBE|NO_GO>
- 근거: <...>
```

## 10. 출처·정합

- ADR 0052 (코딩 외 활동 0건)·0053 (30 앱)·0054 (외부 research)
- `.claude/rules/business-impact-axes.md` (5 질문·Beta 가중치)
- Pieter Levels 70+ 프로젝트 5% 적중률 (외부 research·learnings 사실 94)
- Tony Dinh "6개월 무피드백 = sunset"
- Mom Test (의견 < 행동 < 결제)
