# 30개 단일 기능 앱 포트폴리오 로드맵

> ADR 0053 정합 (PO 2026-05-07)·인디 검증 MRR $22K·1주 1앱 Claude 자율
> ADR 0052 정합·발사·홍보·피드백 = 보류 (PO 미래 결정 시)

## 0. 핵심 원칙

| 원칙 | 적용 |
|---|---|
| 단일 기능 | 1줄 설명 가능 (예: "ISBN → KORMARC") |
| 버그 0 | tests ≥ 10·ruff 0 errors·CI green |
| 1주 완성 | Mon spec → Tue~Wed 코드 → Thu UI → Fri 정제 → Sat·Sun docs |
| 라이선스 | MIT/Apache/BSD 의존성만 |
| 한국어 friendly | docs·UI 한국어 (사서·일반인 1번에 이해) |
| 자관 데이터 X | 헌법 §14·사용자 컴퓨터·SaaS 서버 X |
| 발사 = 보류 | repo private·로컬 코드만·PO 명시 시 즉시 발사 |

## 1. 30 앱 매트릭스

### A. 도서관·사서 (founder fit·우선·#1~#8)

| # | 앱 | 단일 기능 | 입력 → 출력 | 상태 |
|---|---|---|---|---|
| 1 | **kormarc-auto** | KORMARC 자동 생성 | ISBN → .mrc | ✅ 완성 (v0.7.1·1287 tests) |
| 2 | **kdc-classify** | KDC 분류 추천 | 책 정보 → KDC 3 후보 | ✅ Cycle 85 완성 (31 tests·ruff 0·CLI 작동) |
| 3 | callnumber-builder | 청구기호 자동 | KDC + 저자 → 청구기호 | 시드 |
| 4 | librarian-overtime | 사서 야근 추적기 | 일과 시간 → 야근율·통계 | 시드 |
| 5 | library-stats-auto | 도서관 월간 통계 | 대출·이용자·NPS → 보고서 | 시드 |
| 6 | book-withdrawn | 폐기 도서 추천 | 회전율·손상 → 폐기 후보 | 시드 |
| 7 | event-poster-auto | 도서관 행사 포스터 | 행사 정보 → PDF 포스터 | 시드 |
| 8 | newbook-alert | 신간 알림 봇 | KOLAS·DLS → 신간 RSS | 시드 |

### B. 자영업·콘텐츠 (Phase 1 안전·#9~#13)

| # | 앱 | 단일 기능 | 입력 → 출력 | 상태 |
|---|---|---|---|---|
| 9 | **naver-review-responder** | 네이버 리뷰 답변 | 리뷰 → LLM 답변 draft | PoC (auto-clicker-saas) |
| 10 | **sns-multipost** | SNS 다중 업로드 | 사진 → 인스타+X+페북 | PoC (auto-clicker-saas) |
| 11 | pos-revenue-input | POS 매출·재고 | 영수증 OCR → 엑셀 | 시드 |
| 12 | academy-alert | 학원 학부모 알림 | 시간표 → 학부모 SMS | 시드 |
| 13 | youtube-subtitle | 유튜브 자막 자동 | 영상 → 한글 자막 | 시드 |

### C. 모바일 게임 (Phase 2 옵트인·#14~#16)

| # | 앱 | 단일 기능 | 입력 → 출력 | 상태 |
|---|---|---|---|---|
| 14 | **mobile-game-raid** | 레이드 자동 클릭 | 게임 화면 → 레이드 클릭 | PoC (auto-clicker-saas) |
| 15 | daily-attendance | 일일 출석 자동 | 출석 화면 → 클릭 | 시드 |
| 16 | popup-dismiss | 광고 팝업 자동 닫기 | 팝업 → 닫기 | 시드 |

### D. 일반 생산성 (#17~#23)

