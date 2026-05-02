# PILOT 사전 5분 체크리스트 (5/1주 월요일 09:00 PO)

> **사용 시점**: 5월 첫주 월요일 자관 사서 8명 PILOT 4주 회의 직전 5분.
> **목적**: PILOT 1주차 시연 차질 X — 환경·자료·일정 모두 확인.

---

## 0. 5분 체크 (월요일 08:55)

### 환경 (1분)

```powershell
cd "C:\Users\okwhr\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto"
git pull origin main   # cloud routine 자동 commit 받기
.\.venv\Scripts\Activate.ps1
kormarc-auto info      # 환경 진단
```

확인:
- ☐ Python 3.12 OK
- ☐ NL Korea API 키 OK (1~3 영업일 사전 발급 완료해야 함)
- ☐ 알라딘·카카오 API 키 OK
- ☐ KOLAS 마크 반입 폴더 경로 알고 있음

### 자료 (1분)

확인:
- ☐ `docs/sales/pilot-week1-action-manual.md` 폰에 띄움 또는 인쇄
- ☐ `docs/sales/librarian-5min-cheatsheet.md` A4 8장 인쇄 (자관 사서 8명)
- ☐ `docs/sales/pilot-result-templates/` 4 페르소나 양식 폴더 알고 있음
- ☐ KLA 5.31 발표 신청 양식 다운로드

### 일정 (1분)

확인:
- ☐ 5/1주 월요일 09:00 자관 사서 8명 PILOT 4주 안내 회의 (10분)
- ☐ 5/1주 월요일 18:00 사서 E 사서 30분 시연 (1주차 시작)
- ☐ 5/2주~5/4주 사서별 60분 시연 일정 잡기
- ☐ 5/5주 (5.31) KLA 발표 신청 마감 직전 슬라이드 채움

### 시연 환경 (1분)

확인:
- ☐ PO 노트북 + 자관 Wi-Fi
- ☐ Mobile hotspot 백업 1개 (Wi-Fi 끊김 대비)
- ☐ 카카오톡 음성 녹음 ON (시연 코멘트 즉시 캡처)
- ☐ 자관 신착 5권 ISBN 준비 (사서 E 사서가 가장 최근 신착)

### Cloud routine (1분)

확인:
- ☐ 1h routine `trig_01THW9GZG6G4sorCtwgJaR77` Enabled
- ☐ 주간 routine `trig_01Yb5Ze4eAwn4Z6srKDDu2Ma` Enabled
- ☐ 월간 routine `trig_01JGajzBSdRhMnS8KQPz5H8q` Enabled
- ☐ GitHub repo (https://github.com/okwhrlgma-bit/library) commit 늘어나는 중

문제 발생 시: `docs/cloud-routine-monitoring-guide.md` §3 참조.

---

## 1. 사서 8명 회의 발화 (10분 09:00)

```
"안녕하세요. 4월 동안 자관 .mrc 174 파일·3,383 레코드를 검증하는
KORMARC 자동화 시스템을 만들었습니다. 결과 99.82% 정합으로 한국 KOLAS
실무에 정확히 맞춰져 있습니다.

이번 5월 4주 동안 4 페르소나별로 각 사서님께 시연드리고 의견 받겠습니다.
1주차 매크로 사서 (사서 E), 2주차 수서 (사서 A), 3주차 종합 (4명),
4주차 통합 NPS와 결제 의향 측정.

그 결과를 5월 31일 한국도서관협회 전국대회 발표 신청에 사용하려고 하니,
인용 동의 여부도 물어볼 예정입니다. 물론 익명도 가능합니다.

질문 있으신가요?"
```

---

## 2. 1주차 시연 5분 사전 (월요일 17:55)

`docs/sales/pilot-week1-action-manual.md` §0 7 항목 다시 확인:

- ☐ PowerShell 환경 활성
- ☐ ISBN 5권 메모 준비
- ☐ KOLAS 마크 반입 폴더 경로 확인
- ☐ 카카오톡 음성 녹음 ON
- ☐ 본 매뉴얼 + week1 매뉴얼 + cheat sheet 폰에 다 띄움

---

## 3. 1주차 시연 직후 (5월 1주 월요일 18:30)

```powershell
.\.venv\Scripts\python.exe scripts\pilot_collect.py --persona macro
# 인터랙티브로 NPS·Q1·시간 절감 등 입력 → JSON 자동 저장
```

또는 `docs/sales/pilot-result-templates/macro-template.json` 복사 후 채워넣기 → `logs/interviews/2026-05-XX_PILOT_자관_사서 E.json`로 저장.

```powershell
# 즉시 집계 (페르소나별 NPS·Q1·KLA 인용 가능)
.\.venv\Scripts\python.exe scripts\aggregate_interviews.py
```

→ KLA 슬라이드 outline `docs/sales/kla-2026-presentation-outline.md` S6에 결과 채워넣기.

---

## 4. 위험 시나리오 + 회피

| 위험 | 회피 |
|---|---|
| Wi-Fi 끊김 | mobile hotspot 즉시 전환 |
| API quota 초과 | 다른 키 또는 다음날 재시도 |
| KOLAS 반입 실패 | 마크 형식 디버깅 X·"검토 후 답 드리겠습니다" |
| 사서 시간 부족 | 30분 정확 준수 |
| 사서 부정적 반응 | 정직하게 받기 ("어떤 부분이 안 맞으신지") |
| 사서 칭찬 일변도 | 단점도 솔직히 요청 (validation 회피) |

---

## 5. 다음 단계 (PILOT 4주 후)

- 5월 末: KLA 5.31 발표 신청 마감 (자관 PILOT 4주 결과 + 4 페르소나 NPS)
- 6월: 학교·작은·공공·대학·전문 PILOT 8~10관 모집 메일 250+125통
- 7월: 사서교육원 강의·도서관저널 기고
- 9월: PIPA 시행 직후 의학·법률·공공 영업
- 11~12월: 자치구 예산 편성 골든타임

---

## Sources

- `docs/sales/pilot-week1-action-manual.md` (사서 E 30분 시연 정밀)
- `docs/sales/pilot-package-2026-04-29.md` (4 페르소나 4주 시나리오)
- `docs/sales/librarian-5min-cheatsheet.md` (사서 인쇄용)
- `docs/sales/pilot-result-templates/` (4 페르소나 빈 양식)
- `docs/cloud-routine-monitoring-guide.md` (routine 점검)
- `docs/sales/annual-calendar-2026-2027.md` (연간 영업 캘린더)
