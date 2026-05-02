# Part 61 — 완벽 추구 갭 분석 + FMEA 100 실패 시나리오 (2026-05-02)

> PO 명령 (2026-05-02): "난 완벽하기 원함 계속 연구 진행"
> 전략: Part 60 (74 페르소나) 후 잔여 20 갭 식별 + Top 5 심층 시작

---

## 0. "완벽" 정의 = Anthropic·Apple·Toyota 패턴

### 완벽 3 차원

| 차원 | 정의 | 검증 |
|------|----|----|
| **Robust** (견고) | 100 실패 시나리오 모두 사전 차단 | FMEA + Apple-Tesla |
| **Comprehensive** (종합) | 모든 stakeholder·시장·시나리오 커버 | Toyota 5 Why |
| **Adaptive** (적응) | 변화·미래에 대응 가능 | Anthropic Constitutional |

→ **현재 = Comprehensive 80%, Robust 60%, Adaptive 70%** = 갭 식별 시작

---

## 1. 잔여 20 갭 매트릭스 (Part 60 후)

### 카테고리 A: 위험 차단 (Robust)
1. ⚠️ **Failure Mode Analysis (FMEA)** — 100 실패 시나리오 + 완화책 (Part 61 본문)
2. ⚠️ **Disaster Recovery Playbook** — PIPA·해킹·환각·폐업·분쟁 시나리오
3. ⚠️ **Edge case KORMARC** — 점자·데이지·다국어·고서 일부

### 카테고리 B: 시장 확장 (Comprehensive)
4. 🔵 **Adjacent Markets** — 박물관·기록관·미술관·출판사 (Part 62)
5. 🔵 **Global Roadmap Phase 3** — 영어권·중국·일본 KORMARC·MARC21
6. 🔵 **Hidden Personas** — 사서 노조·협회 정치·정부 공무원 (Part 63)

### 카테고리 C: 가격·전환 (Optimization)
7. 🔵 **Pricing Psychology Deep** — anchor·decoy·charm·loss aversion (Part 64)
8. 🔵 **Aha Moment Engineering** — 측정·트리거·optimization (Part 65)
9. 🔵 **Onboarding Deep** — activation triggers·streaks·milestones

### 카테고리 D: Retention·Viral (Growth)
10. 🔵 **Retention Loops Deep** — gamification·sticky features
11. 🔵 **Viral Mechanics Deep** — k coefficient·time to share·incentive
12. 🔵 **Community 3-30-300** — 사서 커뮤니티 거버넌스

### 카테고리 E: 차별화·MOAT (Defense)
13. 🔵 **Competitive Moat Deep** — 네트워크·전환비용·브랜드
14. 🔵 **Exit Scenarios Deep** — Naver·Kakao·NLK 매각·IPO 시나리오
15. 🔵 **Open Source Strategy** — core open + premium·license

### 카테고리 F: 인프라·기술 (Foundation)
16. 🔵 **AI Tech Roadmap** — fine-tuning·RAG·multimodal·agent
17. 🔵 **Mobile Architecture Deep** — Flutter vs Native·결제 우회
18. 🔵 **DB Schema Deep** — 멀티테넌시·sharding·replica
19. 🔵 **API Strategy** — REST vs GraphQL·rate limit·webhook

### 카테고리 G: 자금·관리 (Sustainability)
20. 🔵 **Korean Government Funding Deep** — 17 부처·250 자치구·17 교육청 매트릭스

---

## 2. FMEA 100 실패 시나리오 (Part 61 본문) ★

### 평가 척도
- **Severity (S)**: 1 (경미) ~ 10 (치명)
- **Occurrence (O)**: 1 (희박) ~ 10 (확실)
- **Detection (D)**: 1 (즉시) ~ 10 (못 발견)
- **RPN (Risk Priority Number)** = S × O × D
- **임계 RPN ≥ 100** = 즉시 완화 필요

---

### 카테고리 1: KORMARC·기술 결함 (20)

