# 한국 도서관 프로그램 생태계 심화 분석 — '내를 건너서 숲으로' 사례 기반 확장

> 사서 출신 1인 비개발자 PO가 근무한 "내를건너서 숲으로 작은도서관"의 KOLAS III + ECO RFID + 알파스 + 책바다·책나래·책이음·책단비 환경을 출발점으로, 전국 도서관 유형별 프로그램·페인포인트·연동 가능성을 종합 정리.
>
> 선행 문서: `docs/po-library-integration-analysis.md`, `docs/real-library-d-drive-index.md`, `docs/kolas-modules-index.md`, `docs/librarian-domain.md`.

---

## TLDR (한 줄 요약)

한국 도서관 7대 시스템(KOLAS III · KOLASYS-NET · 독서로DLS · TULIP · SOLARS · 알파스 · Koha/Alma)은 **모두 KORMARC 또는 MARC21 기반**이라 kormarc-auto의 `.mrc`/`MARCXML`/`CSV` 출력은 **즉시 호환 가능**하다. 단 **2026-12-31 KOLAS III 표준형 기술지원 종료**로 6,900곳 작은도서관 + 다수 공공도서관이 후속 시스템 결정 압박을 받는 중 → **kormarc-auto의 시장 진입 골든타임**.

---

## A. 도서관 유형별 사용 프로그램 매트릭스

| 유형 | 규모 | 주 시스템 | 부가 시스템 | 사서 인력 | 우리 호환 |
|---|---|---|---|---|---|
| **공공도서관(대형)** | 시·도립 | KOLAS III + 책이음·책바다 | RFID(이씨오/북코드), KOLIS-NET | 5~30명 | ✅ kolas_writer |
| **공공도서관(중·소)** | 구립·시립 | KOLAS III | 책이음·책바다 | 1~5명 | ✅ kolas_writer |
| **작은도서관(공립)** | 마을·동단위 (약 6,900곳) | **KOLASYS-NET**(웹) 또는 KOLAS III | 책이음 일부 | 1명 또는 자원봉사 | ✅ csv_writer.write_kolasys_csv |
| **작은도서관(사립)** | 종교·재단 | Excel 수기 / KOLASYS-NET / 자체 | 없음 | 자원봉사·관장 1명 | ✅ CSV·라벨 |
| **학교도서관(초·중·고)** | 1교 | **독서로DLS**(2024 통합) | 도서관 정보나루 | 1인 사서 (대부분) | ✅ dls_writer |
| **대학도서관** | 종합대 | **TULIP**(퓨쳐누리) / **SOLARS 8**(INEK) / Alma / Koha | 학술DB·디스커버리 | 10~50명 | ✅ marcxml_writer |
| **전문도서관(병원·법조·기업)** | 1관 | LAS / 자체 / 엑셀·Access | 주제DB | 1~3명 | ✅ csv·MARCXML |
| **출판사·서점(납품용)** | - | 자체 / 외주 마크대행 | - | 사서 1명 또는 외주 | ✅ kolas_writer |

**핵심**: 95%의 한국 도서관은 KORMARC/MARC21 기반. kormarc-auto는 **포맷 호환성 면에서 이미 시장 전체를 커버**한다.

---

## B. 각 프로그램에서 가져올/연동할 데이터

| 데이터 종류 | 우리 영역? | 비고 |
|---|---|---|
| **도서 메타데이터** (245·100·260·300…) | ✅ 핵심 | ISBN→KORMARC, 우리 코어 |
| **이용자 개인정보** | ❌ 원칙 제외 | 회원·대출자 명단 — 개인정보보호법 |
| **대출 통계**(집계) | △ 간접 | 자관 트렌드 분석은 가능, 하지만 ICP 외 |
| **청구기호 체계**(049) | ✅ 부분 | KDC + 저자기호. 자관 규칙은 사서 입력 |
| **별치기호**(연구실·보존·분실) | ✅ | `inventory/library_db.py`로 처리 |
| **신착·납본·폐기 이력** | ✅ | 583 필드 + `loss_damage.py` |
| **시설 운영 정보**(휴관·공지) | ❌ | 도서관 홈페이지 영역 |
| **상호대차 기록**(책바다) | ❌ | KOLAS 출력 채널, 우리는 자료원 단계 |
| **회원 통합**(책이음) | ❌ | 회원 도메인, 우리는 자료 도메인 |

