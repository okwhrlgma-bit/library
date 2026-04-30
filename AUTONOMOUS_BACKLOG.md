# Autonomous Backlog (cloud routine 자율 작업 큐)

> **목적**: 1h cloud routine·주간·월간 fire 시 자율 작업 우선순위 가이드. 매 사이클 cloud agent가 본 파일을 자동 참조해서 다음 작업 결정.
> **자동 갱신**: cloud agent가 작업 완료 시 본 파일에서 항목 제거·신규 추가.
> **단일 진실**: ★ 자관 .mrc 99.82% 정합 + 영업 자료 11건 + Cloud routine 3개

---

## 🟢 우선순위 1 — 매출 직결 + 작은 commit (즉시 진행)

### 4-30 PO 명령 (보편성 + 심층) — Agent 4건 token 한도 후 재시도 ★

KST 07:40 token 회복 후 재실행 또는 cloud routine 위임:

- [x] **Part 11 자관 보편성 검증** ✅ bfdfbb8 (직접 작성·Agent 5 token 한도 대체)
- [x] **Part 12 사서 페인 학술 심층** ✅ 5a83116 (직접 작성·14 학술 출처)
- [x] **Part 13 한국 도서관 시장 TAM/SAM/SOM** ✅ f635c1c (직접 작성·5년 누적 20~23억)
- [x] **Part 14 국제 도서관 자동화** ✅ ae6d80f (직접 작성·미국 동아시아 11관·605,000권)

### 4-30 PO 명령 후속 (적용)

- [x] Part 7 타관 KORMARC 정합 ✅ 7ce6b89 (22,152자)
- [x] Part 8 한국 도구·경쟁사 ✅ f6a2e4b (9,500자)
- [x] Part 9 사서 커뮤니티 ✅ 89ca09f (14,500자)
- [x] Part 10 페인포인트 실측 ✅ 401ebf1 (560줄)
- [x] 향후 코딩 로드맵 13 영역 ✅ c98d590

### Part 6 가이드 격차 4건 (4-30 인계·즉시 적용 가능)

- [x] **CLAUDE.md 323줄 → 206줄** ★ (Step 1~5 완료·Anthropic 권장 거의 도달·9d08904·a0fe201·ebcd5f6·35f88ef·05c5549)
- [x] `/ultrareview` `/ultraplan` 활용 시점 (Part 6 §12 갱신·PILOT 4주차 5/29 발표 직전 활용)
- [x] Routines Pro 5건/일 한도 모니터링 (`docs/cloud-routine-monitoring-guide.md` §7 추가·1h routine 4h 변경 권장)
- [x] stop-double-gate.py `stop_hook_active` 체크 확인 (line 39 정합 검증·이미 정합)

### 코드 (각 1~2시간)

- [x] streamlit_app.py에 prefix-discover 탭 통합 ✅ 338e81d (5 → 6 메인 탭)
- [ ] /signup endpoint에 페르소나 자동 분류 (도서관명·이메일 도메인 패턴)
- [x] /admin/stats에 페르소나별 funnel ✅ a1b07af·8fac5dc
- [x] /webhook/portone POST endpoint ✅ b06f60e + 3 tests f73b4fd
- [x] CLI pilot-collect·sales-funnel ✅ 69f2ec9

### 영업 자료 (각 30분)

- [x] PILOT 2주차 매뉴얼 ✅ 56e79a4 (박지수 수서 60분)
- [x] PILOT 3주차 매뉴얼 ✅ cf325fd (종합 4명 90분)
- [x] PILOT 4주차 통합 매뉴얼 ✅ 289f79b (KLA 5.31 마감)
- [x] 도서관 정보나루 활용 가이드 ✅ docs/sales/data4library-guide-2026-05.md
- [x] KOLIS-NET 마이그레이션 영업 메일 ✅ docs/sales/outreach-kolis-net-migration-2026-05.md
- [x] BIBFRAME 2.0 LOD 영업 메일 ✅ docs/sales/outreach-bibframe-lod-2026-05.md
- [x] 카카오톡 오픈채팅 사서 동호회 영업 메일 ✅ docs/sales/outreach-kakao-openchat-2026-05.md

### 매뉴얼 (각 30분)

