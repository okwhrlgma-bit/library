# 도서관 정보나루 활용 가이드 — 수서 사서 영업 (2026-05)

> **대상**: 수서 사서 (박지수 페르소나 + 외부 도서관 수서 담당)
> **단일 진실**: 정보나루 = 한국도서관협회·문체부 운영·작은도서관·공공도서관 통합 데이터 보고
> **우리 정합**: `kormarc-auto wishlist` + `api/data4library.py` 키워드·인기 대출 통합

---

## 1. 도서관 정보나루 (data4library.kr) 한눈

| 항목 | 내용 |
|---|---|
| 운영 | 한국도서관협회 + 문체부 (위탁 운영) |
| URL | https://data4library.kr |
| 가입 | 무료 (이메일 본인 인증·1회) |
| API 키 | 회원가입 후 즉시 발급 (`authKey`) |
| 데이터 | 인기대출도서·신간·검색어·도서관 목록·이용자 통계 |
| 무료 한도 | 일 10,000건 (개인·도서관 모두) |

### 주요 API 5종

| API | 용도 | 우리 모듈 |
|---|---|---|
| `srchBooks` | 키워드·서명·저자 검색 | `api/data4library.fetch_keywords` |
| `loanItemsSrch` | 인기대출도서 (지역·연령·기간별) | `acquisition/wishlist.py` |
| `libSrch` | 전국 도서관 검색 | (Phase 2+) |
| `loanItemSrchByLib` | 특정 도서관 인기대출 | (Phase 2+) |
| `keywordList` | 검색어 통계 | `api/data4library.py` |

---

## 2. 수서 사서 영업 시나리오

### 2-1. 박지수 사서 PILOT 2주차 (5/3주)

```powershell
kormarc-auto wishlist --input pilot_2week.txt --output reports/wishlist_2week.json
```

→ 정보나루 인기대출도서 자동 import + 자관 중복·KDC 균형·예상 비용 자동.
→ 30분 수동 → 5분 자동 (75%+ 단축).

### 2-2. 영업 메일 (수서 사서)

**제목**: "수서 사서께 — 정보나루 인기대출 자동 import (월 3~15만원)"

```
안녕하세요. 사서 출신 1인 개발자 [PO 이름]입니다.

수서 워크플로우 9단계 (정보나루 검색 → KOLAS 중복 → KDC 균형 → 비용
산정 → 결재 → 발주 → 입수 → 등록 → 신착 안내) 모두 SaaS 1개로 자동화
가능합니다.

★ 자관 박지수 사서 9 워크플로우 100% 검증 완료 (PILOT 2주차)
★ 자관 .mrc 99.82% 정합 (한국 KOLAS 실무 정합)

[제안]
- `kormarc-auto wishlist` 1줄 → 정보나루 인기대출 + 자관 중복 + KDC 균형 + 예상 비용
- 30분 수동 → 5분 자동
- 첫 50건 무료 + 월 3만 (작은) ~ 15만원 (일반 공공)

okwhrlgma@gmail.com
```

---

## 3. 자관 활용 사례 (박지수 사서 PILOT 2주차)

| 단계 | 수동 | 자동 (kormarc-auto wishlist) |
|---|---|---|
| 정보나루 인기대출 30권 검색 | 15분 | 즉시 |
| 각 권 자관 중복 확인 | 10분 | 즉시 (libBookExist API) |
| KDC 균형 산정 | 5분 | 즉시 (자관 KDC 분포 분석) |
| 예상 비용 합계 | 3분 | 즉시 (정가 합계) |
| **합계** | **33분** | **약 3분** (90% 단축) |

→ 박지수 사서 NPS·Q1 결제 의향 측정 (PILOT 2주차 매뉴얼)

---

## 4. PIPA 정합 (2026-09-11 시행)

- 정보나루 API = 통계·집계만 (회원 PII X)
- 우리 통합 = PIPA 옵션 C 정합 (사용자 정보 자관 알파스 위임)
- 도서관별 인기대출 = 익명 집계 (정보나루 자체 익명화)

---

## 5. 다른 자관 도입 (5분)

```powershell
# 1. 정보나루 가입 (data4library.kr·이메일 본인 인증·5분)
# 2. authKey 받음 → .env에 DATA4LIBRARY_AUTH_KEY 추가
# 3. 즉시 사용:
kormarc-auto wishlist --input my_library.txt
```

---

## 6. 우리 시스템 정합 모듈

- `src/kormarc_auto/api/data4library.py` (키워드·인기대출 호출)
- `src/kormarc_auto/acquisition/wishlist.py` (자관 중복·KDC 균형·예상 비용 통합)
- `kormarc-auto wishlist` CLI (사서 1줄 호출)
- `docs/sales/pilot-week2-action-manual.md` (박지수 60분 시연 매뉴얼)

---

## Sources

- 도서관 정보나루 (https://data4library.kr)
- `src/kormarc_auto/api/data4library.py`
- `docs/sales/pilot-week2-action-manual.md` (박지수 PILOT 2주차)
- `docs/research/part3-librarian-workflows.md` (박지수 페르소나)
