# 향후 코딩 진행 로드맵 — 업그레이드·전반적 보강 13 영역

> **출처**: PO 4-30 명령 "향후 코딩 진행 시 추가 고려·업그레이드 사항 + 전반적 부족 영역"
> **목적**: cloud routine·다음 세션 자율 진행 시 본 로드맵 참조 → BACKLOG 1순위 다음 단계.
> **단일 진실**: ★ 자관 99.82% 정합 + 5중 자동화 + Anthropic 200줄 권장 정합.

---

## 1. 즉시 (Phase 0 보강 — 5월~6월)

### 1-1. KORMARC 9 자료유형 모듈 완성 (Phase 1.5+ 보류 해제 검토)

현재 단행본만 정합. 9 자료유형 중 부족:
- [ ] `kormarc/ebook.py` — 008 23 + 856 URL + 538 매체 자동
- [ ] `kormarc/ejournal.py` — 022 ISSN + 310 발행빈도 + 362 권차
- [ ] `kormarc/audiobook.py` — 008 06=j + 007 + 538 음향
- [ ] `kormarc/multimedia.py` — g 시청각자료 + 538 상영
- [ ] `kormarc/thesis.py` 보강 — 502 학위·학과·지도교수

**트리거**: 자관 PILOT 4주 결과에서 단행본 외 자료유형 페인 발견 시 활성. PO MVP CHAPTER 9 명령 ("MVP 단행본만") 정합 유지.

### 1-2. 어셔션 37 → 50 확장

- [ ] /webhook/portone route 어셔션 (이미 module 확인·route 별도)
- [ ] /signup persona 자동 분류 어셔션
- [ ] CLAUDE.md 200줄 hard-limit 어셔션 (현재 250줄 soft)
- [ ] 6-Part 매뉴얼 모두 존재 어셔션
- [ ] ADR 16+건 어셔션
- [ ] docs/sales 16+건 어셔션
- [ ] 5중 자동화 정합 어셔션 (3 routine ID + 2 workflow YAML)

### 1-3. Streamlit prefix-discover 탭 통합 (BACKLOG 미완 1건)

STATUS_REALITY_CHECK 권고 (5페이지 분리)와 충돌 → 신중. 옵션:
- (A) 별도 standalone 유지 (현재·prefix_discover_app.py)
- (B) main streamlit_app에 15탭 추가 (큰 변경)
- (C) Streamlit multi-page (`pages/` 디렉토리·자동 메뉴)

→ 사서 1명 만남 후 결정 (PO 결정 차단점).

---

## 2. 단기 (Phase 1 — 5월~7월)

### 2-1. ADR 0021 책단비 hwp 자동 (PO 결정 후)

- [ ] python-hwpx 의존성 추가 (PO ADR 결정)
- [ ] `chaekdanbi/auto_label_generator.py` (KOLAS F12 엑셀 read·4 양식 hwp)
- [ ] 자관 책단비 5년 1,328건 자동 검증
- [ ] 사서 A 사서 PILOT 2주차 시연 정합

### 2-2. KOLAS F12 엑셀 일괄 importer (Phase 2)

- [ ] `inventory/kolas_f12_importer.py` (xlsx 9 컬럼·EQ/CQ prefix·rapidfuzz)
- [ ] Folder Watcher (KOLAS Downloads 자동 감지·watchdog)
- [ ] 정기차수 자동 import + 비치희망 통합

### 2-3. 회원증 mail merge (Phase 3 옵션 C)

- [ ] PII X·Formtec 정합·자관 알파스 위임
- [ ] 양식 자동 생성 + 발송은 자관 알파스 책임
- [ ] PIPA 시행 (2026-09-11) 정합

---

## 3. 중기 (Phase 2~3 — 6개월~1년)

### 3-1. 사용자 분석·세션 녹화 (PostHog 통합)

- [ ] PostHog 무료 1M 이벤트/월
- [ ] 사서가 어디서 막히는지 화면 녹화
- [ ] funnel A/B 테스트 (가격·UI·결제 흐름)