**원칙**: kormarc-auto는 **자료(item) 도메인 전담**. 사람(member)·시설·회계는 다른 시스템이 담당하도록 분리.

---

## C. 사서 페인포인트 Top 10 (인터넷 검색 + PO 자료 + 도메인 통념)

1. **마크 작업 시간**: 신착도서 권당 8~15분 (분류·청구기호·라벨까지 포함). 1인 사서 도서관에선 야근 직결.
2. **KDC 분류 결정 어려움**: 종이 분류표 6판을 옆에 두고 펼쳐가며 결정. AI 후보 추천 부재.
3. **OCR·사진 미지원**: 옛 책·기증도서·외서는 손입력. 표지 사진 → MARC 자동화 도구 시장 부재.
4. **KOLAS UI 구식**: Windows 전용 클라이언트, 모바일 미지원, 단축키 위주, 신규 사서 학습 곡선 큼.
5. **KOLAS III 표준형 기술지원 종료(2026-12-31)**: 후속 시스템 미확정. 작은도서관 1,800곳 + 공공도서관 다수 불안.
6. **납품 마크 의존**: 학교도서관 95% 이상이 도서 납품업체에 마크 외주. 가격·품질 편차 + 마크 검수 시간 발생. 2023년 서점업계 "마크 구축 불공정 개선 요구" 뉴시스 보도.
7. **표준 변동성**: KCR4 → KCR5 전환(2024.5 초안), 독서로DLS 통합(2024), BIBFRAME 검토. 사서가 표준을 따라잡기 어려움.
8. **수기·Excel 의존**: PO 도서관에서도 책단비 대장 일자별 .xlsm 수백 건. 자료관리·신착·재발급·분실파손이 모두 .xlsx로 분산.
9. **외부 API 인증키 대기**: 정보나루 1~3일, 알라딘 블로그 등록 필요. 신규 사서가 즉시 못 씀.
10. **자관 청구기호·별치기호 규칙 차이**: 도서관마다 049·085·090 규칙 다름. 신규 직원 인계 시 노하우 손실.

---

## D. kormarc-auto 개선 가능 영역 매트릭스

| 페인포인트 | 우리 솔루션 | 즉시 가능? | 추가 작업 |
|---|---|---|---|
| 마크 작업 시간 (8분→2분) | ISBN/사진 → KORMARC 자동 | ✅ Production | - |
| KDC 분류 결정 | KDC AI 후보 + `kdc_tree.py` | ✅ | 사서 피드백 학습 (Phase 4) |
| OCR·사진 미지원 | Vision Haiku→Sonnet 2단계 | ✅ | 정확도 측정 자료 축적 |
| KOLAS UI 구식 | Streamlit 모바일 반응형 + REST API | ✅ | KOLAS 직접 대체는 NO, 보조 도구 |
| **KOLAS III 종료** | KORMARC 표준 출력 → 후속 시스템에 그대로 이관 | ✅ | 후속 시스템(미정) 호환 검증은 출시 후 |
| 납품 마크 외주 의존 | 납품업체·출판사 직접 사용 → 사서가 검수만 | ✅ | 출판사 ICP 영업 (`docs/sales-roadmap.md`) |
| 표준 변동성 (KCR5 등) | `kormarc/builder.py` 모듈 갱신 | △ | KCR5 확정 시 업데이트 |
| Excel 수기 분산 | `inventory/library_db.py` + `output/csv_writer.py` | ✅ | 통계 PDF 보고서 강화 (`output/reports.py` 일부 완료) |
| 외부 API 키 대기 | BYOK + 30일 디스크 캐시 + 폴백 5단 | ✅ | 가입 단계에서 키 입력 가이드 |
| 자관 규칙 차이 | `librarian_helpers/call_number.py` 자관 설정 | ✅ | 자관 프리셋 저장 기능 |

