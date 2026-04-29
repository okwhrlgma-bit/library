# kormarc-auto — 사서 5분 cheat sheet (1장 종이)

> **인쇄 후 사서 책상 옆에 두세요.** A4 1장. 사서가 PowerShell·MARC 모르셔도 5분이면 ISBN → KORMARC .mrc 가능.

---

## 1. 첫 1권 (3분)

```powershell
# (1) PowerShell 열기 (시작 메뉴 → "PowerShell" 검색 → Enter)

# (2) 폴더 이동 (가입 시 안내받은 경로)
cd kormarc-auto

# (3) 시스템 활성
.\.venv\Scripts\Activate.ps1

# (4) ISBN 13자리 입력 (책 뒷면 바코드 숫자)
kormarc-auto isbn 9788912345678

# → 5초 안에 9788912345678.mrc 파일 생성
# → KOLAS 마크 반입 폴더에 복사 → 자동 인식
```

---

## 2. 자관 등록번호 prefix 자동 발견 (1분 · 1회만)

```powershell
kormarc-auto prefix-discover "D:\<자관>\수서"
```

→ EQ·CQ·WQ 같은 prefix 자동 출력 → 안내 문구 따라 복사·붙여넣기.

---

## 3. 자관 .mrc 99% 정합 검증 (1분)

```powershell
.\.venv\Scripts\python.exe scripts\validate_real_mrc.py --dir "D:\<자관>\수서"
```

→ "정합: N건 (99%+)" 출력되면 OK. **자관 「내를건너서 숲으로 도서관」 = 99.82% 검증 완료.**

---

## 4. 자주 쓰는 명령

| 하고싶은 것 | 명령 |
|---|---|
| ISBN 1권 | `kormarc-auto isbn 9788912345678` |
| ISBN 5권 일괄 | `kormarc-auto batch sample.txt` (한 줄당 ISBN 1개) |
| 책 사진 1장 (ISBN 없음) | `kormarc-auto photo cover.jpg` |
| 책단비 hwp 자동 | `kormarc-auto interlibrary --type chaekdanbi` |
| 납본서식 PDF | `kormarc-auto deposit form` |
| 폐기 결재서식 | `kormarc-auto dispose --input list.json` |
| 환경 진단 | `kormarc-auto info` |

---

## 5. 사서 책임 영역 (자동 X)

- **KDC 분류**: AI 후보 3개 보여드림 → 사서가 결정
- **청구기호 (049)**: 자관 정책 적용 → 사서 검수
- **880 한자 페어**: 자동 생성 → 사서 검수
- **저자 (245)**: 외부 API 응답 → 사서 검수

→ **시스템이 결정하지 않습니다.** 사서를 보조할 뿐.

---

## 6. 막혔을 때

| 증상 | 해결 |
|---|---|
| `kormarc-auto` 명령 없음 | (3) Activate.ps1 다시 |
| 한글 깨짐 | `chcp 65001` 입력 후 재실행 |
| API 키 오류 | `.env` 파일에 NL_CERT_KEY 채움 |
| KOLAS 반입 실패 | 마크 파일을 폰으로 PO에게 보내주세요 |
| 인터넷 X | 캐시 7일 — 같은 ISBN은 오프라인 OK |

**카카오 채널 「kormarc-auto」 또는 okwhrlgma@gmail.com — 24시간 내 답변.**

---

## 7. 가격 (사서 본인 또는 도서관 예산)

| 플랜 | 월 |
|---|---|
| 무료 체험 | 50건 |
| 작은도서관 | 3만원 / 500건 |
| 학교/소규모 공공 | 5만원 / 1,000건 |
| 일반 공공 | 15만원 / 5,000건 |
| 대규모·기업 | 30만원 / 무제한 |

**첫 50건 무료. 만족 안 하시면 다음달부터 미차감 (락인 X).**

---

## 8. 자관 「내를건너서 숲으로 도서관」 사례

- 사서 8명·시문학·윤동주 특화·은평구공공도서관 11개 중 1개
- **.mrc 174 파일·3,383 레코드 99.82% 정합 검증 완료** ★
- 049 prefix: EQ(75.5%)·CQ(22.8%)·WQ(1.7% 윤동주 별치)
- 5년 책단비 1,328건 자동 검증
- 2026.5.31 KLA 전국도서관대회 발표 신청

---

**문의·PILOT 신청**: okwhrlgma@gmail.com · 카카오 채널 「kormarc-auto」 · github.com/okwhrlgma-bit/library
