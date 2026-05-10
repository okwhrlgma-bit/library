# P-2026-006 — 한국 직장인 N잡 부업 시간·번아웃 분리 추적 (GO·30 앱 #32 신규)

## 페인

- **ID**: P-2026-006
- **discovered_date**: 2026-05-08
- **direct_quote**: "출퇴근 시간=기획·퇴근 후 2~3시간=실행·주말=집중·자동화로 시간 절약·수면 6시간 이하 2주 = 부업 일시 중단" (브런치·세컨드샐러리·SsJum 종합)
- **source**: SsJum 부업 가이드·세컨드샐러리·브런치 사이드 프로젝트 글·ULPHIC STORY
- **audience**: 한국 직장인 N잡러 (2026 직장인 36% = 추정 1,200만~1,800만명)
- **frequency**: 매일 (퇴근 후 2~3시간)
- **current_workaround**: Toggl·Trello·노션·엑셀·종이 노트 (모두 직장 본업 vs 부업 분리 X)
- **willingness_to_pay_signal**: 부업 매출 월 100만 목표·수단 결제 의향 강함 (월 ₩4,900~14,900)

## 시장성

| 항목 | 값 | 점수 |
|---|---|---|
| 검색량 | 한국 ~5,000/월 ("부업 시간 관리"·"N잡 자동화") | +25 |
| 경쟁사 | Toggl (전문)·Trello (일반)·but 부업 분리 niche = 0 | +20 |
| 인디 검증 | 1인 부업 SaaS 사례 1+ ($1K MRR+·세컨드샐러리·ULPHIC) | +15 |
| 빈도 | 매일 | +15 |
| 결제 의향 | 강함 (월 100만 목표·도구 ₩9,900 ROI 명확) | +10 |
| 한국·글로벌 | 한국 niche·글로벌 N잡 시장도 가능 | +10 |
| 외부 트렌드 | 2026 직장인 36% 부업·N잡 골든타임 | +5 |

**시장 점수: 100/100** ✅

## 캐시카우

| 항목 | 값 | 점수 |
|---|---|---|
| ARPU | ₩4,900~14,900/월 (직장인 자비 결제 가능) | +30 |
| COGS | offline 룰 기반·LLM 옵션 (BYOK) = ₩0 기본 | +25 |
| 자동 갱신 | OK (월정액·N잡 지속 = 락인) | +20 |
| 락인 | 강 (시간 history·매출 history·번아웃 추세) | +15 |
| 1인 PO 운영 | 가능 (자동·CSAT 90%+ 가능) | +10 |

**캐시카우 점수: 100/100** ✅

## 컴플

- PIPA: 직장 시간·부업 시간 = 본인 데이터·사용자 컴퓨터 (헌법 §14 정합)
- 노동법: 회사 자원 사용 X 알림 = 사용자 보호
- Q5: PASS

## 결정

```
market 100 ≥ 60·cashcow 100 ≥ 60·Q5 PASS
→ GO ✅ (강력 권장·30 앱 #32 신규 추가)
```

## 단일 기능 (1줄)

```
input  = list[TimeBlock(date, start, end, project, type, focus_score?)]
                + sleep_hours_recent_2weeks?
output = SideHustleReport(daily_split, weekly_burnout, sleep_alert,
                          revenue_per_hour, recommendations)
```

## 30 앱 매트릭스 추가

- **#32 sidehustle-tracker** (D 생산성 카테고리·신규)
- 폴더: `30-apps/32-sidehustle-tracker/`
- #4 librarian-overtime 패턴 재활용 (시간 추적 + 번아웃 = 동일 도메인)
- 차이: **본업/부업 분리 + 수면 6h 임계값 + 시간당 매출**

## 차별화 (vs Toggl·Trello·노션)

| 항목 | Toggl | Trello | 노션 | #32 sidehustle-tracker |
|---|---|---|---|---|
| 가격 | $10/월 | $5/월 | $8/월 | **MIT 무료 / 향후 ₩4,900~9,900/월** |
| 본업/부업 분리 | X | X | 수동 | ✅ 자동 |
| 수면 모니터 | X | X | X | ✅ 6h 임계 자동 정지 |
| 번아웃 카테고리 | X | X | X | ✅ KOSHA 정합 4 단계 |
| 시간당 매출 | X | X | 수동 | ✅ 자동 |
| 데이터 위치 | Toggl 서버 | Trello 서버 | 노션 서버 | **사용자 컴퓨터 (헌법 §14)** |
| offline | X | X | X | ✅ |

## 다음 단계

1. ✅ 30 앱 매트릭스 #32 신규 추가
2. ⏳ 1 cycle 압축 = #32 spec + 코드 + tests 시작 (이번 사이클)
3. ⏳ 발사·홍보 = ADR 0052 정합 = 보류

## 출처

- [부업 창업 가이드 2026 (SsJum)](https://ssjum.com/startup-side-business.html)
- [직장인 사이드잡 7가지 (ULPHIC STORY)](https://blog.ulph.net/high-profit-sidejob-7-2026/)
- [일반 직장인의 첫 사이드 프로젝트 진행기 (브런치)](https://brunch.co.kr/@kaily/13)
- [현실적인 부업 10가지 (세컨드샐러리)](https://www.secondsalary.co.kr/news/articleView.html?idxno=133)
