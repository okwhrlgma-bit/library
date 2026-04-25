# 트러블슈팅

## 셋업·실행

### `setup-once.bat` 실행 후 "Python 미설치"
- winget이 PATH 갱신을 위해 새 셸을 요구함
- 해결: 모든 cmd 창 닫고 `setup-once.bat` 재실행

### `pip install -e ".[dev]"` 실패 — pyzbar
- Windows: 보통 자동 OK. 실패 시 "Visual C++ Redistributable" 설치
- macOS: `brew install zbar` 후 재시도
- Linux: `sudo apt-get install libzbar0`

### `kormarc-auto: command not found`
- venv 미활성화: `.\.venv\Scripts\Activate.ps1` (Windows) 또는 `source .venv/bin/activate`
- 또는 `python -m kormarc_auto.cli ...` 직접 호출

## 환경변수

### `info` 실행 시 "❌ 미설정"
- `.env` 파일에 키 채워넣었는지 확인
- 따옴표·공백 없는지: `NL_CERT_KEY=abc123` (NOT `NL_CERT_KEY = "abc123"`)
- 셸을 `.env` 작성 후 새로 열어야 적용

### 외부 API 호출 시 "타임아웃"
- 네트워크 점검 (`ping www.nl.go.kr`)
- VPN·방화벽 영향 가능 — 끄고 재시도
- API 자체 일시 장애 가능 — 다른 API는 작동? `kormarc-auto info` 후 다른 ISBN 시도

### Anthropic 호출 "401 Unauthorized"
- 키 만료 또는 오타. console.anthropic.com에서 새 키 발급
- `sk-ant-` 로 시작하는지 확인

## 서버

### `kormarc-server` 시작 실패 — 포트 충돌
- 다른 프로그램이 8000 사용 중. `KORMARC_PORT=9000 kormarc-server` 또는 해당 프로그램 종료

### `/isbn` 호출 시 502
- 외부 API 모두 실패. 로그(`logs/`)에서 어느 소스가 실패했는지 확인
- 캐시 문제일 수 있음: `rm -rf .cache/kormarc-auto` 후 재시도

### 모바일에서 접속이 안 됨
- 단발 터널이면 URL이 바뀜 — 새 URL 발급 필요
- HTTPS 인증서: Cloudflare 터널은 항상 유효. 폰 시간 동기화 확인

## Streamlit UI

### 한글이 깨짐
- `.env`에 `PYTHONIOENCODING=utf-8` 있는지 확인
- 브라우저 인코딩 자동 감지 — 다른 브라우저 시도

### `/docs/quickstart-librarian.md` 링크가 404
- 사이드바 expander로 인라인 표시되도록 수정됨 (v0.3 이후)

### 사진 업로드 시 "Vision 실패"
- ANTHROPIC_API_KEY 미설정 → `.env` 확인
- 이미지 너무 크면 Pillow가 자동 1568px 리사이즈. 매우 큰 RAW 파일은 미리 변환 권장

## KORMARC 결과

### KDC가 "000 (fallback)"으로 나옴
- NL Korea가 KDC 미부여 + AI 호출 실패 (ANTHROPIC_API_KEY 미설정 등)
- 사서가 직접 KDC 입력해야 — 이는 정상 동작 (자동 결정 금지)

### 008 필드 길이 오류
- 발행연도가 4자리 숫자가 아님 — 외부 API 응답 이상
- `docs/known-issues.md`의 발행국부호 매핑 보강 필요

### KOLAS 반입 거부
- `kolas_strict_validate` 결과 확인 (응답에 포함)
- 020 ISBN 체크섬 / 040 ▾a / 245 ▾a / LDR 24자 점검

## 모바일 터널 (cloudflared)

### `cloudflared: command not found`
- 셸을 `setup-once.bat` 후 새로 열어야 PATH 적용
- 직접 설치: `winget install --id Cloudflare.cloudflared --silent`

### `tunnel: connection refused`
- 서버가 안 떠있음. `start-server.bat` 또는 `start-ui.bat` 먼저 실행

### 영구 터널 — 도메인 연결 안 됨
- DNS 전파 5~30분 대기
- `cloudflared tunnel route dns ...` 명령 다시 확인

## 사용량·결제

### 사서가 "한도 초과" 응답을 받음
- 정상 — 50건 무료 사용 후 결제 안내. PO와 협의 (계좌 입금 / 카카오페이)
- 백업본이 있으면 `scripts/backup_logs.py --restore` 로 복구 (테스트 환경)

### `/admin/stats` 403
- 관리자 키 필요. `.env`의 `KORMARC_ADMIN_KEYS`에 등록된 키만

### 사용량 데이터 손실 우려
- `python scripts/backup_logs.py` 매주 1회 권장
- OneDrive·Google Drive 자동 동기화 폴더에 `backups/` 두면 자동 백업

## 정확도 측정

### `accuracy_compare` 결과가 모두 mismatch
- 골든 .mrc와 우리 결과 모두 비어있는지 확인
- 외부 API 키 미설정으로 우리 파이프라인이 데이터를 못 가져옴 가능

### 골든 수집 시 "nl_error"
- `NL_CERT_KEY` 미설정 또는 만료. nl.go.kr/seoji에서 키 갱신 (1~3일)

## 그래도 모르겠으면

1. `kormarc-auto info` 출력 + `logs/` 마지막 30줄 + 입력 ISBN을 PO에게
2. GitHub Issues에 재현 단계 기록 (env 키는 절대 X)
