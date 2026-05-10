# P-2026-001 — 간편 결제 페이지 + PDF/zip 배포 (NO_GO)

## 페인

- **ID**: P-2026-001
- **discovered_date**: 2026-05-08
- **direct_quote**: "just want to host a payment page that delivers a PDF or zip file" (r/SideProject 인용)
- **source**: PainOnSocial·Indie Hackers·r/SideProject
- **audience**: 솔로 개발자·인디 크리에이터·디지털 상품 판매자
- **frequency**: 1회 셋업 + 매월 사용
- **current_workaround**: Gumroad·Lemon Squeezy·Stripe Checkout (모두 작동·but "마켓플레이스 X" 요구)
- **willingness_to_pay_signal**: lifetime $9.99~19.99 약함

## 시장성 (Stage 2)

| 항목 | 값 | 점수 |
|---|---|---|
| 검색량 | 글로벌 ~500/월 (niche) | +5 |
| 경쟁사 | Gumroad·Lemon Squeezy·Sellfy·Payhip·Stripe (5+) | +0 (포화) |
| 인디 검증 | 사례 0~1 ($1K MRR+ 검증 사례 X) | +0 |
| 빈도 | 월 1회 (낮음) | +0 |
| 결제 의향 | 약함 (이미 0% Stripe 사용 가능) | +5 |
| 한국·글로벌 | 글로벌만 | +0 |
| 외부 마이그레이션 | X | +0 |

**시장 점수: 10/100** (포화 + 거대 사업자 정면 경쟁)

## 캐시카우 (Stage 3)

| 항목 | 값 | 점수 |
|---|---|---|
| ARPU | lifetime $9.99 (recurring X) | +0 |
| COGS | Stripe 수수료 2.9% + $0.30 | +10 |
| 자동 갱신 | X (1회성) | +0 |
| 락인 | 약함 (이전 자유) | +5 |
| 1인 PO 운영 | 가능 | +10 |

**캐시카우 점수: 25/100**

## 컴플 (Q5)

- PIPA: PASS (결제 정보 = Stripe 위임)
- 결과: PASS

## 결정

```
market 10 < 60·cashcow 25 < 60·Q5 PASS
→ NO_GO (영구 폐기)
```

## 폐기 이유

1. **거대 사업자 정면 경쟁**: Stripe·Gumroad·LS = 1인 PO가 이길 가능성 = 0
2. **1회성 매출**: lifetime = 캐시카우 X (ADR 0053·0055 정합 X)
3. **인디 검증 사례 부재**: $1K MRR+ 솔로 사례 X
4. **시장 너무 작음**: niche solo dev = SAM ≤ 10,000명

## 재검토 시점

6개월 후 (시장 변화 시)·but 거대 사업자 시장 = 변화 가능성 낮음.

## 출처

- [PainOnSocial](https://painonsocial.com/)
- [50 SaaS Ideas Pulled Straight from Reddit Pain Points (Medium)](https://medium.com/@e2larsen/50-saas-ideas-pulled-straight-from-reddit-pain-points-a64569371691)
- [Indie Hackers solopreneur pain points](https://www.indiehackers.com/post/as-a-maker-or-solopreneur-what-are-your-biggest-pain-points-8c471c0470)
