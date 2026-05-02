# ADR-0020: 책단비 hwpx 자동 라벨 — 선택 의존성 패턴

## Status
Accepted (2026-04-29)

## Context

자관 「○○도서관」 5년 책단비 1,328건 (실측 ≈ 매일 1건) = 사서 페르소나 1순위 통증점.

`docs/sales/INDEX.md`의 "ROI 1순위 4 기능" 첫 번째 항목 = "책단비 hwp 자동". 수동 hwp 작성 시 권당 약 5~7분 (제목·저자·ISBN·청구기호·등록번호·신청관 모두 손으로 입력). 200관 캐시카우 평가축 §0 (사서 마크 시간 단축) 직접 양수.

기술 제약:
- HWP/HWPX는 한글과컴퓨터 독점 포맷. python-hwpx 라이브러리는 존재하나 PyPI 안정성·릴리즈 주기 불확실.
- 의존성을 hard-add 하면 모든 사서가 hwpx 미사용 시에도 설치 부담.
- 자관 외 PILOT 사서(학교 사서·대학 사서)는 책단비 자체가 은평구 한정이라 무관.

## Decision

**선택 의존성(optional dependency) 패턴** 채택. hard requirement 추가 없이 try/except로 분기.

```python
try:
    import hwpx
    HAS_HWPX = True
except ImportError:
    HAS_HWPX = False
```

`generate_label()` 한 함수가 두 분기를 흡수:
- HAS_HWPX=True → `_write_hwpx()` 시도, 실패 시 .txt 폴백 + WARN 로그
- HAS_HWPX=False → 즉시 .txt 폴백

라벨 텍스트 청사진은 `generate_label_text()` 한 곳이 단일 진실 소스. hwpx·txt 양쪽이 같은 텍스트를 사용하므로 양식 변경 비용 1곳 갱신.

## Consequences

### 쉬워지는 것

- hwpx 미사용 사서(학교·대학·작은도서관)는 추가 설치 0
- 자관(은평) 사서가 `pip install python-hwpx` 한 줄만 추가하면 .hwpx 자동
- 책단비 양식 변경 시 `generate_label_text()` 한 함수만 수정
- 자관 5년 1,328건 = 권당 5분 × 1,328 = 110시간 절감 누적 가치 영업 자료
- 다른 자치구 자체 양식 (책가방·책마중·강남·강북) 확장 시 같은 패턴 재사용

### 어려워지는 것

- hwpx API가 라이브러리 메이저 버전마다 바뀔 수 있음 → `_write_hwpx()` 좁은 어댑터 1곳에 캡슐화로 회피
- .txt 폴백이 사서 hwp에 붙여넣기 단계 1회 추가 (양식·서식 손실)
  - 회피: PILOT 1주차 사서에게 "hwpx 자동 라벨" 옵션 명시 + 설치 안내 cheat sheet

### 트레이드오프

- 의존성 단순함 ↔ hwpx 미설치 환경에서 사서 추가 단계 1회
- 우리 선택: 단순함 (대부분 사서는 책단비 비대상 — 자관만 1관)
- 자관 PILOT 결과가 양호하면 v0.5.x에서 `pip install kormarc-auto[chaekdanbi]` extras 그룹 추가 검토

### 후속

- v0.5.x: pyproject.toml `[project.optional-dependencies]`에 `chaekdanbi = ["python-hwpx>=...]"` 추가 (트리거: 자관 PILOT 4주 완주 + 사서 만족도 4.0+)
- 책가방·책마중·강남·강북 자치구 양식 추가 시 같은 모듈 패턴 (chaekdanbi → other_district)
- 라벨 PDF (Avery L7160) 출력 옵션은 기존 `output/labels.py` 활용

## Sources

- 자관 5년 1,328건 책단비 대장 (PO 실측, learnings.md)
- `docs/sales/INDEX.md` ROI 1순위 4 기능 §1
- `src/kormarc_auto/interlibrary/exporters.py` (책나래·책바다·RISS 양식 어댑터 — 같은 패턴 참조)
- ADR-0009 §33 비활성 (선택 의존성 패턴 선례)
- python-hwpx PyPI (https://pypi.org/project/python-hwpx/) — 안정성 모니터링 대상
