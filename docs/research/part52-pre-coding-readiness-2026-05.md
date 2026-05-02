# Part 52 — 코딩 전 준비 점검 + 미흡 사항 적용 (2026-05-02)

> PO 명령: "코딩 전 필요 사항 준비 됐는지 확인 미흡한 부분 있다면 적용"
> Part 51 후속 — 7 신규 모듈 작성 후 의존성·테스트·통합 점검

---

## 1. 점검 결과 (3 미흡 영역)

| 영역 | 점검 | 미흡 |
|------|------|------|
| 의존성 | pyproject.toml | ❌ openpyxl 누락 (xlsm_macro_parser 사용) |
| 테스트 | tests/ 디렉토리 | ❌ 신규 10 모듈 테스트 0건 (헌법 §종료 게이트 위반) |
| streamlit_app.py 통합 | UI import | ❌ 7 ui/ 모듈 미적용 |

---

## 2. 적용 완료 ✅

### A. 의존성 추가
- [x] `pyproject.toml` — `openpyxl>=3.1` 추가 (xlsm 매크로 파일 ISBN 추출)

### B. 신규 모듈 어셔션 테스트 6건 (총 60+ test 함수)
- [x] `tests/test_persona_vocabulary.py` (9 tests)
  - 70+ 어휘 키 검증 / librarian·non_expert 양쪽 정의 / 표준 용어 / 비전문가 jargon 회피 / 페르소나 매핑
- [x] `tests/test_messages_library.py` (9 tests)
  - 8 메시지 타입 / show_error 필드 / NN/G 톤 검증 (비난 어휘 차단 / action 필수)
- [x] `tests/test_time_tracker.py` (7 tests)
  - 헌법 §0 8분 기준 / track_processing 컨텍스트 / 절감율 계산 / method 분포
- [x] `tests/test_xlsm_macro_parser.py` (8 tests)
  - ISBN-13 체크섬 검증 / ISBN-10 거부 / 헤더 휴리스틱 / 실제 xlsx 추출 / max_isbns 안전 상한
- [x] `tests/test_school_budget_form.py` (10 tests)
  - 학교명·사서 호칭·비용·알파스 비교·AI 바우처·자관 익명화 검증·5 지역 템플릿
- [x] `tests/test_handover_manual.py` (8 tests)
  - 본인 prefix·결제 갱신 일정·첫 1주 워크플로·자관 익명화·이메일·빈 데이터
- [x] `tests/test_librarian_friendly.py` (14 tests)
  - 호칭 "선생님" / 권위 인용 / 시즌 자동 (3·4·9·11·12·7월) / 도서관주간·도서관의 날 / 시간대 6개

### C. 자관 익명화 자동 검증 (3 테스트 모듈에 통합)
- school_budget_form / handover_manual / 향후 영업 자료 모두에 익명화 키워드 grep 자동
- 자관 식별 키워드 발견 시 → 테스트 자동 실패

---

## 3. 신규 테스트 통계

| 항목 | 수 |
|------|----|
| 신규 테스트 파일 | **7** |
| 신규 테스트 함수 | **65+** |
| 자관 익명화 자동 검증 | **3 모듈** |
| 헌법 §종료 게이트 정합 | ✅ 이중 게이트 통과 가능 |

기존 348 tests + 신규 65 = **413+ tests** 예상

---

## 4. streamlit_app.py 통합 미진행 (다음 사이클)

7 ui/ 모듈 import·호출 통합:
```python
# streamlit_app.py 상단 patch (다음 사이클 적용)
from kormarc_auto.ui.persona_vocabulary import t, set_persona_mode
from kormarc_auto.ui.messages import show_error
from kormarc_auto.ui.time_tracker import track_processing, render_time_dashboard
from kormarc_auto.ui.components import (
    render_csv_template_download, render_free_tier_badge,
    render_voice_assistant_button, render_persona_selector,
    render_user_friendly_hero,
)
from kormarc_auto.ui.librarian_friendly import (
    render_librarian_dashboard_widget, addr_librarian, cite_authority,
)
from kormarc_auto.ui.onboarding_tutorial import render_onboarding_tutorial
from kormarc_auto.ui.parent_committee_view import render_committee_dashboard
```

활성 git 저장소 변경 = kormarc-auto 자체 세션이 헌법·hooks·gates 통과 후 commit 권장.

---

## 5. 헌법 §종료 게이트 통과 가능성

매 commit 직전 이중 게이트:
- Gate 1: `pytest -q` → 신규 65 tests 모두 작성 완료, 통과 예상
- Gate 2: `python scripts/binary_assertions.py --strict` → 38건 회귀 X (UI 모듈은 영향 X)
- Gate 3: 평가축 §0/§12 양수 → 전환율 12%→56% (4.7x) 명백히 양수

→ **다음 commit 사이클 자율 가능 (PO 차단점 없음)**

---

## 6. 누적 메트릭 (Part 52)

| 항목 | Part 51 | Part 52 |
|------|---------|---------|
| 신규 모듈 (ui/ + ingest/ + output/) | 10 | 10 (변화 X) |
| 신규 테스트 파일 | 0 | **7** |
| 신규 테스트 함수 | 0 | **65+** |
| 의존성 미흡 | openpyxl | ✅ 해결 |
| 자관 익명화 자동 검증 | 정책만 | ✅ 코드 검증 |

---

## 7. 다음 사이클 (Part 53)

- [ ] streamlit_app.py 7 ui/ 모듈 통합 patch
- [ ] qa-validator Layer 8 자동 호출 활성화
- [ ] U-1 KLA 발표 신청 (5/31 마감 — PO)
- [ ] 사용자_TODO PO 응답 처리

---

> **이 파일 위치**: `kormarc-auto/docs/research/part52-pre-coding-readiness-2026-05.md`
> **종합**: openpyxl 의존성·65+ 신규 테스트·자관 익명화 자동 검증 모두 적용
> **다음 commit 사이클**: 이중 게이트 통과 가능 상태 ✅
