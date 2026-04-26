# ADR 0008 — 라이선스 모델 (Apache 2.0 코어 + 상용 SaaS 분리)

**상태**: accepted
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

오픈소스 vs 상용 라이선스 결정. 도서관 시장은 공공 자금이 많고 사서가 직접 코드 수정 의향 있는 경우 일부 존재. PO 입장에서는 매출이 1순위.

옵션:
1. **모두 Closed Source** — 라이선스 매출 극대화, 사서 신뢰·기여 0
2. **모두 Apache 2.0** — 도서관 신뢰 ↑, B2B 영업 시 "왜 돈 받나" 질문
3. **AGPL** — 사서가 수정 시 소스 공개 강제, 학교·공공 사용 부담
4. **Apache 2.0 (코어 엔진) + 상용 SaaS (서버·결제·관리자)** ★

## 결정

**Apache 2.0 코어 + 상용 SaaS 분리** (옵션 4).

### Apache 2.0 (오픈)
- `src/kormarc_auto/api/` (외부 API 클라이언트)
- `src/kormarc_auto/kormarc/` (KORMARC 빌더·검증)
- `src/kormarc_auto/classification/` (KDC·NLSH)
- `src/kormarc_auto/vernacular/` (한자 880)
- `src/kormarc_auto/output/` (kolas·dls·marcxml writer)
- `src/kormarc_auto/legal/` (납본 서식)
- `src/kormarc_auto/librarian_helpers/` (청구기호·등록번호·로마자)
- `src/kormarc_auto/interlibrary/` (책나래·책바다·RISS 어댑터)
- `src/kormarc_auto/acquisition/` (수서 분석)
- `src/kormarc_auto/conversion/` (MARC21 변환)
- `src/kormarc_auto/cli.py`

### 상용 (Closed)
- `src/kormarc_auto/server/` (FastAPI·signup·billing·admin·account)
- `src/kormarc_auto/ui/streamlit_app.py` (사서용 UI — 운영 호스팅)
- 결제·청구·세금계산서 모듈 (포트원 통합 후)
- 자관 인덱스 호스팅 인프라

## 결과

- 사서·연구자가 **코어 엔진 검증 가능** → 도서관계 신뢰 확보
- 도서관 IT 팀이 **자체 호스팅 시 코어만 사용** 가능 (기여 권장)
- **상용 SaaS = 운영 호스팅 + 결제 + B2B API** 매출 단일 소스
- B2B 도서납품업체에 "코어는 무료, API 호스팅은 유료" 명확

## 트레이드오프

✅ **장점**
- 학교·공공도서관 조달팀 신뢰 (오픈소스 항목 가산점)
- 코어 버그·KORMARC 표준 변경 시 사서 PR 가능 (영업 자료 실증)
- B2B 영업 시 "코어 검증 가능"으로 신뢰 격차 차단
- 우리 매출 라인은 호스팅·결제·관리자 기능에 집중 (마진 90%+)

❌ **단점**
- 코어 무료 = 경쟁사가 분기·재포장 가능 (예: 솔루션 업체가 코어 가져다 자기 호스팅)
- "어디까지 코어인지" 경계 분쟁 가능 → 모듈 단위로 명확히 분리
- 분리 유지 비용: 매 commit 시 어느 라이선스인지 자동 검사 필요

## 완화 조치

- 모듈 단위로 `LICENSE` 파일 별도 (코어 폴더에 `LICENSE-APACHE`, server에 `LICENSE-COMMERCIAL`)
- `pyproject.toml`에 license = `"Apache-2.0 AND LicenseRef-kormarc-commercial"` 명시
- `docs/license-faq.md` (사서 IT팀 1차 응답 6 Q&A)
- 어셔션 추가 검토: `assert_license_files_present` (binary_assertions에 후속)
- 코어 영역 신규 모듈 추가 시 file 헤더에 `# SPDX-License-Identifier: Apache-2.0`

## 6개월 후 되돌릴 수 있는가?

**부분** — 추가 폐쇄(Apache → Commercial)는 미래 commit만 적용 가능 (이미 공개된 코드는 Apache 영구 유효, 포크 가능). 반대 방향(Commercial → Apache 추가 공개)은 제한 없음.

## 트리거 (재평가 시점)

- 매출 월 1,000만원 이상 → AGPL 추가 검토 (경쟁사 분기 차단)
- 솔루션 업체 분기 사례 발생 → 상용 영역 확장 (UI도 일부 Closed)
- 도서관계 PR 누적 50건 이상 → 코어 영역 더 공개 검토

## 관련 자료

- `README.md` 라이선스 섹션
- `docs/business-checklist.md` 사업화 체크리스트
- 향후: `LICENSE-APACHE`·`LICENSE-COMMERCIAL` 파일 분리 (트리거 시 commit)
- 향후: `docs/license-faq.md` 사서 IT팀 안내
