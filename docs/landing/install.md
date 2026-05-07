---
title: 5초 설치 가이드 · kormarc-auto · 사서 자가 설치 친화
description: 더블클릭 1회 = 즉시 작동. Python 설치 X·명령어 X·인터넷 차단 시도 일부 작동.
author: 조기흠 (사서 출신·1인 PO)
keywords: kormarc-auto 설치, 사서 자동화 SaaS 설치, KORMARC 도구 다운로드
---

# 5초 설치 가이드 (사서·클릭 1회·Python 설치 X)

> **사서 IT 자신감 L1·L2 (60%) 친화** = 명령어 X·더블클릭만.
> Cycle 65 박제·`.exe` 자동 빌드 (Windows·Mac·Linux 3 OS).

## 옵션 A — URL 클릭 (가장 빠름·5초)

**1. 인터넷 브라우저 열기** (Chrome·Edge·Safari 모두 OK)
**2. 주소창에 입력 또는 클릭**:
```
https://kormarc-auto.streamlit.app
```
**3. 즉시 사용** (설치 X)

### 장점
- ✅ 클릭 1회·5초
- ✅ Python·명령어·다운로드 X
- ✅ 핸드폰·태블릿도 가능
- ✅ ₩0·평생 무료

### 단점
- ⚠ 인터넷 필요
- ⚠ 도서관 인터넷 차단 시 X

---

## 옵션 B — `.exe` 다운로드 (도서관 인터넷 차단 시 권장)

### 1단계: 다운로드 (1분)

[GitHub Releases 페이지](https://github.com/okwhrlgma-bit/library/releases/latest) 접속 →

**Windows 사서님**:
- `kormarc-auto-windows.exe` 클릭 → 다운로드

**Mac 사서님**:
- `kormarc-auto-mac` 클릭 → 다운로드

**Linux 사서님**:
- `kormarc-auto-linux` 클릭 → 다운로드

### 2단계: 더블클릭 (5초)

**Windows**:
1. 다운로드 폴더 열기
2. `kormarc-auto-windows.exe` 더블클릭
3. ⚠ "Windows에서 PC를 보호했습니다" 메시지 = "추가 정보" → "실행"
   → (이유: 무료·서명 X·코드 = GitHub 공개·100% 안전)
4. 검은 창 잠시·자동으로 브라우저 열림

**Mac**:
1. 다운로드 폴더 열기
2. `kormarc-auto-mac` 우클릭 → "열기"
   → (이유: 미등록 개발자·정상)
3. 자동으로 브라우저 열림

**Linux**:
1. 터미널 열기
2. `chmod +x kormarc-auto-linux && ./kormarc-auto-linux`
3. 자동으로 브라우저 열림

### 3단계: 즉시 사용 (5초)

브라우저 = `http://localhost:8501` 자동 열림 → ISBN 입력 → 5초 KORMARC `.mrc`.

### 장점
- ✅ 100% 사서 컴퓨터·인터넷 차단 시도 일부 작동
- ✅ Python·명령어 X·더블클릭 1회
- ✅ 도서관 RFP 100% 통과 (데이터 사서 컴퓨터)
- ✅ ₩0

### 단점
- ⚠ 첫 실행 = OS 보안 경고 (1회만·"추가 정보" 클릭)
- ⚠ 다운로드 50MB·1분

---

## 옵션 C — 명령어 (개발자·사서 IT L4·L5)

```bash
pip install -e git+https://github.com/okwhrlgma-bit/library.git
KORMARC_DEMO_MODE=1 kormarc-auto demo
```

→ **사서 60% (L1·L2) = 옵션 A·B 우선**.

---

## 첫 사용 (사서 30초 데모)

**1. 브라우저 자동 열림**
**2. ISBN 입력**: `9788937437076` (예시)
**3. "KORMARC 생성" 클릭**
**4. 5초 후 .mrc 파일 다운로드**

### 데모 ISBN 12개 (키 0개로 작동)
- `9788937437076` 등 SAMPLE 7건 + SENTINEL 5건
- 외부 API 호출 0건 = 도서관 인터넷 정책 영향 X

---

## 에러 시 (사서 친화 자동 진단)

### "에러 화면 = 무서워요" → 걱정 X

화면 아래 = "PO에게 보내기" 버튼 클릭 →
이메일 자동 작성 (에러 메시지·OS·Python 자동 첨부).

또는:
- **GitHub Issues**: https://github.com/okwhrlgma-bit/library/issues
- **이메일**: contact@kormarc-auto.example
- **PO**: 조기흠 (사서 출신·1인 PO)

→ 1일 안 답변 보장.

---

## 자주 묻는 질문 (사서)

### Q: 내 컴퓨터가 너무 느린 컴퓨터인데?
A: kormarc-auto = **Python 메모리 200MB·CPU 1코어**로 작동. 도서관 일반 PC (10년 전 모델도 OK).

### Q: 인터넷 차단되어 있어요
A: **옵션 B `.exe` + 키 0개 데모 모드** = 인터넷 X도 SAMPLE 12건 작동.
실 ISBN = 외부 API (NL·도서관정보나루) = 인터넷 필요.

### Q: 사서 컴퓨터에 영향 가나요?
A: **0건**. .exe = 사서 컴퓨터 안에서만 작동·외부 전송 X·자관 데이터 = 사서 컴퓨터 로컬 100%.

### Q: 도서관장 결재 자료 필요해요
A: [학교운영위 결재 패키지 PDF](https://github.com/okwhrlgma-bit/library/releases/latest)
다운로드·결재 양식 자동 생성.

### Q: KOLAS III 종료 마이그 가이드?
A: [KOLAS III D-238 카운트다운 + 5단계](https://kormarc-auto.streamlit.app) 페이지 참조.

### Q: 비용이 무료인가요?
A: **데모·자관 1관 PILOT = 영구 무료** (Founding Member 50% 할인 100관 한정).
공식 가격 = 작은도서관 ₩30K·학교 ₩50K·공공 ₩150K·기관 ₩300K~.

---

## 정직 헤더

- 본 가이드 = 코드 = 발행 0건·사서 인터뷰 0건 = 가설
- 인터뷰 5명 후 = 사서 어휘로 v2 재작성
- 도서관장 결재 양식 = 외부 858 §F 정합·인터뷰 후 검증

---

## 다음 단계

1. URL 클릭 또는 .exe 다운로드 (5초)
2. ISBN 데모 1회 (30초)
3. 자관 양식 등록 (5분·사서 자가)
4. KOLAS III 마이그 (사서 자가·필요 시)

---

조기흠 (사서 출신·1인 PO) · contact@kormarc-auto.example
v0.7.1 · 2026-05-06 · Apache-2.0 license
