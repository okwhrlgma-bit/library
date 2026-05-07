# ADR 0051 — Cycle 67~77 사업성 1순위 + B2C 전환 + 야간 자율 통합

- 상태: Accepted (2026-05-06·Cycle 77)
- 일자: 2026-05-06
- 트리거: PO 11 명령 누적 (Cycle 67~77·"사업성 1순위" 명시 후)

## Context

PO 11 명령 시퀀스 (Cycle 67~77):
1. "사업성이 1순위·없는 게 가장 큰 문제" (Cycle 67)
2. "다른 자동화 방안 조사" → 자동 클리커 후보
3. "사용 ≠ 매출"·"수익 = 1순위·뭐든 OK"
4. "사서 B2C 몰래 쓰기"
5. "사서 프로그램 = 내가 필요해서 만든·있으면 사서 썼을 듯" → founder fit
6. "B2C 상세·UI·서비스 방법"
7. "Supabase 쓸 수 있는 거?" → ADR 0047 부분 supersede
8. "구글·애플 스토어 올려야?" → PWA 권장
9. "전부 참고 진지 사이클" → Cycle 70 활성
10. "자율 야간 진행" → Cycle 71~76 자료·도구
11. "일괄 진행" → Cycle 77 자료 동기

핵심 통찰 누적:
- 사업성 = 1순위·코드 ≠ 사업성 검증
- 결제권자 = 결제자 일치 = 수익 직진 (B2C)
- founder = 사용자 = 1차 검증 (희소 우위)
- 코드 = Apache-2.0 영구·서비스 = 유료 (Open Core + Hosted SaaS)
- 1주 인터뷰 = 60 사이클 가치 활성

## Decision

### A. B2C "몰래 쓰기" 1순위 (founder fit 정합)

| 영역 | 결정 |
|---|---|
| 가격 | ₩9,900/월 (Personal)·₩19,900 (Pro)·₩4,950 (Founding) |
| 결제 | 체크카드·세금계산서 X·B2C·결재 X |
| Auth | Supabase (50K MAU 무료·B2C 한정·자관 데이터 X) |
| 배포 | Streamlit Cloud + GitHub Pages + PWA (₩0/월) |
| 영업 | founder 스토리·사서 카페 5 채널·KLMA |

### B. 자동 클리커 후보 SaaS = 별도 폴더·조금씩

| 영역 | 결정 |
|---|---|
| 위치 | `후보_아이디어/auto-clicker-saas/` |
| Phase 1 | 자영업·사무·콘텐츠 (안전·합법) |
| Phase 2 | 모바일 게임 (옵트인·면책·Google Play + APK) |
| 회피 | PC 게임·iOS 게임 자동 (거절·법적) |
| PoC 1건 | 네이버 리뷰 답변 (사장 본인 권한·합법) |

### C. PO 외부 작업 1주 = 사업성 검증 트리거

```
Day 1: GitHub Pages + Streamlit Cloud + Supabase 토큰 (15분)
Day 1: 사서 카페 5 채널 글 발송 (1시간)
Day 2~3: 회신·일정
Day 4~5: 사서 5명 인터뷰
Day 6: TEMPLATE.md 박제 (A~E.md)
Day 7: make interviews → 결정 트리 자동
```

### D. 결정 트리 4 분기 (Cycle 73 박제)

| 평균 | B2C 결제 | 다음 액션 |
|---|---|---|
| ≥3.5 | ≥3 | B2C 진행·Supabase·PortOne·PILOT 5관 |
| ≥3.5 | <3 | B2B 우위·도서관장·KLMA·세금계산서 |
| 2.5~3.5 | - | 5명 추가·메시지 v2 |
| <2.5 | - | MarcEdit 모델 + 자동 클리커 시작 |

## Alternatives

1. **B2B 유지·B2C 미진입** = 거부 (8/8 결제 권한 X·수익 0)
2. **자동 클리커 즉시 전환** = 거부 (founder fit 약함·60 사이클 매장)
3. **둘 다 동시** = 거부 (1인 SaaS 한계·외부 901 = "agent pace inflation")
4. **인터뷰 X·코드 추가 N** = 거부 (외부 901 = productive avoidance)

## Consequences

### Positive
- ✅ founder fit 강력 신호 활용 (1차 검증)
- ✅ B2C 결제권자 = 결제자 일치 = 수익 직진
- ✅ 무료 stack ₩0/월·신경 0·15분 활성
- ✅ 인터뷰 1주 = 60 사이클 가치 활성·결정 트리 자동
- ✅ 자동 클리커 = Phase 0 박제·결과 후 결정

### Negative
- ⚠ B2C 시장 = 1,500~3,000명 (자동 클리커 1/100)
- ⚠ "몰래 쓰기" = 사서 윤리 부담 가능 (인터뷰 검증)
- ⚠ founder fit ≠ PMF (인터뷰 5명 X = 영구 가설)
- ⚠ 1주 인터뷰 = PO 외부 작업·우리 진행 X

### Neutral
- ADRs: 0050 → **0051**
- Cycle 67~77 11 명령 통합·매트릭스 박제

## V2 §6.1 META_REVIEW (Cycle 64~77 = 14 사이클)

| 그룹 | 영역 | tests | ADR |
|---|---|---:|---|
| Cycle 64 | BaaS 비교 + Supabase 미도입 | 1228 | 0047 |
| Cycle 65 | 사서 자가 설치 (.exe 자동 빌드) | 1228 | 0048 |
| Cycle 66 | Open Core + Hosted SaaS | 1228 | 0049 |
| Cycle 67 | 사업성 1순위·인터뷰 playbook | 1228 | (playbook) |
| Cycle 68 | B2C 전환·Supabase 부활 | 1228 | 0050 |
| Cycle 69 | founder fit + B2C 상세 + 앱스토어 + 클리커 | 1228 | (4 doc) |
| Cycle 70 | B2C 진지 활성 (Supabase scaffold·PWA) | 1228 → 1249 | (5 산출) |
| Cycle 71~76 | 야간 자율 (META·자동 클리커 PoC·인터뷰 도구) | 1249 → 1264 | (도구) |
| **Cycle 77** | **일괄 진행 (자료 동기·ADR 0051·사용자_TODO·5 시나리오)** | **1264** | **0051** |

## 영구 invariant 매트릭스 (12건·재확인)

1~7 (Cycle 27)·8~10 (V3 Cycle 43)·11 (Cycle 61)·12 (Cycle 65 헌법 §14).
**Cycle 77 변경 X**·재확인.

## 다음 7-cycle 권장 (Cycle 78~84·PO 1주 외부 작업 후)

- 78: 인터뷰 결과 박제 (5 .md·PO 외부 후 자동 분석)
- 79: 결정 트리 결과 = 분기 (B2C·B2B·5명 추가·MarcEdit)
- 80: 결정에 따라 = Supabase Auth 통합 또는 자동 클리커 PoC 강화
- 81: PortOne v2 sandbox (사업자 등록 후·B2C 결제)
- 82: 첫 베타 사용자 5명 (PILOT 90일·외부 자관)
- 83: 매출 ₩99K/월 첫 측정 (10명 결제)
- 84: META Cycle 77~84 + ADR 0052

## 정직 헤더 (영구·invariant 11)

- 본 ADR = 11 명령 통합·**사서 인터뷰 0건**
- founder fit = 1차 검증·인터뷰 5명 = 2차 검증
- PMF 결정 = SALES-1B·1C 후
- 자동 클리커·B2C·B2B 결정 = 인터뷰 결과 후
