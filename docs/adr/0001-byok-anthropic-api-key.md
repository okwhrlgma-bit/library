# ADR 0001 — BYOK Anthropic API Key

**상태**: accepted
**일자**: 2026-04-25
**의사결정자**: PO

## 컨텍스트

KDC AI 추천·Vision·NLSH 추천에 Anthropic Claude API 호출 필요. 두 모델:

1. **Managed key (우리 부담)** — 사서는 키 입력 안 함, 우리가 API 비용 부담
2. **BYOK (Bring Your Own Key)** — 사서가 본인 Anthropic 키 발급·입력

## 결정

**BYOK 채택**. 사서가 본인 Anthropic 키로 Claude API 호출.

## 결과

- 우리 운영비 권당 약 2원 (Vision/KDC) → **0원**
- 권당 100원 가격에 마진 93% 유지 (서버·외부 API 5원만 우리 부담)
- 사서가 AI 미사용 시 ISBN/Vision/검색 모두 정상 작동 (degraded 아님)
- 사서 자기 결정권: 본인 비용으로 더 정확한 AI 추천 받을지 선택

## 트레이드오프

✅ **장점**
- 우리 비용 0 → 가격 100원 유지 가능
- 사서 신뢰: 우리가 사서의 책 사진을 자기 비용으로 처리 안 함
- Anthropic 콘솔에서 사서 본인이 사용량·비용 직접 통제

❌ **단점**
- 사서가 Anthropic 키 발급 1단계 추가 (`docs/byok-anthropic-key-guide.md` 필요)
- 50대 비IT 사서에게 진입 장벽
- 사서 키 발급률 30~50% 추정 → AI 기능 사용률 동일

## 완화 조치

- **AI 미사용 모드 100% 작동**: ISBN·Vision·검색·KDC 트리·NLSH 시드 어휘만으로도 사서 가치 충분
- 가격 페이지 "AI 추천은 선택" 명시
- 영업 메시지에서 BYOK 비용을 "권당 약 0.5원"으로 사서에게 투명 공개
- AI 사용 시연 시 PO 본인 키로 시연 → 사서가 직접 만들 필요 없음

## 6개월 후 되돌릴 수 있는가?

**Y** — Managed key로 전환은 환경변수 한 줄 변경. 단 가격을 권당 130~150원으로 올려야 마진 유지. 베타 사서 결제 의향 데이터 보고 결정.

## 관련 모듈

- `src/kormarc_auto/_anthropic_client.py` — `user_api_key` 인자
- `src/kormarc_auto/ui/streamlit_app.py` — 사이드바 "AI 추천 보조 키 (선택)"
- `CLAUDE.md §12` 가격 모델
