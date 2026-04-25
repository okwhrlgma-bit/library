# 기술 트렌드 — 도서관·서지·AI

> 분기별 점검. 우리 코드·로드맵에 반영할 것 vs 인지만 할 것 분리.

---

## 1. 서지 표준 진화

### 1.1 BIBFRAME (LC, 2012~)
- **출처**: Library of Congress
- **목적**: MARC 대체, Linked Data 기반
- **현황 2024**: 일부 미국 대학 채택, 미의회도서관 운영
- **한국**: 국회도서관 2024 보고서 권고 (검토 단계)
- **우리 영향**: Phase 3~4 글로벌 진출 시 검토. KORMARC → BIBFRAME 변환 모듈 추가 가능.

### 1.2 MARC21 → 차세대
- 미국·영어권 표준
- 우리: ✅ 양방향 변환 지원

### 1.3 RDA (Resource Description and Access)
- **현황**: AACR2 후속, 글로벌
- **국내**: 대학도서관 일부 적용
- **우리**: 264 RDA·336/337/338 RDA 자동 (현 builder.py)

### 1.4 KCR5 초안 (2024.5)
- FRBR 기반 한국 신표준
- **우리**: 명세서 갱신 시 검토

### 1.5 FRBR / FRAD / IFLA LRM
- **출처**: IFLA
- **글로벌 모델**: Work·Expression·Manifestation·Item
- **우리**: Phase 2~3 메타모델 검토

---

## 2. AI·자동화

### 2.1 자동 분류 (BERT·FastText·SVM)
- **국회도서관 2024 연구**: BERT 80%·FastText 차순
- **Annif (핀란드)**: 오픈소스, 다중 알고리즘
- **OCLC FAST·DDC AI**: 상용
- **우리**: Anthropic Claude Sonnet 4.6 + tool_use 강제

### 2.2 자동 서지 생성 (LLM)
- **국회도서관 2024**: "복잡성 + 학습데이터 부재로 한계"
- **OCLC AI 카탈로깅 2025.12**: 권당 20분 단축 주장
- **우리**: 외부 API 1순위 + AI 폴백 + BYOK 모델

### 2.3 LLM 모델 선택
| 모델 | 용도 |
|---|---|
| Claude Sonnet 4.6 | 메인 (Vision·KDC·Subject) |
| Claude Haiku 4.5 | ISBN 추출만 (저렴) |
| GPT-4 | 미검증 |
| 한국어 특화 (HyperCLOVA·KoGPT) | Phase 2 검토 |

### 2.4 BYOK (Bring Your Own Key) 트렌드
- **이유**: AI 비용 통제·보안·프라이버시
- **우리**: ✅ 이미 적용

### 2.5 OCR·Vision
| 도구 | 비용 | 한국어 |
|---|---|---|
| Tesseract | 0 | △ |
| EasyOCR | 0 | ✅ |
| PaddleOCR | 0 | ✅ |
| Google Vision | 1.5원/장 | ✅ |
| Naver CLOVA | 1.3원/장 | ✅ |
| Claude Vision (Haiku/Sonnet) | 0.1~1.5원/장 | ✅ |

→ 우리: EasyOCR + Claude Vision 하이브리드.

---

## 3. Linked Data·시맨틱웹

### 3.1 Wikidata
- **활용**: 작가·인물·기관 전거 데이터
- **무료 API**
- **우리 검토**: 100/700 ▾d 생몰년 자동 채움 가능성 (Phase 2)

### 3.2 VIAF (Virtual International Authority File)
- **출처**: OCLC
- **활용**: 글로벌 인명 통합 전거
- **우리**: Phase 3 글로벌 진출 시

### 3.3 LCSH·FAST
- 미국 주제명 표준
- **우리**: 글로벌 진출 시

### 3.4 Schema.org
- 검색엔진 인덱싱
- **우리**: ✅ JSON-LD export (`docs/library-science-references.md`)

---

## 4. 도서관 시스템 클라우드 전환

### 4.1 SaaS화 흐름
- 기존: 도서관별 로컬 ILS 설치
- 미래: SaaS 구독 (Alma·Folio·우리)
- **우리 위치**: SaaS-only

### 4.2 데이터 이동성
- API 기반 통합 증가
- 표준 export (MARCXML·JSON-LD) 필수
- **우리**: ✅ 모두 지원

