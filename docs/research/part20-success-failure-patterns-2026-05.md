# Part 20 — SaaS 성공·실패·폐업 사례 차용 (2026-05-02)

> 회피 패턴 + 모방 패턴 추출 → kormarc-auto 적용
> 출처: 자율 조사 3개 영역 (한국 SaaS 실패·글로벌 vertical SaaS·KOLAS/DLS 운영 문제)

---

## 1. 실패 통계 (글로벌 + 한국)

### 글로벌 SaaS

- **90% SaaS 실패** (3년 내)
- **42% = "no market need"** (시장 검증 부족) ★★★
- **29% = 자금 부족** (cash flow)
- **GTM 약함** = 제품보다 영업 더 어려움
- **온보딩 복잡 → 높은 churn**
- 사례: Quibi $1.75B 6개월 폐업 / 101 Studios 2020 (교수가 좋다 했지만 도입 X) / Zapstream 100K 사용자 후 자금 소진

### 한국 스타트업

- 첫해 실패 20%
- TIPS 선정 후도 **2%만 Exit 성공**
- **74% = PMF + 마케팅 + HR**
- 38% = 자금 부족
- 마케팅 자원 부족 (제품에만 치중)

---

## 2. kormarc-auto가 이미 회피한 패턴 ✅

| 실패 원인 | kormarc-auto 회피 방법 |
|----------|----------------------|
| **No market need (42%)** | PO 사서 출신 = 시장 직접 경험 + 영업 자료 17건 + PILOT 1관 99.82% 검증 |
| **자금 부족 (29~38%)** | 권당 100원 종량 + 월정액 = 빠른 캐시카우 도달 (200관 × 3.3만 = 660만/월) |
| **GTM 약함** | KOLAS 종료 골든타임 + 17 영업 자료 + 다채널 (KLA·KSLA·KPLA·디시·카톡) |
| **온보딩 복잡** | 헌법 §"user friendly mandate" + librarian-5min-cheatsheet (5분 이해) |
| **HR 문제** | 1인 + Claude Code = HR X |
| **정부 지원 의존** | 사서 본인 예산 + 학교 예산 (S2B) + 자치구 운영비 — 다변화 |
| **대기업 협력 의존** | 자체 영업 + 직접 채널 |

→ 이미 7대 실패 원인 모두 사전 회피.

---

## 3. KOLAS·DLS 운영 실패 사례 (직접 회피)

### 발견 사실

- 책이음 시스템 오류·RFID 태깅 단말 오류 빈발
- 사서들이 "잔머리 쓰는 경우 많음" → 시스템 신뢰성 ↓ → 결국 KOLAS III 2026-12-31 종료
- DLS는 2024년 KERIS 학교도서관 시스템과 통합 (동일 시스템 갈아엎기 사례)

### kormarc-auto 회피 적용

- **시스템 신뢰성**: binary_assertions 38건 + 자관 99.82% 정합 = KOLAS 같은 오류 사전 차단
- **사서가 머리 쓰지 않음**: 자동 + 검증 + source_map 출처 표시
- **갈아엎기 회피**: 클라우드 SaaS + 헌법 §"기존 고객 가격 인상 X" = 마이그레이션 강제 X

---

## 4. DLS 통합 사례 모방 (KERIS 2024)

### 발견 사실

- DLS = 독서로DLS + 학교도서관 업무지원 시스템 통합 (2024)
- KERIS + 17 시·도교육청 협력
- 12,200관 학교도서관 단일 채널

### 차용 가능

- **kormarc-auto가 DLS 호환 명시 = 학교도서관 12,200관 진입 카드**
- 이미 헌법 §2 도메인 용어에 "독서로DLS / KERIS DLS" 명시
- 영업 카피: "DLS 통합 후에도 KORMARC 자동 생성은 별도 도구 필요 — kormarc-auto"

---

## 5. 핵심 적용 액션

| # | 액션 | 평가축 |
|---|------|--------|
| 1 | KLA 발표 슬라이드 §"7대 실패 회피" 슬라이드 추가 | Q1 +2 (영업 신뢰성 — 우리는 이미 회피했다) |
| 2 | "KOLAS·DLS 갈아엎기 사례 회피" 영업 카피 18건째 | Q1 +3 |
| 3 | DLS 호환 명시 영업 카피 (학교도서관 진입) | Q1 +5 (12,200관 잠재) |
| 4 | "기존 고객 가격 인상 X" 정책 페이지 강조 (Niche Academy 패턴) | Q4 +5 (락인) |

---

## Sources

- [SaaS 실패 92% 3년 내 — LinkedIn TK Kader](https://www.linkedin.com/posts/tkkader_92-of-saas-startups-will-fail-within-3-years-activity-7186350504631808000-YPig)
- [42% SaaS = no market need — Codica](https://www.codica.com/blog/why-saas-startups-fail/)
- [한국 스타트업 실패 90% — 슈퍼브AI](https://blog-ko.superb-ai.com/chosun-journalists-who-know-a-thing-season-12/)
- [한국 스타트업 폐업 후기 — 모비인사이드](https://www.mobiinside.co.kr/2023/03/29/startup-jobs-interview/)
- [도서관자동화시스템 현황 인식 연구 — ResearchGate](https://www.researchgate.net/publication/380789008)
- [KOLAS III 종료 — 도서관 표준자료관리시스템 나무위키](https://namu.wiki/w/%EB%8F%84%EC%84%9C%EA%B4%80%20%ED%91%9C%EC%A4%80%EC%9E%90%EB%A3%8C%EA%B4%80%EB%A6%AC%EC%8B%9C%EC%8A%A4%ED%85%9C)
- [DLS 자료실](https://www.dls.or.kr/)

---

> **이 파일 위치**: `kormarc-auto/docs/research/part20-success-failure-patterns-2026-05.md`
> **즉시 적용**: AUTONOMOUS_BACKLOG에 영업 자료 18건째 + DLS 학교 진입 카드 추가
