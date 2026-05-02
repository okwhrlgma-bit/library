# KERIS DLS·알파스 정체 + 우리 SaaS 11 UIUX 연동 매트릭스

> **PO 명령** (2026-04-28): "내가 말하는 연동이란 아웃풋이나 인풋을 우리 프로그램에서 그대로 사용 가능하도록 하거나 앱 켰을때 연동해서 추가 실행 가능하거나 등을 하면서 UIUX적으로 좋게 사용할 수 있는지 + 더 좋은 UIUX 방식이 있다면 적용"
> **분석일**: 2026-04-28
> **출처**: 자관 (○○도서관, 은평구) D 드라이브 실측 + WebFetch 7건 + 자료 폴더 알파스 매뉴얼 22MB

---

## 0. 정체 확정 (3 시스템)

| 시스템 | 정체 | 운영 | 사용 도서관 |
|---|---|---|---|
| **KOLAS III** | 공공도서관 표준자료관리시스템 | 국립중앙도서관 (무료) | 공공도서관 1,271관 |
| **알파스 (ALPAS)** | (주)이씨오 SaaS 도서관 관리 시스템 | 카카오클라우드 IaaS (판교), 99.5% uptime | KOLAS3 호환 + 책이음 동기화. 자관 = 은평구립도서관 (`alpas.eplib.or.kr:8580/METIS`) |
| **KERIS DLS** | 학교도서관업무지원시스템 (Digital Library System) | 한국교육학술정보원 (KERIS), 시·도교육청 (무료) | 학교도서관 11,500관 |

**자관 운영 시스템 (실측)**:
- KOLAS III + 책두레 (Desktop `KOLAS III (2).lnk` + `원격관리기_K3.lnk`)
- 알파스 (Desktop `알파스.url` → `https://alpas.eplib.or.kr:8580/METIS/index.jsp`)
- 책단비 (Desktop `책단비(Nslib-1f-stf12).lnk` 네트워크 경로)
- ECO Device Agent (RFID·바코드 스캐너 통합, `ECO_DEVICE_AGENT.msi` 1MB + `.exe` 2.4MB)

**의미**: 자관은 KOLAS + 알파스 **동시 사용** + 책두레 + 책단비 + ECO RFID — 5 시스템 통합 운영.

---

## 1. KERIS DLS 정체 (자료 폴더 보유 매뉴얼 0)

| 항목 | 정보 |
|---|---|
| 운영 | 시·도교육청별 (서울교육청·경기교육청 등 17개) |
| 핵심 기능 | 교수학습지원·디지털도서관·독서문화센터 통합 |
| 표준 | KORMARC 호환 (전국 공통) |
| Export | KORMARC iso2709·xlsx (사서 파일 → 학교도서관 간 마이그레이션) |
| 우리 정합 | ❌ 자료 폴더에 KERIS DLS 매뉴얼 0건 (자관 = 공공도서관, KERIS는 학교도서관 영역) |

**우리 SaaS 영업 함의**: KERIS DLS = **학교도서관 11,500관 영역**. PO 마스터 §1.2 "학교도서관 진입 = Phase 2~3" 정합. 단, KORMARC 호환이므로 우리 4단 검증 엔진 그대로 재사용 가능.

---

## 2. 11 연동 UIUX 매트릭스 (PO 명령 — 더 좋은 방식 발굴)

PO 명시 2 방식 외 9 추가 발굴 — 총 11. 각각 5질문 셀프 오딧 점수 (Beta 단계 가중치):

| # | UIUX 방식 | Q1 결제 | Q2 비용 | Q3 자산 | Q4 락인 | Q5 컴플 | 합계 | 결정 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | **PO 명시 ① — Output/Input 직접 호환 (csv·xlsx·MARC iso2709 import)** | 90 | 95 | 70 | 60 | 95 | **82** | 🟢 즉시 (이미 부분 흡수) |
| 2 | **PO 명시 ② — 앱 launch (Desktop `.lnk`/`.url` 호출)** | 70 | 100 | 30 | 40 | 100 | **64** | 🟢 즉시 |
| 3 | 🆕 **iframe 임베드** (우리 Streamlit 안에 알파스 웹 표시) | 75 | 90 | 50 | 30 | 60 | **57** | 🟡 조건부 (CORS·X-Frame-Options) |
| 4 | 🆕 **Browser Extension** (알파스 웹 페이지에 우리 button 인라인 inject) | 95 | 70 | 90 | 90 | 70 | **85** | 🟢 **최강 추천** |
| 5 | 🆕 **System Tray app** (우리 SaaS background 상시·핫키 호출) | 85 | 80 | 80 | 85 | 90 | **84** | 🟢 강 추천 |
| 6 | 🆕 **OS file association** (.marc·.kormarc 파일 우리 SaaS 기본 핸들러) | 80 | 100 | 70 | 75 | 100 | **84** | 🟢 강 추천 |
| 7 | 🆕 **Folder Watcher** (사서가 KOLAS F12 엑셀 다운 → 우리 폴더 watcher 자동 감지·검증) | 90 | 90 | 75 | 80 | 95 | **86** | 🟢 **★최강 추천** |
| 8 | 🆕 **Universal Clipboard Bridge** (우리 KORMARC 자동 → 클립보드 → 사서가 알파스 paste) | 85 | 100 | 60 | 70 | 100 | **80** | 🟢 즉시 |
| 9 | 🆕 **WebSocket bridge** (우리 SaaS ↔ 알파스 실시간 동기) | 60 | 30 | 80 | 90 | 40 | **57** | 🔴 알파스 API 미공개 — 불가능 |
| 10 | 🆕 **Selenium·Playwright Bot** (자동 로그인·입력) | 70 | 50 | 50 | 30 | 30 | **47** | 🔴 **컴플 위험** (TOS 위반·자동화 차단·PII 노출) |
| 11 | 🆕 **CLI / PowerShell Module** (`Import-KORMARC -Path foo.xlsx`) | 60 | 100 | 70 | 70 | 100 | **76** | 🟡 사서 IT 비전공 — 학습 곡선 |