| # | 실패 | S | O | D | RPN | 완화 |
|---|----|---|---|---|---|----|
| 1 | 008 40자리 1자리 오류 → KOLAS 반입 실패 | 9 | 3 | 4 | 108 | binary_assertions 38건 + 자관 99.82% |
| 2 | 880 ▾6 연결표시기호 오류 | 8 | 3 | 5 | 120 | DA7 시뮬 + E1 검증 |
| 3 | 9 자료유형 분기 오류 | 9 | 2 | 3 | 54 | M/A/O 분기 정합 |
| 4 | KDC 추천 환각 (잘못된 분류) | 7 | 5 | 6 | 210 ⚠ | T2 confidence + 사서 검토 |
| 5 | 자관 prefix 잘못 인식 | 8 | 4 | 4 | 128 | sanity-check CLI |
| 6 | ISBN-13 체크섬 오류 | 6 | 2 | 2 | 24 | binary_assertion §13 |
| 7 | 알라딘 출처 표시 누락 | 7 | 3 | 5 | 105 | binary_assertion §17 |
| 8 | 한자 880 페어 누락 | 7 | 4 | 6 | 168 ⚠ | 880 자동 + 검증 |
| 9 | API timeout 처리 X | 6 | 5 | 4 | 120 | binary §13 + try/except |
| 10 | 외부 API 연속 실패 → 데이터 손실 | 9 | 4 | 5 | 180 ⚠ | 5 폴백 + 큐잉 |
| 11 | 동시 1,000명 → 서버 다운 | 8 | 3 | 5 | 120 | T8 Performance |
| 12 | 1만 권 일괄 → 메모리 OOM | 7 | 4 | 4 | 112 | 스트리밍·청크 처리 |
| 13 | UTF-8 인코딩 오류 (한자 깨짐) | 8 | 2 | 3 | 48 | encoding 명시 |
| 14 | pymarc 라이브러리 충돌 | 6 | 3 | 6 | 108 | 의존성 버전 잠금 |
| 15 | 자관 .mrc 99.82% 회귀 | 9 | 2 | 2 | 36 | scripts/validate_real_mrc.py |
| 16 | M/A/O 적용 수준 분기 누락 | 8 | 3 | 4 | 96 | E1 검증 |
| 17 | 008 06 = 'm' (다권물) 누락 | 7 | 4 | 5 | 140 ⚠ | material_type 자동 |
| 18 | 020 ▾g 부가기호 5자리 검증 X | 6 | 3 | 4 | 72 | binary §3 |
| 19 | 245 지시기호 1·2 오류 | 8 | 4 | 5 | 160 ⚠ | binary §4·5 + KCR4 |
| 20 | 049 자관 청구기호 형식 오류 | 7 | 4 | 4 | 112 | 자관 config |

### 카테고리 2: 보안·PIPA (15)

| # | 실패 | S | O | D | RPN | 완화 |
|---|----|---|---|---|---|----|
| 21 | PIPA 5대 패턴 1건 위반 → 매출 10% | 10 | 3 | 4 | 120 | E6 + L2 + audit |
| 22 | 자관 익명화 실패 (자관명 노출) | 9 | 3 | 5 | 135 ⚠ | sanity-check + DA3 |
| 23 | DSAR 자동화 X → 정보주체 권리 위반 | 9 | 3 | 5 | 135 ⚠ | API 자동 |
| 24 | 72h 신고 자동 X | 9 | 2 | 7 | 126 | 자동 알림 |
| 25 | 카카오 학습 패턴 (부분 적용 + 미마이그) | 10 | 4 | 6 | 240 ⚠⚠ | 전수 마이그 강제 |
| 26 | API 키 코드 노출 | 9 | 3 | 6 | 162 ⚠ | .env + secret scan |
| 27 | SQL injection | 9 | 2 | 4 | 72 | ORM·prepared |
| 28 | XSS · CSRF | 7 | 3 | 5 | 105 | CSP + token |
| 29 | DDoS 공격 | 8 | 3 | 6 | 144 ⚠ | rate limit + Cloudflare |
| 30 | JWT 탈취·재사용 | 8 | 3 | 5 | 120 | 짧은 만료·refresh |
| 31 | 다른 자관 데이터 접근 (멀티테넌시) | 10 | 2 | 6 | 120 | row-level security |
| 32 | 백업 데이터 유출 | 9 | 2 | 7 | 126 | 암호화 백업 |
| 33 | 클라우드 데이터 국외 이전 (GDPR) | 8 | 4 | 5 | 160 ⚠ | 한국 리전 명시 |
| 34 | 인증 우회 (OAuth 취약) | 9 | 2 | 5 | 90 | OAuth2 standard |
| 35 | 환각 데이터 학습에 사용 (자관 데이터) | 10 | 3 | 8 | 240 ⚠⚠ | 학습 X 약관 + 격리 |

### 카테고리 3: 결제·세무·법무 (15)

