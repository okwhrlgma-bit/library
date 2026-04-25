---
description: Streamlit UI 실행 (모바일 반응형, 사서용 GUI)
---

## 실행

```powershell
.\.venv\Scripts\Activate.ps1
kormarc-ui
```

기본: `http://localhost:8501` 자동 브라우저 열림.

## 모바일에서 접속

별도 터미널에서:
```powershell
cloudflared tunnel run kormarc-ui
```

또는 단발 터널:
```powershell
cloudflared tunnel --url http://localhost:8501
```

발급된 `*.trycloudflare.com` 주소를 폰 브라우저에서 접속.

## 탭

1. **ISBN** — 단건 변환
2. **검색** — 키워드 → 후보 선택
3. **사진** — 표지/판권지 1~3장 (모바일 카메라 직접)
4. **일괄** — ISBN 다수 → CSV + ZIP

## 종료

브라우저 탭 닫고 터미널에서 `Ctrl+C`
