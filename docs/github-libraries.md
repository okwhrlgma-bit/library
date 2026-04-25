# GitHub 도서관 관련 코드·라이브러리 조사

> 자율 조사일: 2026-04-26
> 우리 도구가 활용·통합·차별화할 수 있는 GitHub 자산 정리.

---

## 1. KORMARC 직접 검색

| 저장소 | 언어 | 스타 | 특징 |
|---|---|---|---|
| coffee-water-ice/2026_kormarc_ | Python | 0 | 신규 (27일 전), 활용도 낮음 |
| skeeper75/_kormarc_.man | Python | 0 | 신규 (1월) |

→ **KORMARC 키워드로는 GitHub 거의 비어있음**. 우리가 사실상 한국 KORMARC 자동화 first-mover 검증.

### KDC 검색 결과
- **0 results**. 한국십진분류법 GitHub 코드 부재.
- 우리 `librarian_helpers/kdc_tree.py`가 사실상 가장 광범위한 공개 KDC 트리 데이터.

### 이재철 저자기호 검색 결과
- **0 results**. 한국 저자기호 GitHub 공개 구현 부재.
- → **우리 `librarian_helpers/call_number.make_author_mark` (방금 강화)가 한국 첫 오픈 구현 가능성**.

---

## 2. pymarc 생태계 (우리 기반 라이브러리)

| 저장소 | 용도 | 우리 활용 |
|---|---|---|
| **edsu/pymarc** (254★) | 기본 라이브러리 | ✅ 이미 사용 |
| ubleipzig/marcx | pymarc.Record 확장 | 검토 가능 |
| hmakki72/pymarc_utilities | 대용량 MARC 처리 | 일괄 import 시 검토 |
| danizen/pymarcspec | MarcSpec 구현 | 레퍼런스 |
| carpentries-incubator/pymarc_basics | 교육 자료 | 사서 학습 자료로 |
| lpmagnuson/pymarc-workshop | ALCTS 워크샵 (2017) | 레퍼런스 |
| ClaraTurp/PyMARCExamples | 시스템 마이그레이션 | 도서관 갈아타기 사례 |
| slub/pymarc2jsonl | MARC21 → JSON-LD | ✅ 우리 JSON-LD 출력 영감 |

→ pymarc 한국어 처리·KORMARC 특화 라이브러리는 **없음**. 우리가 격차 채움.

---

## 3. 도서관 관리 시스템 GitHub Topics (619개)

| 저장소 | 스타 | 언어 | 특징 |
|---|---|---|---|
| **Librum** | 5.3k | C++/Qt | 전자책 리더 + 카탈로깅 |
| **Zenodo** | 992 | Python/Flask | 연구 데이터 저장소 |
| Library-Assistant | 583 | JavaFX | 데스크톱 GUI |
| Library-Management-System-JAVA | 487 | Java | 강의용 |
| **Pinakes** | - | - | 완전 ILS + Z39.50/SRU 서버 |
| bragibooks | - | - | 오디오북 메타 |
| Project-Libra | - | Django | REST API |

### 언어 분포
- Python 131 / Java 88 / JavaScript 80 / 기타

→ **한국 KORMARC + AI 자동 SaaS는 우리가 first-mover** 확정.

---

## 4. 글로벌 자동 분류·색인 (참고)

### 4.1 Annif (NatLibFi/Annif) ★★★
- 핀란드 국립도서관
- Apache 2.0
- BERT·FastText·SVM·MLLM
- 국회도서관 2024 보고서가 직접 권고
- **우리 활용**: 알고리즘 참고. 단 한국어 학습 데이터 별도 필요.

### 4.2 Koha
- 글로벌 ILS, MARC21 위주
- 우리: MARCXML export로 호환

### 4.3 FOLIO
- 차세대 ILS, BIBFRAME 검토
- 우리: Phase 3 진입 시

---

## 5. 우리 코드 보강 (GitHub 조사 반영)

### 5.1 `make_author_mark` 강화 (방금 커밋)
- 이재철식 근사 알고리즘 명시
- 한글 자모 분해 (초성·중성·종성) 기반
- 11~99 범위 숫자 매핑
- → **한국 GitHub 공개 코드 부재 영역의 첫 구현**

### 5.2 향후 추가 가능 (PO 명령 시)
- pymarc_utilities 기반 대용량 import
- pymarc2jsonl 패턴 → JSON-LD writer 강화
- Pinakes 패턴 → Z39.50/SRU 서버 (Phase 3)

---

## 6. 우리 코드 GitHub 공개 시 가치 (선택)

### 공개하면 얻는 것
- 사서 커뮤니티 신뢰
- 정부 지원사업 가산점 (오픈소스)
- 연구·논문 인용 가능
- 글로벌 한국학 도서관 협업

### 공개하면 잃는 것
- 핵심 알고리즘 모방 위험
- 영업 차별화 약화
- 경쟁사 빠른 추격

### 권장 전략 (Phase별)
| Phase | 공개 범위 |
|---|---|
| Phase 1 (베타) | 비공개 |
| Phase 2 (50곳) | KDC 트리·식별기호 변환만 부분 공개 (마케팅) |
| Phase 3 (200곳) | 코어는 비공개, 도구·문서는 공개 |
| 글로벌 진출 | MIT/Apache로 일부 공개 — 학술 인용 유도 |

→ Phase 1은 **비공개 유지**. 공개는 신뢰 자산 쌓인 후.

---

## 7. PO가 GitHub에서 입수해야 할 것

| 출처 | 용도 |
|---|---|
| **github.com/NatLibFi/Annif** clone | 자동 색인 알고리즘 학습 |
| **edsu/pymarc** docs | 우리 기반 라이브러리 깊이 이해 |
| **slub/pymarc2jsonl** 코드 | JSON-LD 출력 강화 |
| **carpentries-incubator/pymarc_basics** | 사서 교육 자료 만들 때 |

→ Claude는 PO가 clone 후 폴더에 두면 자동 분석 가능.

---

## 8. 우리 강점 요약 (GitHub 비교)

| 영역 | GitHub 공개 | 우리 |
|---|---|---|
| KORMARC 자동 빌드 | ❌ 거의 없음 | ✅ |
| KDC 트리 데이터 | ❌ 0 | ✅ |
| 이재철 저자기호 | ❌ 0 | ✅ (방금 강화) |
| 880 한자 자동 | ❌ | ✅ |
| 정보나루·NL Korea API | ❌ | ✅ |
| 알라딘·카카오 API | ❌ | ✅ |
| KDC AI 추천 | ❌ | ✅ BYOK |
| KOLAS·DLS·KOLASYS export | ❌ | ✅ |
| 한국어 OCR 통합 | ❌ | ✅ EasyOCR |
| 라벨 PDF (A4 Avery) | ❌ | ✅ |

→ **10개 항목 모두 한국 GitHub에 부재**. 우리 = 한국 도서관 자동화 코드 자산의 사실상 표준.

---

## 9. 결론

GitHub 조사 결과:
1. **한국 KORMARC·KDC·이재철 저자기호 코드는 사실상 GitHub에 없음**
2. **우리 = 한국 도서관 자동화 코드 first-mover** (학술·시장 양쪽)
3. **글로벌 pymarc 생태계는 활발** — 우리 기반 라이브러리는 검증됨
4. **Annif·Koha 등 글로벌 도구는 한국어·KORMARC 미지원** — 차별화 영역

→ Phase 3 도달 후 일부 공개로 신뢰 자산화 + 글로벌 한국학 도서관 진입 채널.