| # | 실패 | S | O | D | RPN | 완화 |
|---|----|---|---|---|---|----|
| 36 | 부가세 8천만 임계 미인식 → 추징 | 9 | 4 | 6 | 216 ⚠⚠ | L3 routine + 알림 |
| 37 | 면세 vs 일반 결정 오류 → 환급 손실 | 8 | 3 | 7 | 168 ⚠ | L3 자문 |
| 38 | 사업자 등록 X → 5채널 잠금 | 9 | 5 | 3 | 135 ⚠ | U-17 즉시 |
| 39 | 결제 실패 → 매출 누락 | 7 | 4 | 4 | 112 | 포트원 webhook |
| 40 | 세금계산서 자동 X → 수기 부담 | 6 | 5 | 5 | 150 ⚠ | 팝빌 통합 |
| 41 | 환불 요청 폭증 → 1인 응대 한계 | 7 | 3 | 5 | 105 | 약관 + 자동 |
| 42 | 결제 분쟁 (chargeback) | 8 | 3 | 5 | 120 | 명확 약관 |
| 43 | MSA 표준 X → 매번 재작성 | 6 | 6 | 3 | 108 | L1 5종 |
| 44 | DPA 누락 → PIPA 위반 | 9 | 3 | 5 | 135 ⚠ | L1 + L2 |
| 45 | SLA 위반 → 환불 책임 | 8 | 3 | 4 | 96 | T3 99.5% |
| 46 | 소비자보호법 위반 → 과징금 | 9 | 2 | 6 | 108 | L1 검토 |
| 47 | 약관 변경 통지 X → 분쟁 | 7 | 4 | 5 | 140 ⚠ | 자동 통지 |
| 48 | 정부 자금 회계 부정 → 환수 | 9 | 2 | 7 | 126 | L3 감사 |
| 49 | 저작권 분쟁 (서지·표지) | 8 | 3 | 5 | 120 | NLK API 합법 |
| 50 | 경쟁사 특허 침해 | 8 | 2 | 7 | 112 | 사전 검색 |

### 카테고리 4: 비즈니스·운영 (20)

| # | 실패 | S | O | D | RPN | 완화 |
|---|----|---|---|---|---|----|
| 51 | 1인 PO 건강·사고 → 서비스 중단 | 10 | 2 | 5 | 100 | 핸드오버·문서·코드 공개 |
| 52 | PO 동기 소진 → 개발 정체 | 9 | 4 | 6 | 216 ⚠⚠ | Mem0 자율·외부 자문 |
| 53 | 자금 부족 → 폐업 → 데이터 손실 | 10 | 3 | 5 | 150 ⚠ | 정부 자금 + 에스크로 |
| 54 | 캐시카우 도달 X (24개월+) | 9 | 4 | 4 | 144 ⚠ | C5 Bottom-up + LR1 |
| 55 | 경쟁사 가격 인하 (월 1.5만) | 7 | 5 | 3 | 105 | AD1 + 차별화 |
| 56 | 두드림 600관 침투 가속 | 8 | 5 | 4 | 160 ⚠ | 자치구 25관 일괄 |
| 57 | 알파스 KOLAS 종료 후 새 도구 출시 | 8 | 6 | 5 | 240 ⚠⚠ | white-label 협상 |
| 58 | NLK·KISTI 직접 도구 출시 (무료) | 9 | 4 | 5 | 180 ⚠ | NLK MOU + 차별화 |
| 59 | KLA 발표 신청 5/31 마감 놓침 | 8 | 3 | 2 | 48 | U-1 즉시 |
| 60 | AI 바우처 5월 마감 놓침 | 8 | 3 | 2 | 48 | U-49 즉시 |
| 61 | 자치구 일괄 영업 거부 | 7 | 4 | 5 | 140 ⚠ | PT1 + D2 양식 |
| 62 | 학교 사서교사 (DLS만) 거부 | 7 | 5 | 4 | 140 ⚠ | DLS exporter |
| 63 | 대학 (Alma 락인) 진입 X | 7 | 5 | 4 | 140 ⚠ | LCC·Cutter Phase 2 |
| 64 | 작은도서관 가격 거부 (예산 X) | 7 | 4 | 4 | 112 | C5b 9,900 자비 |
| 65 | 사서 신뢰 부족 (신생 SaaS) | 9 | 4 | 6 | 216 ⚠⚠ | LR1 + R1 + PILOT |
| 66 | DA1 알파스 베테랑 거부 | 7 | 5 | 5 | 175 ⚠ | landing 즉석 데모 |
| 67 | DA7 강박 검수 거부 | 8 | 4 | 5 | 160 ⚠ | NLK 등록 + RR/MR |
| 68 | 사서 일자리 위협 우려 → 협회 반대 | 9 | 3 | 6 | 162 ⚠ | AI1 + "AI = 사서 보조" |
| 69 | 후기 부족 (PILOT 1관 익명) | 8 | 4 | 4 | 128 | PILOT 5관 발굴 |
| 70 | NRR < 100% → 이탈 가속 | 9 | 4 | 5 | 180 ⚠ | B2 CSM + retention |

