# ADR 0033 — 블로그 파이프라인 + 자치구 묶음 영업 자동화

- 상태: Accepted (2026-05-06·Cycle 16A + 16B 통합)
- 일자: 2026-05-06
- 트리거: 외부 매출 보고서 P36 (블로그) + P38 (자치구 묶음)

## Context

### A. 블로그 다채널 발행 = 100% 자동 불가 (P36)
- 네이버 블로그 OAPI 신규 발급 제한·Selenium 임시저장만 (publish 자동 = 약관 위반)
- 브런치 외부 API 미공개·클립보드 paste만
- 티스토리 API 사실상 종료
- WordPress·LinkedIn·Medium = 자동 가능
- canonical URL = 자체 블로그 원본·67% 채택 (2025 SEO Web Almanac)

### B. 자치구·교육청 묶음 = 객단가 5-25x 점프 (P38)
- 25관 자치구 묶음·100관 교육청 = 월 600-700만원 → 1.1억+ 견적
- 디지털서비스 이용지원시스템 + 디지털서비스몰 카탈로그 등재 필수
- KG이니시스 가상계좌 + 팝빌 전자세금계산서 = B2B 표준
- 클라우드컴퓨팅법 §20 (SaaS 우선 도입) 인용 = 영업 무기

## Decision

### 1. `src/kormarc_auto/blog_pipeline/` (P36)
- `canonical.py`
  * `BlogPost` dataclass·`extract_frontmatter()` YAML 파싱
  * `add_canonical_footer()` 채널별 본문 끝 출처 첨부
  * `build_canonical_html()` rel=canonical + ko_KR + OG 자동
- `intro_paraphraser.py`
  * `levenshtein_ratio()` 편집 거리 비율
  * `measure_paraphrase_strength()` 30%+ 게이트 (네이버 C-Rank 중복 페널티 회피)
- `fact_checker.py`
  * `KOLAS3_EXPECTED_FACTS` (end_date·scope·successors·libraries 1296)
  * `check_post_facts()` 5 STOP 조건 (종료일 1글자 변경·확장형 종료·후속 4종·도서관 수)
- 15 tests passing

### 2. `src/kormarc_auto/sales/bundle_quote.py` (P38)
- `BundleQuote` dataclass·`to_quote_dict()` 견적 JSON
- `generate_bundle_quote()` = billing.calculate_quote 통합 + 법적 근거 자동
  * 5/10/25/100관 묶음 = 10/15/20/25%
  * `is_simplified_tax_payer=True` = ValueError (학교 거래 차단)
- `_legal_basis_for()` = 클라우드컴퓨팅법 §20 (public·enterprise) + 지방계약법 §25/§30 (분관 수)
- `render_quote_markdown()` 견적서 markdown (PDF 변환 전)
- `build_procurement_pack_index()` = 디지털서비스몰 등재 16 문서
- 18 tests passing

### 3. STOP 조건 박제 (외부 보고서 P36·P38 정합)
- 네이버 publish 자동 = STOP·약관 위반·계정 차단 위험
- KOLAS III 종료일 1글자 변경 = STOP (사실확인 게이트)
- 간이과세자 청구 = ValueError·세금계산서 발급 불가 = 학교 거래 봉쇄
- CSAP 미인증 + "공공 SaaS" 표기 = 허위표시 위반

## Consequences

### Positive
- 자체 블로그 원본 + 다채널 cross-post = 1 source 4 channel
- 사실확인 게이트 = KOLAS III 종료일 회귀 차단
- 자치구 25관 견적 = 1.1억+ 자동 산출
- 디지털서비스몰 등재 16 문서 인덱스 = ZIP 패키지 자동 빌드 가능

### Negative
- 네이버·브런치 publish 자동 X = PO 수동 step 필요 (약관 회피)
- LinkedIn·Medium 자동 = OAPI 키 관리 (P30 PortOne·P40 LLM 비용 vs)
- 견적서 PDF 변환 = reportlab 의존 (Cycle 17+ 추가)

### Risk Mitigation
- intro paraphraser 30% 게이트 = 네이버 C-Rank 중복 페널티 차단
- fact_checker 5 STOP 조건 = 사실 오류 사전 차단
- bundle_quote ValueError = 간이과세자 시도 즉시 차단

## Plan B 큐 갱신 (Cycle 16 후)

| Cycle | P | 상태 |
|---|---|---|
| 16A | P36 블로그 파이프라인 | ✅ |
| 16B | P38 자치구 묶음 영업 | ✅ |
| 17+ | P30 PortOne sandbox (사업자 등록 후) | 대기 |
| 17+ | P32 데모 onboarding 5분 위저드 | 부분 |
| 17+ | P39 사서어 매핑 (KLA 5/31 후) | 부분 |
| 17+ | P40 LLM GEO + 인용 모니터링 | 대기 |

## Alternatives Considered

### Alt 1: GitHub Actions로 네이버 자동 발행
- Reject: 네이버 약관 위반·계정 차단·임시저장만 자동·publish 수동

### Alt 2: 견적서 직접 PDF 생성 (reportlab)
- Reject: markdown 우선·Cycle 17+ 추가 (PO 디자인 결정 후)

### Alt 3: 간이과세자 모드 지원
- Reject: 세금계산서 불가 = 학교 거래 0건·기능 제공 시 PO 등록 실수 유도

### Alt 4: 100% 영문 블로그 (글로벌)
- Reject: 한국 도서관 = 한국어 우선·LinkedIn만 영문 자동

## References

- 외부 매출 성장 보고서 (2026-05-05) P36 + P38
- 2025 SEO Web Almanac (canonical 67% 채택)
- 디지털서비스 이용지원시스템 (digitalmarket.kr)
- 클라우드컴퓨팅법 §20·지방계약법 §25/§30
- ADR 0026 한국 SaaS 결정 (간이과세자 차단 정합)
- ADR 0029·0031 (PIPA 처리방침 정합)
- ADR 0032 (KWCAG·SEO 정합)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · 갈래 B 사이클
