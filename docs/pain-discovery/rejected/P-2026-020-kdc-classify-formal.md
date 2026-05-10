# P-2026-020 — #2 kdc-classify 정식 평가 (NO_GO·시장 매우 작음)

## 배경

ADR 0065 의무·#2 정식 15 요건 평가 (Cycle 105).

## 15 요건 자동 평가

### PO 3 요건 (17/30)

| 요건 | 점수 | 근거 |
|---|---|---|
| 1. 페인 | 6/10 | KDC 분류 = 사서 보조·but 책 등록 시만 |
| 2. 자동화 | 8/10 | 룰 기반·offline·70+ 키워드 |
| 3. 수익성 | **3/10** | 사서 niche·결제 의향 약함·#4와 동일 |

### 자율 12 요건 (7/12)

| 요건 | 결과 |
|---|---|
| 4. 결제권자=결제자 | ⚠ 사서 본인 결제 약함 |
| 5. 1인 PO 운영 | ✅ |
| 6. 정부·거대 무료 X | ⚠ MarcEdit·KOLAS 부분 |
| 7. founder fit | ✅ PO = 사서 |
| 8. 반복 사용 | ⚠ 책 등록 시만 (1주 1~2권) |
| 9. 락인 | ❌ 약함 (history X·1회 사용) |
| 10. 법적 위험 X | ✅ |
| 11. 한국 + 글로벌 | ❌ KDC = 한국 표준만 |
| 12. 인디 검증 | ⚠ |
| 13. ADR 0052 정합 | ✅ |
| 14. 헌법 §14 | ✅ |
| 15. MIT | ✅ |

## 자동 평가 결과

```
po_score = 17/30
autonomy_score = 7/12
overall = (17/30 × 50) + (7/12 × 50) = 28 + 29 = 57

decision: NO_GO (< 60)
fail_reasons:
  - 4. 결제권자 결제 약함
  - 6. 정부·거대 무료 (MarcEdit·KOLAS)
  - 8. 반복 사용 약함 (1주 1~2권)
  - 9. 락인 X
  - 11. 글로벌 X (KDC 한국 표준만)
penalties: []
```

## 정직 진단

### 강점
- founder fit (PO = 사서)
- 룰 기반·offline·헌법 §14
- 31 tests + ruff 0

### 약점 (NO_GO 핵심)
- **시장 매우 작음**: 사서 31,500 × 등록 빈도 ↓ = 결제 가능 매우 작음
- **반복 사용 X**: 책 등록 = 1주 1~2권 (매일 X·#4 librarian-overtime 대비 약함)
- **글로벌 X**: KDC = 한국 표준·일본 NDC·미국 DDC = 호환 X
- **락인 X**: history 누적 X·다른 도구 이전 자유

## 결정

→ **#2 kdc-classify = NO_GO 정식**·MarcEdit 모델 (Apache-2.0 영구 무료) 권장·#1 통합 가능 (#1 + #2 = KORMARC + KDC 자동 = 1 앱).

## 5 정식 앱 정직 평가 종합

| # | 앱 | 평가 | 결정 |
|---|---|---|---|
| 1 | kormarc-auto | 72 | 🟡 MAYBE |
| **2** | **kdc-classify** | **57** | ❌ **NO_GO** (정식·이번) |
| 4 | librarian-overtime | 71 | 🟡 MAYBE |
| 31 | freelancer-tax-helper | 85 | ✅ GO |
| 32 | sidehustle-tracker | (이전) | ✅ GO |

→ **5 정식 중 GO = 2건 (#31·#32)**·정직.