### 카테고리 5: 재해·외부 충격 (15)

| # | 실패 | S | O | D | RPN | 완화 |
|---|----|---|---|---|---|----|
| 71 | KOLAS 종료 연기 (2026-12 → 2027) | 7 | 3 | 3 | 63 | 골든타임 영업 |
| 72 | NLK 정책 변경 (KORMARC 표준) | 8 | 3 | 5 | 120 | E1 + R1 모니터링 |
| 73 | PIPA 시행령 강화 (2026-09 후) | 8 | 4 | 4 | 128 | L2 + 2026-09 진단 |
| 74 | 한국 데이터 주권법 → 클라우드 제한 | 8 | 3 | 6 | 144 ⚠ | 한국 리전 명시 |
| 75 | AI 규제법 (한국 2027) | 8 | 4 | 5 | 160 ⚠ | AI1 + 가이드라인 |
| 76 | Anthropic API 가격 인상 | 7 | 5 | 3 | 105 | Sonnet 4.6 효율·캐싱 |
| 77 | Anthropic API 한국 제한 | 9 | 2 | 7 | 126 | 폴백 (OpenAI·Solar) |
| 78 | 클라우드 (AWS) 한국 리전 장애 | 8 | 2 | 5 | 80 | NHN·KT 멀티 |
| 79 | 자관 .mrc 데이터 유출 (PILOT) | 10 | 2 | 6 | 120 | L2 + 익명화 강화 |
| 80 | KISA 보안 점검 실패 → ISMS-P X | 8 | 3 | 5 | 120 | SEC1 사전 |
| 81 | 카카오 알림톡 정책 변경 (2026-01 강화) | 6 | 4 | 4 | 96 | 정보성만·이메일 폴백 |
| 82 | 네이버 검색 알고리즘 변경 → SEO 손실 | 7 | 5 | 4 | 140 ⚠ | G4 + 다양화 |
| 83 | 도서관 예산 삭감 (정부 정책) | 8 | 3 | 5 | 120 | 정부 자금 + AI 바우처 |
| 84 | KLA·KSLA 협회 신생 SaaS 거부 정책 | 8 | 3 | 6 | 144 ⚠ | LR1 + 추천서 |
| 85 | 도서관 평가 기준 변경 (KOLAS X) | 7 | 3 | 5 | 105 | E4 + 새 평가 정합 |

### 카테고리 6: AI·환각 (15)

| # | 실패 | S | O | D | RPN | 완화 |
|---|----|---|---|---|---|----|
| 86 | KDC 추천 환각 (잘못된 분류) | 8 | 5 | 6 | 240 ⚠⚠ | T2 + AI1 + confidence |
| 87 | 880 한자 환각 (잘못된 한자) | 8 | 4 | 6 | 192 ⚠ | RR/MR 검증 |
| 88 | 책 표지 OCR 오류 (잘못된 ISBN) | 7 | 4 | 4 | 112 | confidence + 사서 검토 |
| 89 | 저자명 환각 (동명이인 혼동) | 7 | 5 | 6 | 210 ⚠ | 전거 통제 + source_map |
| 90 | KORMARC 245 환각 (제목 변형) | 8 | 4 | 7 | 224 ⚠⚠ | 5 API 폴백 + 검증 |
| 91 | 출판사·연도 환각 | 6 | 4 | 5 | 120 | 5 API 우선순위 |
| 92 | 자관 prefix 자동 추천 환각 | 7 | 4 | 5 | 140 ⚠ | sanity-check + 사서 확인 |
| 93 | KOLAS 변환 환각 (반입 실패 → 사서 손해) | 9 | 3 | 6 | 162 ⚠ | binary 38 + DA7 |
| 94 | AI 학습이 자관 데이터 사용 (의심) | 9 | 3 | 8 | 216 ⚠⚠ | 약관 + L1·L2 |
| 95 | 편향 (KDC 종교·정치 분류) | 8 | 3 | 7 | 168 ⚠ | AI1 + 검증 |
| 96 | 다국어 (베트남·태국) 환각 | 6 | 5 | 6 | 180 ⚠ | Phase 2 |
| 97 | 고서·특수자료 환각 | 7 | 5 | 6 | 210 ⚠ | rare_book + 사서 검토 |
| 98 | AI 응답 시간 지연 (5초+) | 6 | 4 | 3 | 72 | 캐싱 + 비동기 |
| 99 | AI 비용 폭증 (Opus 호출) | 7 | 4 | 4 | 112 | Sonnet 4.6 위주 |
| 100 | LLM 모델 deprecation (Sonnet 4.6 → 후속) | 6 | 3 | 5 | 90 | 추상화 layer |

