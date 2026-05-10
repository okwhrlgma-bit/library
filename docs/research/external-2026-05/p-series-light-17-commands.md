# P-series Light 17개 명령어 묶음 — 외부 advanced research 박제

> **출처**: PO advanced research 결과 (2026-05-07·Pieter Levels·Tony Dinh·Marc Lou·Daniel Vassallo·Justin Welsh 인디 패턴 + 한국 1인 사업자 행정·세무·법무 현실)
> **상태**: 참고 자산 박제만·실행 = PO 명시 명령 시 (ADR 0052 정합)

## 0. 인디 검증 패턴 (5명 결제 룰의 근거)

| 인디 핵 | 결과 | 핵심 패턴 |
|---|---|---|
| **Pieter Levels** | 70+ 프로젝트 중 4 winner = ~$250K/mo | 5% 적중률·launch 1주 trigger·매출 발생 X = 다음 |
| **Tony Dinh** | TypingMind = ChatGPT API launch 당일 1day build → $137K/mo | "6개월 무피드백 = sunset"·feedback >> quality |
| **Marc Lou** | 27 실패 → ShipFast = $141K MRR·portfolio cross-link | auth/payment/email 재구축 지긋 → boilerplate |
| **Jon Yongfook** | Bannerbear = $50K MRR | API niche 단일 |
| **Daniel Vassallo / Justin Welsh** | $5M / $12M solo | "small bets" 분산 |

**공통 시그널**: **"5명 결제 > 100명 무료"** = go/no-go 게이트.

## 1. 17 P-series 명령어 ADR 0052 정합 매트릭스

| # | 명령 | 코드 자율 (Claude) | PO 외부 작업 (보류) | ADR 0052 정합 |
|---|---|---|---|---|
| **트랙 A — KORMARC launch (7건)** ||||
| P29L | 사업자 등록 + 통신판매업 자동 점검 | check_kr_business.py·docs/ops/ | 홈택스·정부24 등록 | 🟡 부분 (스크립트만) |
| P30L | 처리방침·이용약관·환불정책 셋 | 3 mdx + footer 컴포넌트 | - | ✅ 코드 자율 |
| P31L | 1페이지 랜딩 + 가격 + 데모 | apps/kormarc/page.tsx | - | ✅ 코드 자율 |
| P32L | 토스 송금 + 노션 수동 처리 | manual checkout 라우트·script | 토스 QR·노션 가입·Resend 가입 | 🟡 부분 (코드만) |
| P33L | Plausible funnel 측정 | analytics 컴포넌트·weekly_funnel | Plausible 가입·도메인 | 🟡 부분 (코드만) |
| P34L | 사서 채널 5곳 콘텐츠 1편 | 콘텐츠 생성 스크립트 | **사서e마을·X·IG·학회·뉴스레터 발행** | ❌ 발행 = 차단 |
| P35L | launch 통합 게이트 + 5명 룰 카운터 | scripts·git tag·슬랙 webhook 코드 | 슬랙 가입·실 launch | 🟡 부분 (코드만) |
| **트랙 B — Chrome 확장 launch (7건)** ||||
| P36L | Chrome 확장 후보 3개 + niche 결정 | docs·dogfooding 노트·결정 로그 | - | ✅ 코드/문서 자율 |
| P37L | MV3 minimal 스캐폴드 + 한국어 prompt 라이브러리 | apps/chrome-ext/ + Vite + CRXJS | - | ✅ 코드 자율 |
| P38L | ExtensionPay + lifetime $9.99 | payments.ts wrapper·환불 페이지 | **ExtPay 가입·Stripe 연결** | 🟡 부분 (코드만) |
| P39L | Chrome Web Store 리스팅 + Trader 등록 | 영문 listing 작성·privacy policy | **$5 fee 결제·Trader 등록·심사** | ❌ 등록 = 차단 |
| P40L | Build-in-public 5채널 발행 | content/hn-show.md·post script | **HN·PH·Reddit·X·GeekNews 발행** | ❌ 발행 = 차단 |
| P41L | 5명 룰 + LS 마이그레이션 게이트 | scripts·SOP doc | LS 가입 | 🟡 부분 (코드만) |
| P42L | packages/ 승격 (3번째 사용처 게이트) | monorepo 5 packages·AGENTS.md | - | ✅ 코드 자율 |
| **트랙 C — 12개월 portfolio 운영 (6건)** ||||
| P43L | 매월 1일 portfolio 상태 자동 점검 | scripts·차트·노션 DB 코드 | 노션·슬랙 webhook 가입 | 🟡 부분 (코드만) |
| P44L | 5명 룰 자동 판정 + archive 추천 | scripts·SOP·결정 로그 | - | ✅ 코드 자율 |
| P45L | 새 프로젝트 boilerplate 자동 생성 | .claude/commands/new-product.md slash | - | ✅ 코드 자율 |
| P46L | 매주 월요일 09:00 KST 마이크로 리포트 | scripts·룰 기반 액션 추천 | 슬랙 가입 | 🟡 부분 (코드만) |
| P47L | 1인 사업자 행정 캘린더 자동화 | calendar.ics·tax_pull.py | - | ✅ 코드 자율 |
| P48L | Q4 portfolio 평가 + 손절·재활용 분류 | q4_evaluation.py·retro·plan | - | ✅ 코드 자율 |