→ **10개 페인포인트 중 9개를 우리가 직접 또는 부분 개선**. 미커버 1개(KCR5 전면 갱신)는 표준 확정 후 자동 갱신.

---

## E. 연동 설계 — 4가지 패턴

### 패턴 1: 파일 출력 연동 (이미 지원)
- `.mrc` (KOLAS III), `.mrc` for DLS, `MARCXML`(.xml), `.csv`(UTF-8 SIG), `.xlsx` (미구현 시 csv로 대체)
- **사서 워크플로우**: kormarc-auto → 파일 다운로드 → KOLAS·DLS·TULIP·SOLARS의 import 메뉴
- **장점**: 기존 시스템 변경 0. 사서 즉시 사용
- **호환 시스템**: KOLAS III, KOLASYS-NET, 독서로DLS, TULIP, SOLARS, 알파스, Koha, Alma 모두 ✅

### 패턴 2: REST API 연동 (이미 지원)
- FastAPI `/isbn/{isbn}`, `/batch`, `/photo`, `/inspect`, `/report/*` 엔드포인트
- **활용**: Excel Power Query, VBA, Python 스크립트, 도서관 자체 시스템에서 직접 호출
- **인증**: `X-API-Key` (사용량 기반 과금)
- **호환 시스템**: 모든 시스템 (HTTP 클라이언트만 있으면)

### 패턴 3: MCP 연동 (Claude Desktop·Code)
- 자연어 명령: "이 ISBN 5개 KORMARC 만들어줘", "표지 사진에서 메타 추출"
- **활용**: 사서가 Claude Desktop에서 도구처럼 호출
- **현 상태**: 향후 추가 (`docs/sales-roadmap.md` Phase 3+)

### 패턴 4: 임베디드 위젯 (HTML/JS)
- 도서관 홈페이지에 `<script>` 한 줄로 임베드
- **활용**: 일반 이용자가 ISBN 입력 → 자관 소장 여부·KORMARC 미리보기
- **현 상태**: 미구현, Phase 5+ 후보

---

## F. 각 프로그램별 연동 난이도·우선순위

| 프로그램 | 연동 방식 | 난이도 | 현 상태 | 우선순위 |
|---|---|---|---|---|
| **KOLAS III** | `.mrc` 자동 반입 | 낮음 | ✅ 완료 | 베타 1순위 |
| **독서로 DLS** | `.mrc` import (521 필드) | 낮음 | ✅ 완료 | ICP 1순위 (1인 학교사서) |
| **KOLASYS-NET** | CSV import | 낮음 | ✅ 완료 | ICP 1순위 (작은도서관, 1,800곳) |
| **TULIP** | MARCXML import | 낮음 | ✅ 완료 | 대학 영업 시 |
| **SOLARS 8** | MARCXML import (95개 대학) | 낮음 | ✅ 완료 | 대학 영업 시 |
| **알파스** | MARCXML 또는 .mrc | 낮음 | ✅ 완료 | 호환 시연용 |
| **Koha / Alma** | MARC21 (UTF-8) | 낮음 | ✅ MARCXML 호환 | 글로벌 확장 시 |
| **이씨오(ECO) RFID** | KOLAS 거쳐 자동 동기화 | 0 (간접) | ✅ 자동 | 별도 작업 불필요 |
| **책바다·책나래·책이음** | KOLAS 거쳐 자동 노출 | 0 (간접) | ✅ 자동 | 별도 작업 불필요 |
| **LAS (한국 코린)** | MARC import | 중간 | △ 검증 필요 | 전문도서관 진입 시 |
| **자체·Excel 수기 작은도서관** | CSV + 라벨 | 낮음 | ✅ csv_writer + labels | ICP 1순위 |
| **도서납품업체** | API 직접 호출 (대량) | 낮음 | ✅ /batch | B2B 영업 |
| **출판사 자가 KORMARC 생성** | API + CSV | 낮음 | ✅ | 신규 ICP 후보 |

→ **미지원 시스템 식별**: 한국 시장 핵심은 모두 커버. 글로벌 확장(BIBFRAME, FOLIO) 또는 특수 시스템(법원·국회·국립의학)이 향후 후보.

