# 모바일에서 kormarc-auto 사용하기 — 터널 셋업

목표: PO/사서가 **폰 브라우저로 kormarc-auto의 Streamlit UI 또는 REST API**에 접속.

설치 도구 (이미 자동 설치됨):
- `cloudflared` (1순위, 무료, 안정)
- `ngrok` (백업, 무료 7시간 세션 한계)

---

## 1순위: Cloudflare Tunnel (무료, 영구)

### A. 5분 단발 터널 (계정 없이, URL 매번 바뀜 — 가장 빠름)

서버를 `kormarc-server`로 띄운 상태에서 별 터미널:

```powershell
cloudflared tunnel --url http://localhost:8000
```

출력 마지막 줄의 `https://abc-def-ghi.trycloudflare.com` URL을 폰 브라우저에서 열기. 끝.

**주의**: 단발 터널은 매번 URL이 바뀝니다. 사서에게 공유하기 어려움.

### B. 영구 터널 (계정 1회 셋업, URL 고정 — 본격 사용)

#### 1. Cloudflare 계정 + 도메인

- [cloudflare.com](https://www.cloudflare.com) 무료 계정 가입
- 본인 도메인 1개 등록 (예: `kormarc-auto.kr`) — 이미 있으면 그거 사용
- 도메인 없으면: 1년 약 1만원에 [Namecheap](https://www.namecheap.com)·[Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)에서 구매

#### 2. 로그인

```powershell
cloudflared tunnel login
```

브라우저가 열리며 도메인 선택 → 인증 1회.

#### 3. 터널 생성

```powershell
cloudflared tunnel create kormarc
cloudflared tunnel create kormarc-ui
```

각 터널의 ID와 credentials 파일 경로를 출력에서 확인.

#### 4. 라우팅 설정

```powershell
cloudflared tunnel route dns kormarc kormarc-api.kormarc-auto.kr
cloudflared tunnel route dns kormarc-ui kormarc.kormarc-auto.kr
```

#### 5. config 파일

`%USERPROFILE%\.cloudflared\config.yml`:

```yaml
tunnel: kormarc
credentials-file: C:\Users\kormarc-auto\.cloudflared\<TUNNEL_ID>.json
ingress:
  - hostname: kormarc-api.kormarc-auto.kr
    service: http://localhost:8000
  - service: http_status:404
```

#### 6. 실행

```powershell
cloudflared tunnel run kormarc
```

폰 브라우저 → `https://kormarc-api.kormarc-auto.kr` 접속.

---

## 2순위: ngrok (백업, 즉시)

```powershell
ngrok http 8000
```

발급된 `https://xxxx.ngrok-free.app` URL을 폰에서 접속.

**한계**:
- 무료 계정: 세션 7시간, 동시 1터널, 분당 40 요청
- URL 매번 바뀜 (계정 등록 후 reserved domain 1개 가능)

`ngrok config add-authtoken <TOKEN>` 1회 등록 후 영구 사용 가능.

---

## 보안 권장 사항

1. **X-API-Key 필수** — `KORMARC_USER_KEYS` 환경변수에 임의 문자열 등록
2. **외부 노출은 항상 터널 통해서** — `0.0.0.0` 직접 바인딩 금지 (settings.json에서 deny)
3. **Cloudflare Access** (선택) — 터널 앞에 Google 로그인 추가 (무료)

---

## Streamlit UI 터널 (사서용)

```powershell
# 별 터미널 1: UI
kormarc-ui

# 별 터미널 2: 단발 터널
cloudflared tunnel --url http://localhost:8501
```

발급 URL을 사서 폰으로 공유. 30분 만에 베타 시범 가능.

---

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| `cloudflared: command not found` | 셸 재시작 (winget이 PATH 갱신) |
| `tunnel: connection refused` | 서버가 안 떠 있음 (`kormarc-server` 확인) |
| 폰에서 SSL 오류 | trycloudflare.com 인증서는 항상 유효 — 사용자 시간 확인 |
| ngrok 인증 오류 | `ngrok config add-authtoken <TOKEN>` 1회 |
