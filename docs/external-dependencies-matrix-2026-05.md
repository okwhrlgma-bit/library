# 외부 작업 매트릭스 — 2026-05-06 (Cycle 24)

> Plan B P29~P52 24개 중 **22 완료·2 미완 (P30·P39)** + 매출 활성 차단점 단일 진실원.
> PO 외부 작업 = `사용자_TODO.txt` (이미 보유)·본 매트릭스 = 의존 관계 + 차단점 우선순위.

## 즉시 가능 (PO 외부 작업·코드 100% 준비됨)

| ID | 작업 | 소요 | 차단 해소 | 매출 영향 |
|---|---|---|---|---|
| **PO-PROD-1** | 일반과세자 홈택스 등록 (722000) | 30분·2-3 영업일 | P30 PortOne 라이브 활성·세금계산서 | 🔴 매출 0 → 가능 |
| **PO-PROD-2** | 통신판매업 신고 (정부24) | 1시간 | PG 심사·도서관 거래 | 🔴 PG 활성 |
| **PO-PROD-3** | 사업자통장 (카뱅·토스 + 시중은행 1) | 30분 | B2B 가상계좌·세금계산서 | 🔴 결제 |
| **PO-PROD-5** | NL_CERT_KEY (SEOJI) 발급 | 1~3일 | 12 KORMARC 필드 자동·SEOJI backbone | 🟡 정확도 |
| **PO-PROD-6** | ANTHROPIC_API_KEY 발급 | 5분 | LLM Vision·KDC 추천·prompt cache 실측 | 🟡 AI 기능 |

## 외부 도구·인증서 (PO 환경)

| ID | 작업 | 소요 | 차단 해소 |
|---|---|---|---|
| TOOL-1 | gh CLI 설치 | 5분 | GitHub Release 자동 (Cycle 2 SKIPPED 회복) |
| TOOL-2 | charmbracelet vhs 설치 | 5분 | README GIF 데모 (Cycle 6 P5 SKIPPED 회복) |
| TOOL-3 | claude-agent-sdk pip install | 1분 | router.py·proposer_critic.py·supervisor.py 활성 |

## 영업 외부 (PO 결정 후)

| ID | 작업 | 시점 | 매출 영향 |
|---|---|---|---|
| SALES-1 | 사서 5명 cold outreach (Mom Test) | 즉시 (외부 901 보고서 진단) | 🔴 인터뷰 = wedge 확정 가능 |
| SALES-2 | KLA 전국도서관대회 발표 (D-28) | 2026-05-31 마감 | 🟡 영업 자료 인용 |
| SALES-3 | 학교장터(s2b.kr) 등록 | 사업자 등록 후 | 🟡 학교 거래 채널 |
| SALES-4 | 디지털서비스몰 카탈로그 | 사업자 + ISMS-P 후 | 🟢 자치구 일괄 |
| SALES-5 | 자치구 IT 담당 5명 콜드 메일 (KOLAS3 D-day) | 즉시 가능 | 🔴 자치구 묶음 진입 |

## 인증·보안 (매출 발생 후 18개월차)

| ID | 작업 | 비용 | 차단 해소 |
|---|---|---|---|
| CERT-1 | ISMS-P 간편인증 | 400-700만원 | 자치구 RFP 통과 |
| CERT-2 | CSAP 하등급 | 850-3,225만원 | 디지털서비스몰 등재·공공 진출 |
| CERT-3 | 한국정보접근성인증마크 (KWCAG 2.2) | 200-500만원·2년 | 정식 인증·도서관 RFP 가산점 |

## 정신건강·운영 (외부 901 보고서 진단·필수)

| ID | 작업 | 우선 |
|---|---|---|
| PO-WELL-1 | 청년 마음건강 신청 (서울/보건복지부) | 🔴 6 free sessions |
| PO-WELL-2 | 1577-0199·1393 phone 저장 | 🔴 |
| PO-WELL-3 | 17:30 shutdown ritual | 🟡 |
| PO-WELL-4 | 일요일 laptop off | 🟡 |

## 의존 그래프

```
[PO-PROD-1 일반과세자]──┐
                       ├──> [P30 PortOne 라이브] ──> 첫 결제 가능
[PO-PROD-2 통신판매]────┤
                       │
[PO-PROD-3 사업자통장]──┘

[PO-PROD-5 NL_CERT_KEY] ──> 12 KORMARC 필드 정확도 ↑
[PO-PROD-6 ANTHROPIC_API_KEY] ──> AI Vision·KDC 추천 활성

[SALES-1 인터뷰 5명] ──> wedge 확정 ──> P39 사서어 매핑 활성
[SALES-2 KLA D-28] ──> 영업 권위 ↑

[CERT-1 ISMS-P] ──> [SALES-3 학교장터] ──> 학교 매출
[CERT-2 CSAP] ──> [SALES-4 디지털서비스몰] ──> 자치구 매출
```

## 첫 매출 가능 시점 추정 (PO 즉시 PROD-1·2·3 진행 시)

- **D+0**: 일반과세자 등록 신청
- **D+3**: 등록 완료·통신판매 신고
- **D+7**: PG 가입·구매안전 확인증
- **D+14**: PortOne v2 라이브 모드 활성·첫 도서관 결제 가능
- **D+30**: 자치구 1관 PoC 시작 (KOLAS3 D-day 마케팅 시너지)

## 정합 메모리

- `~/.claude/projects/.../memory/project_korean_saas_production_2026_05_04.md` (외부 858 출처)
- `~/.claude/projects/.../memory/project_solo_founder_diagnosis_2026_05_03.md` (PO 정신건강)
- `~/.claude/projects/.../memory/project_revenue_growth_research_2026_05_05.md` (P29~P40)
- `~/.claude/projects/.../memory/project_claude_code_automation_v2_2026_05_06.md` (V2 자동화)

---

작성: Claude Opus 4.7 (1M context) · 2026-05-06 · Cycle 24
