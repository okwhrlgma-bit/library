# ADR 0026 — 한국 SaaS 프로덕션 출시 결정 (외부 858 출처)

- 상태: Accepted (PO 자율 위임·2026-05-04)
- 일자: 2026-05-04
- 트리거: 외부 deep research 858 출처 (사업자 등록·결제·영업·가격·인프라·법무 7 영역)

## Context

v0.6.0 release 후 v1.0 4개월 path. 외부 보고서가 7 영역 동시 결정점 제시. PO 자율 위임 (ADR autonomy 정책)으로 archi·법무·결제 결정 박제.

## Decision

### A. 사업자 등록 (즉시)
- **일반과세자** (간이 4,800만원 미만 = 세금계산서 발급 불가 = 도서관 거래 차단)
- **업종 722000** 응용 소프트웨어 개발 (정보통신업)
- **자택 사업장**·통신판매업 즉시 신고 (등록면허세 40,500원/년)
- 부업종 722005 컴퓨터 프로그래밍

### B. 결제 인프라
- **PortOne v2 + NHN KCP Primary + 토스 V2 Secondary**
- portone-server-sdk 0.20.0 pre-1.0 (REST API 하위호환 보장)
- B2B 세금계산서 API alpha = 가입 시 별도 활성화 요청
- Webhook = Standard Webhooks 스펙 (raw body·webhook-id Redis idempotency·GET payments/{id} 재검증)
- 결제 실패 grace = 7일·재시도 [0,1,3,7]
- 카드 만료 감지 = PG 응답 에러 (별도 만료 이벤트 X)
- 100명 × 5만원 매출 → 175,000원 수수료 (3.5%)

### C. 영업 동선 (4 단계)
| Phase | M0~M3 | M3~M9 | M6~M12 | M12~M18 |
|---|---|---|---|---|
| 타깃 | 사립 작은도서관 | 학교도서관 (s2b.kr) | 자치구 단관 (수의 2천만원) | 디지털서비스몰 |
| CSAP | ❌ | ❌ | △ | ✅ |

- 자치구 수의계약 임계: 2천만원 (1인)·5천만원 (2인)·1억 (영세·여성·청년)
- 학교회계 3.1~2.28·자치구 1.1~12.31·다년 계약 사실상 불가
- KOLAS III 2026.12.31 종료 = 5,100 미사용 작은도서관 = 6~12개월 진입창

### D. 가격 4 플랜 (한국도서관법 정합 명명)
- 작은도서관 ₩30,000 / 학교 ₩50,000 / 공공 ₩150,000 / 기관 ₩300,000~
- 연 결제 17% 할인 (2개월 무료)
- 신규 50% 첫 1년·5/10개관 묶음 10/15%
- 영구 freemium 50건/월 + 30일 무료 (신용카드 X)
- 도서관부호 또는 사업자등록번호 1:1 매칭 (남용 차단)

