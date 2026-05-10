# ADR 0054 — 외부 advanced research 흡수 + ADR 0052 정합 매트릭스

- 상태: Accepted
- 결정자: Claude (자율·ADR 0052 정합 분석 결과)
- 일자: 2026-05-07 (Cycle 85)
- 관계: ADR 0052 (코딩 외 활동 0건)·ADR 0053 (30 앱 포트폴리오) 정합

## 맥락

PO가 "코딩 외 활동 0건" 명시 (ADR 0052·2026-05-07) 직후 advanced research 결과 2건 제공:

1. **17 P-series 명령어 묶음** (Pieter Levels·Tony Dinh·Marc Lou 인디 패턴 + 한국 1인 사업자 행정·세무·법무)
2. **kormarc-auto B2C 시장 종합 심층 조사** (페르소나 5종·채널 SEO·경쟁자·가격·법제도·6주 KPI·리스크·일본 수출)

두 보고서 = **launch + 외부 활동 + 5명 결제 게이트 전제** = ADR 0052 직접 충돌.

## 결정

**외부 research = 참고 자산 박제만·실 활성 = PO 명시 명령 시.**

### 박제 (Claude 자율 OK)
- `docs/research/external-2026-05/p-series-light-17-commands.md` ✅
- `docs/research/external-2026-05/b2c-market-deep-research.md` ✅
- 본 ADR 0054
- STATUS·learnings·CLAUDE 갱신

### 실 활성 (PO 명시 명령 시·보류)
- 사업자 등록·통신판매업 신고 (P29L)
- 사서 채널 5곳 콘텐츠 발행 (P34L)
- Chrome Web Store Trader 등록·$5 fee (P39L)
- HN·PH·Reddit·X·GeekNews 발행 (P40L)
- 토스페이먼츠·Plausible·Resend·Notion·ExtensionPay·LS·Stripe 외부 가입
- KLA 5/31 발표·콜드콜·사서 5명 인터뷰

## P-series 17건 ADR 0052 정합 분류

### ✅ Claude 자율 즉시 가능 (9건)
| # | 내용 | 산출물 |
|---|---|---|
| P30L | 처리방침·이용약관·환불 | apps/kormarc/(legal)/privacy·terms·refund mdx |
| P31L | 1페이지 랜딩 + 가격 + 데모 | apps/kormarc/page.tsx |
| P36L | Chrome 확장 niche 결정 | docs/products/chrome-ext-bets.md + 결정 로그 |
| P37L | MV3 minimal 스캐폴드 | apps/chrome-ext/ + Vite + CRXJS |
| P42L | packages/ 승격 (3번째 사용처 게이트) | packages/{payments,analytics,legal,email,ui} |
| P44L | 5명 룰 자동 판정 + archive 추천 | scripts/portfolio/ |
| P45L | 새 프로젝트 boilerplate slash command | .claude/commands/new-product.md |
| P47L | 1인 사업자 행정 캘린더 | docs/ops/calendar.ics·tax_pull.py |
| P48L | Q4 portfolio 평가 + 손절·재활용 | scripts/portfolio/q4_evaluation.py |

### 🟡 부분 자율 (코드만·5건)
| # | 코드 자율 | PO 외부 |
|---|---|---|
| P29L | check_kr_business.py·docs/ops/ | 홈택스·정부24 등록 |
| P32L | manual checkout 라우트·script | 토스 QR·노션·Resend 가입 |
| P33L | analytics 컴포넌트·weekly_funnel | Plausible 가입·도메인 |
| P35L | 통합 게이트·git tag·webhook 코드 | 슬랙 가입·실 launch |
| P38L | payments.ts wrapper·환불 페이지 | ExtPay·Stripe 가입 |
| P41L | 5명 룰·LS 마이그레이션 SOP | LS 가입 |
| P43L | 매월 1일 portfolio 점검 코드 | 노션·슬랙 가입 |
| P46L | 매주 월요일 마이크로 리포트 코드 | 슬랙 가입 |

### ❌ 외부 차단 (3건·발행/등록)
| # | 차단 이유 |
|---|---|
| P34L | 사서 채널 5곳 발행 (사서e마을·X·IG·학회·뉴스레터) |
| P39L | Chrome Web Store Trader 등록 + $5 fee + 심사 |
| P40L | Build-in-public 5채널 발행 (HN·PH·Reddit·X·GeekNews) |

## B2C 보고서 ADR 0052 정합 분류

### ✅ Claude 자율 즉시 가능
- 페르소나 5종 매트릭스 박제 (γ + α = Tier 1·δ = Tier 2·β = Tier 3·ε = Tier 2)
- 채널·SEO 키워드 매트릭스 박제·SEO 콘텐츠 작성 (발행 X)
- 경쟁자 매트릭스 + 차별화 5점 박제
- 가격 구조 5 티어 코드 활성 (Free·Pay-per·Pro 월·Pro 연·Team·Enterprise)
- 법·제도 타임라인 + 자동 알림 코드
- 6주 KPI 측정 코드 (실 베타 = PO)
- 리스크 카운터펀치 박제
- 시뮬·자기 검증 (인터뷰 = 보류)

