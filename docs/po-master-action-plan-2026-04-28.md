# PO 마스터 액션 플랜 (2026-04-28)

> **목적**: 야간 자율 누적 (47 task / 90+ docs / 91 ADR / 자료 100% / D 100%) 결과 → PO 즉시 액션 단일 진실 소스.
> **생명주기**: 2026-04-28 ~ 2026-05-31 (KLA 발표 신청 마감).
> **참조**: `docs/po-pilot-readiness-checklist.md`·`docs/adr-priority-matrix-2026-04-28.md`·`docs/night-autonomous-session-2026-04-28-summary.md`.

---

## 0. 30초 요약 (PO 화면 첫 줄)

🔴 **5월 마감 임박**: KLA 전국도서관대회 발표 신청 (5.31). 자관 PILOT 4주 시나리오 5월 첫주 시작 권장.
🔴 **PO 즉시 결정 9 ADR**: 자율 commit 차단점. 결정 후 일괄 commit 가능.
🟡 **PIPA 시행 2026-09-11**: 매출 10% 과징금. logging PII 5종 마스킹 보강 권장 (PILOT 전).

---

## 1. PO 즉시 결정 9 ADR ★ (자율 commit 차단점)

| # | ADR | 영역 | 결정 트리거 |
|---:|---|---|---|
| 1 | **0021 정정** | 「상호대차 띠지 자동 생성기」 | python-hwpx 의존성 + 자관 라이선스 |
| 2 | **0022** | 양식 우선순위 resolver | forms/ 신규 디렉토리 |
| 3 | **0014** | 가격 4단 정정 | 헌법 §12 (3·5·15·30만원) vs PO 마스터 §6 (Free·₩19K·₩49K·견적) 충돌 해결 |
| 4 | **0013** | 사업 5질문 도입 | rules/business-impact-axes.md active 트리거 |
| 5 | **0015·0023·0032·0036·0064·0084** | pii-guard hook (6 통합) | PIPA 시행 2026-09-11 임박 |
| 6 | **0070** | 자관 .mrc 174 PILOT | 자관 라이선스 동의서 (PO ↔ 자관) |
| 7 | **0076** | KLA 5월 발표 신청 (5.31 마감) | PO 직접 액션 |
| 8 | **0086·0087·0088** | xlsm import + 동등 기능 + IP 보호 | 자관 4,233 매크로 천국 정합 |
| 9 | **0089·0090·0091** | 4 페르소나 ICP rules + 매크로 사서 영업 1순위 + 4주 시나리오 | po-outreach-list 정합 |

→ 9 ADR PO 결정 → 자율 commit 즉시 활성 (5+ commit 일괄).

---

## 2. PO 직접 액션 7건 (자율 X)

| # | 액션 | 시간 | 마감 |
|---:|---|---|---|
| 🔴 1 | KLA 전국도서관대회 발표 신청 | 1~2일 | **2026.5.31** |
| 🔴 2 | 사서교육원 강의 제안서 (신학기) | 1주 | 2026.5월 |
| 🔴 3 | 자관 PILOT 라이선스 동의서 (PO ↔ 자관) | 1일 | PILOT 시작 전 |
| 🟢 4 | NL Korea API 5종 추가 인증키 신청 | 7일 | (즉시) |
| 🟢 5 | 공공데이터포털 「전국도서관표준데이터」 다운 | 30분 | (즉시) |
| 🟡 6 | KLA 회원 가입 (license@kla.kr) | 1일 | 2026.5월 |
| 🟡 7 | logging PII 5종 마스킹 보강 (PIPA 패턴 2) | 30분 (코드) | 2026-09-11 전 |

---

## 3. 자관 PILOT 4주 시나리오 (5월 첫주 시작)

자관 = 「내를건너서 숲으로 도서관」 (은평구·사서 8명 운영)

| 주차 | 페르소나 | 시연 자료 | KPI |
|---|---|---|---|
| 1주 | ★ Excel 매크로 사서 (조기흠) | 책단비 hwp 4 양식·상호대차 쪽지·신착 간지 자동 | Q1 결제 의향 (★ 매크로 사서 페르소나) |
| 2주 | 수서 사서 (박지수 수서) | KOLAS F12 → 4단 검증·xlsx 도서원부 9 컬럼 | 권당 시간 절감·40 차수 routine 자동 |
| 3주 | 종합 사서 4명 | 권당 8~15분 → 2분 (87% 단축)·9 자료유형 정합 | T_manual − T_auto 정량 |
| 4주 | 통합 검증 + 영상 X 명시 | PIPA 5대 자동 차단·6년 NPS 측정 | PILOT 후 NPS ↑ |

→ 4주 결과 → KLA 5.31 발표 슬라이드 직접.

---

## 4. PIPA 시행 2026-09-11 임박 ★ (매출 10% 과징금)