---

## 3. RPN ≥ 200 = 즉시 완화 (10건 ⚠⚠)

| # | 실패 | RPN | 완화 (Phase 1 즉시) |
|---|----|---|----|
| 25 | 카카오 학습 패턴 (PIPA 부분 적용) | 240 | 전수 마이그 강제·코드 hook |
| 35 | 자관 데이터 학습 의심 | 240 | 약관 §X "학습 X" + L1·L2 |
| 86 | KDC 환각 | 240 | T2 confidence threshold + 사서 검토 |
| 94 | AI 학습이 자관 데이터 의심 | 216 | DPA + 약관 + 격리 |
| 90 | 245 제목 환각 | 224 | 5 API 폴백 + cross-validation |
| 36 | 부가세 8천만 미인식 | 216 | L3 routine + 자동 알림 |
| 52 | PO 동기 소진 | 216 | Mem0 자율 + 외부 자문위 |
| 65 | 사서 신뢰 부족 | 216 | LR1 권위자 30명 + R1 NLK |
| 57 | 알파스 KOLAS 후속 | 240 | white-label + LR1 + 차별화 |
| 87 | 880 한자 환각 | 192 | NLK RR/MR 검증 |

→ **10건 즉시 완화 = 사고 사전 차단**

---

## 4. 완벽 목표 임계값

### Robust 100% 달성 조건
- RPN ≥ 100 = 0건 (현재 30+ → 목표 0)
- 100 시나리오 모두 완화책 검증
- DA7 강박 검수가 통과
- SEC1 침투 통과

### Comprehensive 100% 달성 조건
- 74 페르소나 매트릭스 통과
- 23 카테고리 모두 ACCEPT
- 7 Critic Layer 모두 PASS
- Adjacent market 박물관·기록관 ADR

### Adaptive 100% 달성 조건
- Mem0 +26% 학습 누적
- 변화 대응 routine (KOLAS·PIPA·AI 규제)
- exit 시나리오 3종 (M&A·IPO·인수)

---

## 5. AUTONOMOUS_BACKLOG 신규 (Part 61)

### 즉시 (Phase 1·완벽 직결)
- [ ] FMEA RPN ≥ 200 = 10건 즉시 완화 (8시간·L3)
- [ ] 자관 데이터 학습 X 약관 + DPA (L1·L2 협업)
- [ ] T2 confidence threshold (KDC·880 환각 차단)
- [ ] LR1 사서 권위자 30명 routine (PO 작업)
- [ ] L3 부가세 8천만 알림 routine
- [ ] PO 핸드오버 문서 (사고·동기 소진 대비)

### 다음 사이클 (Part 62~65 = Top 5 갭)
- [ ] Part 62: Adjacent Markets (박물관·기록관)
- [ ] Part 63: Hidden Personas (노조·정치·공무원)
- [ ] Part 64: Pricing Psychology Deep
- [ ] Part 65: Aha Moment Engineering

---

## 6. PO 응답 정합

### Q "난 완벽하기 원함 계속 연구 진행"
✅ **완벽 = 3 차원 (Robust + Comprehensive + Adaptive) 모두 100%**
✅ **20 잔여 갭 식별 + Top 5 우선 진행**
✅ **FMEA 100 실패 시나리오 + RPN ≥ 200 = 10건 즉시 완화**
✅ **다음: Part 62 Adjacent Markets → Part 63 Hidden Personas → Part 64 Pricing Psychology → Part 65 Aha Moment**

→ 캐시카우 도달율 240~400% → **완벽 후 260~450% 추정**

---

> **이 파일 위치**: `kormarc-auto/docs/research/part61-perfection-gap-fmea-100scenarios-2026-05.md`
> **종합**: 20 잔여 갭 + FMEA 100 시나리오 + RPN ≥ 200 = 10건 즉시 완화
> **PO 정합**: 완벽 = Robust + Comprehensive + Adaptive 100%
