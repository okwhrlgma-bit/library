---
description: FastAPI REST 서버 실행 (모바일/외부 클라이언트용)
---

## 사전 점검

```powershell
.\.venv\Scripts\Activate.ps1
kormarc-auto info
```

`ANTHROPIC_API_KEY`, `NL_CERT_KEY` 등이 설정돼 있는지 확인.

## 서버 시작

```powershell
kormarc-server
```

기본: `127.0.0.1:8000`. 외부 노출은 cloudflared 통해서만 (직접 0.0.0.0 바인딩 deny).

## 외부에서 접근 (모바일)

별도 터미널에서:
```powershell
cloudflared tunnel run kormarc
```

설정 안 됐으면 `docs/mobile-tunnel.md` 따라 1회 셋업.

## 동작 확인

```powershell
curl http://localhost:8000/healthz
curl http://localhost:8000/pricing
curl -X POST http://localhost:8000/isbn `
  -H "X-API-Key: $env:KORMARC_USER_KEY" `
  -H "Content-Type: application/json" `
  -d '{"isbn":"9788936434120"}'
```

## 종료

`Ctrl+C`
