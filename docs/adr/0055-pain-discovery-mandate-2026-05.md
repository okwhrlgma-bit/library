# ADR 0055 — 페인 발굴 + 시장성·캐시카우 의무 게이트 (PO 명령 2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠
- 일자: 2026-05-08 (Cycle 86)
- 관계: ADR 0053 보강 (모든 신규 앱 = 본 게이트 통과 후만)·ADR 0052·0054 정합

## PO 메시지

> "인터넷 검색으로 사람들 페인포인트를 찾아내서 해결하는 간단 앱·간단 앱 시작 전 시장성과 캐시카우화 조사 후 시행"

## 결정

**모든 신규 앱 시작 전 = 페인 발굴 + 시장성 + 캐시카우 통과 의무.**

기존 ADR 0053 30 앱 매트릭스 = 페인 발굴 단계 X 진행 (founder fit 가정만)·**향후 추가 앱 = 본 게이트 필수**.

## 4 단계 게이트

| Stage | 시간 | Tool | 통과 임계값 |
|---|---|---|---|
| 1. PAIN DISCOVERY | 1시간 | WebSearch + 공개 자료 | 직접 인용 1+·결제 의향 시그널 |
| 2. MARKET SIZE | 30분 | TAM·SAM·SOM 추정 | 시장 점수 ≥ 60/100 |
| 3. CASH COW | 30분 | 5 질문 + 단위 경제 | 캐시카우 점수 ≥ 60/100 |
| 4. GO/NO-GO | 자동 | 룰 기반 | Q5 PASS + 두 점수 ≥ 60 |

## 워크플로우 박제

`docs/process/pain-discovery-workflow-2026-05.md` 참조.

## 자동 룰

```python
def gate_decision(market: int, cashcow: int, q5: bool) -> str:
    if not q5:                    return "NO_GO"
    if market >= 60 and cashcow >= 60: return "GO"
    if market >= 50 and cashcow >= 50: return "MAYBE"
    return "NO_GO"
```

## 박제 형식 (페인 평가 카드)

```yaml
pain_id: P-2026-XXX
discovered_date: YYYY-MM-DD
direct_quote: "..."
source_url: <URL>
market_score: 0~100
cashcow_score: 0~100
q5_compliance: PASS | FAIL
decision: GO | MAYBE | NO_GO
```

## 30 앱 매트릭스 재배치

기존 30 앱 = founder fit + 일반 가설 기반·**일부 = 페인 검증 미흡**.

신규 매트릭스 = **페인 검증 통과한 앱만 우선순위**:
- ✅ #1 kormarc-auto: KORMARC 사서 페인 검증 (외부 research Part 80)
- ✅ #2 kdc-classify: KDC 분류 페인 검증
- ✅ #4 librarian-overtime: 사서 야근 페인 (감정노동 67.9%·외부 research)
- ⏳ 나머지 27 앱 = 본 게이트 통과 후 진행 (또는 영구 폐기)

## ADR 0052 정합

- ✅ WebSearch (외부 공개 자료) = 허용
- ✅ docs 박제 = 코드 자율
- ❌ 사용자 인터뷰·cold email·외부 베타 = 차단

## 1인 PO 효율

- 1 페인 = 2시간 조사 + 7일 앱 (5% 적중률)
- 평균 20 페인 검토 → 1 GO 앱
- ROI = sunk cost 회피 (NO_GO = 0 시간 투자)

## 영구 자산

- 폐기 페인 박제 = `docs/pain-discovery/rejected/`
- 통과 페인 박제 = `docs/pain-discovery/approved/`
- 6개월 후 시장 변화 시 = 재검토 가능

## 메모리 영속

- `feedback_pain_discovery_mandate.md` ⭐⭐⭐⭐⭐ (신규)
- `MEMORY.md` 인덱스 갱신
- `STATUS.md` Cycle 86 갱신
- CLAUDE.md §8F 추가
