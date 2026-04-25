---
description: 모바일 운영 상태 진단 — 서버·터널·키·권한
---

## Step 1 — 서버

```powershell
curl http://localhost:8000/healthz
```

응답 없으면 `kormarc-server`로 시작.

## Step 2 — 환경변수

```powershell
kormarc-auto info
```

필수: `ANTHROPIC_API_KEY`, `NL_CERT_KEY`. 권장: `ALADIN_TTB_KEY`, `KAKAO_API_KEY`.
서버용 추가: `KORMARC_USER_KEYS` (X-API-Key 화이트리스트).

## Step 3 — 터널 상태

```powershell
cloudflared tunnel list
```

활성 터널 없으면 `cloudflared tunnel run kormarc` 시작.

## Step 4 — Claude Code 모바일 권한

`.claude/settings.json` (전역·프로젝트) 둘 다 다음 항목 포함 확인:
- `Bash(streamlit run:*)`, `Bash(uvicorn:*)`, `Bash(cloudflared:*)`
- `Bash(kormarc-auto:*)`, `Bash(kormarc-server:*)`, `Bash(kormarc-ui:*)`

빠진 게 있으면 PC에서 한 번 실행하며 "Always allow" 추가.

## Step 5 — 사용량 점검

```powershell
curl http://localhost:8000/usage `
  -H "X-API-Key: $env:KORMARC_USER_KEY"
```

남은 무료 한도 확인. 5건 미만이면 응답에 `payment_url` 포함.

## 보고 형식

```
모바일 운영 점검 — YYYY-MM-DD HH:MM

✓ 서버: 정상 (v0.1.0)
✓ ANTHROPIC_API_KEY / NL_CERT_KEY 설정됨
⚠ 알라딘 미설정 — 검색 정확도 저하 가능
✓ Cloudflare Tunnel: kormarc 활성 (https://abc.trycloudflare.com)
✓ Claude Code 모바일 권한: 8/8 통과
✓ 사용량: 12/50 (남 38)
```