| # | 앱 | 단일 기능 | 입력 → 출력 | 상태 |
|---|---|---|---|---|
| 17 | **hanja-to-hangeul** | 한자 → 한글 변환 | 한자 → 한글 발음 | 시드 |
| 18 | pdf-korean-ocr | PDF 한글 OCR | PDF → 한글 텍스트 | 시드 |
| 19 | receipt-to-budget | 영수증 OCR → 가계부 | 영수증 → 엑셀 | 시드 |
| 20 | meeting-summary | 회의록 자동 요약 | 음성 → 요약 | 시드 |
| 21 | email-draft | 이메일 답변 draft | 이메일 → 답변 draft | 시드 |
| 22 | gform-to-slack | 구글 폼 → 슬랙 알림 | 응답 → 알림 | 시드 |
| 23 | text-to-calendar | 일정 → 캘린더 자동 | 텍스트 → 구글 캘린더 | 시드 |

### E. 학생·교육 (#24~#26)

| # | 앱 | 단일 기능 | 입력 → 출력 | 상태 |
|---|---|---|---|---|
| 24 | english-flashcard | 영어 단어 자동 카드 | 단어 → 예문·발음 | 시드 |
| 25 | korean-history-timeline | 한국사 연표 자동 | 사건 → 연표 PDF | 시드 |
| 26 | math-step-solver | 수학 문제 단계 풀이 | 문제 → 풀이 단계 | 시드 |

### F. 글쓰기·창작 (#27~#30)

| # | 앱 | 단일 기능 | 입력 → 출력 | 상태 |
|---|---|---|---|---|
| 27 | blog-seo-check | 블로그 SEO 검수 | 글 → 점수·개선 | 시드 |
| 28 | story-generator-5min | 동화 5분 자동 생성 | 키워드 → 동화 | 시드 |
| 29 | resume-to-coverletter | 이력서 → 자기소개서 | 이력 → 자기소개서 | 시드 |
| 30 | poem-novel-opening | 시·소설 첫 단락 | 키워드 → 5 후보 | 시드 |

### G. 페인 검증 통과 신규 (#31~·ADR 0055 게이트 통과)

| # | 앱 | 단일 기능 | 페인 ID | 시장/캐시카우 | 상태 |
|---|---|---|---|---|---|
| **31** | **freelancer-tax-helper** | 한국 프리랜서 비용처리·종소세 | P-2026-004 | 90/100 | ✅ Cycle 87 완성 (33 tests·ruff 0·CLI 작동) |
| **32** | **sidehustle-tracker** | 직장인 N잡 부업 시간·번아웃·시간당 매출 | P-2026-006 | 100/100 | ✅ Cycle 88 완성 (27 tests·ruff 0·CLI 작동) |
| (확장) | sns-multipost B모드 (블로그→다중) | #10 확장 | P-2026-002 | 95/95 | ✅ GO·#10 통합 |

## 2. 1주 1앱 사이클

```
Day 1 (Mon) — 단일 기능 명확화
  - 1줄 설명 = "<input> → <output>"
  - docs/spec.md (1 페이지·기능·평가축)
  - 의존성 결정 (MIT/Apache only)

Day 2 (Tue) — 핵심 로직 골격
  - src/<app>/__init__.py
  - src/<app>/main.py (entry point)
  - src/<app>/core.py (핵심 함수)

Day 3 (Wed) — 단위 테스트 ≥ 10
  - tests/test_core.py
  - pytest -q + ruff check
  - 회귀 게이트 정합

Day 4 (Thu) — UI (Streamlit·CLI·웹)
  - streamlit_app.py 또는 cli.py
  - 한국어 라벨·KWCAG 2.2 AA (UI 있을 시)
  - 사서/일반인 1번에 이해

Day 5 (Fri) — 정제·CI
  - ruff·mypy·pytest 전 통과
  - .github/workflows/ci.yml
  - 통합 테스트 ≥ 3

Day 6~7 (Sat·Sun) — docs·다음 앱 시드
  - README.md (한국어·1 페이지·사용법)
  - LICENSE (MIT/Apache)
  - learnings.md 갱신
  - 다음 앱 # 시드
```

## 3. 평가축 (각 앱)

매 commit 게이트 (kormarc-auto 평가축 정합):
- [ ] 단일 기능 명확 (1줄)
- [ ] tests 통과 + ruff 0 errors
- [ ] 1주 이내 완성 (7일)
- [ ] 라이선스 = MIT/Apache/BSD
- [ ] 한국어 docs·UI
- [ ] 자관/PII 데이터 X (헌법 §14)
- [ ] LICENSE 파일 존재
- [ ] README 1 페이지

