# Part 70 — 추가 놓친 영역 12 식별 (2026-05-02)

> PO 명령 (2026-05-02): "이 외의 놓친 것 있는지 파악"
> 정직한 자체 감사 = Part 60~69 외 = 12 추가 갭 발견

---

## 0. 자체 감사 방법 (113 페르소나 시각으로 전수 점검)

기존 점검:
- ✅ 영업·마케팅·전환 (Part 56~62)
- ✅ FMEA 100 시나리오 (Part 61)
- ✅ Bottom-up PLG·B2C (Part 60)
- ✅ UI/UX·디자인 (Part 65·66)
- ✅ 페르소나 (Part 67·68 = 113명)
- ✅ 정부 자금·IP·Lifecycle (Part 68)
- ✅ 디바이스 (Part 69)

**누락 확인 시각**: 사서 일과 + 데이터 + 보안 + 통합 + 운영 + 결제 + 글로벌

---

## 1. 데이터 신뢰·관리 영역 (3 갭) ★★★★★

### 갭 1: 데이터 export 다양화 (TXT·MARC만 = 부족)

**현재**: KOLAS·KLMS .mrc + CSV
**갭**: MARCXML·MODS·BIBFRAME·JSON·OAI-PMH·LOD 미지원
**페인**: 대학 (BIBFRAME)·국제 (MODS)·웹 통합 (JSON·LOD) 진입 X

**즉시 보완**:
- `output/export_marcxml.py` (대학·KORIBLE)
- `output/export_mods.py` (NLK 디지털 컬렉션)
- `output/export_json.py` (API·웹 통합)
- `output/export_oai_pmh.py` (수확·종합목록)
- `output/export_bibframe.py` (Phase 2 = 대학 2027 표준)

### 갭 2: 데이터 import 다양화

**현재**: ISBN·CSV·xlsm 일부
**갭**: MARCXML import·MODS import·기존 도서관 시스템 마이그
**페인**: 알파스 → kormarc-auto 마이그·KOLAS 백업 → 신규 시스템

**즉시 보완**:
- `ingest/marc_importer.py` (MARC·MARCXML 파싱)
- `ingest/mods_importer.py` (MODS XML 파싱)
- `ingest/kolas_backup_importer.py` (KOLAS .mrc 백업 일괄 가져오기)

### 갭 3: 중복 검출·합본·데이터 품질

**현재**: 단순 추가만
**갭**: 같은 책 중복 ISBN·복본 처리·합본 X
**페인**: 자관 1만 권 = 중복 5%+ = 사서 검증 부담

**즉시 보완**:
- `quality/dedup_detector.py` (ISBN·제목·저자 기반)
- `quality/merge_records.py` (중복 합본·정합성)
- `quality/integrity_check.py` (008 40자리·245·880 자동 검증)

---

## 2. 보안·인증 영역 (3 갭) ★★★★★

### 갭 4: 2FA·SSO·권한 관리

**현재**: 단일 API 키 (kma_)
**갭**: 2FA (이중 인증)·SSO (대학·자치구)·다중 사용자 권한
**페인**: 대학·자치구 = 보안 요구 = 진입 차단점

**즉시 보완**:
- 2FA = TOTP (Google Authenticator·Authy)
- SSO = SAML 2.0 (대학)·OAuth (Google·카카오)
- 권한 = 사서·관장·자원봉사·관리자 4단계 (RBAC)

### 갭 5: API rate limiting + abuse 방지

**현재**: 무제한 (이론) = abuse 위험
**갭**: rate limit·DDoS·SQL injection 방어 미공식
**페인**: 1관 abuse = 인프라 비용 폭증·SLA 위반

**즉시 보완**:
- API rate limit (분당 60건·시간당 1,000건 등)
- Cloudflare WAF (DDoS·DOS 방어)
- ORM·prepared statement (SQL injection)
- CSP·CSRF·XSS 방어 헤더

### 갭 6: 활동 로그·감사·DSAR

**현재**: 기본 로깅만
**갭**: 사서별 활동 로그·감사 trail·DSAR (개인정보 자동 제공)
**페인**: PIPA 권리 요구 시 = 수동 처리 = 위반 위험

**즉시 보완**:
- `audit/activity_logger.py` (사서별 작업·해시 체인)
- `privacy/dsar_handler.py` (자동 DSAR 처리·30일 내 응답)
- `privacy/data_deletion.py` (right to forget 자동)

---

## 3. 사서 일과 영역 (3 갭) ★★★★

