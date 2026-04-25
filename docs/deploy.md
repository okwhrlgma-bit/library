# 운영 배포 가이드 (선택, MVP-2 단계)

베타 단계는 PO PC + Cloudflare Tunnel로 충분합니다. 하지만:
- 사서 5명 이상 동시 사용
- PO PC 꺼져도 서비스 운영
- 영구 도메인 (`kormarc.your-domain.com`)

이 단계가 되면 클라우드에 띄우는 것을 권장합니다. 가장 쉬운 3가지:

---

## 옵션 1: Fly.io (권장 — 무료 $5 크레딧, 한국에서 빠름)

### 1회 셋업

```powershell
# Fly CLI 설치
winget install --id Fly-io.Flyctl --silent --accept-source-agreements --accept-package-agreements

# 로그인
flyctl auth signup     # 또는 flyctl auth login
```

### 앱 생성·배포

루트에 `Dockerfile` (이미 작성):
```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y libzbar0 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --no-cache-dir -e .
EXPOSE 8000
CMD ["python", "-m", "kormarc_auto.server.app"]
```

루트에 `fly.toml`:
```toml
app = "kormarc-auto"
primary_region = "nrt"  # 도쿄 (한국에서 가장 빠름)

[http_service]
  internal_port = 8000
  force_https = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

배포:
```powershell
flyctl launch --no-deploy
flyctl secrets set NL_CERT_KEY=... ALADIN_TTB_KEY=... KAKAO_API_KEY=... ANTHROPIC_API_KEY=... KORMARC_ADMIN_KEYS=kma_admin_xxx
flyctl deploy
```

발급 도메인: `https://kormarc-auto.fly.dev` → 사서에게 공유.

---

## 옵션 2: Render.com (무료 플랜 가능, 슬립 있음)

1. github.com/<your>/kormarc-auto 에 push
2. render.com에서 "New Web Service" → 위 repo 연결
3. Runtime: Python 3.12, Build: `pip install -e .`, Start: `python -m kormarc_auto.server.app`
4. Environment에 `.env` 키들 추가
5. 배포 완료. 무료 플랜은 15분 비활성 시 슬립 (첫 요청 30초 콜드 스타트).

---

## 옵션 3: 본인 VPS (월 5,000원, 가장 저렴)

KT Cloud / Vultr / Hetzner 등 1GB VPS:

```bash
# Ubuntu 22.04 가정
sudo apt update && sudo apt install -y python3.12-venv libzbar0 git nginx
git clone <repo> kormarc-auto && cd kormarc-auto
python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# .env 작성 (scp .env user@vps:~/kormarc-auto/.env)

# systemd 서비스
sudo tee /etc/systemd/system/kormarc.service >/dev/null <<'EOF'
[Unit]
Description=kormarc-auto
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/kormarc-auto
EnvironmentFile=/home/ubuntu/kormarc-auto/.env
ExecStart=/home/ubuntu/kormarc-auto/.venv/bin/python -m kormarc_auto.server.app
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now kormarc

# nginx + Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d kormarc.your-domain.com
```

---

## 운영 체크리스트

| 항목 | 빈도 |
|---|---|
| `logs/usage.jsonl` 백업 | 매주 (S3/Google Drive) |
| `logs/feedback.jsonl` 점검 | 매주 |
| `/admin/stats` 호출 (관리자 키) | 매일 |
| Anthropic 사용량 확인 | 매일 (예산 알람) |
| 의존성 업데이트 (`pip install -U`) | 월 1회 + 보안 패치 즉시 |
| .mrc 정확도 회귀 (`scripts/accuracy_check.py`) | 베포 전 |

---

## 비용 가이드 (MVP-2 시점)

| 항목 | 월 |
|---|---|
| Fly.io shared 1cpu 512MB | $0~5 |
| Anthropic Vision (사서 5명 × 100건/월) | 약 $1 |
| Cloudflare Tunnel | $0 |
| 도메인 | 약 ₩1,000 (연 1.2만원) |
| **합계** | **약 ₩6,000~10,000/월** |

권당 100원 × 사서 5명 × 100건 = ₩50,000/월 매출. 마진 80%+.

---

## 보안 권장

- `KORMARC_USER_KEYS` 화이트리스트 모드로 운영 (개발 모드 금지)
- `KORMARC_CORS_ORIGINS`를 정확한 도메인만으로 제한
- `KORMARC_ADMIN_KEYS`는 PO만 (절대 공유 금지)
- 운영 도메인에는 Cloudflare Access (무료) 추가 권장
- HTTPS 강제 (Fly/Render는 자동, VPS는 certbot)
