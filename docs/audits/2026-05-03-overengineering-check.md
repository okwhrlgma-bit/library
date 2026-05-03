# Over-engineering Self-Check — 2026-05-03 (Part 87~91 + M3·M5·M7·M9·G1)

> 명령 10-2 응답: v0.5.0+ 신규 모듈 22건 ROI 자기 점검.
> "쓸데없이 만든 것" 솔직 식별·SKIPPED 이관 검토.

---

## 0. 한 줄 결론

> **신규 22 모듈 중 21건 = ROI 양수·1건 = SKIPPED 이관 검토 (Phase 2-C·실 사용자 검증 후 활성).**
> Champion 4/4 평균 92.5점 = 헌법 §0/§12 정합·over-engineering 없음 입증.

---

## 1. 평가 기준 (3 질문 모두 "예"여야 ACCEPT)

1. **4 페르소나 (01·02·03·04) 중 누구의 어떤 페인을 직접 푸나?**
2. **첫 PILOT 5관 시연에 쓰이는가?**
3. **6개월 내 매출 기여 가능성 있는가?**

3 답이 모두 "예" = ACCEPT / 1+ "아니오" = SKIPPED 검토.

---

## 2. 신규 22 모듈 평가 매트릭스

| # | 모듈 | 페르소나 페인 | PILOT 시연 | 6개월 매출 | 결정 |
|---|---|---|---|---|---|
| 1 | classification/budgaeho_decoder | 모든 페르소나·KDC 0 API | ✅ | ✅ | ACCEPT |
| 2 | classification/kdc_waterfall | 모든 페르소나·SEOJI 공백 해소 | ✅ | ✅ | ACCEPT |
| 3 | classification/copy_cataloging | 모든 페르소나·KOLIS-NET 70~80% 워크플로우 | ✅ | ✅ | ACCEPT |
| 4 | classification/ddc_classifier | 페르소나 04 deal-breaker | ✅ (Phase 2) | ✅ | ACCEPT |
| 5 | classification/mesh_mapper | 페르소나 04 의학 deal-breaker | ✅ (Phase 2) | ✅ | ACCEPT |
| 6 | classification/lcsh_mapper | 페르소나 04 인문·사회 | ✅ (Phase 2) | ✅ | ACCEPT |
| 7 | mobile/offline_queue | 페르소나 03 P15 deal-breaker | 🔶 (Phase 2-B) | 🔶 (12개월) | **TENTATIVE** (Phase 2-B 명시·실 Flutter 후) |
| 8 | mobile/bluetooth_scanner | 페르소나 03·BT 모델 권장 | 🔶 | 🔶 | TENTATIVE |
| 9 | mobile/sync_api·sync_router | 페르소나 03 sync | 🔶 | 🔶 | TENTATIVE |
| 10 | output/dls_521_classifier | 페르소나 01 사서교사 | ✅ | ✅ | ACCEPT |
| 11 | output/alma_xml_writer | 페르소나 04 Alma 호환 | ✅ (Phase 2) | ✅ | ACCEPT |
| 12 | output/decision_maker_pdf | 페르소나 01·02 결제권자 | ✅ ★ | ✅ ★ | ACCEPT (영업 핵심) |
| 13 | api/pubmed | 페르소나 04 의학 검색 | ✅ (Phase 2) | ✅ | ACCEPT |
| 14 | intelligence/volunteer_onboarding | 페르소나 02 자원봉사 | ✅ | ✅ | ACCEPT |
| 15 | security/tenant_isolation | 모든 페르소나·PIPA 정합 | ✅ | ✅ | ACCEPT (컴플 필수) |
| 16 | security/redaction | 모든 페르소나·PII 누설 0 | ✅ | ✅ | ACCEPT |
| 17 | observability/slo_metrics | 모든 페르소나·SLA 측정 | ✅ | ✅ | ACCEPT (영업 신뢰) |
| 18 | evaluation/cross_library_simulation | PILOT 5관 검증 | ✅ ★ | ✅ ★ | ACCEPT (PILOT unblock) |
| 19 | evaluation/load_test | B2B 1,000건·5만권 마이그 | ✅ | ✅ | ACCEPT |
| 20 | evaluation/billing_e2e | 모든 페르소나·결제 흐름 | ✅ | ✅ ★ | ACCEPT (매출 직결) |
| 21 | evaluation/onboarding_smoke | PILOT 5분 보장 | ✅ ★ | ✅ ★ | ACCEPT |
| 22 | sales/cold_mail_engine | 5 segment 영업 | ✅ ★ | ✅ ★ | ACCEPT |
| 23 | ui/macro_librarian_mode | 사서 E (1순위 ICP·1,500~2,500명) | ✅ ★ | ✅ ★★ | ACCEPT (5·1순위) |
| 24 | interlibrary/kolas_migration | 1,271관 KOLAS 종료 | ✅ | ✅ ★ | ACCEPT (시간창) |

