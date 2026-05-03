# Part 94 — 1,447 출처 8 sub-research 통계 (2026-05-03)

> PO 제공 dossier = Part 92 재확인 + 8 sub-research 영역별 출처 1,447개 누적
> Part 92 핵심 결론 = 모두 적용 완료 (commit 994fc0d·2cc81cf)
> 본 Part 94 = 출처 trail 영구 보존 + 잔여 v0.6.0/v0.7.0 권고 백로그 등록

---

## 0. 출처 통계 (1,447 source)

| 출처 | 개수 | 비중 |
|---|---:|---:|
| github.com | 94 | 6.5% |
| namu.wiki | 39 | 2.7% |
| librarian.nl.go.kr | 39 | 2.7% |
| arxiv.org | 38 | 2.6% |
| 기타 | 1,237 | 85.5% |
| **총계** | **1,447** | 100% |

---

## 1. 8 sub-research 영역 (각 출처 수)

| # | 영역 | 출처 | 핵심 결론 (Part 92 정합) |
|---|---|---:|---|
| 1 | 기술 청사진 v0.6.0+ | 146 | VCR cassettes·uv tool·PyApp·prompt caching 80~90% 절감 |
| 2 | 한국 정책·시장 (KOLAS EOL·CSAP) | 190 | 20,000+ 도서관·CSAP 인증 도메스틱 LLM 필수 |
| 3 | Python·결제 stack (PortOne·Toss) | 188 | uv tool 2026 default·PortOne v2 = ₩50M 무료 |
| 4 | UX 트러스트 (ghost text·provenance) | 135 | 시각 provisional·field diff·order matters (anchoring) |
| 5 | KOLAS 2,242·법령 정정 | 156 | KOLAS Ⅲ 2,242관 (1,271 X)·법 §35-3 = PIPA |
| 6 | 12~18개월 first-mover 윈도우 | 213 | KOLAS EOL 시간창·1,271+ 마이그·incumbent 미응답 |
| 7 | 학술 공백 (LLM-KORMARC) | 221 | 2024-2026 한국 LIS 논문 0건·F1 < 0.35 (subject) |
| 8 | 카탈로깅 도구 frustrations | 198 | edit distance·subject manual hell·non-determinism |

---

## 2. Part 92 = 이미 적용 (verify)

| 적용 항목 | commit | 상태 |
|---|---|---|
| 정확도 disaggregation 모듈 | 994fc0d | ✅ `evaluation/accuracy_disaggregation.py` |
| LLM Provider Router (M8·6 provider) | 994fc0d | ✅ `llm/provider_router.py` |
| KOLAS 2,242관 정정 (33 파일) | 994fc0d | ✅ |
| "86% 자원봉사" 정정 (18 파일) | 994fc0d | ✅ |
| CLAUDE.md slim 70줄 | 994fc0d | ✅ |
| fakellm offline mock (30초 데모) | 2cc81cf | ✅ `demo/offline_mock_server.py` |

---

## 3. 잔여 v0.6.0/v0.7.0 권고 (이번 사이클 + 백로그)

### 즉시 적용 (이 사이클)
- ✅ 본 Part 94 보고서
- 🔄 `tests/cassettes/` 디렉토리 + VCR config
- 🔄 `tests/test_property_based.py` (Hypothesis stub·round-trip·idempotence·leader)
- 🔄 `kormarc/provenance.py` (588 auto-stamp + 결정성 fixed seed)

### Phase 2 백로그 (다음 사이클)
- uv tool install canonical (pyproject scripts entry)
- console_scripts (`kormarc-auto demo·serve·update·record` subcommands)
- charmbracelet vhs (.tape 파일 → CI 자동 GIF)
- inline-snapshot 마이그
- HypoFuzz continuous fuzzing
- 8K prompt caching prefix + Batch API
- Anthropic Structured Outputs (Pydantic)
- librarian-judge LLM-as-judge subagent

### v1.0 critical-path
- KWCAG 2.2 conformance (Korean Sense Reader)
- KRDS 디자인 토큰 (Pretendard GOV)
- PortOne v2 Toss·KakaoPay
- PyApp build + Windows 코드 사인
- Reflex/Next.js 마이그 (≥200 concurrent 시)

---

## 4. 출처 trail 보존 (peer review·diligence·학술 발표)

본 Part 94 = 1,447 source·8 sub-research collection의 영구 보존 reference.
v1.0 KOSIM/CCQ peer-reviewed 논문 작성 시 = §7 학술 공백 영역 221 출처 활용 가능.
KLA 부스 발표 시 = §6 first-mover 213 출처 + §1 기술 146 출처 인용.
공공 영업 diligence 시 = §2 정책 190 + §5 사실 정정 156 출처 안전망.

---

## 5. 결론

> **Part 92 dossier 핵심 5건 모두 적용 완료** (994fc0d·2cc81cf push).
> **본 Part 94 = 1,447 출처 영구 보존 + 잔여 v0.6.0 권고 즉시 + Phase 2/v1.0 백로그**.
> **다음 commit = VCR cassettes + Hypothesis property tests + 588 provenance 모듈**.

---

> **이 파일 위치**: `kormarc-auto/docs/research/part94-1447-sources-subresearch-2026-05.md`
> **Part 92 dossier**: `kormarc-auto/docs/research/part92-integrated-dossier-2026-05.md`
> **MCP 통합**: `kormarc-auto/docs/research/part93-data4library-mcp-integration.md`
