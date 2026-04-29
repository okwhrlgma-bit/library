# 누적 84 ADR 우선순위 매트릭스 + PO 즉시 결정 영역

> **PO 명령** (2026-04-28): "야간 자율 = 명령 0 무한 진행 정책"
> **누적 ADR**: 0001~0026 (이전 26건) + **0027~0084 (이번 야간 신규 58건)** = **84 ADR**
> **분석일**: 2026-04-28
> **결론**: PO 즉시 결정 7건 (★) → 자율 commit 활성 차단점 해제 후 일괄 commit 가능.

---

## 0. 5질문 셀프 오딧 + 단계별 가중치 (PO 사업 마스터 정합)

| 단계 | 가중치 (Q1·Q2·Q3·Q4·Q5) |
|---|---|
| MVP (현재) | 30·20·10·15·25 |
| Beta | **40·25·15·10·10** ★ (현재 가까운 단계) |
| Payment Launch | 25·30·20·15·10 |
| Stable | 20·25·25·20·10 |

**Beta 단계 임계값**: 합계 ≥ 70 → ACCEPT, 50~69 → 검토, < 50 → 폐기.

---

## 1. 즉시 ACCEPT (Q1 결제 트리거 ★ 80+) — 18 ADR

| ADR | 제목 | Q1 | 합계 | PO 결정 |
|---|---|---:|---:|---|
| **★ 0021 정정** | 「상호대차 띠지 자동 생성기」 (책단비 + 자관 양식) | **100** | **92** | 🔴 PO 승인 후 commit |
| **★ 0022** | 양식 우선순위 resolver (`forms/resolver.py` 4단 fallback) | 95 | 89 | 🔴 |
| **★ 0027** | KOLAS F12 엑셀 자동 import (`inventory/kolas_f12_importer.py`) | 95 | 90 | 🔴 |
| **★ 0049** | 주제명표목 자동 (`kormarc/subject_headings.py` + NLK LOD) | 90 | 85 | 🔴 |
| **★ 0058** | xlsx 도서원부 자동 import (자관 9 컬럼) | 95 | 88 | 🔴 |
| **★ 0061** | 자관 9 수서 워크플로우 통합 모듈 | 90 | 85 | 🔴 |
| **★ 0065** | Formtec 라벨 자동 생성 (자관 2,387 파일 정합) | 85 | 82 | 🔴 |
| **★ 0070** | 자관 .mrc 174 파일 PILOT 검증 자동화 | 90 | 88 | 🔴 |
| 0033 | 책두레 F12 자동 (KOLAS III 메뉴 매핑) | 85 | 80 | 🔴 |
| 0029 | 별치기호 일괄 부여 모듈 | 80 | 75 | 🔴 |
| 0040 | 한셀 (.cell) import 어댑터 | 80 | 75 | 🔴 |
| 0048 | 로마자 표기 자동 (KORMARC 880) | 80 | 75 | 🔴 |
| 0053 | 5 자료유형 모듈 (Phase 1.5 — multimedia·audiobook·ejournal·ebook·thesis) | 85 | 82 | 🔴 |
| 0066 | 비치처리 누락도서 자동 회수 (자관 xlsx 정합) | 85 | 80 | 🔴 |
| 0077 | 학위논문 모듈 정합 검증 (자관 18건 PILOT) | 85 | 82 | 🔴 |
| 0078 | 학술논문 모듈 정합 검증 (자관 17건) | 80 | 78 | 🔴 |
| 0072 | NL Korea OPEN API 5종 추가 (`api/aggregator.py`) | 85 | 82 | 🔴 |
| 0083 | 도서관 이용 종료 매뉴얼 자동 생성 | 80 | 75 | 🔴 |

---

## 2. 검토 후 ACCEPT (Q1 50~79) — 25 ADR

