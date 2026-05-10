# ADR 0068: MongoDB = 운영 로그만·사용자 데이터 client-side·헌법 §14 정합

**상태**: Active
**날짜**: 2026-05-10 (Cycle 1361)
**관련**: 헌법 §14 + ADR 0048 (자관 데이터 정책) + `_meta/118` (보안 결정 박제)

---

## 1. 컨텍스트

PO가 MongoDB Atlas Free M0 클러스터 발급 + Network Access에 `0.0.0.0/0` 추가·"클로드 활동용". Vercel serverless 고정 IP 부재로 인한 트레이드오프 결정 의무.

자율 진단 (Cycle 1361 grep 결과):
- 14 SaaS 中 **3 SaaS만 MongoDB 실제 import** (#100 명함관리·#101 영어회화·#102 어린이그림일기)
- 11 SaaS = pymongo·MongoClient import 0건 = client-side·헌법 §14 정합
- kormarc-auto 본체 = MongoDB 사용 X (자관 PC만)

## 2. 결정 (옵션 A + 옵션 C 혼합)

### 보안 정책
- ✅ Network Access `0.0.0.0/0` 단기 유지 (Free plan + Vercel 정합)
- ✅ DB 비밀번호 32자+ 무작위 (1Password 생성·brute-force 사실상 불가·10^60 조합)
- ✅ Built-in Role: `readWrite only` (atlasAdmin·dbAdmin 금지)
- ✅ SCRAM-SHA-256 인증 (Atlas 기본)
- ✅ Atlas Account 2FA 의무

### 데이터 분리 원칙 (헌법 §14 정확 정합)

| 데이터 종류 | 저장 위치 | 사유 |
|---|---|---|
| Polar webhook 결제 시도 로그 | MongoDB (3 SaaS) | M25 정합·외부 시도 영구 보존 |
| Polar order.created·paid·refund | MongoDB | 매출 audit log |
| 결제 카드 정보 | Polar 자체 DB | PCI DSS·우리 미터치 |
| **사용자 가계부·할일·약 복용·식단·일기 데이터** | **client localStorage** | **헌법 §14 정확 정합·SaaS 서버 X** |
| kormarc-auto 사서 데이터 | 자관 PC만 | ADR 0048·invariant 12·도서관 RFP 통과 |

### Connection String 관리
- 로컬: PowerShell `setx MONGODB_URI "..."` (영구 환경변수)
- Vercel production: `vercel env add MONGODB_URI production` (3 SaaS 각 project)
- Git: `.env.example`만 commit (placeholder·실제 값 X)
- 채팅·문서 X 정책 (Cycle 1361 노출 사례 학습)

## 3. Phase 단계

### Phase 1: 현재 (외부 사용자 0)
- Free M0 + 0.0.0.0/0 + 32자 비밀번호
- 운영 로그만 (결제 webhook)
- 사용자 데이터 = localStorage

### Phase 2: 외부 사용자 1명+ 발생 시
- Atlas Pro plan ($9/월) 또는 Vercel Postgres 전환
- Network Peering 또는 Private Endpoint
- audit log + hash chain (이미 박제됨·`hash_chain.py`)

### Phase 3: 사용자 100명+ (PIPA Q5 의무)
- 암호화 (at-rest + in-transit)
- DSAR 자동화 (제35·36조)
- 72h 신고 자동화 (해킹 시)
- SOC2 type 2 또는 ISMS-P (도서관 RFP 정합)

## 4. 적용 범위

### MongoDB 등록 의무 SaaS (3건)
1. `30-apps/100_명함_관리/landing/api/webhook.py` (business-card-manager)
2. `30-apps/101_영어회화_카드/landing/api/webhook.py` (english-phrase-cards)
3. `30-apps/102_어린이_그림일기/landing/api/webhook.py` (kids-picture-diary)

### MongoDB 미사용 SaaS (11건·헌법 §14 정합)
- kormarc-auto·simple-budget·simple-todo·medication-reminder·simple-budget·general-docs-auto·group-member-manage·receipt-ocr-auto·ai-writer-auto·diet-workout-tracker·robux-morse-converter·all-access-bundle

→ 11 SaaS = MONGODB_URI 등록 X·자율 회피 의무.

## 5. 회수 조건 (Phase 1 → Phase 2 전환)

다음 트리거 中 1건 발생 시 즉시 Phase 2 전환:
- 외부 사용자 1명+ 발생
- Polar 결제 시도 1건+ 발생
- DB 비밀번호 노출·rotate 의무
- 0.0.0.0/0 보안 사고 발생

## 6. 평가축 (헌법 §0/§12)

- §0 사서 마크 시간 단축: 직접 영향 X (kormarc-auto는 MongoDB 사용 X)
- §12 사서 결제 의향: 도서관 RFP 통과 = §14 정합 = §12 양수 (사서 신뢰)
- Q5 컴플 (PIPA): PASS (사용자 데이터 서버 저장 X)

## 7. 참조

- 헌법 `CLAUDE.md §14` (사서 데이터 자관 PC만)
- `ADR 0048` (자관 데이터 정책·invariant 12)
- `_meta/118_mongodb_security_decision_2026_05_10.md` (보안 결정 박제)
- `_meta/116_244cycle_url_hallucination_correction.md` (자기 진단 박제 회피 정합)
- `business-impact-axes.md` Q5 (PIPA 5대 패턴)