| 패턴 | 우리 정합 |
|---|---|
| 1. Reader entity ERD 부재 | ✅ 자관 알파스 위임 + pii-guard hook 설계 완료 |
| 2. 암호화 (bcrypt·AES·TLS) | 🟡 logging PII 5종 보강 필요 ★ |
| 3. DSAR | ✅ /account/export·delete |
| 4. 72h 신고 | ❌ 베타 PILOT 도달 시 |
| 5. audit_log + 해시 체인 | ❌ 5만명+ 도달 시 |

→ ⚠️ logging PII 5종 (email·phone·patron_name·patron_id·birth_date) 마스킹 보강 = PILOT 전 권장.

---

## 5. 5월 1~31일 일정표

```
5월 1주차 (5.1~5.7):
  ☐ ADR 9 PO 결정
  ☐ 자관 PILOT 라이선스 동의서 서명
  ☐ logging PII 5종 마스킹 보강
  ☐ NL Korea API 5종 추가 신청

5월 2주차 (5.8~5.14):
  ☐ 자관 PILOT 1주: ★ 매크로 사서 (조기흠) 시연
  ☐ KLA 회원 가입
  ☐ 공공데이터포털 ICP DB 다운

5월 3주차 (5.15~5.21):
  ☐ 자관 PILOT 2주: 수서 사서 (박지수 수서) 시연
  ☐ KLA 발표 슬라이드 초안

5월 4주차 (5.22~5.28):
  ☐ 자관 PILOT 3주: 종합 사서 4명 시연
  ☐ KLA 발표 슬라이드 자관 PILOT 결과 추가

5월 5주차 (5.29~5.31): ★ 마감
  ☐ 자관 PILOT 4주: 통합 검증 + PIPA + NPS 측정
  ☐ KLA 전국도서관대회 발표 신청 (5.31 마감)
  ☐ 사서교육원 강의 제안서 제출
```

---

## 6. KPI 측정 (PILOT 4주 후)

| KPI | 측정 | 목표 |
|---|---|---|
| Q1 결제 의향 | 4 페르소나별 자관 사서 8명 인터뷰 | ★ 매크로 사서 ≥ 90 |
| 권당 시간 절감 | T_manual (자관 实측) − T_auto | 87%+ 단축 |
| 매크로 자작 시간 절감 | 5년 历사 vs 우리 SaaS | ★ 매크로 사서 80%+ |
| .mrc 4단 검증 정합률 | 자관 174 파일 자동 | ≥99% |
| PILOT 후 NPS | 4주 후 자관 사서 만족도 | 자관 6년 历사와 비교 |
| 권당 비용 측정 | Q2 검증 (₩7 vs ₩70) | ADR 0014 결정 자료 |

---

## 7. 참조 docs (90+ 누적)

### 7.1 핵심 (이번 야간 자율)

- [business-evaluation-criteria-2026-04-28.md](business-evaluation-criteria-2026-04-28.md) — 통합 평가 헌법
- [pii-guard-hook-design.md](pii-guard-hook-design.md) — PIPA 패턴 1 자동 보강
- [saseo-personas-2026-04-28.md](saseo-personas-2026-04-28.md) — 4 페르소나 매트릭스
- [po-pilot-readiness-checklist.md](po-pilot-readiness-checklist.md) — PILOT 시작 체크리스트
- [adr-priority-matrix-2026-04-28.md](adr-priority-matrix-2026-04-28.md) — 91 ADR 우선순위
- [night-autonomous-session-2026-04-28-summary.md](night-autonomous-session-2026-04-28-summary.md) — 종합 보고서

### 7.2 자관 D 드라이브 audit (8개)

- d-drive-bookforest·acquisition·mrc-validation·reading-rooms·history-tools·yoondongju-thesis·final-completion·xlsm-macros

### 7.3 KORMARC 표준 + Phase 1.5 (3개)

- kormarc-2023-standard·online-materials·nlk-cataloging-guidelines

### 7.4 KOLAS·KERIS·책이음·책나래 + 영업 (8개)

- kolas-iii·chaekeum·chaeknarae·keris-dls-phase2-prd
- keris-alphas-integration·5systems·25gu-naming·central-institutions-update

### 7.5 알파스·정책·메타 (7개)

- alphas-bookband·acquisition·registration·workflow
- yangsik-matrix·government-policy·chaekdanbi

---

## 8. Sources

- 야간 자율 누적 (47 task / 90+ docs / 91 ADR)
- 자료 폴더 100% (66 파일) + D 드라이브 100% (87 항목)
- KORMARC KS X 6006-0:**2023.12** + PIPA 2026-09-11 + ISMS-P 2027-07-01
- KLA 전국도서관대회 5.31 마감
- 자관 「내를건너서 숲으로 도서관」 PILOT (사서 8명·5 시스템·6년 NPS·.mrc 174·35 윤동주·xlsm 4,233)
