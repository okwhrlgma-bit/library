# P-2026-012 — 한국 1인 PT 트레이너 회원 관리 SaaS (NO_GO·시장 포화)

## 페인

- audience: 한국 1인 PT 트레이너·프리랜서 약 5만명+
- frequency: 매일 (회원 관리·스케줄·식단·운동 일지)
- current_workaround: **바디코디·헬스노트·헬린캠프·피트·트쌤일지 (5+ SaaS 점유·일부 무료)**

## 평가

| 항목 | 점수 |
|---|---|
| 시장 = 5만+·매일 사용 | +20 |
| 경쟁 = 5+ 거대 SaaS (바디코디 키오스크·CRM 통합·1인 PO X) | +0 (포화) |
| 인디 검증 = Health-Note GitHub 오픈 소스·but 시장 = 거대 사업자 점유 | +5 |
| 빈도 매일 | +15 |
| 결제 의향 = 트레이너 본인 ₩30K~50K/월 가능 | +5 |
| 한국 niche | +5 |

**시장 점수: 50/100** (포화·거대 점유)

## 캐시카우

| 항목 | 점수 |
|---|---|
| ARPU = ₩30K~50K/월 | +20 |
| 자동 갱신 OK | +20 |
| 락인 강 (회원 history) | +15 |
| 1인 PO 운영 = 매우 어려움 (CRM·키오스크·출입·결제 통합 = 5인+ 팀) | +0 |
| COGS 서버 비용 (회원 데이터·이미지·동영상) | +5 |

**캐시카우 점수: 60/100** (1인 운영 X)

## Q5

- PIPA: 회원 PII + 식단·체중 = 민감정보 위험
- 의료법: 식단 처방·운동 처방 = 의료 자문 X 의무
- Q5: 위험 (PIPA + 의료법)

## 결정

```
market 50 < 60·cashcow 60 (경계)·Q5 위험
ADR 0058 4 조건 = market <75·캐시카우 <80
→ NO_GO (영구 폐기)
```

## 폐기 이유

1. **거대 SaaS 5+ 정면**: 바디코디·헬스노트·헬린캠프·피트·트쌤일지 = 1인 PO X
2. **CRM + 키오스크 통합** = 5인+ 팀 필요
3. **PIPA + 의료법 위험** = 1인 PO 법무 부담 ↑
4. **회원 데이터 = 민감** = 외부 SaaS 거부 가능

## 출처

- [바디코디](https://bodycodi.com/)
- [Health-Note GitHub](https://github.com/Health-Note/Health-Note)
- [헬린캠프](https://hellin.camp/)
- [피트 App Store](https://apps.apple.com/kr/app/%ED%94%BC%ED%8A%B8/id1490531630)
- [트쌤일지](https://gongysd.com/template/?idx=99)
