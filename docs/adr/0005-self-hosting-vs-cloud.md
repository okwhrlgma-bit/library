# ADR 0005 — Self-Hosting vs Cloud (베타 운영)

**상태**: accepted
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

베타 기간(2026-04~12) 운영 인프라 옵션:
1. **PO PC + Cloudflare Tunnel** — 호스팅비 0, SLA 본인 책임
2. **Render Free Tier** — 무료, 슬립 후 콜드스타트 30초
3. **Fly.io Hobby** — 월 $5, 작은 인스턴스 24/7
4. **VPS (NHN Cloud·KT)** — 월 1.5만원+, 한국 IP

## 결정

**1단계 (현재~베타 50명)**: PO PC + Cloudflare Tunnel.
**2단계 (베타 50명 도달 또는 매출 월 30만원)**: Fly.io Hobby로 이전.

## 결과 (1단계)

- 호스팅비 0 → 매출 발생 전 부담 X
- 5분 셋업, 더블클릭 `start-tunnel.bat`
- 사서 50명 PILOT은 동시 부하 낮음 (사용 패턴: 매일 5~10권 처리)

## 트레이드오프 (1단계)

✅ **장점**
- 매출 발생 시점 앞당김 (현금흐름 우선)
- PO 본인 PC = 디버깅 즉시 가능
- 외부 의존성 1개만 (cloudflared CLI)

❌ **단점**
- PC 절전·정전·OS 업데이트 재부팅 시 즉시 다운
- 한국 IP 아니라 학교·공공 도서관 일부 차단 가능 (Cloudflare는 한국 PoP 사용하지만 IP 신뢰도 다양)
- 백업 OneDrive 단일 (운영 감사 HIGH #5)

## 완화 조치 (1단계)

- `scripts/backup_logs.py` 매주 1회 cron (S3·Google Drive 이중화 검토)
- PC 절전·hibernation OFF
- UPS (무정전 전원장치) 베타 30명 도달 시 도입
- 베타 약관에 "베타 기간 SLA 없음" 명시 (`docs/terms-beta.md` §3)

## 트리거 (2단계 전환)

다음 중 하나 충족 시 즉시 클라우드 이전:
- 동시 활성 사서 ≥ 50명
- 매출 월 30만원 (호스팅비 1.5만원 5%)
- 24시간 다운타임 발생 (1회라도)
- 학교·공공 도서관에서 PC IP 차단 보고

## 6개월 후 되돌릴 수 있는가?

**Y** — Cloudflare Tunnel은 클라우드 인스턴스에서도 동일 작동. Docker 이미지 1개로 어디든 배포 가능 (`Dockerfile` + `docs/deploy.md` 보유).

## 관련 자료

- `docs/deploy.md` — Fly·Render·VPS 3 옵션
- `docs/real-world-operations-audit.md` HIGH #4·#5
- `Dockerfile` — 클라우드 이전용
- `start-tunnel.bat` — 1단계 단발 터널
