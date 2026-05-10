# P-2026-023 — 한국 1인 인디 빌더 영문 SEO 자동 (NO_GO·보수 보정)

## 페인

- audience: 한국 1인 인디 빌더 약 5,000~10,000명
- frequency: 매주 (콘텐츠·SEO)
- current_workaround: **Ahrefs ($99~999/월)·SEMrush·MOZ·Google Search Console (무료)·LaunchTry**

## 15 요건 자동 평가

### PO 3 요건 (22/30)
| 요건 | 점수 |
|---|---|
| 1. 페인 | 8/10 (90% 인디 distribution 실패·외부 research) |
| 2. 자동화 | 7/10 (LLM 영문 메타·블로그) |
| 3. 수익성 | 7/10 (₩9,900~29,900/월) |

### 자율 12 요건 (8/12)
| 요건 | 결과 |
|---|---|
| 4. 결제권자=결제자 | ✅ |
| 5. 1인 PO 운영 | ✅ |
| 6. 정부·거대 무료 X | ❌ Ahrefs·SEMrush·Google Search Console |
| 7. founder fit | ✅ PO = 한국 1인 빌더 |
| 8. 반복 사용 | ✅ 매주 |
| 9. 락인 | ⚠ |
| 10. 법적 위험 X | ✅ |
| 11. 한국 + 글로벌 | ✅ |
| 12. 인디 검증 | ✅ Indie Hackers·90% distribution 실패·강력 |
| 13~15 | ✅ |

## 페널티

- `giant_competitor_billion` = ✅ (Ahrefs $1B+ 가치) = **-10**

## 자동 평가

```
po_score = 22/30 = 37
autonomy_score = 8/12 = 33
overall = 37 + 33 = 70
페널티 -10 = 60

decision: MAYBE (60·경계선)·v5 통과 (founder ✅·indie ✅)
```

## 정직 보수 보정 = NO_GO

자동 = MAYBE 60·but 정직:
1. **Ahrefs 시가총액 $1B+** = 1인 PO 정면 X
2. **시장 작음**: 한국 인디 빌더 SAM 5,000~10,000·SOM 500
3. **Google Search Console 무료** + Indie Hackers 커뮤니티 무료
4. SEO niche = 글로벌 거대 SaaS 다수 (Ahrefs·SEMrush·Surfer SEO)

→ **보수 NO_GO** (MAYBE 경계 + 거대 페널티 = 사람 판단).

## ADR 0065 v5 한계 발견

v5 = founder + indie 동시 ✅ → MAYBE/GO 통과·but **거대 사업자 페널티만으로 부족**.

→ **다음 cycle 룰 v6 후보**:
- `giant_competitor` + 시장 SAM < 10,000 = NO_GO 자동 강제

## 출처

- [Indie Hacker Marketing Playbook 2026 (Prems AI)](https://prems.ai/blog/indie-hacker-marketing-playbook-2026)
- [Indie Hacker SEO Checklist (LaunchTry)](https://launchtry.com/resources/seo-checklist/indie-hacker)
- [Google's January 2026 Update (Indie Hackers)](https://www.indiehackers.com/post/googles-january-2026-update-indie-hackers-your-personal-brand-is-now-your-seo-a49ce4ca14)
