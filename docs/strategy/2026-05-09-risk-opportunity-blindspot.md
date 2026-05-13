# Risk·기회·블라인드스팟 정직 평가 (Cycle 733·PO #84·#85 산출물 #6)

> **목표**: 614 cycle critical_lockup 해소 가능성 정량 + Top 3 winner 발견 가능성

---

## 🔴 Risk (위험·정직)

### R1: 매출 ₩0 critical_lockup 영속화 (확률 ★★★★)
- 현재 = 619 cycle 매출 ₩0
- Polar publish 미진행 = 결제 활성 X
- 외부 발사 차단 (ADR 0052) = 트래픽 0
- 자관 dogfooding 1건 = 시그널 부족
- **완화**: PO 30분 외부 작업 + 30일 데이터 수집

### R2: 9 SaaS 분산·어느 하나도 깊이 X (확률 ★★★)
- PO #81 Q6 = "가장 두려운 것"
- Top 3 winner 발견 = 30~60일 매출 데이터 의무
- 개별 SaaS = MVP 깊이 부족 (kormarc-auto 1739 라인만 깊음·나머지 5~7 함수)
- **완화**: 30일 후 Top 3 결정·6 SaaS sunset·1 winner 깊이

### R3: 도메인 fit 불일치 (확률 ★★★)
- PO 사서 출신 = kormarc-auto 1개만 ★★★
- 8 SaaS = PO 도메인 X·dogfooding 불가
- 사용자 응대·CS 부담 ↑ (B2C 5건)
- **완화**: 30일 데이터 후 Top 3 = kormarc 우선 (정적 점수 44점·1위)

### R4: Polar publish 차단 가능성 (확률 ★)
- Polar 정책 = MoR·세금 자동·검증 의무
- 한국 법인 X = 일부 제품 publish 거부 가능
- **완화**: 베타 = 개인 카드 결제·법인 등록 후 정식

### R5: Streamlit Cloud 배포 fail (확률 ★)
- requirements.txt 23 패키지·설치 실패 가능
- secrets 입력 오류 시 → 데모 모드만
- **완화**: Cycle 672 미리 fallback 시드·demo mode 자동

---

## 🟢 기회 (정직)

### O1: KOLAS III 골든윈도우 (★★★★★)
- 2026-12-31 종료 = D-235 (현재 5월 9일)
- 18,400관 도서관 전환 = TAM 매우 큼
- kormarc-auto = 첫 번째 winner 가능
- **활용**: 매월 KOLAS 종료 D-N 카운트다운 노출

### O2: 광고 X·데이터 보호 차별화 (★★★★)
- B2C 4 SaaS 모두 적용 (simple-budget·ai-writer·simple-todo·diet-workout)
- 경쟁사 (뱅크샐러드·Todoist·MyFitnessPal) = 광고 + 데이터 사용
- 한국 사용자 = PIPA 2026-09-11 시행 후 = 차별화 가치 ↑
- **활용**: 모든 landing·SEO·블로그 강조

### O3: Bundle 전략 ($25/월·50% 절감) (★★★★)
- 단일 SaaS 평균 $7.21/월 → Bundle $25/월 = LTV 3.5배
- 락인 ↑ (해지 = 9개 모두)
- 새 SaaS 자동 추가 = 추가 매출 X·기존 사용자 가치 ↑
- **활용**: 첫 매출 후 Bundle 강조·Cross-saas marketing

### O4: 정부 자금 (사업자 등록 후) (★★★)
- AI 바우처: ₩4,400만/년
- 디딤돌·TIPS: ₩3억~15억
- 매출 ₩100K+ 도달 → 사업자 등록 → 정부 자금 신청
- **활용**: 사업자 등록 후 즉시 신청

### O5: 자관 PILOT (PO 도메인 fit) (★★★)
- PO 자관 = 8명 사서·1관·PO 6년 사서 운영 도메인 fit
- kormarc-auto 1관 검증 = 베타 사용자 1명·신뢰도 ↑
- 자관 사서 = 5월 PILOT 5관 모집 가능 (PO 외부 작업)
- **활용**: 30일 데이터 + 자관 검증 → 자치구 공공 1관 영업

---

## 🔵 블라인드스팟 (정직)

### B1: 한국 사용자 결제 의향
- USD 환산 결제 = 한국 사용자 거부감 (₩7,000·UI 환산)
- PortOne v2 직접 결제 = 사업자 등록 후
- B2C 사용자 = 환율 변동·1~2개월 후 KRW 직접 의무

### B2: SEO·검색 트래픽 효과 (불확실)
- 18 SEO URL·llms.txt·robots·sitemap = 시드만
- Google·네이버 색인 = PO 외부 작업 (검색엔진 등록)
- 자연 트래픽 = 30~90일 후

### B3: 사용자 응대·CS 부담
- cs_helper FAQ DB·complaint·auto_repair = 시드만
- 실 사용자 발생 시 = 24h 내 응답 부담
- B2C 5건·B2B 4건 = 9 SaaS × 3채널 (이메일·채팅·DM)

### B4: AI 모델 비용 (BYOK 영역)
- ai-writer·kormarc KDC 추천·OCR = AI API 호출
- BYOK = 사용자 키·비용 0
- 그러나 사용자 키 입력 진입 장벽 ↑

### B5: 법적·세무 (한국)
- 사업자 등록 X = 부가세 의무 X (간이과세자도 X)
- 매출 ₩2,400만+/년 = 일반과세자 의무 (홈택스)
- VAT·소득세·지방세·국민건강보험 미이해 가능
- **완화**: 매출 ₩100K+ 후 세무사 외주 (PO 외부 작업)

---

## 📊 critical_lockup 해소 가능성 정량

```
시나리오 A: PO 30분 작업 + 외부 발사 X (현재 노선)
- 24h: 매출 ₩7,000 (자관 1건)
- 7일: 매출 ₩7,000~₩50,000 (PO 1관·검색 색인 시작)
- 30일: ₩50,000~₩300,000 (자연 트래픽 + dogfooding)
- 60일: ₩300,000~₩1,500,000 (Top 3 결정 + 자관 PILOT)
- 확률: 70% (보수적)

시나리오 B: PO 외부 발사 (ADR 0052 해제 시)
- 24h: ₩7,000 + ProductHunt 1~5건 = ₩50,000~₩200,000
- 7일: ₩300,000~₩1M (HN·X 입소문)
- 30일: ₩1~5M (Top 3 명확)
- 확률: 30% (의존도 ↑·발사 실패 시 critical_lockup 영속)

시나리오 C: PO 진행 0 (현 상태)
- 매출 ₩0 영속·critical_lockup 1000 cycle+
- 확률: 0% 매출
```

→ **권장 = 시나리오 A** (PO 30분·자관 dogfooding 우선·30일 데이터·Top 3·외부 발사 보류).
