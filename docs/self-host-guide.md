# Self-host 가이드 — kormarc-auto 외부 호스팅 (Render·Fly.io·Docker)

> **대상**: 자관 PC 외부에서 kormarc-auto FastAPI + Streamlit 호스팅 원하는 PO·사서
> **선택지**: Render (간단·무료) · Fly.io (한국 latency·무료~$5) · Docker (직접·자관 사내망)
> **추천 시나리오**: Phase 1 (1관·자관 PC) → Phase 2 (5관+·Render/Fly) → Phase 3 (200관+·Fly + Supabase)

---

## 1. Render (가장 간단·무료)

### 1-1. 셋업 (10분)

1. https://render.com 가입 (GitHub 로그인)
2. "New +" → "Web Service"
3. GitHub repo 연결 (https://github.com/okwhrlgma-bit/library)
4. 설정:
   - Name: `kormarc-auto`
   - Region: Singapore (한국 latency 약 50ms)
   - Branch: `main`
   - Runtime: `Python 3.12`
   - Build Command: `pip install -e ".[dev]"`
   - Start Command: `uvicorn kormarc_auto.server.app:create_app --factory --host 0.0.0.0 --port $PORT`
5. Environment:
   - `NL_CERT_KEY`·`ALADIN_TTB_KEY`·`KAKAO_API_KEY`·`ANTHROPIC_API_KEY` 등록
6. "Create Web Service" → 자동 deploy

### 1-2. 비용

- Free: 750h/월 (충분·1인 운영)
- Starter $7/월: 24/7 + 외부 도메인

---

## 2. Fly.io (한국 latency 최적·NRT/ICN 리전)

### 2-1. 셋업 (15분)

```powershell
# 1. flyctl 설치
winget install fly-io.flyctl

# 2. 가입 + 로그인
fly auth signup    # 또는 fly auth login

# 3. 앱 초기화 (fly.toml 자동 생성)
cd kormarc-auto
fly launch --name kormarc-auto --region nrt   # 도쿄 (한국 latency 30ms)
# 또는 --region icn (서울 - 가장 빠름)

# 4. 환경변수 등록
fly secrets set NL_CERT_KEY=xxx ALADIN_TTB_KEY=yyy KAKAO_API_KEY=zzz ANTHROPIC_API_KEY=sk-...

# 5. 배포
fly deploy
```

### 2-2. fly.toml 예시

```toml
app = "kormarc-auto"
primary_region = "icn"  # 서울 (또는 nrt 도쿄)

[build]
  builder = "paketobuildpacks/builder:base"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  size = "shared-cpu-1x"  # $1.94/월
  memory = "512mb"
```

### 2-3. 비용

- Free: $5/월 사용량 면제 (소규모 OK)
- Pro $0~ + 사용량 (Phase 2 베타 50관 = 약 $5~10/월)

---

## 3. Docker (자관 사내망 self-host)

### 3-1. Dockerfile (이미 있음)

```bash
docker build -t kormarc-auto:latest .
docker run -d -p 8000:8000 \
  -e NL_CERT_KEY=xxx \
  -e ALADIN_TTB_KEY=yyy \
  --name kormarc-auto \
  kormarc-auto:latest
```

### 3-2. docker-compose (Postgres·Meilisearch 포함·Phase 2+)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

### 3-3. 자관 사내망 (PIPA 옵션 C 정합)

- 회원 PII = 자관 알파스 위임 (외부 호스팅 X)
- 우리 SaaS = 양식·통계·템플릿만 (사내망 호스팅 가능)
- HTTPS는 자관 도메인 + Let's Encrypt (자동 갱신)

---

## 4. 비용 시뮬레이션 (1인 → 200관)

| 단계 | 사용자 | Render | Fly.io | Self-host (사내) |
|---|---|---|---|---|
| 1관 (자관) | 1 | $0 (Free) | $0~5 | $0 (PC) |
| 50관 (Phase 1) | 50 | $7 (Starter) | $5~15 | 자관 PC 한계 |
| 200관 (Phase 3) | 200 | $25+ | $15~30 | Postgres + Supabase 필요 |
| 1,000관 (Phase 4) | 1,000 | $50+ | $30~80 | Supabase Pro $25 + Fly $30 |

→ **추천**: Phase 1 = Render Free·Phase 2~3 = Fly.io ICN/NRT·Phase 4 = Supabase + Fly·자관 PIPA 옵션 C 사내 호스팅 = Docker.

---

## 5. SSL·도메인

- **Render**: Free plan 자동 (`*.onrender.com`)·Pro plan 외부 도메인
- **Fly.io**: 자동 SSL (`*.fly.dev`)·외부 도메인 무료 (`fly certs add`)
- **Docker self-host**: Caddy 또는 Nginx + Let's Encrypt (자동 갱신)

---

## 6. 모니터링

- Render: 자체 메트릭 + 로그 stream
- Fly.io: `fly logs` + Grafana 통합
- Docker: Prometheus + Grafana 또는 Sentry

권장: Sentry (Phase 2+·Free 5K 에러/월)

---

## Sources

- `docs/research/part4-uiux-seo-marketing-deployment.md` §배포 의사결정
- `docs/research/part5-tools-and-automation.md` §3 Vercel·§4 Supabase
- `docs/mobile-tunnel.md` (Phase 1 Cloudflare Tunnel)
- ADR-0011 (managed-stack-cashcow)