**합계**:
- ✅ 코드 자율 = **8건** (P30·P31·P36·P37·P42·P44·P45·P47·P48 = 9건)
- 🟡 부분 = **7건** (P29·P32·P33·P35·P38·P41·P43·P46 = 8건·코드만 OK)
- ❌ 외부 발사·등록·발행 = **3건** (P34·P39·P40)

→ **ADR 0052 정합 가능 = 14건 (코드 자율 + 부분 코드만)·실 활성 = PO 명시 명령 시**.

## 2. 12개월 실행 로드맵 요약 (PO 미래 결정 시)

| 월 | 액션 | 5명 룰 판정 | 자산 carry-over |
|---|---|---|---|
| Month 1 (2026.5) | 트랙 A KORMARC launch | KORMARC D+30 | - |
| Month 2 (2026.6) | 트랙 B Chrome 시작 | KORMARC 1차 점검 | - |
| Month 3 (2026.7) | 트랙 B launch | Chrome D+30 | - |
| **Month 4 (2026.8)** | **packages/ 승격** + Windows 매크로 시작 | KORMARC D+90·Chrome D+60 | 5 packages → Windows |
| Month 5 (2026.9) | Windows 매크로 launch | Chrome D+90·Windows D+30 | packages 활용 |
| Month 6 (2026.10) | GPT 래퍼 시작 | Windows D+60 | + 한국어 prompt carry |
| Month 7 (2026.11) | GPT 래퍼 launch | Windows D+90·GPT D+30 | - |
| Month 8 (2026.12) | **Q4 평가** | 4 product 비교 | - |
| Month 9 (2027.1) | double-down or archive | GPT D+90 | unique 자산 → packages |
| Month 10~12 (2027.2~4) | v2·종소세·다음 12개월 plan | - | retrospective |

## 3. 핵심 인사이트 (영구 자산)

### 3-1. 사업자 등록 타이밍 (PO 외부)
- SW업 = 간이과세 배제 (62010·722000) → **일반과세자 강제**
- 부업종 525101/525103 (전자상거래 소매업) 함께 등록·통신판매업 신고 시 구청 반려 회피
- 통신판매업 등록면허세 ₩40,500/년 (인구 50만+ 시)·**1월 신청 정석** (12월 = 이중부과)
- 토스페이먼츠 "사업자등록 바로신청" 모바일 5분 가능

### 3-2. 결제 4 옵션 (외부 가입)
| 옵션 | 수수료 | 한국 적합 | 글로벌 | MoR |
|---|---|---|---|---|
| ExtensionPay | Stripe + 마진 5~10% | ⚠ EU VAT 직접 | ✅ Chrome ext 전용 | ❌ |
| **Lemon Squeezy** | 5% + $0.50 | ✅ MoR | ✅ 글로벌 VAT 위임 | ✅ |
| Polar | 4% + $0.40 | 신흥 저수수료 | ✅ | ✅ |
| Stripe Direct | 2.9% + $0.30 | ⚠ 부가세 영세율 직접 | ✅ | ❌ |
| **PortOne v2** | 한국 적합 | ✅ 한국 카드 | ❌ | ❌ |

→ **KORMARC = PortOne (한국)·Chrome 확장 = ExtensionPay → $500/월 도달 시 LS 마이그레이션**.

### 3-3. Chrome Web Store SEO·Trader
- $5 일회성 fee·**2024.02.17부터 Trader/Non-Trader 자기선언 의무**
- Trader = 사업자명·주소·전화 listing 하단 공개
- MV2 = Chrome 138 마지막·139부터 완전 제거 → **MV3 service worker + declarativeNetRequest 필수**
- title 80% 무게·35자 frontload·WAU = ranking signal

### 3-4. 손절 정량 룰 (5명 결제 게이트)
```
D+30: 1~2명 → continue·3+ → 좋음·0 → 채널 보강 추천
D+60: 5+ → continue + double-down·3~4 → 채널 1개 추가·0~2 → 위험 경고
D+90: 5+ → keep·3~4 → maintenance mode·0~2 → archive 추천 (강한 어조)
```
→ archive 결정 = 사람 confirm 필수 (fail-safe·매몰비용 편향 방지).

