# AEO + GEO 전략 (검색 + AI 인용) — Cycle 61

> PO 명령 (2026-05-06): "검색이나 AI가 잘 찾게 만드는 법 있다던데?"
> 답: ✅ 이미 모듈 박제 (Cycle 15B SEO·Cycle 18B P40 GEO)·**활성 = PO 외부 작업 후**.

## 1. 3 가지 가시성 (개념)

| 영역 | 대상 | 측정 |
|---|---|---|
| **SEO** | 네이버·구글 검색 결과 | 키워드 순위 (1~10위) |
| **AEO** (Answer Engine Optimization) | 검색 결과 페이지 답변 박스·Featured snippet | 답변 박스 차지율 |
| **GEO** (Generative Engine Optimization) | ChatGPT·Claude·Perplexity LLM 답변 | LLM 인용 횟수 |

→ **셋 다 = 3 다른 최적화·우리는 모두 박제됨**.

## 2. 우리 SaaS 적용 매트릭스 (Cycle 15B + 18B)

### 2-A. SEO (네이버 60-70% 점유)
- ✅ JSON-LD SoftwareApplication·FAQPage·Organization (P35·`seo/jsonld.py`)
- ✅ OG meta tags ko_KR (`seo/meta_tags.py`)
- ✅ robots.txt = Yeti·GPTBot·ClaudeBot Allow (`seo/meta_tags.py`)
- ✅ 사서 키워드 매트릭스 16건 (Cycle 61 본 doc)

### 2-B. AEO (구글 답변 박스)
- ✅ Answer-first 첫 단락 40-60단어 + 정의문 (`geo/answer_first.py`)
- ✅ 통계 밀도 = 150-200단어마다 1개 (76.1% AI 인용 = 구글 Top 10)
- ✅ FAQPage JSON-LD = 10 사서 FAQ (KOLAS III·DLS·880·가격·환각·PIPA)

### 2-C. GEO (LLM 답변 인용)
- ✅ llms.txt 발행 (Search Engine Land 2025·채택률 10.13%)
- ✅ 표준 쿼리 10개 = 주 1회 베이스라인 측정 (`geo/citation_monitor.py`)
- ✅ ChatGPT·Claude·Perplexity·Gemini·Copilot 5 LLM 추적
- ⏳ 비용 캡 ($50/월) = Phase 2 (Anthropic API 키 후 활성)

## 3. AI가 우리를 잘 찾게 하는 6 원칙 (외부 256 출처 V3 §4 + 매출 보고서 P40)

### 원칙 1. Answer-First (40-60단어 정의문)
```
❌ "kormarc-auto는 다양한 기능을 제공하는 SaaS입니다..."
✅ "kormarc-auto는 한국 도서관 사서가 ISBN을 입력하면 5초 안에 KORMARC .mrc 파일을
    자동 생성하는 SaaS입니다. KOLAS III·독서로 DLS·알파스 즉시 반입 호환."
```
→ LLM이 첫 단락만 읽고도 정확히 인용 가능.

### 원칙 2. 통계 밀도 = 150-200단어마다 1 통계
- "1,296 공공도서관 + 12,200 학교도서관"
- "권당 8분 → 2분 (Part 49 시뮬 56% 전환)"
- "자관 174 파일 round-trip 100%"
- "KOLAS III 종료 = 2026-12-31 (D-238)"

→ **인용 가능한 사실 = LLM 인용 +76.1%** (외부 매출 보고서 §A).

### 원칙 3. JSON-LD 구조화 데이터
- SoftwareApplication = 가격 5단·offer KRW 명시 (ALPAS·Alma 비공개 대비 차별화)
- FAQPage = 10 사서 FAQ (LLM 학습 친화)
- Organization sameAs = 네이버 블로그·LinkedIn·브런치 연결