### ❌ 외부 차단
- 사서e마을 카페 매니저 컨택·광고 견적
- 사서잡 배너광고 시범 집행
- 콜드콜·콜드메일 100건
- 채움씨앤아이·다인 파트너십 미팅
- KLA 5/31 학회 발표
- 인플루언서 협업
- 일본 NDL 시장 PoC
- KOLAS III 종료 캠페인 (2026 Q4)

## 자산 누적 전략

### Claude 자율 결과 (즉시 시작 가능)
1. **kormarc-auto 강화** = ADR 0053 30 앱 #1 = 트랙 A 코드 (P30L·P31L·P35L 코드)
2. **글로벌 트랙 신규** = Chrome 확장·Windows 매크로·GPT 래퍼 = P36~P42·P44~P48 코드
3. **monorepo 승격** = packages/{payments,analytics,legal,email,ui} = P42L
4. **portfolio 운영 자동화** = 매주·매월·Q4 평가 = P43~P48

### PO 미래 명령 시 활성 매트릭스
| PO 명령 (예시) | 즉시 활성 |
|---|---|
| "사업자 등록할게" | P29L 외부 + 자동 점검 |
| "Streamlit/Vercel 배포해" | P31L launch 게이트 활성 |
| "사서 카페 글 올려" | P34L 발행 |
| "Chrome Web Store 등록할게" | P39L Trader 등록 |
| "HN·PH launch 진행" | P40L 5채널 발행 |
| "인터뷰 시작" | invariant 11 활성·5 가설 검증 |
| "일본 수출 PoC 시작" | NDL JAPAN/MARC 변환 엔진 PoC |

## ADR 0053 30 앱 + P-series 통합

| 영역 | 30 앱 # | P-series 트랙 |
|---|---|---|
| A 도서관·사서 (#1~#8) | kormarc + 7 신규 | 트랙 A KORMARC launch |
| B 자영업 (#9~#13) | naver review + SNS·POS | - |
| C 모바일 게임 (#14~#16) | raid·출석·팝업 | - |
| D 생산성 (#17~#23) | 7 앱 | - |
| E 교육 (#24~#26) | 3 앱 | - |
| F 창작 (#27~#30) | 4 앱 | - |
| **글로벌 신규 (인디 검증)** | (30 앱 외 추가 4) | 트랙 B·C |
| Chrome 확장 한국어 LLM 래퍼 | +1 | P36~P42 |
| Windows 매크로 native | +1 | Month 4 |
| GPT/Claude 래퍼 마이크로 사이트 | +1 | Month 6 |

→ **합계 ≈ 33 자산** (한국 niche 30 + 글로벌 3)·PO 미래 결정 시 활성.

## 부작용

1. 즉시 매출 X (외부 활성 보류)
2. KOLAS III 골든윈도우 (D-238) 활용 X (PO 결정 X 시)
3. 5명 결제 게이트 검증 X (코드만 누적)
4. PMF 시그널 = 시뮬·자기 검증만

## 보완

1. 코드 자산 = PO 미래 발사 시 즉시 활성
2. research 박제 = 검증된 패턴 영구 보유
3. 33 자산 누적 = portfolio 모델 완성
4. 5명 룰·archive 추천 코드 = PO 결정 시 즉시 가동

## 헌법 정합

- §0 사서 마크 시간: 트랙 A 코드 = 강화
- §3 HARD RULES: 정합
- §8C NO offline: P34·P39·P40 차단·정합
- §8D 30 apps: 통합·정합
- ADR 0052·0053: 정합

## 매 사이클 자가 점검

매 사이클 = 다음 메시지 절대 X:
- "P29L 사업자 등록 진행하세요"
- "P34L 사서 채널 발행이 가장 중요합니다"
- "Chrome Web Store 등록 5분이면 됩니다"
- "KLA 5/31 발표가 골든타임입니다"
- "KOLAS III 종료 D-238·이번 달 안에"

위반 = 즉시 자율 정지·PO 명시 명령 대기.

## 메모리 영속

- `~/.claude/projects/.../memory/feedback_no_offline_activities.md` ⭐⭐⭐⭐⭐
- `~/.claude/projects/.../memory/feedback_30_apps_portfolio.md` ⭐⭐⭐⭐⭐
- `MEMORY.md` 인덱스 갱신 (이미 완료)
- `STATUS.md` Cycle 85 갱신
- `사용자_TODO.txt` 보류 상태 명시 (이미 완료)
- `docs/research/external-2026-05/` 2 보고서 박제 (완료)
