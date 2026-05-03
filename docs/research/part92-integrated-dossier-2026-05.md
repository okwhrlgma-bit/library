# Part 92 — kormarc-auto v0.6.0+ Integrated Research Dossier (2026-05-03)

> PO 제공 deep research dossier (4 영역·100+ 출처).
> 핵심 = 정확도 disaggregation·CSAP·KOLAS 2,242·CLAUDE.md slim·v0.7→v1.0 로드맵.

---

## 0. 한 줄 결론

> **99.82% 단일 정확도 = 불가검증·peer review 미통과 위험.** MARC block별 분리 + eval corpus v1 즉시 발행.
> **CSAP + 도메스틱 LLM 추상화 = 공공 영업 unblock 필수** (Anthropic-only = 공공 deathline).
> **KOLAS Ⅲ 2026-12-31 EOL = 12~18개월 first-mover 윈도우** (incumbents OEM 응답 예상).

---

## 1. 즉시 정정 5건 (Highest leverage·Lowest cost)

### 1.1 정확도 99.82% 분리
- 현재 = 단일 number 마케팅 → peer review·diligence 미통과
- 정정: descriptive (245/250/260/300/020·ISBN-grounded) vs subject (6XX·F1 0.35~0.79) vs full-record 분리
- 근거: SemEval-2025 Task 5 (F1@5 < 0.35), KoBERT-NLSH 2023 (micro-F1 0.6059), Yang & Zhang 2025 (F1 0.7920 cover)

### 1.2 사실 정정
| 항목 | 잘못 | 정정 |
|---|---|---|
| KOLAS Ⅲ 2,242관 | **2,242관** (NL Korea 사용도서관 현황) |
| 1,271 = | KOLAS 설치 | 2023년 공공도서관 총수 (2025=1,328) |
| 학교 사서교사 배치 | 13.9% | **16.16%** (2025·진선미 의원실)·공무직 포함 ~57% |
| "정규 사서교사 미배치 84% (공무직·기간제 포함 시 48~57% 배치)" | 단순 | "정규 사서교사 미배치 ~84%·공무직·기간제 포함 시 48~57% 배치" |
| 도서관법 §35-3·§36 | Library Act | **PIPA §35의2·§36** (2024-03-15 시행) |
| 도서관법 §21 납본 | 옛 번호 | **§23** (2021-12-07 전부개정 후) |
| KOLAS 종료 후 | "보급 종료" | 2026-12-31 EOL·KOLAS-WEB 오픈소스 (2021-12-14)·시장 주도 마이그 |

### 1.3 CLAUDE.md slim
- 현재 240줄 → **<60줄 권장** (HumanLayer empirical ceiling 150~200·Claude Code system prompt이미 50)
- 분할: agent_docs/{kormarc_field_reference·running_evals·vcr_recording·release_process}.md

### 1.4 LLM 추상화 (M8) = 공공 영업 unblock
- DPG 가이드라인 2.0 (2025-04) + PIPC 생성형 AI 안내서 (2025-08) = api.anthropic.com 행정망 차단
- **AWS Bedrock Seoul (ap-northeast-2)** = CSAP 인증·Claude 사용 가능 (Anthropic 직접 X)
- 추가: HyperCLOVA X (Naver)·KT 믿:음·LG EXAONE·Azure OpenAI Korea Central
- v1.0 critical-path = polish X

### 1.5 KLA 학술 발표 (Part 86 → docs/academic/)
- 한국 LIS 저널 = **LLM-driven KORMARC 자동화 학술 논문 0건** (2024-2026)
- → 정보관리학회지 (KOSIM) 또는 Cataloging & Classification Quarterly 투고 = 시장 공백 점유

---

## 2. 4 영역 핵심 발견

