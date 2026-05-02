# Part 86 — 유사 자동화·논문 조사 (2026-05-03)

> PO 질문: "우리가 하고있는 자동화와 유사한 아웃풋이나 논문 등이 있을까?"
> 11종 도구 + 6건 학술/특허 + 위협도 + USP + 협력 후보 + 학습 포인트
> 자체 조사 (general-purpose subagent web 24 tool calls)

---

## 0. 결론 한 줄

> **국내 KORMARC 자동 생성 SaaS 학술·상용 선행 연구는 사실상 공백.**
> MarcAI = 한국어/KORMARC X · OCLC = 한국 미진입 · KOLAS·DLS = 자동 생성 X.
> kormarc-auto = **3중 공백 점유 유일 솔루션** + KOLAS 종료 골든타임 정렬.

---

## 1. 글로벌 자동화 도구·서비스 (7건)

| # | 이름 (기관) | 유사점 | 차별점 | 위협도 |
|---|---|---|---|---|
| G1 | **MarcAI** (libmatic.com) — 사진/PDF/텍스트 → MARC21·UNIMARC, Koha 1-click, 크레딧 | 입력 모달리티 동일·AI SaaS | **KORMARC X·한국어 X·KOLAS·DLS X**·크레딧제·KS X 6006 미검증 | **HIGH** |
| G2 | **OCLC WorldShare + Connexion AI** (2025-12) | 카피 카탈로깅·AI DDC/LCC/LCSH·1건 20분 절감 | KORMARC X·KDC X·NLK 주제명 X·구독료 高·한국 채택 거의 0 | **MID** |
| G3 | **MarcEdit** (Terry Reese, OSU) | MARC 편집·변환·OAI·BIBFRAME↔MARC | **데스크톱 GUI**·SaaS X·KORMARC 프로파일 X·1인 비개발자 부적합 | **LOW** |
| G4 | **LC BIBFRAME / Marva** (2025-01 프로덕션·Conv 3.0 2025-12) | 서지 자동 변환 도메인 | KORMARC 무관·BIBFRAME 2.0 LD 전환·SaaS X·한국 시기 미정 | **LOW** |
| G5 | **Annif / Finto AI** (NLF 핀란드·OSS) | Tensorflow·fastText·spaCy 자동 주제명, 독일·스웨덴·폴란드 채택 | **주제명 색인만**·KDC X·KCR4 X·자체 운영 부담 | **LOW (협력)** |
| G6 | **Liblime Koha + AI** (2025) | OSS LMS + AI HITL | LMS 자체·자동 KORMARC X·예산 62% 채택 장벽 자체 보고 | **LOW** |
| G7 | **MARCmin Alpha** (yeschat.ai GPT) | LLM 기반 MARC 초안 | 알파·MARC21 only·KORMARC X·신뢰도 미검증 | **LOW** |

---

## 2. 한국 자동화 도구·API (4건)

| # | 이름 | 유사점 | 차별점 | 위협도 |
|---|---|---|---|---|
| K1 | **NLK ISBN 서지 Open API** | ISBN → 서명·저자·페이지·키워드 무료 | **원천 데이터**일 뿐·자동 KORMARC X | **LOW (협력)** |
| K2 | **도서관 정보나루 Open API** | 17 API·도서 상세·인기·키워드 | 분석·통계 중심·KORMARC 출력 X | **LOW (협력)** |
| K3 | **알라딘 Open API** (5,000회/일 무료) | 표지·저자·판차·가격 | 상업 카탈로그·KORMARC X·학술 부족 | **LOW (협력)** |
| K4 | **KOLAS III·DLS·KLAS** (다인·KAIT) | 한국 표준 LMS·KORMARC 내장 | **자동 생성 약함**·8분/건 페인 잔존·클라우드 약함 = **우리 타겟** | **LOW (보완)** |

---

## 3. 학술 논문·특허 (6건)

| # | 출처 | 핵심 | 우리 관련성 |
|---|---|---|---|
| **P1** | **MDPI Publications 14:1:19, 2026** "LLM-Based Bibliographic Cataloging Agent in CNMARC Context" | 4-Agent (MEA·DCA·SAIA·QCA)·33,000 CNMARC + 中圖法5판 | **가장 가까운 학술 선행**. 우리 멀티에이전트 (Part 54·60)와 동형 → 인용 가능 |
| **P2** | **PCC Task Group on AI/ML Cataloging Final Report** (LC, 2025) | OS ML 23,000 ebook·Annif 35%·LLM 26% LCSH·HITL 권고 | **자동화 정확도 한계 객관 근거** = 우리 99.82% 대비 격차 영업 |
| P3 | Aycock et al., C&RL News 2024 "Prompting Generative AI to Catalog" | GPT MARC = 끊임없는 검수 필요 | HITL·sanity-check CLI 정당화 |
| P4 | CCQ 62:5, 2024 "Creating MARC 21 with ChatGPT" | ChatGPT 기반 평가 | 도메인 룰엔진 + LLM 보조 = 정확도 우위 |
| P5 | 국내 KORMARC 논문 (DBpia): 비도서·통합서지·마을기록물 KORMARC | 표준·적용 사례 (자동 생성 솔루션 연구 없음) | **국내 KORMARC SaaS 학술 공백** = 시장 선점 |
| P6 | 특허 KR101200442B1 (2012, 만료) "도서용 마크 데이터 입력시스템" | 마크 다운로드·매핑 자동 | **존속 만료** = 자유 실시 |

