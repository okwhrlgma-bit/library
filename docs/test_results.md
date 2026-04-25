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