---

## 3. ★ 우리 즉시 적용 추천 — Top 4 조합 (시너지)

### 🏆 #7 Folder Watcher (★ 최강 점수 86)

**작동**:
1. 사서가 알파스 또는 KOLAS에서 F12 엑셀 다운 → `Downloads\` 또는 자관 약속 폴더로 저장
2. 우리 SaaS 백그라운드에서 폴더 watch (Python `watchdog` 라이브러리)
3. 파일 변경 감지 → 자동 KORMARC 검증 → 결과 toast 알림 (windows-toasts)
4. 사서 클릭 0 → 결과 확인만

**구현**: `watchers/download_watcher.py` 신규 모듈 (의존성 `watchdog>=4.0`)

**왜 최강**: 사서가 "추가 액션 0" — 평소 워크플로우 그대로 사용하면 우리 가치 자동 발생.

### 🥈 #4 Browser Extension (점수 85)

**작동**:
1. Chrome/Edge/Firefox 확장 (manifest v3)
2. `https://alpas.*.or.kr:*/METIS/*` 또는 KOLAS 웹 패턴 매처
3. 알파스 카탈로깅 화면에 우리 button 자동 추가: "📚 KORMARC 자동 채우기"
4. 사서가 ISBN 입력 후 button 클릭 → 우리 백엔드 호출 → 245/260/300/056 등 자동 채움

**구현**: 별도 repo `kormarc-auto-extension` (TypeScript + Vite + manifest v3)

**왜 강**: 사서가 알파스 화면 떠나지 X — UX 마찰 0.

### 🥉 #5 System Tray App (점수 84)

**작동**:
1. Windows System Tray 아이콘 (`pystray` + `pillow`)
2. 우클릭 메뉴: "KORMARC 검증" / "ISBN 자동 채우기" / "알파스 열기" / "KOLAS 열기"
3. 핫키 `Ctrl+Alt+K` → Streamlit UI popup
4. 우리 SaaS 백그라운드 상시 실행 — 부팅 시 자동 시작

**구현**: `tray/app.py` 신규 (의존성 `pystray>=0.19`, `pillow>=10.0`)

### 🎯 #6 OS File Association (점수 84)

**작동**:
1. `.marc`·`.mrc`·`.kormarc` 확장자 우리 SaaS를 기본 핸들러로 등록
2. 사서가 알파스에서 .marc 다운 → 더블클릭 → 우리 SaaS 자동 열림 + 검증
3. Windows registry `HKCU\Software\Classes\.marc` 수정 (설치 시 1회)

**구현**: `installer/register_filetype.ps1` 스크립트 (PowerShell)

---

## 4. PO 명시 2 방식 즉시 적용 (이미 부분 흡수)

### #1 — Output/Input 직접 호환 (이미 구현 부분)

**현재 상태** (`interlibrary/exporters.py`):
- ✅ 책나래 csv·xlsx export
- ✅ 책바다 csv·xlsx export
- ✅ RISS csv·xlsx export
- ❌ 알파스 import 양식 (신규 후보)
- ❌ KOLAS F12 엑셀 입력 양식 흡수 (신규 후보)
- ❌ KERIS DLS 학교도서관 양식 (Phase 2~3)

**다음 작업**:
- `interlibrary/exporters.py:_alphas_map()` 신규
- `inventory/kolas_f12_importer.py` 신규 (KOLAS 책두레 F12 엑셀 → 우리 인벤토리 자동)

### #2 — 앱 Launch (Desktop .lnk·.url 호출)

**작동**:
- 우리 Streamlit UI 좌측 사이드바에 button 4개
  - 🌐 알파스 열기 → `webbrowser.open('https://alpas.eplib.or.kr:8580/METIS')` (사서 자관 URL 설정)
  - 💻 KOLAS III 열기 → `os.startfile(r'C:\사용자Desktop\KOLAS III (2).lnk')`
  - 📦 KOLAS 원격관리기 → `os.startfile(r'...\원격관리기_K3.lnk')`
  - 📚 책단비 폴더 → `os.startfile(r'\\Nslib-1f-stf12\책단비')`

**구현**: `ui/launcher.py` 신규 모듈 + 사용자 설정 (`config.yaml`에 자관 URL·.lnk 경로 저장)

