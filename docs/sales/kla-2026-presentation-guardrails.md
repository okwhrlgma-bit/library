# KLA 2026-05-31 발표 가드레일 (D-28 ~ D-0)

> 한국도서관협회 KLA 전국도서관대회 (2026-05-31) 부스/발표 일정.
> 발표일까지 절대 깨지면 안 되는 가드레일 (자동 검증 우선).

---

## 0. 카운트다운 (D-28 = 2026-05-03)

| D-Day | 날짜 | 마감 작업 |
|---|---|---|
| D-28 | 2026-05-03 | 가드레일 작성·시연 시나리오 첫 검증 |
| D-21 | 2026-05-10 | 4 페르소나 시연 자동 스크립트 |
| D-14 | 2026-05-17 | 부스 노트북 환경 재현 가이드 |
| D-7  | 2026-05-24 | 발표 슬라이드 ↔ 데모 결과 정합 검증 |
| D-3  | 2026-05-28 | fallback 영상 사전 녹화 |
| D-1  | 2026-05-30 | 부스 노트북 dry-run + 시연용 ISBN 50개 사전 캐시 |
| D-0  | 2026-05-31 | 발표·노트북만 |

---

## 1. 5분 시연 시나리오 (가드레일 #1)

### 시나리오 (3회 평균 5초 이내 완료)
```
[1단계] ISBN 9788937437076 입력 → Enter
[2단계] kormarc-auto가 SEOJI/data4library/budgaeho 폴백 실행
[3단계] KORMARC .mrc 5초 내 출력
[4단계] KOLAS 반입 폴더 자동 복사
[5단계] 사서 검토 단계 표시 (자동화 vs 검수 정직)
```

### 자동 검증 스크립트
- `scripts/demo/kla_5min.sh` (작성 필요)
- 입력: 시연용 ISBN 50개
- 검증: 평균 응답 시간 < 5초·성공률 100%

---

## 2. 4 페르소나 시연 (각 1분·가드레일 #2)

### 페르소나 01 김지원 (사립 중학교 사서교사)
- ISBN 1권 입력 → DLS 521 자동 분류 (BK/SR/NB/LR/ET)
- 행정실장 1페이지 결재 PDF 자동 (decision_maker_pdf.py)
- "자원봉사 86% 학교 = 5분 도입" 메시지

### 페르소나 02 박서연 (작은도서관 관장 1인)
- 책단비 hwp 자동 (interlibrary/exporters.py)
- 1인 운영 통합 대시보드 (personal_stats_dashboard)
- 자원봉사 onboarding 5분 튜토리얼

### 페르소나 03 이민재 (P15 순회사서) — Phase 2-B
- 모바일 offline_queue 시연 (와이파이 X 시뮬)
- 셀룰러 회복 시 sync API 자동 push
- 학교별 자관 정책 전환 (multi-school 추후)

### 페르소나 04 정유진 (사립대 의과대학 분관)
- DDC + MeSH + LCSH 3중 분류 자동
- Alma MARCXML 출력 (의학분관 holdings 852)
- PubMed 검색 → KORMARC 변환

---

## 3. 실패 시나리오 정직 시연 (가드레일 #3)

### 3-1. ISBN 없는 자가출판
- 표지 사진 1장 입력 → Vision (Haiku → Sonnet) 폴백
- AI 추정 결과 + 사서 검토 단계 표시
- "100% 자동 X·사서 최종 검수 보존" 메시지

### 3-2. KDC 자동 실패
- 신간·SEOJI 미등록 ISBN
- 부가기호 → AI 추천 top-3 → 사서 1클릭 선택
- "자동화 ≠ 검수 제거" 메시지

---

## 4. 부스 노트북 환경 (가드레일 #4)

### 작성 필요: `docs/sales/kla-booth-laptop-setup.md`
- Python 3.12·venv·.env (4 API 키)
- 오프라인 캐시 (시연용 ISBN 50개 사전 fetch)
- Streamlit 부팅 < 3초
- 백업 노트북 1대 (장애 대비)

---

## 5. 발표 슬라이드 정합 (가드레일 #5)

### 정합 항목
- 슬라이드의 "권당 8분 → 1.5분" = 실 데모 측정값과 일치
- 슬라이드의 "자관 99.82%" = "PILOT 자관 1관 한정·다른 자관 cross-validation 진행 중" 정확 표현 (Reality Check 1-1 권고)
- 슬라이드의 "9 자료유형" = "17 세부 → KORMARC 표준 8 카테고리 매핑" 정정

### docs/sales/kla-2026-presentation-outline.md ↔ 데모 동기화
- 발표 D-7 (2026-05-24) 마감

---

## 6. fallback 영상 (가드레일 #6)

### 작성 필요: `scripts/demo/record_fallback.sh`
- 5분 시연 사전 녹화 (asciinema 또는 OBS)
- 부스 인터넷 장애 시 즉시 재생
- D-3 (2026-05-28) 마감

---

## 7. 자동 검증 체크리스트 (매일 cron)

```yaml
# .github/workflows/kla-guardrails.yml (작성 필요)
on:
  schedule:
    - cron: "0 0 * * *"  # 매일 00:00 UTC

jobs:
  guardrails:
    steps:
      - 5분 시연 검증 (scripts/demo/kla_5min.sh)
      - 4 페르소나 시연 (scripts/demo/persona_demo.sh)
      - 실패 시나리오 정직성 (scripts/demo/honest_failure.sh)
      - 슬라이드 ↔ 데모 정합 (docs/sales/kla-2026-presentation-outline.md grep)
      - 결과 PR comment (자동)
```

---

## 8. 헌법 정합

- 발표 카피 = §0·§12 양수만 사용
- "100% 자동" 약속 X = 사서 검수 단계 항상 명시
- 자관 99.82% = "PILOT 1관 한정" 정직 표현
- PIPA 2026.09 시행 명시 = 신뢰 ↑

---

## 9. 출처

- 명령 1-2 (PO 제공 명령 패키지)
- Reality Check 1-1 (`docs/audits/2026-05-03-reality-check.md`)
- Part 88 v2 전략 (결제자 ≠ 사서)
- Part 91 100점 로드맵 (Champion 4 모듈)
- KLA 공식 일정: https://www.kla.kr/