### 갭 7: 상호대차 통합 (5 시스템)

**현재**: 자관 단일
**갭**: 책바다·책나래·책이음·책두레·책단비 통합 X
**페인**: 사서 일과 30% = 상호대차 = 별도 작업

**즉시 보완** (Phase 1.5):
- `interlibrary/chaek_bada.py` (책바다·NLK 5,200원·전국)
- `interlibrary/chaek_narae.py` (책나래·NLD 무료·장애인)
- `interlibrary/chaek_ieum.py` (책이음·KOLAS 통합 회원증)
- `interlibrary/chaek_dure.py` (책두레·KOLAS 모듈)
- `interlibrary/chaek_danbi.py` (책단비·은평구·자관 정합)

### 갭 8: 사서 일과 외 (수서 결정·신간 추천)

**현재**: 정리 단계만
**갭**: 수서 결정·신간 추천·예산 관리 X
**페인**: 사서 일과 = 수서·정리·배가 = 1단계만 자동

**즉시 보완** (Phase 1.5):
- `acquisition/decision_helper.py` (출판사·가격·평점 통합)
- `acquisition/new_book_recommender.py` (KDC 기반 추천)
- `acquisition/budget_tracker.py` (자관 예산 추적)

### 갭 9: 분실·파손·제적 (Withdrawn) 처리

**현재**: 등록만·withdrawn X
**갭**: 008 변경·853 제적 일자·자관 history 보존
**페인**: 폐기 도서 = 수동 = KORMARC 정합 X

**즉시 보완**:
- `lifecycle/withdrawn_processor.py` (008·853 자동·history)

---

## 4. 운영·DevOps 영역 (1 갭) ★★★★

### 갭 10: 모니터링·관측 인프라

**현재**: 기본 logging만
**갭**: Sentry·Datadog·UptimeRobot·CDN·DDoS 보호
**페인**: SLA 99.5% 약속 X·장애 발견 X·이용자 영향

**즉시 보완** (T3 DevOps 자율):
- Sentry (에러 모니터링)
- UptimeRobot (uptime 99.5%+)
- Cloudflare (CDN·WAF·DDoS)
- 자동 알림 (PO 카톡)
- 분기 SLA 보고서 자동

---

## 5. 결제·과금 영역 (1 갭) ★★★

### 갭 11: 결제 다양화·자동 환불·invoice

**현재**: 포트원 권장 (수동 환불·세금계산서)
**갭**: 결제 수단 다양화·자동 환불·invoice 자동·연 결제 자동 할인
**페인**: 환불 = 수동 = 1인 부담·자치구 일괄 청구 X

**즉시 보완**:
- 결제 수단: 카드·계좌이체·카카오페이·네이버페이·페이팔
- 자동 환불 routine (1주 100% 보장)
- 세금계산서 자동 (포트원 + 팝빌)
- invoice PDF 자동 다운로드
- 자치구 일괄 청구 (월·분기·연)
- 연 결제 자동 20% 할인

---

## 6. 사서 개인 통계·Personal Win (1 갭) ★★★★★

### 갭 12: 사서 개인 통계 대시보드 (Part 65 wow #4 직격)

**현재**: time_tracker (단순) = Part 49
**갭**: 사서 개인 통계 대시보드·평가 자료·승진 자료
**페인**: Personal Win 메시지 X = 결제 의향 ↓

**즉시 보완** (DT2 BI Developer 자율):
- `ui/personal_stats_dashboard.py` 신규
- 이번 달 처리 권수·시간·절감
- 작년 동월 대비
- 사서 평가 가산점 자동 (PDF·분기)
- KLA·KSLA 발표 자료 자동
- LinkedIn·이력서 인용 가능
- 1주년·3주년 인증서 자동

---

## 7. 종합 갭 12 우선순위 매트릭스