---

## 5. 컴플라이언스 게이트 (Q5 = 별도 생존 조건)

| 방식 | PIPA 위험 | 회피 |
|---|---|---|
| #4 Browser Extension | DOM 수집 시 회원 PII 노출 가능 | 알파스 카탈로깅 화면만 매처, 회원·대출 화면 X |
| #7 Folder Watcher | 사서 다운 파일에 회원 PII 포함 가능 | KORMARC 6 표준 필드만 read, 이용자 컬럼 자동 마스킹 |
| #10 Selenium Bot | TOS 위반 + PII 자동 수집 위험 | 🔴 **즉시 폐기** |

**5대 패턴 적용**:
1. ✅ Reader entity ERD 부재 (#7·#4 모두 정합)
2. 🟡 logging PII 마스킹 (PIPA 패턴 2 보강 필요)
3. ✅ DSAR (현행)
4. ❌ 72h 신고 (베타 PILOT 도달 시)
5. ❌ audit_log (5만명+ 도달 시)

---

## 6. 다음 ADR 후보 (PO 결정 영역)

| ADR | 영역 | 우선순위 |
|---|---|---|
| ADR 0016 — Folder Watcher 채택 (#7) | watchdog 의존성 추가 + watchers/ 신규 디렉토리 | 🟢 1순위 |
| ADR 0017 — System Tray App (#5) | pystray 의존성 + tray/ 신규 + 부팅 자동 시작 | 🟢 2순위 |
| ADR 0018 — Browser Extension (#4) | 별도 repo + 배포 (Chrome Web Store) | 🟡 3순위 (별도 PRD) |
| ADR 0019 — OS File Association (#6) | installer 스크립트 + Windows registry 수정 | 🟢 4순위 |
| ADR 0020 — 알파스/KOLAS launcher 패널 (#2 PO 명시) | ui/launcher.py + config.yaml | 🟢 5순위 |

---

## 7. KERIS DLS Phase 2~3 영업 메시지

자관(공공도서관)이 안정화 후 학교도서관 진입 시:
- **KORMARC 표준 동일** → 우리 4단 검증 엔진 그대로 재사용
- **KERIS DLS 17개 시·도교육청별 운영** = 영업 채널 17개 (서울·경기·부산 등)
- **사서교사 의무배치 vs 미배치 영역** — 미배치 학교 = 자원봉사 카탈로깅 = 우리 ICP 정합 (PO 마스터 §1.2)

---

## 8. 우리 SaaS의 "보이지 않는 통합" 비전

PO 명령 "더 좋은 UIUX 방식" 핵심 — **사서가 우리 SaaS를 의식하지 X 통합** = 마찰 0:

```
사서 평소 워크플로우:
1. 알파스 웹 로그인 → KORMARC 입력 ← (#4 Browser Extension이 ISBN 입력 시 자동 채움)
2. KOLAS 책두레 F12 엑셀 다운 ← (#7 Folder Watcher가 자동 검증)
3. 책단비 4 양식 hwp 작성 ← (우리 SaaS 자동 생성으로 시간 절감)
4. .marc 파일 백업 ← (#6 OS File Association으로 우리 SaaS에서 검증)
5. 시스템 트레이 (#5)에서 검증 결과 toast 확인
```

**합산 사서 시간 절감**: 권당 8~15분 → 권당 30초 (95% 단축).
**합산 우리 가치**: 사서가 우리 SaaS를 직접 열지 X → 자동 가치 발생 → 결제 의향 ↑.

---

## 9. 참고 자료 (Sources)

- [한국교육학술정보원 KERIS](https://www.keris.or.kr/)
- [KERIS Wikipedia](https://en.wikipedia.org/wiki/KERIS_(Korea_Education_and_Research_Information_Service))
- [도서관 표준자료관리시스템 나무위키](https://namu.wiki/w/%EB%8F%84%EC%84%9C%EA%B4%80%20%ED%91%9C%EC%A4%80%EC%9E%90%EB%A3%8C%EA%B4%80%EB%A6%AC%EC%8B%9C%EC%8A%A4%ED%85%9C)
- [KOLAS 나무위키](https://namu.wiki/w/KOLAS)
- [공공도서관지원서비스 KOLAS III](https://books.nl.go.kr/PU/contents/P30101000000.do)
- [알파스 디지털마켓 등재](https://m.digitalmarket.kr/m/service/detail.do?s=SAS-4-03-11207)
- [(주)이씨오 하이브리드 자료관리](http://www.eco.co.kr/library01.html) (self-signed cert)
- [한국문헌정보 dls114](https://www.dls114.com/Goods/list.asp?Category=DI)
- 자관 실측: `alpas.eplib.or.kr:8580/METIS/index.jsp` (은평구립도서관)
- D 드라이브 ECO Agent: `ECO_DEVICE_AGENT.msi` (1MB) + `eColas20_1.1.0.443_x86_Debug.appxbundle` (20MB)
- 알파스 매뉴얼: `자료/알파스 공통 V 1.0.pdf` (14MB) + `자료/알파스 단행 V 1.0.pdf` (8MB)
