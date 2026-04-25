# 테스트 결과 누적

> Phase별 정확도·회귀 추적. 새 테스트마다 표를 추가하세요.

---

## Phase 1 — ISBN → KORMARC

### 테스트 일시: (미실행 — `pytest` 실행 후 채워넣기)

| ISBN | 책 정보 | API 응답 | 채워진 필드 | KORMARC 생성 | .mrc 크기 | 비고 |
|------|--------|---------|-----------|------------|----------|------|
| 9788936434120 | 한강, 작별하지 않는다, 창비 | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788932020789 | 김영하, 작별인사 | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788937834790 | 정유정, 28 | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788954692410 | 한국 인문서 (예시) | ⏳ | ⏳ | ⏳ | ⏳ | |
| 9788972752310 | 자연과학 (예시) | ⏳ | ⏳ | ⏳ | ⏳ | |

---

## 골든 데이터셋 비교

(추후) 100권의 정답 KORMARC와 자동 생성 결과를 비교한 필드별 일치율.

| 필드 | 자동 생성 정확도 | 비고 |
|------|---------------|------|
| 020 (ISBN) | ⏳ | |
| 245 (표제) | ⏳ | |
| 100 (저자) | ⏳ | |
| 264 (발행) | ⏳ | |
| 300 (형태) | ⏳ | |
| 056 (KDC) | ⏳ | 3자리 / 6자리 별도 |
| 650 (주제명) | ⏳ | |
| 880 (병기) | ⏳ | 페어링 정확도 |

---

## v0.3 추가 — Phase 2/3/3+ + 서버 + UI 검증

### 자동 테스트 (mock)

- 2026-04-25: pytest 52건 모두 통과 (`test_anthropic_client` 8, `test_isbn` 19, `test_kdc` 8, `test_search` 3, `test_server` 7, `test_vision` 7)
- 린트: ruff check 0 errors
- 환경: Python 3.12.10 + .venv + 모든 의존성 설치

### 수동 검증 (PO가 키 설정 후 진행)

| 항목 | 명령 | 기대 |
|---|---|---|
| Phase 1 회귀 | `kormarc-auto isbn 9788936434120` | .mrc 생성 |
| Phase 2 사진 | `kormarc-auto photo cover.jpg` | Vision 추출 |
| Phase 3 KDC AI | `kormarc-auto isbn <KDC 미부여>` | 후보 3개 |
| 검색 | `kormarc-auto search "한강"` | 후보 표 |
| 서버 | `kormarc-server` + `curl /healthz` | `{"ok":true}` |
| UI | `kormarc-ui` | 모바일 친화 4탭 |
| 모바일 터널 | `cloudflared tunnel --url http://localhost:8501` | trycloudflare URL |

---

## 골든 데이터셋 정확도 측정 (PO 통찰 반영)

> **PO 결정**: "정답"은 국립중앙도서관·각 도서관 검색 결과를 사용한다.
> 사서들이 이미 검증한 데이터를 그대로 정답 KORMARC로 변환해 비교.

### 2단계 워크플로

**1) 정답 자동 수집** — `scripts/build_golden_dataset.py`
- NL Korea ISBN 서지 API로 메타 가져옴 → KORMARC 빌드 → `tests/samples/golden/{ISBN}.mrc`
- KOLIS-NET으로 다른 도서관 분류 비교 정보도 함께 수집 (보조)
- 시드 50건 (다양한 KDC) 또는 `--isbns my_list.txt`

**2) 정확도 측정** — `scripts/accuracy_compare.py`
- 우리 풀 파이프라인(aggregator + 알라딘·카카오 + KDC AI) vs 골든 직답
- 필드별 일치율: ISBN / 245 본표제 / 100 저자 / 264 출판사 / 056 KDC
- exact / partial / mismatch / one_empty / both_empty 5단계

### 사서 신뢰 입증 흐름

베타 사서 첫 미팅에서:
1. `python scripts/build_golden_dataset.py --limit 30` 실행 → 30건 정답 수집
2. `python scripts/accuracy_compare.py --output reports/<날짜>.json` → 표 출력
3. 사서에게 "ISBN/본표제/저자 99% 일치, KDC는 NL Korea 미부여 케이스에 AI 보조" 입증
4. 의심 케이스만 직접 확인 → 결제 결정 근거