| ADR | 제목 | Q1 | 합계 |
|---|---|---:|---:|
| 0016 | Folder Watcher (`watchers/download_watcher.py`) | 75 | 86 ★ |
| 0017 | System Tray App (`tray/app.py` + pystray) | 75 | 84 |
| 0019 | OS File Association (.marc·.kormarc 핸들러) | 70 | 84 |
| 0028 | KOLIS-NET 반입 자동 (`api/kolisnet_compare.py` 강화) | 75 | 75 |
| 0030 | 연속간행물 권호 예측 단계증가 매트릭스 | 70 | 70 |
| 0034 | 책이음 통계 자동 (KOLAS III 메뉴 매핑) | 70 | 72 |
| 0037 | 자원봉사 친화 UI (단순 입력·즉시 검증) | 75 | 78 |
| 0039 | 원부대장관리 (`librarian_helpers/registry_book.py`) | 75 | 75 |
| 0050 | 전거레코드 활용 (`kormarc/authority.py` + NLK 전거 178만) | 75 | 75 |
| 0051 | `legal/deposit_form.py` 5 자료유형 분기 검증 | 70 | 72 |
| 0054 | 특수문자 처리 (`kormarc/special_chars.py`) — LaTeX·대체문자 | 70 | 72 |
| 0055 | 재포맷팅 품질 3단 (KORMARC 533 ▾n) | 65 | 68 |
| 0056 | 깨진 글자 [실은X] 표기 자동 | 65 | 68 |
| 0057 | 자관 등록번호 prefix 정책 ③ (config.yaml) | 75 | 75 |
| 0059 | MARC8 ↔ UTF-8 자동 변환 | 75 | 78 |
| 0062 | 북큐레이션 자동화 (`programs/book_curation.py`) | 75 | 78 |
| 0063 | 기관대출 자동화 (`interlibrary/group_loan.py`) | 70 | 72 |
| 0067 | System Tray 정시 toast routine (09·18·22시) — 자관 3년 정합 | 70 | 75 |
| 0069 | KDC·별치 prefix 자동 추론 | 70 | 72 |
| 0071 | 차수 routine 자동 (`acquisition/batch_routine.py`) — 정기·희망 | 75 | 75 |
| 0073 | 공공데이터포털 ICP DB | 70 | 72 |
| 0079 | 자관 출판물 KORMARC 자동 (작품집 8 시리즈) | 65 | 65 |
| 0080 | 연속간행물 표지 사진 → KORMARC OCR | 70 | 72 |
| 0081 | 자관 6년 NPS 영업 신뢰성 인용 | 75 | 80 |
| 0082 | 자관 직원 교육자료 → 우리 SaaS 사서 교육 | 70 | 72 |

---

## 3. 컴플라이언스 게이트 (Q5 별도 — 생존 조건) — 8 ADR

PIPA 패턴 5대 보강·회피:

| ADR | 제목 | PIPA 패턴 |
|---|---|---|
| **0015 정정** | pii-guard hook (`reader_*·borrower_*·patron_*` grep) | 1 (Reader entity 부재) |
| **0023** | 자관 양식 라이선스 게이트 | IP + 정보주체 |
| **0032** | 책이음 회원 PII 영역 진입 X 명문화 | 1 |
| **0036** | 학교도서관 미성년 PII 영역 진입 X | 1 (강화) |
| **0042** | 검수취소 워크플로우 | (자관 운영 정합) |
| **0064** | 자관 사서 PII 영역 진입 X (사서 개인 폴더 매처 deny) | 1 |
| **0068** | 휴관일 자동 처리 (코로나 历사 정합) | (운영 정합) |
| **0084** | 자관 PII 영역 진입 X 명문화 (NPKI·재발급·아이핀·전산 비상연락망 7종) | 1 (광범위) |

---

## 4. 인프라·관측 (Q3 자산) — 11 ADR

