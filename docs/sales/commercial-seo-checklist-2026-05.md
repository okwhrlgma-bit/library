# 상업성 · 검색 가시성 체크리스트 (Cycle 61·8 페르소나 정합)

> PO 명령 (2026-05-06): "상업적·검색 잘되게·여러 가지 추가로 따져야".
> 이미 박제 (Cycle 11~16·18B) = 코드 scaffolding·**실 발행 0건** = 활성 가속 필요.

## 1. 상업성 매트릭스 (10 영역)

| 영역 | 코드 상태 | 활성 상태 | 차단점 |
|---|---|---|---|
| 가격 4 플랜 (P31·Cycle 11) | ✅ | ❌ | 사업자 등록 |
| 결제 PortOne v2 (P30) | ⏳ scaffold | ❌ | 사업자 등록 |
| 세금계산서 자동 (B2B) | ✅ scaffold | ❌ | PortOne 라이브 |
| Founding Member 영구 50% | ✅ scaffold | ❌ | 결제 라이브 |
| 권당 200원 alt 모델 | ✅ scaffold | ❌ | 결제 라이브 |
| 자치구 묶음 (P38·Cycle 16B) | ✅ | ❌ | 사업자 등록 |
| 학교장터 s2b.kr 등록 | ⏳ | ❌ | 사업자 등록 |
| 디지털서비스몰 등록 | ⏳ | ❌ | CSAP 인증 |
| KLMA·KLA 회원 | ⏳ | ❌ | 즉시 가능 (회비 ₩50K) |
| 도서관 백서 광고 (₩200K/page) | ⏳ | ❌ | 매년 12월 |

→ **활성 1순위 = 일반과세자 등록** (모든 차단 1차 해소).

## 2. 검색 가시성 매트릭스 (12 영역)

| 영역 | 코드 (Cycle) | 활성 | 차단점 |
|---|---|---|---|
| JSON-LD SoftwareApplication (P35·Cycle 15B) | ✅ | ❌ | 도메인·랜딩 |
| JSON-LD FAQPage 10선 | ✅ | ❌ | 랜딩 발행 |
| JSON-LD Organization sameAs | ✅ | ❌ | SNS 연결 |
| OG meta tags (네이버 60-70%) | ✅ | ❌ | 랜딩 발행 |
| robots.txt (Yeti·GPTBot·ClaudeBot Allow) | ✅ | ❌ | 도메인 |
| llms.txt (LLM 친화 사이트맵) | ✅ | ❌ | 도메인 |
| 네이버 SEO (C-Rank·D.I.A.+) | ⏳ scaffold | ❌ | 블로그 0건 |
| 네이버 블로그 발행 (P36·Cycle 16A) | ✅ scaffold | ❌ | 콘텐츠 0건 |
| 브런치·LinkedIn·Medium | ⏳ | ❌ | 콘텐츠 0건 |
| AEO (ChatGPT·Claude 인용) | ✅ scaffold (P40) | ❌ | 인용 측정 0건 |
| KOLAS3 카운트다운 PR (Cycle 12 P37) | ✅ | ❌ | 플래텀·벤처스퀘어 미발행 |
| 사서 카페 (Daum·Naver) | ⏳ | ❌ | 가입·발행 0건 |

## 3. 사서 페르소나별 SEO 키워드 (8 ICP 정합)

| 페르소나 | 1순위 키워드 | 2순위 |
|---|---|---|
| P1 작은도서관 | "작은도서관 KORMARC 자동" | "자치구 도서관 SaaS" |
| P2 학교 사서교사 | "학교도서관 KORMARC" | "자료구입비 3% 효율" |
| P3 공공 계약직 | "KOLAS III 종료 마이그레이션" | "공공도서관 SaaS" |
| P4 대학도서관 | "대학도서관 RDA MODS" | "ProQuest 대체 국산" |
| P5 자관 PO | "사서 KORMARC 자동" | "자관 양식 KOLAS" |
| P6 자원봉사 | "도서관 자원봉사 카탈로깅" | "사서교사 보조" |
| P7 책나래 | "책나래 책이음 통합" | "장애인 도서관 SaaS" |
| P8 도서관장 | "도서관장 KPI 대시보드" | "사서 야근 줄이기" |

