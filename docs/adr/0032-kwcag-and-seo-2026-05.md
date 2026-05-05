# ADR 0032 — KWCAG 2.2 + KRDS + SEO + JSON-LD + llms.txt (v0.7.0 종착)

- 상태: Accepted (2026-05-06·갈래 A 종착 + 갈래 B P35 통합)
- 일자: 2026-05-06
- 트리거: 갈래 A 헤더 P7 (KWCAG·KRDS·vhs) + 외부 매출 보고서 P35

## Context

### A. 디지털포용법 §21 + 시행령 §20 (P20)
- 도서관 RFP 접근성 인증마크 요구
- KWCAG 2.2 Level AA = 정식 인증 2년 200~500만원
- 자체 점검 + axe-core 자동 회귀 = 매출 발생 후 정식 인증 검토

### B. 네이버 60-70% 점유 + AI 봇 70-80% (P35)
- C-Rank·D.I.A.·D.I.A.+ 정합 = OG 우선·HTML 메타 등록
- searchadvisor.naver.com 등록·sitemap.xml + RSS
- llms.txt 채택률 10.13% but low-cost 발행
- 진짜 GEO = SoftwareApplication + FAQPage + Organization JSON-LD (76.1% AI 인용 = 구글 Top 10 정합)

## Decision

### 1. `src/kormarc_auto/a11y/` 신설 (P20·v0.7.0 종착)
- `kwcag22.py`
  * 4 원칙 (인식·운용·이해·견고)
  * `color_contrast_ratio()` WCAG 4.5:1 / 3:1 계산
  * `is_korean_lang_attr_present()` <html lang="ko">
  * `audit_html()` 5 핵심 검사 (alt·lang·h1·label·table caption)
  * `audit_kwcag22_text_content()` 시간제한·색상 의존 휴리스틱
  * `A11yReport.is_passing` = critical 0 게이트
- `krds.py`
  * `PRETENDARD_CDN_URL` (jsdelivr·v1.3.9)
  * `KRDS_COLOR_TOKENS` 12종 (Korea blue·amber·green·red·gray)
  * `KRDS_TYPOGRAPHY` (Pretendard·1.6 line height·400/500/700 weight)
  * `color_meaning_matrix()` 3 카테고리 (확실/검토/불확실) + 아이콘 + 한국어 (KWCAG 1.4.1 색상 의존 회피)
- 23 tests passing

### 2. `src/kormarc_auto/seo/` 신설 (P35)
- `jsonld.py`
  * `build_softwareapplication_jsonld()` 5단 Offer KRW 명시
  * `librarian_faq_10()` 10선 (KOLAS III·DLS·880·가격·환각·PIPA·30초 데모·자치구)
  * `build_faqpage_jsonld()` Question·Answer schema
  * `build_organization_jsonld()` sameAs (네이버 블로그·브런치·GitHub)
- `meta_tags.py`
  * `librarian_top_10_keywords()` 검색량·경쟁·우선순위 매트릭스
  * `naver_search_keywords_density()` 홈페이지 키워드 빈도 검증
  * `build_og_tags()` ko_KR locale + canonical 필수
  * `build_robots_txt()` Yeti + GPTBot/ClaudeBot/PerplexityBot Allow (AI 봇 차단 = STOP)
- `llms_txt.py`
  * `build_llms_txt()` 제품 요약 + 핵심 페이지 markdown 링크 + Q&A
- 27 tests passing

### 3. CLAUDE.md 헌법 §12 추가
> 모든 UI = KWCAG 2.2 Level AA·KRDS 색상 토큰·Pretendard CDN

### 4. v0.7.0 종착 갈래 A 7건 완료
- ✅ Cycle 7 STATUS 통합 + 익명화
- ✅ Cycle 8 결정론적 재생성 (P12·ADR 0028)
- 🟡 Cycle 9 1차 audit JSONL (P13·ADR 0029)
- ✅ Cycle 10A Ghost text + per-field (P14·ADR 0029)
- ✅ Cycle 13A 카테고리형 신뢰 (P15·ADR 0030)
- ✅ Cycle 14A visible diff (P16·ADR 0031)
- ✅ Cycle 15A KWCAG + KRDS (P20·ADR 0032·이번)

## Consequences

### Positive
- 도서관 RFP 접근성 인증마크 요구 사전 대응
- 네이버 검색 색인 (Yeti)·AI 인용 (GPTBot/ClaudeBot/Perplexity) 동시 가능
- SoftwareApplication KRW 명시 = ALPAS·Alma 비공개 대비 차별화 무기
- FAQPage 10선 = AI Overviews 인용 친화 (76.1% 구글 Top 10)
- v0.7.0 = 도서관 동료에게 5분 데모 가능 상태 도달

### Negative
- 정식 KWCAG 인증 (2년 200~500만원) = 매출 발생 후
- llms.txt 효과 = 채택률 10.13% = 기대치 낮춤
- vhs GIF = 외부 도구 부재 (Cycle 6 SKIPPED 유지)·PO 수동 설치 후 회복

### Risk Mitigation
- audit_html = critical 0 게이트 = CI에서 회귀 차단
- AI 봇 차단 디렉티브 = STOP 조건 (외부 보고서 P35)
- 색상 의미 매트릭스 = 아이콘 + 텍스트 동시 (1.4.1 색상 의존 회피)

## v0.7.0 Release Plan

### 종착 7건 (갈래 A 헤더 §0)
- [x] STATUS 단일 진실원 (Cycle 7)
- [x] 결정론적 재생성 (Cycle 8 = P12)
- [x] 588 provenance + audit log (Cycle 9 = P13)
- [x] Ghost text + per-field UI (Cycle 10A = P14)
- [x] 카테고리형 신뢰 (Cycle 13A = P15)
- [x] visible diff (Cycle 14A = P16)
- [x] KWCAG 2.2 + KRDS (Cycle 15A = P20·이번)

### v0.7.0 tag 명령
- pyproject 0.6.0 → 0.7.0
- __init__.py 0.6.0 → 0.7.0
- CHANGELOG_NIGHT v0.7.0 항목
- git tag -a v0.7.0 push

### v0.7.0 종착 후 (PO 결정 대기)
A) STOP — PO가 도서관에서 매일 사용하면서 검증
B) 갈래 B production 트랙 (P30 PortOne·P38 자치구)
C) 갈래 A 추가 항목 (T3 Anthropic 최적화·T5 Korean sovereignty)

## Alternatives Considered

### Alt 1: WCAG 2.1 (구버전)
- Reject: KWCAG 2.2 = 한국 표준 + 디지털포용법 정합

### Alt 2: noto-sans-cjk-kr (구글 폰트)
- Reject: Pretendard = 한국 사서 PC 친화·KRDS 표준

### Alt 3: schema.org Product (커머스)
- Reject: SoftwareApplication = SaaS 자연스러움·AI 인용 정합

## References

- 갈래 A 헤더 P7 (KWCAG·KRDS·vhs)
- 외부 매출 보고서 (2026-05-05) §5 + P35
- 디지털포용법 §21 + 시행령 §20
- KWCAG 2.2 (a11ykr.github.io/kwcag22)
- Pretendard CDN (orioncactus·jsdelivr)
- searchadvisor.naver.com (Yeti)
- developers.google.com schema.org SoftwareApplication·FAQPage
- ADR 0028~0031 (Cycle 8~14 정합)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · v0.7.0 종착 사이클
