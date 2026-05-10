# P-2026-002 — 블로그 글 → 다중 플랫폼 자동 재작성 (MAYBE → 30 앱 #10 정합)

## 페인

- **ID**: P-2026-002
- **discovered_date**: 2026-05-08
- **direct_quote**: "want automation for taking a blog post and rewriting it for different platforms (Twitter, LinkedIn, newsletters)" (r/SideProject·Medium 종합)
- **source**: r/SideProject·Indie Hackers·Medium "50 SaaS Ideas"
- **audience**: 콘텐츠 크리에이터·1인 마케터·인디 해커·솔로프리너
- **frequency**: 주 1~3회 (높음)
- **current_workaround**: Buffer·Hootsuite·Hypefury·수동 복사 (모두 비싸거나 niche 부족)
- **willingness_to_pay_signal**: 월 $9~19 직접 발언 다수

## 시장성

| 항목 | 값 | 점수 |
|---|---|---|
| 검색량 | 글로벌 ~5,000/월 ("content repurposing tool") | +25 |
| 경쟁사 | Buffer·Hootsuite·Hypefury (3+ but 솔로 niche 부족) | +20 |
| 인디 검증 | Hypefury·Typefully ($10K~50K MRR+) | +15 |
| 빈도 | 주 1~3회 (높음) | +15 |
| 결제 의향 | 강함 ($9~19/월 다수) | +10 |
| 한국·글로벌 | 글로벌·한국 양면 | +10 |
| 외부 마이그레이션 | X | +0 |

**시장 점수: 95/100** ✅

## 캐시카우

| 항목 | 값 | 점수 |
|---|---|---|
| ARPU | $9~19/월 (월정액) | +30 |
| COGS | LLM API 권당 ₩50~100 (Claude Sonnet) | +25 |
| 자동 갱신 | OK (월정액) | +20 |
| 락인 | 중 (콘텐츠 history·brand voice 학습) | +10 |
| 1인 PO 운영 | 가능 (지원 자동) | +10 |

**캐시카우 점수: 95/100** ✅

## 컴플

- PIPA: PASS (사용자 콘텐츠만·자관 X)
- Q5: PASS

## 결정

```
market 95 ≥ 60·cashcow 95 ≥ 60·Q5 PASS
→ GO (강력)·but 30 앱 #10 sns_multipost와 정합
```

## 30 앱 정합 분석

기존 #10 sns_multipost (auto-clicker-saas):
- 입력: 사진 → 인스타+X+페북 (사진 중심)

본 페인 P-002 = **블로그 글 → 다중 플랫폼** (텍스트 중심)

→ **#10 sns_multipost 확장** 권장:
- A모드: 사진 → 다중 SNS (기존)
- B모드: 블로그 글 → 다중 플랫폼 재작성 (신규)
- 통합 = 1 앱·2 모드·시장 ↑·캐시카우 ↑

## 다음 단계

1. ✅ 30 앱 매트릭스 #10 = MAYBE → GO 승격
2. ⏳ 다음 1주 사이클 = #10 코드 시작 (sns_multipost 확장)
3. ⏳ 발사·홍보 = ADR 0052 정합 = 보류

## 출처

- [PainOnSocial Find Real Customer Pain Points](https://painonsocial.com/)
- [50 SaaS Ideas Pulled Straight from Reddit Pain Points](https://medium.com/@e2larsen/50-saas-ideas-pulled-straight-from-reddit-pain-points-a64569371691)
- [17 Solo Founder SaaS Ideas](https://painonsocial.com/blog/solo-founder-saas-ideas)