### 3-2. 에러 추적 (Sentry 통합)

- [ ] Sentry SDK 5K 에러/월 무료
- [ ] 5xx 즉시 알림 (PO 카카오톡)
- [ ] PII 마스킹 자동

### 3-3. 이메일 자동 (Resend 통합)

- [ ] 영업 메일 자동 발송 (4 페르소나별)
- [ ] PILOT 결과·NPS 자동 발송
- [ ] 영수증·청구서 자동 (포트원 webhook 후)

### 3-4. 일정 자동 예약 (Cal.com)

- [ ] PILOT 시연 30분 자동 예약
- [ ] 카카오 채널·README에 링크
- [ ] PO 캘린더 (구글·네이버) 통합

### 3-5. DB 마이그레이션 (SQLite → Supabase Postgres)

- [ ] 사서 100관+ 동시 접속 한계 도달 시
- [ ] Postgres + Auth + Storage + RLS
- [ ] DSAR (개인정보보호법 §35-3) Postgres SQL 직접 조회

### 3-6. 호스팅 마이그레이션 (PC + Cloudflare → Fly.io ICN)

- [ ] Phase 2 베타 50관 후 검토
- [ ] Fly.io ICN 리전 ($5~15/월·한국 latency 30ms)
- [ ] HTTPS 자동·도메인 (kormarc-auto.kr)

---

## 4. 장기 (Phase 3~5 — 1년~5년)

### 4-1. 미국 동아시아 컬렉션 진출 (ADR 0009 §33)

- [ ] 트리거 3/3 충족 후 active (현재 inactive·ACTIVATED=False)
- [ ] Berkeley·Harvard·Stanford·Yale·Princeton·UCLA·U Chicago·Columbia·Cornell·U Washington·U Hawaii 11개
- [ ] KORMARC ↔ MARC21 자동 변환 (이미 모듈 정합)
- [ ] Stripe PG (한국 외 결제·ADR 0007 trigger 분기)

### 4-2. 일본 NACSIS-CAT·NDL 진출

- [ ] 일본 학교 12만관 + 공공 3,200관
- [ ] KORMARC ↔ NDL MARC 변환 모듈
- [ ] 일본어 토크나이저 (Mecab·Sudachi)

### 4-3. BIBFRAME 2.0 LOD 정식 통합

- [ ] LC SHARE-VDE 호환
- [ ] Sinopia·LD4P 협력
- [ ] RDF/Turtle 출력

### 4-4. 사서 AI 어시스턴트 (Anthropic Claude API)

- [ ] 사서 자연어 질문 → KORMARC 빌드 (예: "이 책 마크해줘")
- [ ] KDC 후보 추천 + 사서 결정 보조
- [ ] 자관 정책 학습 (자관별 049 prefix·청구기호·KDC 분포)

---

## 5. 보안·컴플라이언스 (지속·법적 의무)

### 5-1. PIPA 시행 (2026-09-11) 5대 패턴

- [x] Reader/Borrower entity ERD 부재 ✅ (옵션 C·자관 알파스 위임)
- [ ] 암호화 (bcrypt·AES-256·TLS 1.2+) — bcrypt 권장 → Argon2id 검토
- [x] DSAR (제35·36·37조) ✅ (`/account/export·delete`)
- [ ] 72h 신고 자동화 (1,000명+ 시·민감정보 시)
- [ ] audit_log + 해시 체인 (5만명+ 시·민감정보)

### 5-2. CVE 점검 (Next.js 11.1.4–15.2.2 CVE-2025-29927 같은 이슈)

- [ ] 우리 = FastAPI라 무관·streamlit-authenticator 정기 패치
- [ ] Snyk·Dependabot 자동 (이미 GitHub Actions 정합)
- [ ] gitleaks pre-commit (시크릿 검출)

### 5-3. 백업·복구 테스트 (분기 1회)

- [ ] 30일 일일 + 12주 주간 + 7년 월간 + 7일 PITR
- [ ] 별도 인스턴스에 실 복구 + 회원수·대출 검증
- [ ] "백업했다 ≠ 복구 검증"