### E. 인프라 (월 25,000~50,000원)
- AWS Lightsail Seoul $10 + Cloudflare Free + 가비아 .co.kr
- AWS SES Seoul + DNS SPF/DKIM/DMARC 3종 (G메일/네이버 정책)
- SSL 47일 자동 갱신 (Let's Encrypt + Caddy)
- Pretendard CDN + KRDS 토큰 = KWCAG 90%
- pg_dump → S3 IA·SLA 99.5%·RPO 24h·RTO 4~8h
- 자치구 진출 시 → NCP/NHN CSAP 클라우드 전환

### F. 법무 Day 1 7종 + Quarter 2 보강
1. 처리방침 (§30 8항목 + §28의8 6항목 Anthropic·AWS·PortOne·Google + §37의2 입장)
2. 이용약관 (표준약관 10023호 + 자동갱신 + 책임 한도 직전 12개월)
3. 환불정책 (4곳 표시·§17 4유형·3영업일 환급)
4. SLA 99.5% (5~15% 환급)
5. DPA (PIPA §26 시행령 §28 8항목)
6. 사업자정보 footer (전상법 §10 12 항목)
7. AI disclaimer (3곳·인공지능 기본법 §31 2026.1.22 사전 적용)

### G. 가장 위험한 1번: §28의8 국외이전 6항목 누락
- PIPC 결정 2024-010-184 동일 사유 시정 선례
- 처리방침에 Anthropic 6항목 표 (이전 항목·국가·일시·받는 자·목적·거부 방법)
- §28의8 ①항 3호 = 계약 위탁 + 처리방침 공개 = 동의 갈음

### H. §37의2 KORMARC 적용
- 도서 메타데이터 = 일반 개인정보 X = 발동 전제 미충족
- "사서 검토·수정·승인" 전제 = 완전 자동화 X
- 처리방침 안전 기재 (설명요구 30일 내 회신)
- ⚠ 정정: §35의2 = 전송요구권 (2025.3.13)·§37의2 = 자동화 결정 (2024.3.15)

### I. 인증 의사결정
- ISMS-P 의무 = 매출 100억 OR 일평균 100만 사용자 = 1년차 대상 X
- KISA 간편인증 (300억 미만·40항목·400~700만원) = 자치구 진출 시
- CSAP = 매출 발생 후 18개월차 검토 (소기업 70% 할인)
- 2026 CSAP 개편 (국정원 보안적합성 일원화) 모니터링

### J. 2026.9.11 PIPA 개정 대응
- 과징금 매출 3% → 10%
- Quarter 2 점검 일정화

## Consequences

### Positive
- 일반과세자 = 모든 도서관 거래 가능 (간이 trap 회피)
- KCP + 토스 V2 dual = 빌링키 안정 + 가상계좌 강력 + 세금계산서 통합
- 4 플랜 한국도서관법 명명 = 즉시 인지·전환율 ↑ (Lite/Standard/Pro 대비)
- §28의8 6항목 사전 작성 = PIPC 시정 선례 회피
- KOLAS III 종료 마이그레이션 패키지 = Quarter 2 핵심 출시 항목

### Negative
- 4대보험 지역가입자 전환 = 월 ~155,000~700,000원 추가
- 일반과세 부가세 의무 = 매분기 신고 (1·4·7·10월)
- portone-server-sdk pre-1.0 = 인터페이스 변경 가능성
- B2B 세금계산서 alpha = 가입 시 활성화 요청 누락 시 B2bNotEnabledError
- 자치구 자동결제(빌링키) 거의 불가 = 분기/연 일괄 청구 흐름 강제

## Plan B 큐 추가 (P29~P31 신설)

기존 P1~P28 (B안 §0)에 추가:
- **P29**: 처리방침 v1 (§28의8 Anthropic 6항목 표·법무 7종 모듈)
- **P30**: PortOne v2 + KCP Primary 통합 (FastAPI webhook + 빌링키 + B2B 세금)
- **P31**: 4 플랜 가격 페이지 (도서관 카테고리 명명·30일 freemium·견적서 PDF)

P29 = Cycle 8·P30 = Cycle 9·P31 = Cycle 10 (자동 전환).

## PO 외부 작업 (TODO 재배치)

P0 즉시:
- 일반과세자 홈택스 등록 (722000·자택)
- 통신판매업 신고 (PG 가입 → 구매안전서비스 → 정부24)
- 사업자통장 (카뱅/토스 비대면 + 시중은행 1)
- 4대보험 지역가입자 전환 + 자영업자 고용보험 임의가입

## Alternatives Considered

### Alt 1: 간이과세자 시작
- Reject: 세금계산서 발급 불가 = 도서관 거래 0건

### Alt 2: 토스페이먼츠 Primary
- Reject: KCP 가상계좌 강력성 + 연관리비 면제 우위

### Alt 3: KT Cloud / 가비아 클라우드 호스팅
- Reject: Lightsail Seoul $10 = 가성비·CSAP 진출 시 NCP 전환 단순

### Alt 4: CSAP 1단계 신청
- Reject: 852~3,225만원 + 5~12개월 = 매출 0 단계 비합리

## References

- 외부 858 출처 deep research (2026-05-04)
- Memory: project_korean_saas_production_2026_05_04.md
- ADR 0023 (LLM provider 추상화·Bedrock Seoul CSAP)
- ADR 0025 (Plan B 무중단 자율)
- 1차 출처: hometax.go.kr·developers.portone.io·digitalmarket.kr·privacy.go.kr 결정 2024-010-184·isms.kisa.or.kr·a11ykr.github.io/kwcag22

---

작성: Claude Opus 4.7 (1M context) · 2026-05-04 · ADR autonomy + Plan B 정합