- [x] Cloud routine 3개 모니터링 가이드 ✅ 0a29e07·09ca181 (Pro 한도 §7)
- [x] GitHub Releases 발행 자동화 ✅ .github/workflows/release.yml (git tag v*.*.* push → 자동)
- [x] Self-host 가이드 ✅ docs/self-host-guide.md (Render·Fly.io·Docker·1관→1,000관 시뮬)

---

## 🟡 우선순위 2 — Phase 1+ 작업 (PO 결정 후)

- [x] **ADR 0020**: chaekdanbi/auto_label_generator.py 선택 의존성 패턴 ✅ ac70a28 (8 tests·python-hwpx 미설치 시 .txt 폴백)
- [ ] **ADR 0021 후**: inventory/kolas_f12_importer.py (xlsx 9 컬럼·EQ/CQ prefix·rapidfuzz fuzzy) — Phase 2·5/3주차
- [ ] **ADR 0007 후**: 포트원 PG 실 SDK 통합 (charge·subscribe·tax invoice 실 구현)
- [ ] **ADR 0013 후**: business-impact-axes.md hooks active (Q1·Q2·Q3·Q4·Q5 자동 측정)

---

## 🟠 우선순위 3 — Phase 1.5+ KORMARC 추가 자료유형

PO MVP CHAPTER 9 명령상 단행본 우선. 본 항목은 단행본 정점 후:

- [x] kormarc/ebook.py ✅ 29d7a86 (008 23 + 856 + 538)
- [x] kormarc/ejournal.py ✅ 29d7a86 (022 + 310 + 362 + FREQUENCY_CODES)
- [x] kormarc/audiobook.py ✅ 29d7a86 (007 + 538 + 511 낭독자)
- [x] kormarc/multimedia.py ✅ (008 33 + 007 + 300 + 306 + 538) — Phase 1.5 완성
- [x] kormarc/thesis.py ✅ (502 + 504 + 700 지도교수 + format_502_text) — Phase 1.5 완성

→ **9 자료유형 모듈 100% 커버 달성** (KORMARC 2023.12 정합)

---

## 🔴 우선순위 4 — UI/UX 큰 변경 (사서 1명 만남 후)

STATUS_REALITY_CHECK.md (4-27) 권고:

- [ ] streamlit_app.py 1,424 lines → 5 page 분리 (사서 1명 만남 후)
- [ ] 22 button → 5 button 압축
- [ ] multi-page (Streamlit pages/ 디렉토리)
- [ ] Pretendard 폰트 + 16px (이미 적용)

---

## 🔵 우선순위 5 — 외부 도구 통합 (사용자 가입 후)

`docs/research/part5-tools-and-automation.md` 정합:

- [ ] Resend 통합 (영업 메일 자동 발송·월 3,000건 무료)
- [ ] Cal.com 통합 (PILOT 시연 자동 예약)
- [ ] PostHog 통합 (사서 funnel·세션 녹화)
- [ ] Sentry 통합 (5xx 에러 즉시 알림)

---

## ⚪ 우선순위 6 — 영업 후속 (PILOT 결과 누적 후)

- [ ] 자관 PILOT 4주 결과 → docs/sales/pilot-results-2026-05.md 자동 생성
- [ ] KLA 5.31 발표 슬라이드 PDF 자동 생성 (Marp 또는 Reveal.js)
- [ ] 사서교육원 강의 슬라이드 (60분·30분 양본)
- [ ] 도서관저널 기고문 PDF 변환·발송 자동

---

## 🔄 매 cloud routine fire 시 자동

1. 본 backlog 위에서 아래로 스캔
2. 🟢 1순위에서 미완료 항목 1건 선택
3. 작업 → pytest·ruff·assertions 통과 → commit·push
4. 본 backlog에서 완료 항목 제거 + 신규 발굴 시 추가

---

## 매 commit 평가축

- §0 사서 마크 시간 단축 OR §12 결제 의향 ↑ 양수 영향만 commit
- 흥미·완성도·기술 호기심은 평가축 X
- pytest·ruff·binary_assertions (34/34) 통과 후 commit·push

---

## Sources

- `CLAUDE.md §0 + §12` (헌법 평가축)
- `docs/sales/INDEX.md` (영업 자료 인덱스)
- `docs/sales/annual-calendar-2026-2027.md` (계절별 우선순위)
- `STATUS_REALITY_CHECK.md` (4-27 솔직한 점검·UI 권고)
- `docs/mvp-redefinition-2026-04-29.md` (PO MVP 명령)
- `.claude/rules/business-impact-axes.md` (사업 5질문)
