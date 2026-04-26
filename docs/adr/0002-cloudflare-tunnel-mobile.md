# ADR 0002 — Cloudflare Tunnel for Mobile Access

**상태**: accepted
**일자**: 2026-04-25
**의사결정자**: PO

## 컨텍스트

사서가 폰 카메라로 책 표지를 촬영해 KORMARC 생성하려면 Streamlit UI를 외부에 노출해야. 옵션:

1. **0.0.0.0 직접 바인딩** — 방화벽 포트 개방 + 동적 IP 추적
2. **ngrok** — 무료 1세션, URL 매번 변경
3. **Cloudflare Tunnel** — 무료 영구·임시 둘 다, 자동 TLS, DDoS 보호
4. **클라우드 호스팅 (Render·Fly)** — 매월 호스팅비 1.5만원+

## 결정

**Cloudflare Tunnel** 채택. 베타 기간은 trycloudflare(임시 URL), Phase 5 후반에 named tunnel(영구).

## 결과

- 외부 노출 즉시 가능 (PC만 켜져 있으면)
- 자동 HTTPS, 사서가 폰에서 보안 경고 안 봄
- 호스팅비 0원 (매출 발생 전 부담 X)
- DDoS·봇 보호 무료 (Cloudflare 자동)

## 트레이드오프

✅ **장점**
- 베타 8개월 호스팅비 0
- 5분 셋업 (`cloudflared tunnel --url ...`)
- 모바일 사서 카메라 권한 자동 동작 (HTTPS 필수 조건 충족)

❌ **단점**
- TryCloudflare 무료 = SLA 없음 (운영 감사 HIGH #4)
- PC 절전모드·정전 시 즉시 다운
- 200 동시요청 제한 + SSE 미지원 → 사서 50명 동시 한도

## 완화 조치

- 베타 한도 50명 명시 (PILOT 전제)
- 매출 월 30만원 도달 시 Render·Fly 이전 (ADR 0005에서 후속)
- named tunnel 셋업 가이드 `docs/mobile-tunnel.md` 보유
- PC 절전모드 OFF + UPS 권장

## 6개월 후 되돌릴 수 있는가?

**Y** — Cloudflare named tunnel(영구 도메인) 또는 클라우드 이전 모두 호환. 외부 의존성 cloudflared CLI 1개만.

## 관련 자료

- `docs/mobile-tunnel.md` — 셋업 가이드
- `start-tunnel.bat` — 더블클릭 단발 터널
- `docs/real-world-operations-audit.md` HIGH #4 — Cloudflare SLA 부재 경고