### 원칙 4. llms.txt (LLM 친화 사이트맵)
```
# kormarc-auto
> 한국 도서관 KORMARC 자동 생성 SaaS

## 핵심
- [기능 매트릭스](/features.md)
- [가격 4 플랜](/pricing.md)
- [KOLAS III 종료](/migration/kolas3.md)

## 신뢰
- 자관 PILOT 1관·174 파일·round-trip 100%
- v0.7.1·1,186 tests·ADRs 0024~0044
```

### 원칙 5. robots.txt LLM Allow
```
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Yeti  # 네이버
Allow: /
```
→ LLM 학습·인용 가능 = 인용 시 우리 사이트 link.

### 원칙 6. AI 인용 모니터링 (cron)
```bash
# 주 1회·5 LLM·10 표준 쿼리 = 50 측정
python -c "
from kormarc_auto.geo import STANDARD_QUERIES, parse_citation_response
for q in STANDARD_QUERIES:
    # ChatGPT·Claude·Perplexity·Gemini·Copilot 5 LLM 호출
    # 응답 → parse_citation_response → 우리 인용 여부 추출
    pass
"
```
→ **인용율 baseline 측정 후 콘텐츠 개선 사이클**.

## 4. 사서 페르소나 × AEO/GEO (8 ICP)

| 페르소나 | LLM 검색 시 query | 우리 인용 가능성 |
|---|---|---|
| P1 작은도서관 | "작은도서관 마크 자동 만드는 법" | 🟢 자관 양식 + KOLAS III |
| P2 학교 사서교사 | "학교도서관 KORMARC 자료구입비 3%" | 🟢 학교 자료 정합 |
| P3 공공 계약직 | "KOLAS III 종료 후 어떻게?" | 🟢 D-238 카운트다운 |
| P4 대학도서관 | "RDA MODS 한국 SaaS" | 🟡 학술 모듈 부분 |
| P5 자관 사서 | "자관 양식 KOLAS 통합" | 🟢 6년 NPS 인용 |
| P6 자원봉사 | "도서관 자원봉사 카탈로깅 도구" | 🟢 단순 모드 (Cycle 65 후) |
| P7 책나래 | "책나래 책이음 통합 SaaS" | 🟢 5종 통합 |
| P8 도서관장 | "사서 야근 줄이는 법" | 🟢 KPI 대시보드 |

## 5. 즉시 적용 (PO 외부 작업 0건·이번 사이클)

1. ✅ JSON-LD 자동 inject (FastAPI `/seo` endpoint·streamlit_app)
2. ✅ Answer-first 첫 단락 = 모든 페이지 60단어 정의문
3. ✅ 통계 박스 = "1,296·12,200·D-238·100%·1,186" 5 사실 매 페이지
4. ✅ 본 doc 박제

## 6. PO 외부 작업 (1주)

1. **도메인 등록** (`kormarc-auto.kr`·₩30K/년)
2. **랜딩 발행** (GitHub Pages 무료)
3. **llms.txt 발행** (`/llms.txt`·정적 파일)
4. **robots.txt 발행** (`/robots.txt`·LLM Allow)
5. **JSON-LD 발행** (랜딩 head 자동 inject)
6. **네이버 서치어드바이저 등록** (sitemap.xml + 도메인 인증)
7. **구글 서치 콘솔 등록** (sitemap.xml)
8. **첫 블로그 1편** (KOLAS III D-238 카운트다운·외부 보도자료 정합)

## 7. AI 인용 측정 cron (Phase 2)

```bash
# .github/workflows/aeo-citation-cron.yml (Phase 2 활성)
# 매주 일 03:00 KST = 50 측정 → 인용율 변화 알림
```

→ Cycle 70+ (Anthropic API 키 발급 후·비용 $50/월).

## 8. 정직 헤더

- **모든 모듈 박제됨·발행 0건** = scaffolding·실 효과 0
- 활성 = PO 외부 작업 (도메인·랜딩 등록·블로그 발행) = 1주 시간
- **인용율 baseline 측정 = Phase 2 (API 키 후) = 1개월+ 데이터 후 의미**

→ **검색·AI 가시성 = 코드 0%·발행 100%·인내 1~3개월**.