### A. 기술·구현 (v0.6.0+)
- **uv tool install** = 2026 default (pipx fallback)·PyApp self-update
- **fakellm/mockllm + pytest-recording** = "30초·API 키 X" 데모 표준
- **Hypothesis + HypoFuzz** (2025-11) + Anthropic agentic property-based testing (arXiv 2510.09907)
- **inline-snapshot + syrupy** = pymarc bad_*.dat 차용
- **Claude prompt caching + Batch API** = 95% off 가능·8K 안정 prefix 권장
- **Agent Skills** (Oct 2025) = .claude/skills/kormarc-build/ 권장
- **Anthropic Routines** (cloud-hosted) + git worktrees + agent/* namespace

### B. 경쟁 환경
- **국내 = AI KORMARC 벤더 0건** (다인·이씨오·미래누리·INEK 모두 미발표)
  - ALPAS·이젠터치·KLAS·TULIP+ = 150~1,200관 customer base
- **MarcEdit** = 무료 워크호스·LLM native X
- **OCLC Connexion + WorldShare AI** (2025-12-08 launch) = 권당 20분 절감 마케팅
- **Alma AI Metadata Assistant** = MARC21 + LCSH·**한국어/KORMARC 미지원**
- **MDPI Publications 14:1:19 (2026)** "CNMARC 4-Agent" = 가장 가까운 학술 선행
- **SemEval-2025 LLMs4Subjects**: F1@5 < 0.35 (subject)
- **Korean BERT-NLSH 2023**: micro-F1 0.6059
- **Annif 1.0** = OSS·SemEval 1위·KDC fine-tune 가능 = 컴포넌트 후보

### C. UX·온보딩
- **Linear·Stripe·Notion·Vercel·Figma** = 7 화면 이내·sandbox-as-onboarding
- **Toss TDS** = "One Page One Thing"·"Easy to Answer"·해요체
- **트러스트 UX 합의 (2024~2026)**: provenance chips > confidence percentages
- **Ghost text + per-field accept/reject** (Copilot/Cursor pattern)
- **Categorical risk tiers** (확실/검토/불확실) > raw probability
- **Order matters** = 라디오 자동화 편향 (arXiv 2205.09696)·고위험 필드 = librarian-first
- **PCC 588 provenance** = AI 카탈로깅 표준화 (2024·revised 2025)

### D. 한국 시장·정책
- **KOLAS Ⅲ EOL 2026-12-31** 확정 (NL Korea 2026-01 통지)
- **CSAP**: api.anthropic.com 행정망 차단·Bedrock Seoul만 안전
- **NIPA AI 바우처**: 도서관 = 직접 수혜자 X·기업 consortium 통해 수요기업
- **NL Korea 자체 AI** (포티투마루·바이브컴퍼니·AI 실감서재) = 직접 경쟁 위험·학교/작은/대학/personal 우회
- **License-risk** (SNU 기계공학부 2025): publication-text 절대 LLM 송신 X = "메타데이터 only" 마케팅
- **사서 PMF 신호**: 카페 비공개·인터뷰 5~8명 필요·KLA 학술대회 부스

---

## 3. v0.6.0 → v0.7.0 → v1.0.0 로드맵

### v0.6.0 (highest-leverage·lowest-cost)
- demo subcommand + fakellm 번들 (30초 데모)
- uv tool install canonical
- pytest-recording cassettes + --block-network CI
- inline-snapshot + syrupy + Hypothesis
- charmbracelet vhs (quickstart.tape·cli.tape)
- README 정확도 disaggregation
- 사실 정정 5건 (KOLAS 2,242·법령·86%)
- CLAUDE.md slim <60줄
- .claude/skills/kormarc-build/

### v0.7.0 (credibility)
- **kormarc-eval-corpus-v1** (1,000 records 공개)
- prompt caching 8K prefix + Batch API
- Structured Outputs (Pydantic schemas)
- 결정적 regeneration (fixed seed·visible diff)
- 588 provenance 자동 stamp
- Persona-segmented onboarding (1 question·sandbox)
- 테스트 모드 sentinel ISBNs
- Ghost text + per-field accept/reject
- Categorical risk tiers + provenance chips
- OCR-then-vision sandwich (CLOVA OCR/Upstage)
- fastapi-users magic-link + slowapi + structlog
- Anthropic Routines + agent/* worktree namespace

### v1.0.0 (public-deployment)
- **M8 LLM 추상화** (Bedrock + HCX + 믿:음 + EXAONE)
- KWCAG 2.2 conformance
- KRDS 디자인 토큰 (Pretendard GOV·Korea blue)
- Reflex/Next.js 마이그 (≥200 concurrent·SAML·KRDS·KWCAG fail 시)
- PortOne v2 (Toss·KakaoPay)
- PyApp self-update + Windows 코드 사인
- KOSIM 또는 CCQ peer-reviewed 논문
- KOLAS-successor SI OEM 포지셔닝 (이씨오·두드림·다인·미래누리)

---

## 4. 위험 매트릭스 (확률·영향 가중)

| 위험 | 확률 | 영향 | 시간창 | 대응 |
|---|---|---|---|---|
| **99.82% 정확도 붕괴** | High | High | 즉시 | v0.6.0 disaggregation + v0.7.0 eval corpus |
| **CSAP 공공 차단** | High | High (공공) | 즉시 | M8 LLM 추상화·Bedrock Seoul |
| **Incumbent SI OEM 응답** | Medium | High | 12~18개월 | KDC+NLSH+determinism+provenance moat·OEM 포지셔닝 |
| **NL Korea 직접 경쟁** | Medium | High | 12~24개월 | 학교/작은/대학/personal segment 우회 |
| **License-risk 사고** | Medium | Medium | 즉시 | 메타데이터 only 명시·audit log |
| **Streamlit 생산 한계** | Medium | Medium | 12개월 | Reflex/Next.js 마이그 plan·v0.8 ready |
| **결정성 실패 공개** | Medium | Medium | 6개월 | v0.7.0 fixed seed·visible diff |
| **Solo + agent 회귀** | Medium | Medium | 항상 | branch protection·eval corpus gate |
| **Anthropic 가격·정책** | Low-Med | High | 6~18개월 | M8 추상화 = 동일 mitigation |
| **AhnLab false positive** | Low-Med | Medium | 즉시 | code sign 인증서 (~$200/yr) |

---

## 5. PO 외부 작업 갱신 (사용자_TODO)

추가:
- **U-API-6**: AWS Bedrock Seoul (ap-northeast-2) 계정 = CSAP 인증·Claude 사용
- **U-API-7**: Naver HyperCLOVA X 키 (도메스틱 LLM·공공)
- **U-API-8**: Upstage Document Parse (한국어 OCR·OCR-then-vision sandwich)
- **U-NEW-16**: Windows 코드 사인 인증서 (~$200/yr·v1.0 전)

---

## 6. 헌법 정합성

- §0 사서 시간: ↑↑↑ (모든 v0.6.0+ 항목 정합)
- §12 결제 의향: ↑↑↑ (정확도 신뢰성·CSAP·OEM·KOLAS 시간창)
- Q5 컴플: PASS (CSAP·license-risk·provenance·KWCAG)
- Over-engineering: 0건 (v0.6.0 = 모두 highest-leverage)

---

## 7. 출처 (deep research 100+ 검증)

웹 검증 주요 (PO dossier §Appendix):
- Anthropic platform.claude.com (pricing·caching·structured outputs·skills·routines)
- Astral uv·PyApp·Charmbracelet vhs·Hypothesis·HypoFuzz
- arXiv 2510.09907 (Anthropic agentic property-based testing)
- pytest-recording·vcrpy·inline-snapshot·syrupy
- MDPI Publications 14:1:19 (2026 4-agent CNMARC)
- arXiv 2504.07199·2504.19675·2504.21589 (SemEval-2025 LLMs4Subjects)
- Cataloging & Classification Quarterly 62(5)·C&RL News 2025·CILIP CI 211
- 정보관리학회지 39(3)·KCI ART002961357 (BERT-NLSH 2023)
- NL Korea KOLAS Ⅲ EOL 2026-01 통지·사용도서관 현황 2,242
- 디지털플랫폼정부 가이드라인 2.0 (2025-04-16)
- 개인정보보호위원회 생성형 AI 안내서 (2025-08-06)
- 도서관법 전부개정 (2021-12-07·법률 제18547호)·PIPA §35의2 (2024-03-15)
- KS X 6006-0 (2023-12) KORMARC 통합서지용
- 교육부 제4차 학교도서관 진흥 기본계획 2024-2028
- KESS 2024·진선미 의원실 2025·ZDNet Korea 2026-04-24
- ELUNA 2025·Code4Lib 2025·MLA cataloging committee Mar 2025
- KRDS·KWCAG 2.2·Toss TDS·Pretendard GOV
- Linear·Stripe·Notion·Vercel·Figma·Spellbook·Harvey·CoCounsel·Cursor

---

> **이 파일 위치**: `kormarc-auto/docs/research/part92-integrated-dossier-2026-05.md`
> **다음 commit**: 사실 정정 + 정확도 disaggregation + CLAUDE.md slim + LLM 추상화 stub
