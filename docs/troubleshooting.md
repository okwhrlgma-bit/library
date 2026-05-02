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

## 자관 PILOT 트러블슈팅 (2026-04-28 신규)

### 자관 .mrc 174 4단 검증 실패

**증상**: 자관 .mrc 파일이 4단 검증에서 fail
**원인 분석**:
1. **MARC8 인코딩** (자관 발견 — UTF-16LE little-endian) → pymarc `force_utf8=False` 또는 인코딩 자동 감지
2. **자관 등록번호 prefix** (EQ/CQ) 미인식 → config.yaml.kolas_register.registration_prefix 자관별 변형 (정책 ③)
3. **자관 청구기호 형식** (`시문학811.7/ㅇ676ㅁ`) 별치기호 미매핑 → 자관 별치기호 사전 등록

**해결**:
```bash
# 자관 PILOT 사전 검증
python -m kormarc_auto.cli validate "D:/PILOT_자관/수서/2024/2024_마크파일/정기1차/*.mrc" \
  --library-id pilot_lib \
  --encoding-auto-detect
```

### 자관 책단비 hwp 4 양식 자동 mail merge 실패

**증상**: 책단비 만료/반납/제공/지하철 hwp 양식 출력 X
**원인**:
1. `python-hwpx` 의존성 미설치 (ADR 0021 PO 결정 후 활성)
2. 자관 양식 토큰 (`<[내숲]><[은평]><권>`) 미매핑

**해결**:
1. ADR 0021 PO 결정 → `python-hwpx>=0.5` 설치
2. config.yaml에 자관 토큰 등록 (정책 ③):
```yaml
forms:
  chaekdanbi:
    library_name_token: "[내숲]"
    region_token: "[은평]"
    template_dir: "data/forms/eunpyeong_naesum/chaekdanbi/"
```

### 자관 xlsm 매크로 import 시 "VBA 매크로 보존 안 됨"

**증상**: xlsm 시트 import 후 VBA 매크로 사라짐
**의도된 동작**: 자관 IP 보호 (ADR 0088) — VBA 미접근·시트 데이터만 추출
**해결**: 동일 기능을 우리 SaaS Python 자체 구현 (ADR 0087):
- `output/insert_paper.py` (신착도서 간지)
- `interlibrary/request_label_generator.py` (책두레 쪽지 8장)
- `chaekdanbi/auto_label_generator.py` (책단비 띠지)

### KOLAS F12 엑셀 import 시 "컬럼 매핑 실패"

**증상**: KOLAS 책두레 F12 엑셀출력 → 우리 SaaS import 시 컬럼 인식 X
**원인**: KOLAS III 버전 차이 (자관 보유 ver.20210322001 vs 최신)
**해결**:
1. `inventory/kolas_f12_importer.py` 컬럼 매핑 자동 추론 (heuristic)
2. 자관 9 컬럼 정합 (순번·구분·등록번호·도서명·권차·서명·저자·출판사·청구기호)
3. 컬럼명 fuzzy 매처 (rapidfuzz)

### 페르소나별 시연 시 페인포인트

| 페르소나 | 페인포인트 | 해결 |
|---|---|---|
| ★ 매크로 사서 | "내 매크로가 더 빨라요" | xlsm 시트 자동 import + 사서 매크로는 그대로 보존 (병행 사용) |
| 수서 사서 | "KOLAS와 다른 결과가 나와요" | 우리는 KORMARC 표준 + 자관 prefix 정책 ③ |
| 종합 사서 | "AI가 KDC 잘못 분류해요" | AI 후보 3개 (사서 검토·결정 — 우리 영역 X) |
| 영상 편집 사서 | "내 일에 도움 안 돼요" | ✅ 우리 영역 X 명시 (사서 본업 = 카탈로깅) |

### Streamlit 모바일 반응형 안 보임

**증상**: 자관 사서 폰에서 Streamlit UI 깨짐
**해결**:
1. `streamlit_app.py` 모바일 반응형 4탭 정합 검증
2. Cloudflare Tunnel 영구 URL 사용 (단발 X)
3. 폰 홈 화면에 추가 (PWA 형태)

---

## 5월 마감 임박 ★ (KLA 발표 신청)

| 액션 | 마감 | 트러블 |
|---|---|---|
| KLA 전국도서관대회 발표 신청 | 2026.5.31 | 자관 PILOT 4주 결과 미확보 → 자관 6년 NPS·.mrc 174·5 시스템 등 기존 자료 인용 |
| 사서교육원 강의 제안서 | 2026.5월 | 자관 직원 교육자료 (2023·2024) 인용 |

---

## 그래도 모르겠으면

1. `kormarc-auto info` 출력 + `logs/` 마지막 30줄 + 입력 ISBN을 PO에게
2. GitHub Issues에 재현 단계 기록 (env 키는 절대 X)
3. 자관 PILOT 트러블 시 `docs/po-pilot-readiness-checklist.md` 9 ADR 결정 영역 점검