---

## 4. 위협도 매트릭스

- **HIGH (1)**: MarcAI — 가장 직접 경쟁. KORMARC·한국어 미지원이 결정적 진입 장벽
- **MID (1)**: OCLC AI Connexion — 글로벌 빅, 한국 시장 미진입
- **LOW (다수)**: 보완재·소스·참고

---

## 5. kormarc-auto Unique Value Proposition

1. **유일한 KORMARC 특화 SaaS** — 글로벌 (MARC21/UNIMARC) + 국내 LMS (자동 생성 약) **3중 교차 공백**
2. **ISBN 1건 → 1분 내 KOLAS·DLS 호환** — PCC LC LLM 단독 26% 대비 어셔션 38건 + 자관 99.82% + 9 자료유형 빌더로 **실용 정확도**
3. **사서 출신 1인 비개발자 PO 직접 설계** = 한국 사서 어휘·일과·KCR4·KS X 6006 적합 UX (Part 49~51)
4. **B2C 사서 개인 PLG** (Part 60) — 글로벌·국내 경쟁사 모두 B2B-only
5. **KOLAS 2026-12-31 종료 + AI 바우처 8,900억 정부 자금** 한국 시장 골든타임 정렬

---

## 6. 잠재 협력·통합 후보

- **NLK ISBN Open API** (K1) — 정식 데이터 소스. MOU·인증 마크 추진
- **도서관 정보나루** (K2) — 통계·인기 통합 (Part 49 권위 인용 강화)
- **알라딘 Open API** (K3) — 표지·가격 보강 (이미 사용)
- **Annif / Finto AI** (G5) — KDC 자동 주제명 색인 모듈 (OSS)
- **MarcEdit** (G3) — 고급 사서용 export·후처리 보완재 안내

---

## 7. 학습 포인트

| 출처 | 학습 |
|---|---|
| MarcAI 크레딧 모델 | 사서 1인 부담 → 우리 정액·체험 무료 적합 (Part 51) |
| OCLC HITL 메시지 | "안전망 (safety net)" 사서 채택률 ↑ → 영업 카피 차용 |
| MDPI 4-Agent (P1) | 우리 멀티에이전트 (Part 54)와 동형·학술 인용 + 영업 신뢰도 |
| PCC LC 26% (P2) | 경쟁사 한계 객관 근거 → 99.82% 격차 영업 자료 |

---

## 8. 영업 활용 가이드

### 콜드메일 추가 문구 (P2 인용)

> "미국 의회도서관(LC) 산하 PCC Task Group이 발표한 보고서에 따르면, 일반 LLM의 LCSH 자동 분류 정확도는 26%에 그칩니다.
> kormarc-auto는 한국 도서관 표준(KORMARC KS X 6006-0:2023.12)에 특화된 룰엔진과 자관 99.82% 정합 검증을 통해
> 1분 내 KOLAS·DLS 호환 레코드를 생성합니다."

### 학술 발표 (KLA 2026 등)

> "MDPI Publications (Vol.14, No.1, 2026) 4-Agent 자동 카탈로깅 연구 결과와 일치하는 멀티에이전트 구조를
> KORMARC 환경에 최초로 적용한 사례."

### 자치구·NLK MOU 제안

> "국내 KORMARC 자동 생성 SaaS 학술·상용 선행 연구가 사실상 공백인 상태에서,
> kormarc-auto는 NLK ISBN Open API를 정식 데이터 소스로 활용하며 KORMARC 표준 보급에 기여합니다."

---

## 9. 출처 (web 검증 24건)

- MarcAI: https://marcai.cloud/
- OCLC AI: https://www.oclc.org/en/news/releases/2025/20251208-ai-recordmanager-connexion.html
- MarcEdit: https://marcedit.reeset.net/features
- LC BIBFRAME: https://www.loc.gov/bibframe/
- Annif: https://annif.org/ (NatLibFi GitHub)
- Liblime AI 2025-10: https://liblime.com/2025/10/11/how-ai-will-transform-library-cataloging/
- PCC Task Group LC: https://www.loc.gov/aba/pcc/taskgroup/AI-and-Machine-Learning-TG-final-report.pdf
- C&RL News (Aycock): https://crln.acrl.org/index.php/crlnews/article/view/27045/34924
- CCQ 62:5: https://www.tandfonline.com/doi/abs/10.1080/01639374.2024.2394513
- MDPI Publications 14:1:19: https://www.mdpi.com/2304-6775/14/1/19
- DBpia KORMARC 논문 3건
- 특허 KR101200442B1 (만료): https://patents.google.com/patent/KR101200442B1/ko
- NLK ISBN Open API·도서관 정보나루·알라딘 Open API
- KOLAS III 다인: https://www.dainlib.co.kr/?PID=0206
- ALA News 2025-09 / LC Signal 2024-11 / ScienceDirect 2025

---

> **이 파일 위치**: `kormarc-auto/docs/research/part86-similar-automation-papers-2026-05.md`
> **다음 활용**: 콜드메일 50 (`docs/sales/35-cold-mail-50-templates-5segments-2026-05.md`)·KLA 발표·NLK MOU 제안서