---

## 6. 코드 품질·리팩토링 (지속)

### 6-1. streamlit_app.py 리팩토링 (1,424 lines)

STATUS_REALITY_CHECK 권고 = 5페이지 분리. **사서 1명 만남 후** 본격 진행.

- [ ] 22 button → 5 button 압축
- [ ] multi-page (Streamlit pages/ 디렉토리)
- [ ] 사서 친화 도입 시간 5분 → 2분

### 6-2. Type hints + mypy strict

- [ ] 현재 부분 적용·full strict 마이그레이션
- [ ] Zod 패턴 (Python = pydantic) 도입 검토

### 6-3. 테스트 296 → 500 확장

- [ ] /signup·/usage·/billing 추가 endpoint 테스트
- [ ] 통합 테스트 (Streamlit + FastAPI + DB)
- [ ] E2E (Playwright·사서 플로우)

### 6-4. AI 코드 함정 회피 (Part 6 §7 정합)

- [ ] AI 코드 35~40% 보안 결함 → 자동 검증 (Snyk·CodeQL)
- [ ] Slopsquatting (19.7% 환각 패키지) → npm/pip lock file 검증
- [ ] Over-engineering 회피 (YAGNI·KISS·Rule of Three)

---

## 7. UX·사서 친화 (지속)

### 7-1. 한국어 UI 정합 (Pretendard·16px·네이비/살구)

이미 정합. 추가:
- [ ] 모바일 반응형 (폰 카메라 → 30초 .mrc)
- [ ] 사서 친화 에러 메시지 (영문 stack trace X·해결법 카드)
- [ ] 5분 시연 가능 화면 (5페이지 이내·STATUS_REALITY_CHECK)

### 7-2. 카카오 로그인 통합 (Auth.js v5 패턴 또는 자체)

- [ ] 사서 카카오 1줄 가입 (이메일 입력 X·5초)
- [ ] 카카오톡 알림 자동 (카카오 채널 푸시)

### 7-3. 모바일 앱 (Phase 4+)

- [ ] React Native + ML Kit (바코드 스캔)
- [ ] iOS·Android (사서 폰 1관 PILOT)
- [ ] 오프라인 모드 (캐시 7일 TTL)

---

## 8. 영업·매출 자동화 (지속)

### 8-1. 결제 PG 정식 통합 (포트원·ADR 0007 활성)

- [ ] 사업자 등록 + 통신판매 신고 + 포트원 가맹
- [ ] PortOneAdapter 실 SDK 통합 (charge·subscribe·tax invoice)
- [ ] 자동 차감 + 영수증 PDF + 세금계산서

### 8-2. 영업 funnel 자동 측정 (이미 정합)

- [ ] /admin/stats by_persona (이미 ✅)
- [ ] 매월 Notion·구글 시트 자동 sync
- [ ] 사서 NPS 추적 (PILOT 후속)

### 8-3. 영업 채널 자동화

- [ ] 카카오 채널 콘텐츠 자동 발행 (cloud routine 1h sync)
- [ ] 블로그 (네이버·티스토리) 자동 게시
- [ ] 도서관저널 기고문 자동 PDF·발송

---

## 9. 해외 진출 (Phase 4~5)

### 9-1. 미국 동아시아 11관 PILOT

- [ ] §33 ACTIVATED=True 트리거 충족 (자관 + 미국 1관 LOI)
- [ ] 영문 영업 자료 (KORMARC vs MARC21·BIBFRAME)
- [ ] Stripe PG 통합

### 9-2. 일본 NACSIS·NDL

- [ ] 일본어 영업 자료
- [ ] NACSIS-CAT 1,200관 + NDL Search 정합

---

## 10. 매뉴얼·문서 (지속)

### 10-1. 6-Part → 10-Part+ 매뉴얼 확장 (4-30 진행 중)

