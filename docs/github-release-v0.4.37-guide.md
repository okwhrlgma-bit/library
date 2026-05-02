# GitHub Release v0.4.37 발행 가이드 (PO 5분)

> **목적**: GitHub repo (https://github.com/okwhrlgma-bit/library)에 정식 v0.4.37 release 발행 → 외부 사용자가 다운로드 가능 + 영업 자료 강화.
> **단일 진실**: 자관 .mrc 174 파일·3,383 레코드 → 99.82% 정합 ★

---

## 1. 발행 5분 단계

### 1-1. GitHub Web UI (가장 쉬움)

1. https://github.com/okwhrlgma-bit/library 접속
2. 우측 사이드바 "Releases" 클릭 → "Create a new release" 또는 "Draft a new release"
3. 입력:
   - **Tag**: `v0.4.37`
   - **Target**: `main` (default)
   - **Title**: `v0.4.37 — Phase 0 MVP 완성 + 자관 99.82% 정합`
   - **Description**: 본 §2 release notes 그대로 복사
4. ☐ "Set as the latest release" 체크
5. **Publish release** 버튼 클릭

### 1-2. gh CLI (자동·1줄)

```powershell
cd "C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto"
gh release create v0.4.37 --title "v0.4.37 — Phase 0 MVP 완성 + 자관 99.82% 정합" --notes-file docs/github-release-v0.4.37-guide.md
```

(gh CLI 없으면 `winget install GitHub.cli` 1회 설치)

---

## 2. Release Notes (그대로 복사 가능)

```markdown
# v0.4.37 — Phase 0 MVP 완성 + 자관 .mrc 99.82% 정합 ★

## 핵심 ★

- **자관 「○○도서관」 .mrc 174 파일·3,383 레코드 → 99.82% 정합 검증** (KORMARC 2023.12 한국 KOLAS 실무 정합)
- 4-Part 종합 매뉴얼 113,500자 + Part 5 외부 도구 추천 (`docs/research/`)
- 영업 자료 9건 (`docs/sales/INDEX.md`)
- 사서 5분 cheat sheet (A4 1장·`docs/sales/librarian-5min-cheatsheet.md`)
- KLA 5.31 발표 outline (15 슬라이드)
- 사서교육원·도서관저널·작은·학교·대학·전문 영업 메일

## 신규 모듈

- `kormarc/application_level.py` — KORMARC 2023.12 M/A/O 자동 판정
- `validator.validate_record_full` — KORMARC + M/A/O 통합 검증
- `librarian_helpers/prefix_discovery.py` — 자관 049 prefix 자동 발견
- `server/portone_webhook.py` — 포트원 v2 webhook stub (ADR 0007 트리거 후)
- `scripts/validate_real_mrc.py` — 자관 .mrc 전수 검증 (cp949 인코딩 자동)
- `scripts/pilot_collect.py` — PILOT 시연 결과 1줄 수집
- `scripts/sales_funnel.py` — 영업 funnel + 페르소나별 결제 전환률
- CLI `kormarc-auto prefix-discover <dir>` (UTF-8 stdout)
- `builder.build_kormarc_record(..., auto_validate=True)`

## 검증

- 292 tests / binary_assertions **34/34** / ruff 0 errors
- aggregator TTL 30일 → 7일 (PO MVP CHAPTER 10 정합)
- /admin/stats sales_funnel 통합

## Cloud Routine

- 매시간 자율 진행 routine 등록 (24/7 자동 commit)
- 매주 월요일 KST 09:00 주간 리뷰 routine

## 5월 임박 ★

- 자관 PILOT 4주 (5/1주~5.31)
- KLA 5.31 전국도서관대회 발표 신청 마감
- 사서교육원·도서관저널·작은·학교·대학·전문 영업 메일 250+ 발송

## PILOT 신청

- 카카오 채널 「kormarc-auto」
- okwhrlgma@gmail.com
- 첫 50건 무료 + 월 3·5·15·30만원 (작은·학교·일반·대규모)
```

---

## 3. Release 후 외부 영업 활용

| 채널 | 활용 |
|---|---|
| 카카오 채널 「kormarc-auto」 | "v0.4.37 정식 발행 — 99.82% 정합" 알림 |
| 네이버·티스토리 블로그 | release notes 본문 → 블로그 글 |
| 도서관저널 기고문 | "GitHub Release v0.4.37 (github.com/okwhrlgma-bit/library/releases)" 인용 |
| KLA 5.31 발표 슬라이드 | S15 마무리에 release URL 노출 |
| 사서교육원 강의 | 수강 사서가 GitHub에서 직접 clone 가능 |
| 작은·학교 영업 메일 | 신뢰도 ↑ (정식 release = 정식 제품) |

---

## 4. 향후 release 계획

| 버전 | 시기 | 핵심 |
|---|---|---|
| **v0.4.37** ★ | **오늘** | 자관 99.82% + 4-Part 매뉴얼 + 영업 패키지 |
| v0.5.0 | 5월 末 | 자관 PILOT 4주 결과 + KLA 발표 슬라이드 |
| v0.6.0 | 6월 中 | 학교·작은·공공·대학·전문 PILOT 10관 결과 |
| v1.0.0 | 사업자 등록 + 포트원 PG 활성 후 | 정식 결제·정식 release |

---

## Sources

- `CHANGELOG_NIGHT.md` v0.4.37 (35+ commit 시리즈)
- `CLAUDE.md §11` 변경 이력
- `docs/sales/INDEX.md` (영업 자료 9건)
- `docs/research/part1~5` (4-Part + Part 5)
- `scripts/binary_assertions.py` (34/34)