| ADR | 제목 |
|---|---|
| 0012 | Always Night Mode (이전, ADR 0010 §3 supersede) |
| 0018 | Browser Extension (별도 repo) |
| 0020 | 알파스/KOLAS launcher 패널 (`ui/launcher.py`) |
| 0024 | 책바다 결제 5,200원 통계 자동 — 자관 4년 历사 정합 (낮은 ROI: 자관 책바다 25~46건/년) |
| 0031 | 우리 SaaS 자체 브라우저 임베드 (KOLAS III 패턴) |
| 0035 | KERIS DLS 자료 등록 양식 자동 (Phase 2) |
| 0038 | DLS export 양식 (Phase 2~3 영업) |
| 0044 | KORMARC 2023 개정 표준 100% 정합 명문화 |
| 0045 | 3 적용 수준 (M/A/O) binary_assertions 분기 |
| 0046 | 9 자료유형 100% 확장 (Phase 1.5) |
| 0052 | KORMARC ↔ MODS XML 양방향 변환 |

---

## 5. PO 직접 영역 (자율 X — Q4 lock-in/Q5 거버넌스) — 8 ADR

| ADR | PO 직접 액션 |
|---|---|
| 0013 | 사업 5질문 도입 결정 (헌법 §0+§12 영향) |
| 0014 | 가격 4단 정정 (헌법 §12 vs 권장 4단 충돌 — Free·₩19K·₩49K·견적 vs 3·5·15·30만원) |
| 0026 | 통계 파일명 vs 내용 자동 검증 (자관 routine 오류 회피) |
| 0047 | NLK 공식 web 자동 매뉴얼 정합 audit (Phase 1.5) |
| 0060 | 자관 .mrc 174 파일 PILOT 자동 실행 (PO 동의서 후) |
| 0074 | 입찰정보 자동 알림 (clip.go.kr·mcst.go.kr) — PO 모니터링 권한 필요 |
| 0075 | 자관 PILOT 직접 (베타 사서 1관 - 내숲) |
| **0076** | **🔴 KLA 회원 가입 + 전국도서관대회 5월 발표 신청 (5.31 마감)** |

---

## 6. PO 즉시 결정 7 영역 ★ — 자율 commit 활성 차단점

| # | PO 결정 | 트리거 | Commit 영향 |
|---|---|---|---|
| 1 | **🔴 ADR 0021 정정 — 「상호대차 띠지 자동 생성기」** 채택 | python-hwpx 의존성 + data/forms/ 신규 | Commit 2 (야간 단일화) 후 즉시 활성 |
| 2 | **🔴 ADR 0022 — 양식 우선순위 resolver** 채택 | `forms/resolver.py` 4단 fallback | Commit 3~4 |
| 3 | **🔴 ADR 0014 — 가격 4단 정정** | 헌법 §12 vs 권장 4단 충돌 해결 | 헌법 갱신 + 영업 메시지 일괄 |
| 4 | **🔴 ADR 0013 — 사업 5질문 도입** | rules/business-impact-axes.md 신규 | hooks·CLAUDE.md 갱신 |
| 5 | **🔴 ADR 0015·0023·0032·0036·0064·0084 — pii-guard hook 6 영역 통합** | `.claude/hooks/pii-guard.py` 신규 | 컴플라이언스 회귀 가드 |
| 6 | **🔴 ADR 0070 — 자관 .mrc 174 PILOT** | 자관 라이선스 동의서 (PO ↔ 자관) | 영업 신뢰성 ★ |
| 7 | **🔴 ADR 0076 — KLA 5월 발표 신청** | PO 직접 (5.31 마감) | 영업 채널 |

---

## 7. 자율 활성 가능 (Q5 게이트 통과) — 즉시 commit 후보 5건

PIPA·라이선스·계약 영역 X — 자율 commit 가능:

| ADR | 영역 | commit 단위 |
|---|---|---|
| 0044 | KORMARC 2023.12 표준 정합 명문화 | docs only (CLAUDE.md §2 정정) |
| 0045 | M/A/O 3 적용 수준 binary_assertions 분기 | binary_assertions.py 갱신 |
| 0048 | 로마자 표기 자동 (KORMARC 880) — `python-hanja` 의존성 | 의존성 추가 + 모듈 |
| 0067 | System Tray 정시 toast (09·18·22시) — `pystray` 의존성 | 모듈 + ADR |
| 0044+0045 통합 | 표준 정합 + binary_assertions 분기 일괄 | 단일 commit |