- ✅ Part 1 바이브 코딩
- ✅ Part 2 KORMARC 구현
- ✅ Part 3 사서 워크플로우
- ✅ Part 4 UI/SEO/마케팅/배포
- ✅ Part 5 외부 도구 12종
- ✅ Part 6 Claude Code 운영 종합
- ✅ Part 7 타관 KORMARC 정합 사례 (Agent 1 결과·22,152자)
- ✅ Part 8 한국 도구·SaaS 경쟁사 (Agent 3 결과·9,500자)
- ✅ Part 9 사서 커뮤니티·블로그·브이로그 (Agent 2 결과·14,500자)
- 🔲 Part 10 사서 페인포인트 실측 (Agent 4 진행 중)
- 🔲 Part 11 자관 보편성 검증 (Agent 5 진행 중)
- 🔲 Part 12 사서 페인 학술 심층 (Agent 6 진행 중)
- 🔲 Part 13 한국 도서관 시장 TAM/SAM/SOM (Agent 7 진행 중)
- 🔲 Part 14 국제 도서관 자동화 (Agent 8 진행 중)

→ 결과 후 INDEX.md 갱신 + 영업 자료 보강.

### 10-2. 영업 자료 16 → 25+건 확장

- [ ] 자치구별 도서관 영업 메일 (서울 25개·광역시 6개)
- [ ] KOLAS 종료 마이그레이션 가이드 (사서 직접 사용)
- [ ] BIBFRAME LOD 데모 영상 (대학·학회용)
- [ ] PIPA 시행 대응 가이드 (옵션 C 정합)

---

## 11. 운영·모니터링 (지속)

### 11-1. PO 매주 5분 점검 (이미 정합)

- ✅ Cloud routine 3개 모니터링 가이드
- ✅ /admin/stats 1번 호출 → funnel·매출·영업
- ✅ GitHub commit 늘어나는지 모바일 앱

### 11-2. 자율 진행 게이트 강화

- ✅ 평가축 §0/§12 양수만 commit
- ✅ pytest·ruff·assertions 통과 후 commit
- ✅ AUTONOMOUS_BACKLOG 위→아래 스캔
- ✅ 5중 자동화 (Cloud 3 + Actions 2)

---

## 12. ADR 16 → 30+ 결정 기록 (지속)

향후 추가 ADR 후보:
- [ ] 0017 KORMARC 자료유형 모듈 우선순위 (단행본 → 전자책)
- [ ] 0018 PostgreSQL 마이그레이션 시점 (50관·100관·200관)
- [ ] 0019 Fly.io 호스팅 마이그레이션 시점
- [ ] 0020 카카오 로그인 통합 (Auth.js v5 vs 자체)
- [ ] 0021 책단비 python-hwpx (PO 결정 대기)
- [ ] 0022 양식 우선순위 resolver
- [ ] 0023 사서 AI 어시스턴트 (Anthropic Claude API 통합)
- [ ] 0024 Stripe PG (§33 미국 활성 시·ADR 0007 분기)

---

## 13. 사용자 명령 정합 (PO 4-30)

- "부족한 부분 자율 조사" → Agent 8개 launch (4 + 4 추가) ✅
- "타관 사례 보편성 확인" → Part 11 Agent 5 ✅ (진행 중)
- "더 깊고 넓게 조사" → Part 12·13·14 Agent 6·7·8 ✅ (진행 중)
- "향후 코딩 업그레이드 사항" → 본 docs ✅
- "전반적 부족 영역" → 13 영역 모두 정리 ✅

→ Agent 8개 결과 후 본 docs § 갱신 (Part 7~14 매뉴얼 인덱스 + 영업 자료 보강).

---

## Sources

- 이번 세션 102+ commit (db88f67~)
- `AUTONOMOUS_BACKLOG.md` (cloud agent 큐)
- `docs/research/part1~6` + Part 7·8·9 (Agent 결과)
- `STATUS_REALITY_CHECK.md` (4-27 권고·streamlit 5페이지)
- `docs/mvp-redefinition-2026-04-29.md` (PO MVP CHAPTER 9·10)
- ADR 0007·0009·0011·0013·0014·0015·0016 (결정 기록)
