# Kill List 30일 보고서 (COLD_START 적용·Cycle 807·2026-05-09)

> PO 5 명령 #4 응답·_meta/21 GTM 비판 정합·매출 0 단계 변별력 확보 (COLD_START_WEIGHTS).

## 1. 요약 (1줄)

```
9 등록 SaaS 중 1 KEEP (kormarc 82) + 8 SUNSET (36~50)·실 SUNSET 실행 = PO 직접 지시 의무 (PO #76 영구 충돌)
```

## 2. 적용 가중치 (COLD_START·매출·트래픽 0 단계)

| 기준 | OPERATIONAL | COLD_START | 비고 |
|---|---:|---:|---|
| revenue | 30 | 5 | 매출 0 = 변별력 0 |
| traffic | 20 | 5 | 색인 미완 = 변별력 0 |
| **po_fit** | 20 | **45** | 초기 B2B = 창업자 도메인만 돌파구 |
| differentiation | 10 | 15 | 무료 default와의 차별 |
| legal_risk | 8 | 15 | 공공 납품 PIPA·세금 필수 |
| cross_saas | 7 | 5 | B2B+B2C 혼합 = 허상 |
| maintenance | 5 | 10 | 멘탈·관리 부하 |

## 3. 9 SaaS 점수 (COLD_START)

| SaaS | Category | OP | CS | Status (CS) |
|---|---|---:|---:|---|
| **kormarc-auto** | B2B 도서관 | 44 | **82** | **🟢 KEEP** |
| group-member-manage | B2B 모임 | 29 | 50 | 🔴 SUNSET |
| receipt-ocr-auto | B2B 자영업 | 29 | 47 | 🔴 SUNSET |
| simple-budget | B2C 가계부 | 28 | 47 | 🔴 SUNSET |
| general-docs-auto | B2B 일반 | 28 | 46 | 🔴 SUNSET |
| ai-writer-auto | B2C 콘텐츠 | 27 | 46 | 🔴 SUNSET |
| medication-reminder | B2C 노년·만성 | 26 | 45 | 🔴 SUNSET |
| simple-todo | B2C 생산성 | 23 | 40 | 🔴 SUNSET |
| diet-workout-tracker | B2C 헬스 | 21 | 36 | 🔴 SUNSET |

## 4. KEEP 1 (kormarc-auto·점수 82·KEEP 임계 70 이상)

```
✅ PO Domain Fit 100 (사서 출신·도메인 절대 적합)
✅ KOLAS III EOL 2026-12-31 = D-235 골든윈도우
✅ KORMARC + 폐쇄형 B2B 생태계 = 진입 장벽 (해자)
✅ 알파스 ₩1,000만/라이선스 vs SaaS ₩30~50만/년 = 가격 경쟁력
✅ TAM 1,296 공공 + 11,826 학교도서관
```

## 5. SUNSET 8 (점수 36~50·임계 60 미달)

| SaaS | 진단 |
|---|---|
| group-member | 카톡 단톡방·밴드 무료 default·신뢰 0 |
| receipt-ocr | 홈택스 호환 강점·B2B 피벗 시 75 가능 (보류 후보) |
| simple-budget | 토스·뱅샐 마이데이터 = 경쟁 불가 |
| general-docs | 뤼튼·노션 무료 default |
| ai-writer | 뤼튼 GPT-5·노션 AI 무료 default |
| medication | 한국화 niche·B2B 약국 피벗 시 보류 가능 |
| simple-todo | 카톡 "나에게 보내기" = 1만:1 격차 |
| diet-workout | 다이어트신·삼성헬스 = 무료 default |

## 6. 보류 후보 2 (B2B 피벗 시 75 달성 가능)

```
- receipt-ocr (B2B 자영업·세무사·홈택스 자동 = niche 가능)
- medication (B2B 약국·요양원 = niche 가능)
```

## 7. 자원 재배분 권고 (PO 결정 시)

```
SUNSET 8 → kormarc 깊이 강화:
- pymarc 952·981 태그 일괄 검증
- KOLIS-NET 연동 시뮬
- KOLAS III 마이그레이션 도구
- 사서 1인 운영 자동 보고서 (월말 통계·업무 일지)
- 무료 파일럿 3 기관 case study 시드
- 카톡 비즈니스 채널·네이버 블로그·세금계산서 helper
```

## 8. PO 결정 매트릭스

| 시나리오 | 매출 가능성 | sunk cost | 추천 |
|---|---|---|---|
| **A. 즉시 8 SUNSET + kormarc 집중** | 高 (KOLAS III 골든윈도우) | 0 | ⭐ 권고 |
| B. 30일 외부 데이터 후 결정 | 中 (외부 발사 의존) | +30일 | 차선 |
| C. 다중 투망 유지 (PO #76) | 低 | 高 | 현 동결 |

## 9. 자율 처리 (Claude 영역)

```
- 8 SaaS COLD_START 점수 = SUNSET_RECOMMENDED 자동 분류
- sunset_manual 8 step 시드 = PO 1클릭 시 즉시 자동
- PO 직접 지시 X = 실 SUNSET 실행 X (PO #76 영구 충돌)
- 보고서 갱신 = 매주 자동 (Atlas Trigger 시드 가능)
```

## 10. 다음 액션

```
1. PO 결정 (시나리오 A/B/C) 대기
2. 시나리오 A 시 = sunset_manual 가동 + kormarc 깊이 강화
3. 시나리오 B 시 = 외부 발사 (PO 외부 작업) 의존
4. 시나리오 C 시 = 현 동결 + 매주 보고서 갱신
```