| # | 갭 | 영역 | 우선 | Phase |
|---|----|----|----|----|
| 1 | 데이터 export (MARCXML·MODS·JSON·OAI-PMH) | 데이터 | ★★★★ | Phase 1 |
| 2 | 데이터 import (MARC·MODS·KOLAS 백업) | 데이터 | ★★★★ | Phase 1 |
| 3 | 중복 검출·합본·정합성 | 데이터 | ★★★★ | Phase 1 |
| 4 | 2FA·SSO·권한 (RBAC) | 보안 | ★★★★★ | Phase 1 |
| 5 | API rate limit·WAF·CSRF | 보안 | ★★★★★ | Phase 1 |
| 6 | 활동 로그·감사·DSAR 자동 | 보안·PIPA | ★★★★★ | Phase 1 |
| 7 | 상호대차 5 시스템 통합 | 사서 일과 | ★★★ | Phase 1.5 |
| 8 | 수서 결정·신간 추천·예산 | 사서 일과 | ★★ | Phase 2 |
| 9 | 분실·파손·제적 처리 | 사서 일과 | ★★ | Phase 1.5 |
| 10 | 모니터링·관측 (Sentry·Cloudflare) | 운영 | ★★★★★ | Phase 1 |
| 11 | 결제 다양화·자동 환불·invoice | 결제 | ★★★★ | Phase 1 |
| 12 | **사서 개인 통계 대시보드** | Personal Win | ★★★★★ | Phase 1 |

---

## 8. Phase 1 즉시 적용 우선순위 (Top 7 = 캐시카우 직결)

### 즉시 자율 진행
1. **사서 개인 통계 대시보드** (DT2·Personal Win = wow #4)
2. **2FA·SSO·권한 RBAC** (대학·자치구 진입 차단점)
3. **API rate limit + WAF** (보안·SLA)
4. **활동 로그·DSAR 자동** (PIPA 정합)
5. **모니터링 인프라** (Sentry·UptimeRobot·Cloudflare)
6. **데이터 export 4종** (MARCXML·MODS·JSON·OAI-PMH)
7. **결제 다양화·자동 환불·invoice 자동**

→ 7건 = 약 60시간·L2~L3 = 1~2 주 자율 가능

---

## 9. AUTONOMOUS_BACKLOG 신규 (Part 70)

### Phase 1 즉시 (Top 7 = 자율)
- [ ] DT2 사서 개인 통계 대시보드 (`ui/personal_stats_dashboard.py`)
- [ ] T3 + L2 = 2FA + SSO + RBAC (4단계 권한)
- [ ] T3 + SEC1 = API rate limit + Cloudflare WAF + CSRF
- [ ] L2 + 자동 = 활동 로그 + DSAR + right-to-forget
- [ ] T3 = Sentry + UptimeRobot + Cloudflare CDN
- [ ] T17 = export_marcxml + export_mods + export_json + export_oai_pmh
- [ ] L1 + L3 = 결제 다양화 + 자동 환불 + invoice + 자치구 일괄

### Phase 1.5
- [ ] 상호대차 5 시스템 통합 (책바다·책나래·책이음·책두레·책단비)
- [ ] 데이터 import (MARC·MODS·KOLAS 백업)
- [ ] 중복 검출·합본·정합성

### Phase 2
- [ ] 수서 결정·신간 추천·예산 관리
- [ ] 분실·파손·제적 처리
- [ ] BIBFRAME (대학 2027)
- [ ] 글로벌 (영어·중국어·일본어·MARC21)

---

## 10. 캐시카우 도달율 갱신

| Part | 시스템 | 도달율 |
|------|------|------|
| 69 | 디바이스 90%+ | 390~640% |
| **70 (12 갭 중 Top 7 보완)** | + Personal Win + 보안 + 데이터 + 모니터링 | **410~670%** |

→ **사서 신뢰 + Personal Win + 보안 + 운영 = 캐시카우 도달율 30%p 추가**

---

## 11. PO 응답 정합

### Q "이 외의 놓친 것 있는지 파악"
✅ **12 추가 갭 식별** (정직한 자체 감사):

**최우선 7 (즉시 자율 진행)**:
1. 사서 개인 통계 대시보드 (Personal Win)
2. 2FA·SSO·RBAC
3. API rate limit·WAF
4. 활동 로그·DSAR
5. Sentry·UptimeRobot·CDN
6. 데이터 export 4종 (MARCXML·MODS·JSON·OAI-PMH)
7. 결제 다양화·자동 환불·invoice

**Phase 1.5 (3건)**: 상호대차 5종·데이터 import·중복 검출
**Phase 2 (2건)**: 수서 결정·withdrawn 처리

→ **70 Part·113 페르소나·11 subagent·45 사용자 작업·24 카테고리·캐시카우 410~670%**

---

> **이 파일 위치**: `kormarc-auto/docs/research/part70-additional-missed-areas-12-2026-05.md`
> **종합**: 12 추가 갭 (데이터·보안·일과·운영·결제·Personal Win)
> **PO 정합**: 자체 감사 = 정직 = 완벽 추구의 다음 차원