→ 키워드 16건·블로그 시드 16개 가능 (Cycle 65+ 발행).

## 4. 도서관 시장 검색량 (외부 매출 보고서 정합·추정)

| 키워드 | 월 검색량 (네이버) | 경쟁 |
|---|---:|---|
| KORMARC | 800~1,200 | 낮음 |
| KOLAS | 2,000~3,000 | 낮음 |
| 도서관 자동화 | 1,500~2,500 | 중간 |
| 작은도서관 | 5,000~8,000 | 낮음 |
| 학교도서관 | 8,000~12,000 | 중간 |
| 공공도서관 SaaS | 100~300 | 낮음 (블루오션) |

→ **"공공도서관 SaaS"·"KORMARC 자동" = 우리가 1순위 진입 가능**.

## 5. 즉시 가능 (PO 외부 작업 0건·이번 사이클 내)

1. ✅ **JSON-LD 8 페르소나 분기** = streamlit_app·FastAPI /landing 자동 inject
2. ✅ **블로그 콘텐츠 시드 16개** = `docs/blog/seed-titles-2026-05.md`
3. ✅ **PR 보도자료 시드 5개** = `docs/sales/pr-templates-2026-05/`
4. ✅ **사서 카페 가입 + 발행 첫 1편** = PO 외부 작업 (1시간)

## 6. 도메인·랜딩·SNS (PO 외부 작업·1주)

1. **도메인 등록**: `kormarc-auto.kr` 또는 `mark.lib.kr` (가비아·₩30K/년)
2. **랜딩 발행**: GitHub Pages·Vercel 무료·streamlit_app 직접 노출
3. **SNS 신설**:
   - 네이버 블로그 (사서·도서관 SEO·C-Rank 보호)
   - 브런치 (전문성·long-form)
   - LinkedIn 영문 (외국 도서관·국제 확장 시드)
   - YouTube (5분 데모·KOLAS3 카운트다운)
4. **사서 카페 가입**:
   - 한국도서관협회 카페 (1만명)
   - 사서끼리 (Daum·Naver·5천명)

## 7. 발행 시작 시점

| 자료 | 시점 | 사이클 |
|---|---|---|
| JSON-LD 자동 inject | 즉시 | Cycle 61 (이번) |
| 블로그 시드 16개 | 즉시 (markdown) | Cycle 61 (이번) |
| 도메인 등록 | PO 외부 (1일) | Cycle 65+ |
| 랜딩 발행 | PO 외부 (3일) | Cycle 65+ |
| 첫 블로그 발행 | PO 외부 (1주) | Cycle 65+ |
| KOLAS3 PR 발행 | D-200 (2026-06-15) | Cycle 70+ |
| 도서관 백서 광고 | 2026-12 | Cycle 90+ |

## 8. 측정 (P40 AEO·이미 모듈 있음)

```bash
python -c "
from kormarc_auto.geo import STANDARD_QUERIES, parse_citation_response
print('기준 쿼리:', len(STANDARD_QUERIES))
"
```

→ Cycle 70+ (Phase 2·Anthropic API 키 발급 후) cron 활성.

## 9. 정직 헤더

- 검색 가시성 = **scaffolding·발행 0건** = 코드만 있고 실 효과 X
- 활성 = PO 외부 작업 = 도메인·랜딩·SNS·블로그 = 1주 시간
- **사서 인터뷰 5명 = 검색·메시지 가설 검증 = 우선순위 1위**

→ Cycle 61 = 매트릭스 박제·**활성 = PO 외부 작업 후 Cycle 65+**.
