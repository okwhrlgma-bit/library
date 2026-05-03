# 자관 049 prefix 자동 발견 — 5분 가이드 (사서용)

> **목적**: PILOT 1주차 사서가 본인 도서관 .mrc 파일에서 049 ▾l 등록번호 prefix를 자동으로 찾아내고, 우리 시스템에 즉시 적용.
> **시간**: 5분 (Python 설치 별도)
> **결과 예**: 자관 「○○도서관」 → EQ·CQ·**WQ** 자동 발견 → 99.82% 정합 도달.

---

## 0. 왜 이 작업이 필요한가요?

각 도서관마다 049 ▾l (등록번호) 첫 두 글자(prefix)가 다릅니다.

| 자관 prefix 예 | 의미 |
|---|---|
| EQ | 일반 도서 |
| CQ | 아동 도서 |
| WQ | 윤동주·시문학 별치 |
| (선생님 자관) | ??? |

우리 시스템이 선생님 자관 prefix를 모르면 **49% 정합도가 99% 가까이 떨어집니다**. prefix 자동 발견 1줄 실행 → 99% 회복.

---

## 1. 사전 준비

### 1.1 Python 3.12 설치 (1회·5분)

설치 안 됐으면 PowerShell에서:

```powershell
winget install Python.Python.3.12
```

### 1.2 kormarc-auto 받기

```powershell
git clone https://github.com/[저장소URL] kormarc-auto
cd kormarc-auto
.\setup-once.bat
```

(또는 PO가 zip 파일로 보내드린 경우 압축 해제 후 위 폴더에서 작업)

---

## 2. 자관 .mrc 디렉토리 위치 확인

KOLAS III에서 자관 .mrc를 어디에 보관하시는지 확인. 일반적으로:

- KOLAS 출력 폴더: `D:\<자관명>\수서\<연도>\마크파일\` 같은 경로
- 알파스 출력 폴더: 자관 알파스 설정에 명시
- 직접 export한 경우: 사서 PC의 임의 폴더

→ 어디든 OK. **재귀 검색**이라 하위 폴더 모두 자동 탐색.

---

## 3. 1줄 실행

PowerShell에서 (자관 폴더 경로 입력):

```powershell
cd kormarc-auto
.\.venv\Scripts\Activate.ps1
kormarc-auto prefix-discover "D:\<자관명>\수서"
```

---

## 4. 출력 해석 (예: 자관)

```
분석 중: D:/○○도서관/수서

총 레코드: 3383건

049 prefix 분포:
  EQ:  2553건 ( 75.5%)  [권장]
  CQ:   773건 ( 22.8%)  [권장]
  WQ:    57건 (  1.7%)  [권장]

권장 (>= 1.0% 적용):
  ('CQ', 'EQ', 'WQ')

config.yaml snippet:
# kormarc-auto가 자관 .mrc 분석으로 자동 발견한 prefix 정책.
# 사서 검수 후 본 config 적용.
kolas_register:
  registration_prefix: ["CQ", "EQ", "WQ"]
```

### 무엇을 보세요?

1. **총 레코드** = 분석한 .mrc 레코드 수 (자관 = 3,383건)
2. **분포** = 자관에 사용 중인 prefix와 비율
3. **[권장]** = 1% 이상 사용 → 우리 정합 SET에 포함
4. **config.yaml snippet** = 다음 단계에 사용

---

## 5. 적용 (1분)

`config.yaml` 파일에 위 snippet을 그대로 붙여넣기:

```yaml
# config.yaml
kolas_register:
  registration_prefix: ["CQ", "EQ", "WQ"]
```

(자관별 prefix는 다릅니다. 위 4번 출력의 snippet 그대로 복사 + config.yaml 저장)

---

## 6. 검증

```powershell
.\.venv\Scripts\python.exe scripts\validate_real_mrc.py --dir "D:\<자관명>\수서"
```

목표 출력:

```
=== 자관 .mrc 검증 결과 ===
파일: N건
레코드 합계: N건
정합: N건 (>= 99%)
위반: 소수
```

**99% 이상**이면 PILOT 시작 OK.

---

## 7. 잘 안 되시면

| 증상 | 해결 |
|---|---|
| `winget` 안 됩니다 | 윈도우 11이거나 winget 설치 필요. PO에게 카카오톡. |
| `kormarc-auto` 명령 못 찾음 | `Activate.ps1` 안 했음. Step 3 다시. |
| 한국어 깨짐 | PowerShell `chcp 65001` 입력 후 재실행. |
| `D:\...` 디렉토리 없음 | 자관 .mrc 폴더 경로 다시 확인. |
| 99% 미만 | 위반 유형 확인 → PO에게 출력 결과 보내주세요. 자관별 정책 검토 후 모듈 보강. |

PO 컨택: contact@kormarc-auto.example / 카카오 채널 [채널명]

---

## 8. 다음 단계 (PILOT 2주차로)

- 자관 신착 5권 ISBN 입력 → KORMARC .mrc 5초
- 자관 KOLAS에 .mrc 반입 (반입 폴더에 두면 자동 인식)
- 매크로 사서면 → 책단비 hwp 자동 (`docs/sales/pilot-package-2026-04-29.md §1.2`)
- 수서 사서면 → 정보나루 인기 대출 import (PILOT 2주차)

---

## Sources

- `src/kormarc_auto/librarian_helpers/prefix_discovery.py` (모듈)
- `scripts/validate_real_mrc.py` (검증)
- 자관 「○○도서관」 174 파일·3,383 레코드 실측 (2026-04-29)
- WQ prefix 발견 → 99.82% 정합 도달 사례