### 3-5. premature abstraction 회피
- Sandi Metz AHA 원칙 (Avoid Hasty Abstraction)
- **3번째 사용처 등장 시 packages/ 승격** (1개 사용처 = STOP·4개 = 너무 늦음)
- pnpm workspaces + Turborepo + Changesets + Renovate
- Better Auth (2025~26 supastarter NextAuth → Better Auth 전환)
- root `AGENTS.md` 1개 source of truth·CLAUDE.md/.cursor/rules/copilot = reference

## 4. ADR 0052 정합 응답 매트릭스

| Research 추천 | ADR 0052 정합 | Claude 자율 | PO 결정 시 |
|---|---|---|---|
| 사업자 등록 (P29L) | 외부 | docs·script만 | PO 발급 |
| 처리방침 (P30L) | 코드 | ✅ Claude | - |
| 랜딩 (P31L) | 코드 | ✅ Claude | - |
| 토스 송금 (P32L) | 외부 가입 | 코드만 | PO 가입 |
| Plausible (P33L) | 외부 가입 | 코드만 | PO 가입 |
| 사서 채널 5곳 발행 (P34L) | **외부 발행** | content 작성만 | PO 발행 |
| 통합 게이트 (P35L) | 코드 + git tag | ✅ Claude | - |
| Chrome 확장 niche·코드·packages (P36~P38·P42·P44·P45·P47·P48) | 코드 | ✅ Claude | - |
| Chrome Web Store Trader (P39L) | **외부 등록** | listing 작성만 | PO 등록 |
| HN·PH·Reddit launch (P40L) | **외부 발행** | content 작성만 | PO 발행 |
| LS 마이그레이션 (P41L) | 외부 가입 | 코드만 | PO 가입 |

→ Claude 자율 = **9건 즉시 진행 가능**·외부 발사 = **3건 차단** (P34·P39·P40)·부분 = **5건** (코드만).

## 5. 헌법 정합

- §0 사서 마크 시간 단축: P-series 트랙 A = KORMARC 강화 = 정합
- §3 HARD RULES: API 키 하드코딩 X·timeout=10·UTF-8 = 모든 트랙 적용
- §8 자율 정책: 매 사이클 자율 + ADR 0052 보류
- §8C NO offline activities: P34·P39·P40 차단
- §8D 30 apps portfolio: P-series + 30 앱 매트릭스 (ADR 0053) 통합·6 카테고리 + 글로벌 4 트랙

## 6. 통합 = ADR 0053 30 앱 + P-series 4 트랙

| 30 앱 카테고리 | 30 앱 # | P-series 트랙 |
|---|---|---|
| A 도서관·사서 (#1~#8) | kormarc-auto + 7 신규 | 트랙 A (KORMARC launch) |
| B 자영업·콘텐츠 (#9~#13) | naver review + SNS·POS·학원·유튜브 | - |
| C 모바일 게임 (#14~#16) | raid·출석·팝업 | - |
| D 생산성 (#17~#23) | 한자·OCR·영수증·회의록·이메일·구글폼·캘린더 | - |
| E 교육 (#24~#26) | 영단어·한국사·수학 | - |
| F 창작 (#27~#30) | SEO·동화·자기소개서·시·소설 | - |
| **글로벌 트랙 (신규·인디 패턴)** | - | **트랙 B Chrome ext + 트랙 C portfolio** |
| Chrome 확장 한국어 LLM 래퍼 | (30 앱 외 추가) | P36~P42 |
| Windows 매크로 native | (30 앱 외 추가) | Month 4 |
| GPT/Claude 래퍼 마이크로 사이트 | (30 앱 외 추가) | Month 6 |

→ **30 앱 (한국 niche) + 4 글로벌 트랙 (인디 검증 패턴) = 약 34 자산**·PO 미래 결정 시 일부/전체 활성 가능.

## 7. 출처

- Pieter Levels (PhotoAI·InteriorAI 등 70+ 프로젝트·5% 적중률)
- Tony Dinh (TypingMind·DevUtils·Xnapper·BlackMagic)
- Marc Lou (ShipFast·ZenVoice·ByeDispute·IndiePage·CodeFast·DataFast·TrustMRR)
- Jon Yongfook (Bannerbear $50K MRR)
- Daniel Vassallo·Justin Welsh (small bets·solopreneur portfolio)
- Indie Hackers·Hacker News·beehiiv 인용
- Chrome Web Store Trader 정책 (2024.02.17 시행)
- 한국 부가가치세법 시행령 §101①10호 (영세율)
- Sandi Metz AHA 원칙 (premature abstraction)
- supastarter·shipfa.st·Better Auth 비교 (2025~26)
