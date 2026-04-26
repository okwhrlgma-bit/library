# ADR 0011 — 매니지드 스택·웹 vs 모바일·캐시카우 운영

**상태**: accepted
**일자**: 2026-04-26
**의사결정자**: PO

## 컨텍스트

PO 운영 원칙 (2026-04-26):
- 개발 경험 적음 → vibe coding + 매니지드 서비스
- 스택: Vercel/Supabase/Stripe·포트원 같은 "손 안 가는" 인프라
- 목표: Claude Code 자율 개발 → 배포 → **패시브 인컴**

기존 ADR 0001~0010과 조화시키며 캐시카우 운영 원칙 명문화.

## 결정 1 — 매니지드 스택 (vibe coding + Pro 호환)

| 영역 | 채택 | 근거 |
|---|---|---|
| 백엔드 API | **FastAPI on Cloudflare Tunnel** (현재) → 베타 50명 후 **Fly.io Hobby ($5/월)** | ADR 0005 트리거 |
| 프런트 (사서) | **Streamlit** (현재) | vibe coding 친화·14탭·Pretendard |
| 랜딩 | 정적 HTML (`landing/`) → 향후 **Vercel** | CDN·SSL 자동 |
| 결제 PG | **포트원** (proposed ADR 0007) → 사업자 등록 후 즉시 | 한국 사서 친숙·세금계산서 자동 |
| DB | JSON/JSONL (현재) → 베타 20명 후 **Supabase Postgres** | ADR 0004 트리거 + Row-Level Security |
| 인증 | API key (현재) → Supabase Auth (선택) | OAuth + Magic Link 매니지드 |
| 모니터링 | 자체 jsonl → **Logtail / Better Stack** ($24/월부터) | 매니지드 알림 |
| 외부 메시징 | 카카오톡 비즈 채널 (현재) | 한국 사서 1:1 SLA |
| 도메인 | Cloudflare → **Namecheap·가비아** (사업자 등록 후) | 영구 URL |

**원칙**: 자체 호스팅 → 매니지드 전환 트리거를 ADR로 사전 결정. 매출 직전(월 30만원 도달)까지는 호스팅비 0 유지.

## 결정 2 — 웹 vs 모바일 (캐시카우 적합도)

| 축 | 웹 (PWA) | 네이티브 모바일 (iOS/Android) |
|---|---|---|
| 사서 사용 패턴 | PC 책상 + 폰 보조 | 폰 단독 |
| 개발 시간 (vibe) | ★★★★★ Streamlit + Cloudflare 1주 | ★ React Native·Flutter 4~8주 |
| 배포 마찰 | URL 공유 1초 | App Store 심사 7~14일 |
| 결제 마찰 | 포트원 한 번 통합 | 애플/구글 30% 수수료 회피 어려움 |
| 사서 친숙도 | 높음 (이메일 링크) | 중간 (앱 설치 부담) |
| 카메라 시연 | HTTPS만 있으면 OK (현재 적용) | 더 빠른 반응 |
| 패시브 인컴 적합도 | **★★★★★** | ★★ |

### 결정: **웹 (PWA) 우선**, 모바일은 **Streamlit 모바일 반응형 + Cloudflare URL** 그대로 사용.

근거:
1. **Streamlit + Cloudflare Tunnel**이 이미 폰 카메라·반응형 완성 (`docs/mobile-tunnel.md`·v0.4.16 확인)
2. App Store 심사·30% 수수료·iOS/Android 양쪽 유지 = 패시브 인컴에 역행
3. PWA는 폰 홈 화면 추가 가능 → 사실상 앱 경험
4. 향후 사서 50명 도달·NPS 30+ 시 React Native PWA 래퍼 검토 (별도 ADR)

## 결정 3 — 패시브 인컴 자동화 4축

매니지드 인프라 위에서 **PO 시간 0**으로 매월 결제 발생 흐름:

| 축 | 도구 | 자동화 수준 |
|---|---|---|
| 1. 사서 가입 | `/signup` 응답 즉시 키 발급 + welcome 메시지 | ✓ 적용 |
| 2. 사용량 카운터 | `server/usage.py` + `consume()` 매 요청 | ✓ 적용 |
| 3. 청구·영수증 | `server/billing.py` + 포트원 정기결제 | ✓ 모듈 / ✗ PG (ADR 0007 트리거 후) |
| 4. 잔여 알림 | Streamlit 사이드바 + 카카오 채널 자동응답 | ✓ 적용 |

**PG 도입 직후 자동화 완성**: 사서 가입 → 50건 무료 → 자동 결제 등록 안내 → 사용 시 자동 차감 → 매월 자동 청구 → PO 입금 알림만 받음.

## 트레이드오프

✅ **장점**
- 매니지드 = PO 1인 운영 가능 (디버깅·DB 백업·SSL 자동)
- vibe coding 호환 (Streamlit·FastAPI는 Claude Code 자율 commit 친화)
- 베타 호스팅비 0 → 매출 발생 직전까지 부담 X
- 웹 단일 = 배포 마찰 0

❌ **단점**
- 매니지드 비용은 매출 비례 증가 (Supabase Pro $25/월·Fly.io $5+·Logtail $24·포트원 PG 3%)
- 한국 사서 일부는 모바일 네이티브 선호 (해결: PWA 홈 화면 추가 가이드)
- 매니지드 lock-in (해결: 매 ADR에 "6개월 후 되돌릴 수 있는가" 명시)

## 6개월 후 되돌릴 수 있는가?

**Y** — 모든 매니지드 서비스는 표준 Postgres·OAuth·Stripe 호환. Lock-in 없이 자체 호스팅·다른 PG로 전환 가능. 단 PG 거래 데이터는 우리 DB에 영속 저장.

## 트리거 (도입 시점)

| 도구 | 도입 시점 |
|---|---|
| 포트원 PG | 사업자 등록 + 통신판매 신고 직후 (ADR 0007) |
| Supabase Postgres | 베타 사서 20명 또는 동시 10건/초 (ADR 0004) |
| Fly.io Hobby | 매출 월 30만원 또는 베타 50명 (ADR 0005) |
| Vercel 정적 랜딩 | 도메인 구매 후 |
| Logtail/Better Stack | 매출 월 100만원 도달 (모니터링 의무 비례) |

## 평가축 부합

- **§0 마크 시간**: 매니지드 스택 자체는 사서 시간 영향 X (현 Streamlit 14탭 충분). 단 PG 자동화로 사서가 결제 직접 처리 시간 0.
- **§12 매출 의향**: PG·세금계산서 자동 = 학교/공공 결제팀 거부 0% → 결제 전환율 직접 향상. **캐시카우 직결**.

## 관련 자료

- ADR 0001 BYOK · 0002 Cloudflare · 0003 100원 · 0004 SQLite · 0005 Self-host · 0007 PG · 0009 §33 · 0010 야간
- `docs/business-checklist.md` 사업화 체크리스트
- `docs/sales-roadmap.md` 캐시카우 3단계 (Phase 1~3)
- `docs/mobile-tunnel.md` 폰 접속 가이드