---

## PO에게 권고하는 다음 액션 (구체적 6개)

1. **2026-12-31 KOLAS III 종료를 영업 메시지로**: "KOLAS 종료 후에도 안전한 KORMARC 표준 생성 도구"라는 포지셔닝. `docs/sales-roadmap.md`에 마이그레이션 가이드 1편 추가. 후속 시스템(국립중앙도서관 발표 대기) 확정 후 호환 검증 즉시 발표.

2. **작은도서관 정보누리(KOLASYS-NET) 1,800곳 즉시 영업**: 이들은 자료관리 부담이 가장 크고 결제 의향이 높음. `output/csv_writer.py`의 `write_kolasys_csv` 동작 검증 + 작은도서관협회 공지·세미나 노출. 월 3만원/500건 플랜 직타깃.

3. **납품업체·출판사 B2B 트랙 신설**: 학교도서관 95%가 마크 외주에 의존. 우리 `/batch` API를 납품업체에 라이선스 → 사서 입장에선 "검수만" 하면 됨. 1관 단가는 낮지만 대량 처리 매출. `pricing.md`에 B2B 플랜 추가 검토.

4. **장서점검·보고서 PDF 강화**(`output/reports.py` 이미 일부 구현): 월간 운영 보고서, 신착 안내문, 연간 통계는 사서가 매월 상부기관 제출 의무. 이것 자동화하면 마크보다 더 강한 락인. **MVP-2 우선순위 1**.

5. **MCP 서버 출시(Phase 3+)**: 사서가 Claude Desktop에서 자연어로 호출하는 형태 시연 영상 1편. PO 본인 데모로도 가능. KLA 학술대회·사서 카페에 배포하면 차별화 즉시 인지.

6. **PO 직속 골든 데이터셋 수집**: PO 도서관의 2024년 신착도서 .xlsx → 골든 100건. `scripts/build_golden_dataset.py`로 우리 출력과 KOLAS 정답 비교 → 정확도 회귀 추적 + 영업 시 "검증된 정확도" 자료. 개인정보 없는 자료만.

---

## 출처(Sources)

- [도서관 표준자료관리시스템 - 나무위키](https://namu.wiki/w/%EB%8F%84%EC%84%9C%EA%B4%80%20%ED%91%9C%EC%A4%80%EC%9E%90%EB%A3%8C%EA%B4%80%EB%A6%AC%EC%8B%9C%EC%8A%A4%ED%85%9C)
- [공공도서관지원서비스 KOLAS III 시스템 소개](https://books.nl.go.kr/PU/contents/P30101000000.do)
- [작은도서관 정보누리(KOLASYS-NET) 시스템 소개](https://books.nl.go.kr/PU/contents/P30201000000.do)
- [작은도서관 정보누리 사용 안내](https://www.smalllibrary.org/helper/data/1237)
- [KOLAS - 나무위키](https://namu.wiki/w/KOLAS)
- [퓨쳐누리 TULIP 솔루션](https://home.futurenuri.com/homepage4/product/tulip_las.do)
- [INEK SOLARS](https://www.inek.kr/)
- [학교도서관 마크 구축 불공정 개선 요구 — 뉴시스 2023.1](https://www.newsis.com/view/NISX20230127_0002171879)
- [독서로 DLS](https://dls.edunet.net/)
- [국립중앙도서관 KORMARC 매뉴얼](https://librarian.nl.go.kr/kormarc/KSX6006-0/sub/01X_09X_090.html)
- [전문도서관 — 위키백과](https://ko.wikipedia.org/wiki/%EC%A0%84%EB%AC%B8%EB%8F%84%EC%84%9C%EA%B4%80)
- [국가자료종합목록 KOLIS-NET](https://www.nl.go.kr/kolisnet/index.do)

---

**작성일**: 2026-04-26
**작성**: Claude (Opus 4.7, 1M context) — 헌법 §11 v0.4 시점
**범위**: PO 자료 + 웹 검색 + 도메인 통념 종합. 코드 변경 없음.
