# Autonomous Backlog (cloud routine 자율 작업 큐)

> **목적**: 1h cloud routine·주간·월간 fire 시 자율 작업 우선순위 가이드. 매 사이클 cloud agent가 본 파일을 자동 참조해서 다음 작업 결정.
> **자동 갱신**: cloud agent가 작업 완료 시 본 파일에서 항목 제거·신규 추가.
> **단일 진실**: ★ 자관 .mrc 99.82% 정합 + 영업 자료 11건 + Cloud routine 3개

---

## 🟢 우선순위 1 — 매출 직결 + 작은 commit (즉시 진행)

### Part 6 가이드 격차 4건 (4-30 인계·즉시 적용 가능)

- [x] **CLAUDE.md 323줄 → 206줄** ★ (Step 1~5 완료·Anthropic 권장 거의 도달·9d08904·a0fe201·ebcd5f6·35f88ef·05c5549)
- [x] `/ultrareview` `/ultraplan` 활용 시점 (Part 6 §12 갱신·PILOT 4주차 5/29 발표 직전 활용)
- [x] Routines Pro 5건/일 한도 모니터링 (`docs/cloud-routine-monitoring-guide.md` §7 추가·1h routine 4h 변경 권장)
- [x] stop-double-gate.py `stop_hook_active` 체크 확인 (line 39 정합 검증·이미 정합)

### 코드 (각 1~2시간)

- [ ] streamlit_app.py에 prefix-discover 탭 통합 (별도 standalone 외 14탭 → 15탭) — STATUS_REALITY_CHECK 권고 신중
- [ ] /signup endpoint에 페르소나 자동 분류 (도서관명·이메일 도메인 패턴)
- [x] /admin/stats에 페르소나별 funnel ✅ a1b07af·8fac5dc
- [x] /webhook/portone POST endpoint ✅ b06f60e + 3 tests f73b4fd
- [x] CLI pilot-collect·sales-funnel ✅ 69f2ec9

### 영업 자료 (각 30분)

- [x] PILOT 2주차 매뉴얼 ✅ 56e79a4 (박지수 수서 60분)
- [x] PILOT 3주차 매뉴얼 ✅ cf325fd (종합 4명 90분)
- [x] PILOT 4주차 통합 매뉴얼 ✅ 289f79b (KLA 5.31 마감)
- [ ] 도서관 정보나루 활용 가이드 (수서 사서 영업)
- [ ] KOLIS-NET 마이그레이션 영업 메일 (작은도서관 6,830관)
- [ ] BIBFRAME 2.0 LOD 영업 메일 (대학·디지털 컬렉션)
- [ ] 카카오톡 오픈채팅 사서 동호회 영업 메일

### 매뉴얼 (각 30분)

- [x] Cloud routine 3개 모니터링 가이드 ✅ 0a29e07·09ca181 (Pro 한도 §7)
- [ ] GitHub Releases 발행 자동화 (gh CLI workflow)
- [ ] Self-host 가이드 (Render·Fly.io·Docker)

---

## 🟡 우선순위 2 — Phase 1+ 작업 (PO 결정 후)

- [ ] **ADR 0021 PO 결정 후**: chaekdanbi/auto_label_generator.py (python-hwpx·KOLAS F12 엑셀 read·4 양식 hwp 자동) — Phase 1·5/2주차
- [ ] **ADR 0021 후**: inventory/kolas_f12_importer.py (xlsx 9 컬럼·EQ/CQ prefix·rapidfuzz fuzzy) — Phase 2·5/3주차
- [ ] **ADR 0007 후**: 포트원 PG 실 SDK 통합 (charge·subscribe·tax invoice 실 구현)
- [ ] **ADR 0013 후**: business-impact-axes.md hooks active (Q1·Q2·Q3·Q4·Q5 자동 측정)

---

## 🟠 우선순위 3 — Phase 1.5+ KORMARC 추가 자료유형

PO MVP CHAPTER 9 명령상 단행본 우선. 본 항목은 단행본 정점 후:

- [ ] kormarc/ebook.py (008 23 + 856 URL + 538 매체 자동)
- [ ] kormarc/ejournal.py (022 ISSN + 310 발행빈도 + 362 권차 자동)
- [ ] kormarc/audiobook.py (008 06=j + 007 + 538 음향 매체)
- [ ] kormarc/multimedia.py (g 시청각자료)
- [ ] kormarc/thesis.py 보강 (502 학위논문·학과·지도교수 자동)

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
