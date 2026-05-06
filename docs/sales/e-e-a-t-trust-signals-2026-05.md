# E-E-A-T 신뢰도 4 신호 (Cycle 63·검색·LLM 노출 핵심)

> Google·LLM·네이버 모두 = E-E-A-T 신뢰도 = 노출 1순위 결정 요인.
> Google Search Quality Rater Guidelines 2022·Anthropic Claude·OpenAI ChatGPT 모두 동일 정합.

## E-E-A-T 4 신호 정의

| 신호 | 의미 | 도서관 SaaS 적용 |
|---|---|---|
| **Experience** (체험) | 1차 자료·실 사용·운영 | 자관 PILOT 6년·NPS 누적·174 파일 |
| **Expertise** (전문성) | 분야 깊이·코드·자격 | 사서 출신·KORMARC 2023.12 100% 정합·1,228 tests |
| **Authoritativeness** (권위) | 외부 인용·표준·MOU | NLK·KAIT·KLA 정합·KOLAS III 후속 |
| **Trustworthiness** (신뢰) | 정직 헤더·법무·약관 | invariant 11·privacy-policy·SLA·환불 정책 |

→ Google 2022 업데이트 = **Trust = 가장 중요·E-E-A 셋의 합**.

## 우리 SaaS E-E-A-T 매트릭스 (Cycle 63 검증)

### Experience (체험·1차 자료)
- ✅ 자관 PILOT 1관 (PO 본인 자관·6년 NPS 누적)
- ✅ 174 파일 = 3,383 레코드 = round-trip 100% (실측)
- ✅ 60 사이클 자율 개발 누적 (외부 901 보고서 진단 인지)
- ⚠ N=1·외부 자관 검증 0 (정직 헤더 박제 = invariant 11)
- ⏳ 외부 5관 PILOT 모집 (Cycle 65+)

### Expertise (전문성)
- ✅ 사서 출신 1인 PO (도메인 + 코드 통합 자격)
- ✅ KORMARC 2023.12 (KS X 6006-0 NLK 2차 개정) 100% 정합
- ✅ 9 자료유형 builder (단행본·연속·비도서·고서·전자책·전자저널·오디오북·멀티미디어·학위논문)
- ✅ 1,228 tests·ruff 0·binary_assertions 39/39
- ✅ 23 ADRs (0024~0046) 의사결정 박제
- ✅ V2 + V3 자율 인프라 100% scaffolding

### Authoritativeness (권위 인용·외부 신뢰)
- ✅ KOLAS III 종료 = books.nl.go.kr (NLK 공식 공지) 출처
- ✅ 헌법 §10·§11·§12 = 인공지능 기본법 §31·디지털포용법 §21 정합
- ✅ KORMARC 2023.12 = NLK 표준 직접 정합
- ✅ KS X 6006-0:2023.12 = 한국 산업 표준 정합
- ⏳ NLK·KAIT·KLA·KLMA MOU (사업자 등록 + 인터뷰 후·Cycle 70+)
- ⏳ 도서관 백서 광고 (2026-12·₩200K/page)

### Trustworthiness (신뢰·정직)
- ✅ 영구 invariants 11건 박제 (PR 차단)
- ✅ 정직 헤더 의무 (페르소나 시뮬 ≠ 인터뷰·invariant 11)
- ✅ privacy-policy-2026-05 = §28의8 5수신자 × 6항목
- ✅ ai-disclaimer-2026-05 = 인공지능 기본법 §31 사전 대응
- ✅ SLA 99.5% (작은도서관)·100% baseline (round-trip)
- ✅ Apache-2.0 license = 코드 오픈·검증 가능
- ✅ ADR 0045 §D = 1인 SaaS 출구 전략 (.mrc 100% export·계약 종료 시)
- ✅ 외부 901 진단 인지·재발 방지 invariant 11 박제
- ⏳ 환불 정책 (refund-2026-05·이미 박제·법적 발행 = 사업자 등록 후)
- ⏳ DPA (Data Processing Agreement·이미 박제·실 계약 = 사업자 등록 후)

## E-E-A-T 코드 적용 (도메인 0원)

### 1. Schema.org Person + Organization JSON-LD 자동
모든 페이지 head = Person·Organization 자동 inject.
sameAs = GitHub·LinkedIn·브런치·네이버 블로그 (도메인 등록 후 추가).

### 2. Author meta 모든 페이지
```html
<meta name="author" content="조기흠 (사서 출신·1인 PO)">
<meta name="publisher" content="kormarc-auto">
```

### 3. About 페이지 (E-E-A-T 4 영역 모두)
`docs/landing/about.md` = 신설 (E + E + A + T 4 섹션 박제).

### 4. 통계 박스 (모든 페이지)
- KOLAS III 종료 D-{N}일 (출처: books.nl.go.kr)
- 자관 PILOT 1관·174 파일·round-trip 100%
- 1,228 tests·v0.7.1·invariants 11
- ADRs 0024~0046 (23건 의사결정 박제)

### 5. 외부 권위 인용 (5 출처)
- 📖 NLK (국립중앙도서관·books.nl.go.kr)
- 🏛 KAIT (한국정보통신산업진흥원·KOLAS III 운영사)
- 🏛 MCST (문화체육관광부·도서관 통계)
- 📚 KLA (한국도서관협회·연 회의 5/31)
- 📚 KLMA (한국도서관경영자협의회)

### 6. License + GitHub badge
- Apache-2.0 license badge
- Build status·tests·ruff·KWCAG·invariants badge 11종

### 7. 정직 헤더 영구 (Trust 핵심)
- 모든 페르소나 doc = "시뮬·인터뷰 N건" 명시
- 모든 발행 자료 = "발행 N건·자관 N관" 명시
- "100% 자동" 약속 X (헌법 §3)

## E-E-A-T → 검색·LLM 노출 영향

| 신호 | Google | 네이버 | LLM (Claude·GPT) |
|---|---|---|---|
| Experience | featured snippet 우선 | C-Rank 가중 | 인용 1순위 |
| Expertise | YMYL 페이지 = 핵심 | 신뢰 ↑·D.I.A.+ | E-E-A-T 점수 |
| Authority | 백링크·sameAs | 외부 인용 가중 | 인용 가능 사실 ↑ |
| Trust | HTTPS·privacy·refund | 신고 X = 신뢰 | hallucination ↓ |

## 측정 (코드 0건 발행 후)

- Google Search Console = "E-E-A-T 신호" 상위 vs 하위 페이지 차이
- 네이버 서치어드바이저 = C-Rank 점수
- AI 인용 모니터링 (Phase 2·`geo/citation_monitor.py`)·인용 횟수 변화

## 정직 헤더

본 매트릭스 = 코드 적용 가능 영역·발행 = PO 외부 작업 후 측정 가능.
E-E-A-T = 단기 효과 X·1~6개월 누적 후 의미 (Google EEAT update 표준).
