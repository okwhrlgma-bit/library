---
title: About kormarc-auto · 사서 출신 1인 PO 한국 도서관 KORMARC SaaS
description: 사서 6년·자관 PILOT·KOLAS III 종료 D-238 마이그·1,228 tests·v0.7.1·invariants 11·정직 헤더 의무
author: 조기흠 (사서 출신·1인 PO)
publisher: kormarc-auto
canonical: https://okwhrlgma-bit.github.io/library/about
og_image: https://okwhrlgma-bit.github.io/library/og-image.png
keywords: KORMARC, KOLAS III, 사서, 도서관 SaaS, 자관 PILOT, 한국 도서관, NLK, KAIT
---

# About kormarc-auto

> **사서가 만든 사서를 위한 KORMARC 자동화 SaaS**.
> Cycle 63·E-E-A-T 4 신호 박제·노출·신뢰 핵심 페이지.

## Experience (체험·1차 자료)

- **자관 PILOT 1관** = PO 본인 자관 (8명 운영·6년 NPS 누적)
- **174 파일·3,383 레코드·round-trip 100%** = 자관 직접 검증 (Cycle 1·2026-05-04 측정)
- **60 사이클 자율 개발** = 외부 901 보고서 (솔로 PO 진단) 인지·재발 방지 invariant 11 박제
- **N=1 한계 정직 명시** = 외부 자관 검증 0관·5관 PILOT 모집 중 (`/pilot`)

## Expertise (전문성)

- **사서 출신 1인 PO** = 도메인 + 코드 통합 자격 (한국 도서관 6년 경력)
- **KORMARC 2023.12** = KS X 6006-0:2023.12 NLK 2차 개정 100% 정합
- **9 자료유형 builder** = 단행본·연속·비도서·고서·전자책·전자저널·오디오북·멀티미디어·학위논문
- **1,228 tests·ruff 0·binary_assertions 39/39** = 코드 품질 영구 게이트
- **23 ADRs (0024~0046)** = 모든 의사결정 박제·재현 가능
- **V2 + V3 자율 인프라** = 100% scaffolding (외부 256 출처 흡수)

## Authoritativeness (권위 인용)

### 외부 권위 5 출처
- 📖 **NLK** (국립중앙도서관·books.nl.go.kr) = KORMARC 표준 발행자
- 🏛 **KAIT** (한국정보통신산업진흥원) = KOLAS III 운영사
- 🏛 **MCST** (문화체육관광부) = 도서관 통계 발행
- 📚 **KLA** (한국도서관협회) = 연 회의 5/31
- 📚 **KLMA** (한국도서관경영자협의회) = 도서관장 영업 채널

### 법적 정합
- **인공지능 기본법 §31** (AI 출처 표시 의무) = 헌법 §10·`ai-disclaimer-2026-05`
- **디지털포용법 §21** (접근성) = 헌법 §12·KWCAG 2.2 Level AA·KRDS·Pretendard
- **PIPA §28의8** (국외이전 6항목) = `privacy-policy-2026-05` 5수신자 박제
- **도서관법 §21** (자료구입비 3% 의무) = 학교 영업 명분
- **KORMARC 2023.12** (KS X 6006-0) = NLK 2차 개정 100% 정합

### 시장 진입
- **KOLAS III 종료** = 2026-12-31 23:59 KST (1,296 공공 + 12,200 학교 영향)
- **자치구 단관 수의계약** = 2천만원 한도·디지털서비스몰
- **학교장터 s2b.kr** = 1,700 학교 사서교사 영업 채널 (사업자 등록 후)
- **Founding Member** = 영구 50% 할인·100관 한정·2026-06-30 데드라인

## Trustworthiness (신뢰·정직)

### 영구 invariants 11건 (PR 차단·우회 X)
1. 헌법 위반 0건
2. 자관 데이터 git 누설 0건
3. 결정론 (ADR 0028)
4. AI 출처 표시 (ADR 0029)
5. 카테고리형 신뢰·raw % 금지 (ADR 0030)
6. KWCAG 2.2 Level AA (ADR 0032)
7. KOLAS3 종료일 = 2026-12-31 (ADR 0026)
8. 야간 자율 = cost_supervisor 래핑 (ADR 0041)
9. budget-cap-precheck.sh exit 2 우회 금지 (ADR 0041)
10. audit.jsonl append-only (ADR 0041)
11. **페르소나 시뮬 ≠ 실 인터뷰·정직 헤더 의무 (ADR 0046)**

### 법무 박제 (8 doc)
- privacy-policy-2026-05.md = 처리방침
- dpa-data-processing-agreement-2026-05.md = DPA
- sla-2026-05.md = SLA 99.5%
- refund-policy-2026-05.md = 환불 정책
- aladin-compliance-2026-05.md = 알라딘 출처 표시
- incident-response-2026-05.md = 사고 응답
- data-retention-2026-05.md = 데이터 보관
- ai-disclaimer-2026-05.md = AI 표시

### 1인 SaaS 출구 전략 (ADR 0045 §D)
- 사서 .mrc 데이터 = 100% export (계약 종료 시)
- 도메인 양도 가능
- 코드 오픈소스화 (Apache-2.0 license)
- **"두면 사라져도 사서 데이터 안전"** 신뢰 1순위 시그널

### 정직 헤더 (영구)
- 모든 페르소나 시뮬 = 가설·인터뷰 0건 명시
- 모든 통계 = 출처 명시 (NLK·KAIT·외부 보고서 901·858·매출)
- "100% 자동" 약속 X (헌법 §3·사서 검수 단계 보존)
- raw % 금지 (헌법 §11·카테고리형 신뢰만)

## 연락처·외부 link

- **GitHub**: https://github.com/okwhrlgma-bit/library
- **이메일**: contact@kormarc-auto.example
- **License**: Apache-2.0
- **버전**: v0.7.1 (2026-05-06)
- **Cycle**: 62 + 63 (마케팅·E-E-A-T)

## 다음 단계 (PO 외부 작업)

1. 일반과세자 등록 (홈택스 30분)
2. 사서 5명 인터뷰 (1주·invariant 11 활성)
3. 도메인 등록 (`kormarc-auto.kr`·1주)
4. 외부 자관 5관 PILOT 모집 (90일·후기 1편 조건)

## 정직 한 줄

> **코드는 충분하다 (1,228 tests·v0.7.1)·발행이 부족하다 (도메인 X)·검증이 부족하다 (인터뷰 0건)·매출은 0이다.**
> **사서 5명 인터뷰 + 도메인 등록이 60 사이클 코드보다 100배 가치다.**
