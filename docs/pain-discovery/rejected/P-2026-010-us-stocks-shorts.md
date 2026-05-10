# P-2026-010 — 미국 주식 자동 유튜브 숏츠 (NO_GO·RPM 낮음·시장 작음)

## 페인 (PO 통찰 I-001 정식 평가)

- audience: 한국 미국 주식 투자자 1,400만+·but **콘텐츠 도구 사용자 = 매우 작은 부분**
- frequency: 매일 (자동)
- current_workaround: Opus Clip ($10M+ ARR)·Virvid·Vozo (AI 영상)·Pictory·InVideo

## 시장성

| 항목 | 점수 |
|---|---|
| 검색량 | +15 |
| 경쟁 = 글로벌 거대 (Opus Clip·Virvid·Vozo·Pictory·InVideo·Synthesia) | +0 (포화) |
| 인디 검증 | +5 |
| 빈도 = 매일 | +15 |
| 결제 의향 = 채널 운영자 niche | +5 |
| 한국·글로벌 | +5 |
| 외부 트렌드 = 자동 숏츠 시장 ↑ | +5 |

**시장 점수: 50/100** (포화·거대 사업자 다수)

## 캐시카우

| 항목 | 점수 |
|---|---|
| ARPU $9~29/월 | +25 |
| COGS LLM + TTS + 영상 = ↑ | +5 |
| 자동 갱신 = OK | +20 |
| 락인 = 약함 (이전 자유) | +5 |
| 1인 PO 운영 = 어려움 (영상 인프라·YouTube API) | +5 |

**캐시카우 점수: 60/100** (직접 운영 시 광고 RPM 매우 낮음·$0.01~0.05/1K views)

## Q5

- PIPA: 사용자 데이터 X (공개 시장 데이터만) = PASS
- **자본시장법**: "이 종목 사세요" X·"단순 정보 요약" 명시 의무 = 면책
- 결과: PASS (조건부)

## 결정

```
market 50 < 60·cashcow 60·ADR 0058 4 조건 = market <75·캐시카우 <80
→ NO_GO (영구 폐기)
```

## 폐기 이유

1. **유튜브 숏츠 RPM 매우 낮음**: $0.01~0.05/1K views·실 수익 = $100~500/월 (대부분 크리에이터)
2. **글로벌 거대 사업자 정면**: Opus Clip ($10M+ ARR)·InVideo·Synthesia ($50M+ ARR) = 1인 PO X
3. **단순 자동 영상 = 차별화 부족**: 한국 미국 주식 niche → 인플루언서 채널 = 사람 출연 + 분석 = 자동 영상 차별화 약함
4. **B2B SaaS (다른 채널 운영자) = 시장 매우 작음**: 한국 미국 주식 채널 운영자 niche·SAM ≤ 5,000명
5. **운영 부담**: 매일 새벽 자동·YouTube API·영상 인프라·yfinance·LLM·TTS = 1인 PO 부담 ↑

## 대안 (재검토 가능)

I-001 변형 = NO_GO·but 다음 변형은 GO 가능:
- **A**: 미국 주식 데이터 → 한국어 일일 텍스트 뉴스레터 (영상 X·LLM만·SubStack 모델)
  - 시장: 한국 미국 주식 투자자 1,400만 = HIGH
  - 캐시카우: SubStack ₩4,900/월·간단
  - 1인 운영 가능
  - **MAYBE GO·재평가 가치 있음**
- **B**: 미국 주식 시뮬레이터 (모의 투자·게임화) = 시장 포화 (한국투자·미래에셋)·NO_GO
- **C**: 자본시장법 정합 면책 정보 요약 도구 (B2B 채널 운영자·but 시장 작음)·NO_GO

## 6개월 후 재검토

직접 운영 = NO_GO·but **변형 A (텍스트 뉴스레터)** = 다음 사이클 별도 검토 가치.

## 출처

- [YouTube Shorts Monetization 2026 (Ssemble)](https://www.ssemble.com/blog/youtube-shorts-monetization-2026)
- [How to Make Money AI Videos 2026 (Kineclip)](https://www.kineclip.com/blog/how-to-make-money-with-ai-videos-2026/)
- [Faceless YouTube Monetization 2026 (Mixcord)](https://www.mixcord.co/blogs/content-creators/faceless-youtube-monetization-ai-automation)
- [Creator Monetization 2026 (Communipass)](https://communipass.com/blog/creator-monetization-2026-complete-guide-ai-era-2/)