음수 = commit X.

## 4. 폴더 구조

```
클로드 코드 활동용/
├── kormarc-auto/                     # #1 (완성)
├── 후보_아이디어/
│   └── auto-clicker-saas/            # #9·#10·#14 PoC 통합
└── 30-apps/                          # 신규 (Cycle 85+)
    ├── 02-kdc-classify/
    ├── 03-callnumber-builder/
    ├── ...
    └── 30-poem-novel-opening/
```

각 앱 폴더 = 독립 Python 프로젝트:
- pyproject.toml
- src/<app>/
- tests/
- docs/
- README.md
- LICENSE
- .github/workflows/ci.yml

## 5. 발사 보류 정책 (ADR 0052 정합)

```
Claude 자율:
✅ 코드 작성·테스트·docs·repo 누적
✅ 로컬 git commit·private repo
✅ tests + ruff + CI

PO 미래 결정 시:
❌ 앱스토어 등록
❌ Streamlit Cloud 배포
❌ 도메인 구매
❌ 사용자 피드백 수집
❌ MRR 측정·결제·홍보
❌ git push (외부 repo·remote)
```

→ **저장만**: 로컬 코드·private repo·docs·tests.
→ **PO 명시 명령 시 활성**: "30 앱 발사해" / "<n>번 앱 발사해" 등.

## 6. 1주 1앱 ROI

| 시점 | 누적 앱 | 코드 자산 | 발사 시 (PO 결정) |
|---|---:|---|---|
| Cycle 85 (Week 1) | #1 + #2 = 2 | kormarc + KDC | 즉시 발사 가능 |
| Cycle 88 (Week 4) | #1~#5 = 5 | 도서관 5 | 카테고리 A 묶음 |
| Cycle 100 (Week 16) | #1~#16 = 16 | 6 카테고리 절반 | 다양화 |
| Cycle 114 (Week 30) | #1~#30 = 30 | 풀 포트폴리오 | 인디 패턴 활성 |

→ 30주 = 약 7개월 = 30 앱 코드 자산 = PO 미래 발사 시 인디 검증 패턴 활성.

## 7. MRR $22K 검증 패턴 (인디 출처·PO 인용)

| 패턴 요소 | 우리 변형 |
|---|---|
| 30개 단일 기능 앱 | ✅ 동일 |
| 빠른 출시 | ✅ 코드 1주 (출시 = 보류) |
| 버그 X | ✅ tests + ruff |
| 사용자 피드백 | △ 시뮬·페르소나 (실 = 보류) |
| 다음 앱 결정 | △ 자율 (PO 결정 시 피드백 기반 재배치) |
| 12개월 MRR $22K | △ PO 결정 시 활성 가능 |

## 8. Cycle 85+ 첫 적용

| Cycle | Week | 앱 | 카테고리 |
|---|---|---|---|
| 85 | 1 | #2 KDC 분류 추천 | A 도서관 |
| 86 | 2 | #4 사서 야근 추적기 | A 도서관 |
| 87 | 3 | #11 POS 매출·재고 | B 자영업 |
| 88 | 4 | #17 한자 → 한글 변환 | D 생산성 |
| 89 | 5 | #5 도서관 월간 통계 | A 도서관 |
| 90 | 6 | #21 이메일 답변 draft | D 생산성 |

→ founder fit 우선 (A) + 다양화 (B·D) 교차.

## 9. 메모리·헌법 정합

- CLAUDE.md §8C (NO offline)·§8D (30 apps)·§14 (자관 데이터 X)·§15 (자가 설치)
- ADR 0052·0053
- feedback_no_offline_activities ⭐⭐⭐⭐⭐
- feedback_30_apps_portfolio ⭐⭐⭐⭐⭐
- 사용자_TODO.txt 정합 (PO 외부 = 보류)

## 10. 출처

- Indie Hackers (PO 인용·2026-05-07): 30개 단일 기능 앱 포트폴리오 = 12개월 MRR $22,000
- 핵심 = 단일 기능 + 버그 X + 빠르게 + 피드백 → 다음 앱
- Claude Code 워크플로우 = 1주 1앱 현실적