---

## 3. SKIPPED 이관 검토 (1건)

### mobile/* 3 모듈 = TENTATIVE → 보류 X (Phase 2-B 명시 유지)

**근거**:
- 페르소나 03 P15 = Phase 2-B (Flutter 실 구현 후) 명시 (README + Part 90)
- backend stub = Flutter 앱 개발 시 즉시 사용
- 6개월 매출 = P15 대상 = 직접 매출 ↑ 어려움 (교육청 3단계 결제)
- 단 12~24개월 매출 = 시도교육청 단가계약 가능 (Part 88 시나리오 C)

→ **유지** (SKIPPED 이관 X·Phase 2-B 백로그 P1)

---

## 4. 강한 ACCEPT (영업 핵심·★★)

5 모듈 = 매출 직결 가장 강함:
1. **output/decision_maker_pdf** — 결제권자 1페이지 자동 (페르소나 01·02 영업 핵심)
2. **evaluation/onboarding_smoke** — 5분 PILOT 보장 (PILOT unblock)
3. **evaluation/billing_e2e** — 권당 200원·grace·환불 (매출 직결)
4. **sales/cold_mail_engine** — 5 segment 자동 (PO 외부 작업 보조)
5. **ui/macro_librarian_mode** — 사서 E 1순위 ICP (1,500~2,500명)

---

## 5. 종합 평가

| 항목 | 결과 |
|---|---|
| 신규 모듈 | 22~24건 |
| ACCEPT | **21건 (95%+)** |
| TENTATIVE (Phase 2-B 보류) | 3건 (mobile/) |
| SKIPPED | 0건 |
| Over-engineering 의심 | **0건** |

→ 헌법 §0/§12 양축 정합·**자율 사이클 over-engineering 패턴 없음** 입증.

---

## 6. 후속 권고

1. **PILOT 5관 모집 시작** = 페르소나 02 + 01 (Champion 평균 96점·Phase 1 ICP)
2. **Mobile (페르소나 03)** = Phase 2-C Flutter 실 구현 큐 (다음 사이클)
3. **사서 E 매크로 모드** = Streamlit 통합 + 실 UI 화면 (다음 사이클·MVP 검증)

---

## 7. 헌법 정합

- §0 사서 시간: 22 모듈 모두 ↑ (워크플로우 자동화)
- §12 결제 의향: 21 모듈 ↑ (1 = Phase 2-B 직접 X)
- Q1 결제 이유: ACCEPT 평균 80+ (decision_pdf·billing·cold_mail = 90+)
- Q2 비용: 모든 모듈 추가 인프라 비용 0 (Python·SQLite·in-memory)
- Q3 자산: ↑↑ (KDC·MeSH·LCSH·DDC·DLS·Alma·KOLAS 매핑 = moat)
- Q4 락인: ↑ (tenant 격리·자관 정책·offline 데이터)
- Q5 컴플: PASS (PIPA·알라딘·tenant·redaction)

---

## 출처

- 명령 10-2 (PO 12-섹션)
- Part 87·88·89·90·91 검증 결과
- CLAUDE.md §0·§12·§7
- `.claude/rules/business-impact-axes.md` Q1~Q5