---

## 5. 도서관 모바일·UX

### 5.1 모바일 우선
- 사서 책장 옆 작업
- 이용자 폰 OPAC
- **우리**: ✅ Streamlit 반응형 + Cloudflare Tunnel

### 5.2 PWA (Progressive Web App)
- 앱스토어 거치지 않고 폰 홈 추가
- **우리**: ✅ `landing/manifest.webmanifest`

### 5.3 음성 입력 (TBD)
- 사서가 책 들고 음성으로 입력
- 미래 검토

---

## 6. 데이터 표준 동향

### 6.1 ONIX (출판계)
- **출처**: EDItEUR
- **활용**: 출판사 → 도서관 메타데이터 전송
- **우리**: ONIX import 가능성 (Phase 2)

### 6.2 KOMARC (한국형)
- **현재**: KORMARC가 표준 (KOMARC는 유사 명칭)

### 6.3 OAI-PMH
- **활용**: 대량 메타데이터 수확
- **우리**: Phase 2~3 (대학도서관 진입 시)

---

## 7. AI 윤리·규제

### 7.1 EU AI Act (2024+)
- AI 시스템 위험 등급 분류
- 우리: 도서관 분류 = 저위험. 부담 적음.

### 7.2 한국 AI 윤리 지침
- 과기부·KISA 가이드
- 우리: ✅ "사서 결정권 보존" 정책

### 7.3 AI 환각·할루시네이션
- **방어**: tool_use 강제·검증·사서 후보 형태
- **우리**: ✅ 모두 적용

---

## 8. 자동 분류 정확도 진화

| 시기 | 도구 | DDC 정확도 | 주제어 정확도 |
|---|---|---|---|
| 2018 | SVM (Annif) | ~70% | ~40% |
| 2022 | BERT | ~80% | ~50% |
| 2024 | LLM (GPT-4·Claude) | ~85%+ | ~60% |
| 2026 추정 | LLM + RAG | ~90%+ | ~70% |

→ 우리도 동등 수준. 정보나루·KOLIS-NET 데이터 기반 RAG 추가 시 향상 가능.

---

## 9. 한국 도서관계 정책 동향

### 9.1 KCR5 전환
- 2024.5 초안
- 2026~2027 확산 예상

### 9.2 독서로DLS 통합 (2024)
- 학교도서관 표준 통합
- 우리: dls_writer.py 호환

### 9.3 작은도서관 진흥 (문체부)
- 매년 신규 작은도서관 200~300곳
- 우리 ICP 확대

### 9.4 지역서점·작은도서관 연계
- 출판유통진흥원 정책
- 우리 영업 채널

---

## 10. 글로벌 도서관 트렌드

### 10.1 Open Source ILS 증가
- Koha·Folio 채택률 ↑
- **우리**: MARCXML 호환

### 10.2 동아시아 한국학 도서관
- 미국·유럽 대학 동양학과
- KORMARC + 880 한자 전문성
- **우리**: ✅ 강점

### 10.3 디지털 자료 비중 증가
- 전자책·오디오북·점자도서
- **우리**: material_type.py 분기

---

## 11. 우리 코드 반영 우선순위

### 즉시 (이미 반영)
- ✅ Claude Sonnet 4.6 + Haiku 4.5
- ✅ tool_use 강제
- ✅ BYOK
- ✅ MARC21 변환
- ✅ MARCXML·MODS·Dublin Core·JSON-LD
- ✅ EasyOCR + AI 하이브리드

### Phase 2 검토
- ⏸ KCR5 적용
- ⏸ Wikidata 인명 전거
- ⏸ ONIX import
- ⏸ NDC 활성

### Phase 3 검토
- ⏸ BIBFRAME export
- ⏸ OAI-PMH 수확
- ⏸ VIAF 통합

### Phase 4+ 인지만
- ⏸ EU AI Act 영향
- ⏸ 한국어 특화 LLM (HyperCLOVA)
- ⏸ 음성 입력

---

## 12. 분기별 점검 (Claude 자동)

PO가 매분기 시작 시:
> "기술 트렌드 1년 변화 점검. 새 표준·도구·논문·정책 정리해줘"

→ Claude 자동 WebFetch + `docs/technology-trends.md` 갱신 + 우리 영향 평가.
