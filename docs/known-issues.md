# 알려진 이슈 / 타협 / 미해결

> 발견된 이슈를 기록. 해결되면 [DONE] 표시 + 해결 방법 추가.

---

## [2026-04-25] NL Korea API 응답 필드 매핑이 추정치

- **상황**: `nl_korea.py:_normalize`에서 `PUBLISHER_URL`을 발행지로 임시 사용. 공식 문서에 `PUBLICATION_PLACE`가 명시되지 않아 실응답 확인 전 추정.
- **영향**: 008 발행국부호와 264 ▾a가 부정확할 수 있음.
- **해결 조건**: 첫 실호출 시 응답 JSON을 docs/spec.md에 첨부 → `_normalize` 보정.
- **담당**: PO가 인증키 발급 후 Day 3에 확인.

---

## [2026-04-25] 발행국부호(008 15-17) 매핑 표가 부분적 [DONE 2026-04-26]

- **상황**: `mapping.py:PUBLICATION_PLACE_CODES`에서 일부 도시(인천, 충남 등) 부호가 정확하지 않음. 공식 KORMARC 매뉴얼 부호표를 모두 반영하지 못함.
- **영향**: 008 15-17이 'xx '로 표시되는 케이스 발생 가능.
- **해결 [v0.4.1]**:
  - 한국 17개 시도별 고유 코드로 분리 (이전엔 광역시가 모두 'ulk'로 통일된 버그).
  - 외국 35+개국 LC MARC Country Codes 추가 (xxu·ja·cc·enk·fr·gw 등).
  - `lookup_publication_country()` 헬퍼: 정확/부분/소문자 매칭, 영문 도시명 지원.
  - 회귀 테스트 8건 (`tests/test_mapping.py`).
- **잔여 작업**: 시·군·구 단위 미매핑은 여전히 도(道) 코드로 폴백. 자관별 표준 우선시 시 환경변수로 오버라이드 가능하게 추후 확장.

---

## [2026-04-25] hanja 라이브러리 `translate()` API 버전 의존성

- **상황**: `hanja_to_hangul`이 `hanja.translate(text, "substitution")` 호출. 라이브러리 버전에 따라 API 시그니처 다를 수 있음.
- **영향**: 880 한자 병기 자동 생성 실패 시 원본 유지 (defensive).
- **해결 조건**: 실제 hanja 라이브러리 설치 후 테스트, 필요 시 분기 처리.

---

## [2026-04-25] [DONE] Phase 2 Claude Vision 구현 완료

- **상황 (해소됨)**: `vision/claude_vision.py`의 `extract_metadata_from_photos()`가 NotImplementedError였음.
- **해결**: `_anthropic_client.py` 공유 클라이언트 + 2단계 (Haiku ISBN → Sonnet 종합) + tool_use 강제 + diskcache 30일 + prompt caching. Pillow로 1568px 리사이즈로 비용 ½.
- **남은 작업**: 실 사진 5~10장으로 정확도 측정.

---

## [2026-04-25] [DONE] Phase 3 KDC AI 분류 구현 완료

- **상황 (해소됨)**: `classification/kdc_classifier.py`의 AI 폴백이 자리만 있었음.
- **해결**: Sonnet 4.6 + KDC 6판 주류·강목 인라인 시스템 프롬프트 + tool_use → 후보 1~3개 (신뢰도·이유). prompt caching로 재호출 비용 절감.
- **남은 작업**: 실제 KDC 미부여 ISBN 20~30건으로 정확도 측정.

---

## [2026-04-25] OneDrive 동기화 충돌 위험

- **상황**: 작업 폴더가 OneDrive 안. 동시 동기화 중 git 작업 시 충돌 가능.
- **영향**: `.pyc`·`__pycache__`·`.venv` 동기화로 OneDrive 용량 낭비.
- **해결 조건**: `.gitignore`로 1차 차단 완료. OneDrive 설정에서도 `.venv` 제외 권장.
