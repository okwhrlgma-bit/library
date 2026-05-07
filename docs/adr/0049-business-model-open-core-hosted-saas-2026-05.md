# ADR 0049 — 비즈니스 모델: Open Core + Hosted SaaS (Cycle 66)

- 상태: Accepted (2026-05-06·Cycle 66)
- 일자: 2026-05-06
- 트리거: PO "GitHub 다운로드 무료면 구독비 낼까?"

## Context

PO 우려 (정확·매우 중요):
- `.exe` GitHub Releases = 무료 다운로드 = 사서 자가 사용 가능
- 사서가 자기 외부 API 키 발급 = 우리 결제 X 가능
- → "구독 모델 = 작동 X 위험?"

**검증된 사례** (오픈소스 + SaaS 매출):
- Koha (1,399 도서관 결제·ByWater Solutions)
- FOLIO (100+ 도서관·EBSCO 호스팅)
- GitLab (₩7,000억 매출·Community 무료)
- Sentry (₩1,000억·self-host 무료)
- **반례 MarcEdit** = 무료 영구·수익 ₩0·26년 (= 우리는 아님)

## Decision

**Open Core + Hosted SaaS 모델 채택**.

### A. 무료 (영구·Apache-2.0)
- 코드 전체
- KORMARC 빌더·검증·9 자료유형
- offline demo (SAMPLE 12건·키 0개)
- `.exe` 다운로드 (GitHub Releases·자가 빌드 가능)
- 자관 .mrc 처리 (수동 입력)

### B. 결제 (서비스 패키지)
1. **외부 API 키 통합** = NL_CERT_KEY·DATA4LIBRARY·ALADIN_TTB·KAKAO 통합 (우리 키)
   - 자가 = 정부 사이트 1~3일 신청·복잡
   - 결제 = 즉시 사용
2. **AI 기능 (Anthropic Claude)** = SaaS 제공
   - BYOK 부담 X·통합 결제
3. **자동 업데이트** = 신버전 알림 + 1클릭
4. **세금계산서 자동** = 사업자 등록 후 PortOne v2
5. **SLA 99.5%** = 작은도서관·SLA 99.9% = 공공
6. **환불 정책** = 30일 무조건 (외부 858 §4 정합)
7. **1일 답변 약속** = GitHub Issues + 이메일
8. **학교운영위 결재 자료 자동** = PDF 생성·견적서·예산표
9. **자치구 단관 수의계약 자료** = 디지털서비스몰 정합·견적
10. **CSAP·ISMS-P 인증** (Phase 3·자치구·공공)
11. **자관 양식 등록 자동** (사서 IT L1·L2 친화)
12. **알라딘 라이선스 통합** = 합법 사용 보장

### C. 가격 (Cycle 11·P31 정합)
- Free 50건/월 · 30일 trial
- 작은도서관 ₩30K
- 학교도서관 ₩50K
- 공공도서관 ₩150K
- 기관 ₩300K~
- 권당 200원 alt
- Founding Member 영구 50%·100관 한정·2026-06-30

## 도서관 결제 가능성 (현실 분석)

| 페르소나 | 결제 권한 | 결제 가능성 | 이유 |
|---|---:|---|---|
| 사서 개인 (B2C) | 100% | 🟡 5% | 자가 빌드 가능자 = 무료 사용 |
| 학교 (운영위 결재) | 50 | 🟢 70% | "GitHub 무료" = 결재 회피 (책임)·"공식 SaaS" = 통과 |
| 자치구 (작은도서관) | 10 | 🟢 90% | RFP = 공식 사업자·세금계산서·CSAP 필수 |
| 공공도서관 | 5 | 🟢 95% | CSAP 자가 빌드 X·우리만 가능 |
| 도서관장 (P8) | 90 | 🟢 80% | 책임·SLA·공식 SaaS 선호 |
| 기관 (대학·전문) | 20 | 🟢 75% | RFP·법적 책임 |

→ **자가 빌드 무료 = 5%·결제 SaaS = 80~95%** (학교·자치구·공공·기관·도서관장).

## Alternatives

1. **코드 closed source** = 거부·도서관 RFP·신뢰 시그널 ↓·MarcEdit 사례 무시
2. **MarcEdit 모델 (영구 무료·기부 거부)** = 거부·매출 ₩0·1인 SaaS 지속 X
3. **freemium만** = 50건/월 무료 = 일부·but 외부 API·AI·세금계산서·SLA = 결제 의무
4. **유료 closed + GPL 일부** = 거부·복잡·도서관 신뢰 ↓
5. **Koha/FOLIO 동일** (자체 호스팅 컨설팅만) = 거부·사서 친화 ↓·우리 = SaaS UX 우위

## Consequences

### Positive
- ✅ 코드 = 오픈·신뢰 시그널·도서관 RFP 자가 빌드 가능 명시 = 안심
- ✅ 결제 = 서비스 패키지·법적 책임·SLA·세금계산서 = 도서관 의무 자동 정합
- ✅ 가난한 사서 (5%) = 자가 사용 가능·매출 큰 영향 X
- ✅ 95% 도서관 = 결제 의무 (학교·자치구·공공·기관·도서관장)
- ✅ Open Core = LLM 학습·E-E-A-T·검색 노출 ↑

### Negative
- ⚠ 자가 빌드 = 5% 사서 = 매출 X (수용)
- ⚠ 코드 = 오픈 = 경쟁사 fork 가능 (but 한국 도서관 시장 = 1인 SaaS·영업 = 우리 우위)
- ⚠ "왜 결제?" = 사서 친화 메시지 필수 (랜딩 페이지·README 강조)

### Neutral
- ADRs: 0048 → **0049**
- 가격 (Cycle 11) 유지·변경 X
- Founding Member·alt 모델 유지

## "왜 결제하는가?" 매트릭스 (랜딩·README 표시)

```
무료 사용 = 가능 (Apache-2.0)
   ↓ but
"우리 SaaS = 시간 절감 + 법적 책임 + 자치구 결재 통과"
   ↓
1. 외부 API 키 통합 (정부 신청 1~3일 → 즉시)
2. AI 기능 (BYOK 부담 X)
3. 세금계산서·SLA·환불 (도서관 RFP 통과)
4. 자동 업데이트·1일 답변
5. 학교운영위 결재 자료 자동
6. 자치구 단관 수의계약 견적
7. CSAP·ISMS-P (Phase 3·공공)
```

## 추가 invariant 13 후보 (Cycle 70+ 박제 권장)

> **"코드 = Apache-2.0 영구 오픈·자가 빌드 권리 보장. 매출 가치 = 외부 API 통합·법적 책임·SLA·인증·지원 + 사서 친화 시간 절감. 코드 closed 전환·license 변경 = STOP·헌법 위반."**

## 다음 적용 (Cycle 66 즉시)

1. README "왜 결제?" 섹션 신설
2. `docs/landing/install.md` "옵션 무료 vs SaaS" 비교
3. `docs/sales/why-pay-2026-05.md` 신설 (도서관장·학교운영위 결재 자료)
4. 자료 일괄 갱신 (STATUS·META·SUMMARY·CHANGELOG·learnings)

## 정직 헤더

- 본 ADR = 외부 사례 (Koha·FOLIO·GitLab·Sentry) 종합·**한국 도서관 사용자 0명 검증 X**
- 결제 가능성 % = 시뮬·인터뷰 후 v2 재작성 (invariant 11)
- Phase 1 PILOT 1관 (PO 자관) = 결제 X·검증 단계