→ **자율 commit 5건 가능** 단 `pystray`·`python-hanja` 의존성 추가는 효율 가드 §의존성 빈도 위반 회피 위해 PO 결정 영역.

---

## 8. ADR 누적 통계 (이번 야간 자율)

| 묶음 | ADR | 누적 |
|---|---|---:|
| 이전 (2026-04-25 ~ 2026-04-27) | 0001~0026 | 26 |
| KOLAS 정합 | 0027~0031 | 5 |
| 책이음·KERIS DLS | 0032~0038 | 7 |
| 알파스 정합 | 0039~0043 | 5 |
| KORMARC 2023 표준 + 9 자료유형 | 0044~0047 | 4 |
| NLK 사서 지침 5종 | 0048~0051 | 4 |
| Phase 1.5 (MODS·5 자료유형) | 0052~0056 | 5 |
| 자관 수서·.mrc·prefix | 0057~0061 | 5 |
| 자관 자료실 (북큐레이션·기관대출) | 0062~0064 | 3 |
| 자관 历사·도구 (Formtec·누락도서·toast·휴관) | 0065~0068 | 4 |
| .mrc 검증·차수 routine | 0069~0071 | 3 |
| central-institutions 갱신 | 0072~0076 | 5 |
| 자관 윤동주·작품집·연속간행물 | 0077~0080 | 4 |
| D 드라이브 100% (NPS·교육자료·PII X) | 0081~0084 | 4 |
| **합계** | | **84** |

---

## 9. 흡수 audit 최종 (이번 야간 자율 100% 완료)

| 카테고리 | 흡수율 |
|---|---:|
| 자료 폴더 (PO 제공 55 + PO 자작 11 = 66) | **100% ✅** |
| D 드라이브 자관 (87 항목) | **100% ✅** |
| Compass·Autonomous Modes 가이드 | 100% ✅ |
| PO 종합 검증 보고서 6종 (800 sources) | 100% ✅ |
| PO 사업 마스터 문서 (2026-04-28) | 100% ✅ |
| 자관 사서 8명 페르소나 식별 (PIPA 정합) | 100% ✅ |
| KORMARC KS X 6006-0:2023.12 표준 정합 | 100% ✅ |
| **종합 흡수율** | **100% ✅** |

---

## 10. PO 다음 액션 우선순위 (★ 5월 마감 임박)

| 순위 | 액션 | 마감 |
|---:|---|---|
| 🔴 1 | 전국도서관대회 발표 신청 (KLA) | **2026.5.31** |
| 🔴 2 | 사서교육원 강의 제안서 | 2026.5월 |
| 🔴 3 | ADR 0021·0022·0014·0013·0015 PO 결정 | (자율 commit 활성 차단점) |
| 🟢 4 | NL Korea API 5종 추가 인증키 신청 | 7일 |
| 🟢 5 | 공공데이터포털 ICP DB 다운 | 30분 |
| 🟢 6 | 자관 PILOT 동의서 작성 | 자관 협의 |
| 🟡 7 | KLA 회원 가입 | 1일 |

---

## 11. Sources

- 이번 야간 자율 누적 docs 25개 (`alphas-*`·`chaek*`·`kolas-iii*`·`keris-*`·`d-drive-*`·`yangsik-matrix`·`online-materials-*`·`kormarc-2023-standard-*`·`nlk-cataloging-guidelines-*`·`central-institutions-update-*`·`d-drive-yoondongju-thesis-*`·`d-drive-final-completion-*`)
- PO 자작: `자료/00_마스터_인덱스.md` + `자료/REAL_LIBRARY_INDEX.md` + `자료/business_framework_2026_04_28.md`
- 자료 폴더: 55 파일 (100%) + PO 자작 11 = 66 (100%)
- D 드라이브: 87 항목 100% 분류 완료
- KORMARC KS X 6006-0:2023.12 표준 (NLK 공식)
- PO 사업 마스터 §0~§14 (5질문·단계 가중치·PIPA 5대·가격 4단·KPI 25개)
