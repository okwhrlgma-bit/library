# CLAUDE.md — kormarc-auto (slim·60줄 ceiling)

> Claude Code 매 세션 자동 로드. 절대 우선. 상세 → `agent_docs/`.

## 0. 정체성
한국 도서관 **KORMARC 자동 생성 SaaS**. ISBN/사진 → KOLAS·DLS·알파스 호환 .mrc.
**목표**: 사서 마크 시간 권당 8분 → 1.5분 (descriptive 블록).
**PO**: 사서 출신 1인 비개발자.

## 1. 헌법 (3원칙)
1. **의심하라** — 미션 정합 검증
2. **검증하라** — 추측 X·코드/문서 직접 확인
3. **정제하라** — 자기 비판 후 다듬기

## 2. 평가축 (commit 거부 조건)
모든 변경 = 다음 둘 중 1+ 양수:
- §0 사서 마크 시간 단축
- §12 결제 의향 ↑

음수 = commit X.

## 3. HARD RULES
- ❌ API 키 하드코딩 (`.env` 사용)
- ❌ 알라딘 출처 표시 누락 ("도서 DB 제공 : 알라딘 인터넷서점")
- ❌ "100% 자동" 약속 (사서 검수 단계 보존)
- ❌ 외부 API timeout 미지정 (10초)
- ❌ 한국어 변수명 (식별자 = 영문)
- ✅ try/except + timeout=10 외부 호출
- ✅ confidence 점수 + source_map 추적
- ✅ pymarc UTF-8 명시
- ✅ 한국어 docstring
- ✅ §9 동일 입력 = 동일 출력 (모델 pinning + temperature=0·top_p=1·ADR 0028)
- ✅ §10 AI 생성 사실은 KORMARC 588 + audit log + UI ghost text 4곳 명시 (ADR 0029·인공지능 기본법 §31)
- ✅ §11 신뢰도 = 카테고리 (확실/검토 필요/불확실)·raw % UI/API/CLI 모두 금지 (ADR 0030·llm/confidence.py)
- ✅ §12 모든 UI = KWCAG 2.2 Level AA·KRDS 색상 토큰·Pretendard CDN (ADR 0032·a11y/kwcag22.py·디지털포용법 §21)
- ✅ §13 페르소나 시뮬 ≠ 실 사서 인터뷰·PMF 결정 = SALES-1 후·정직 헤더 의무 (ADR 0046·invariant 11)
- ✅ §14 사서 데이터 = 사서 컴퓨터·SaaS 서버 저장 X (invariant 12 후보·ADR 0048)·도서관 RFP 100% 통과
- ✅ §15 사서 자가 설치 친화 = `.exe` 더블클릭 + URL 클릭만·Python·명령어 X (Cycle 65·`docs/landing/install.md`)

## 4. 자율성 4단계
- L1 자율: 오타·린트·docstring
- L2 보고: 로드맵·버그
- L3 승인: API·DB 스키마·메이저 버전
- L4 PO만: 운영 키·결제·운영 배포

## 5. 종료 게이트 (이중)
- pytest 통과 + ruff 0 errors
- binary_assertions 39/39 (2026-05-03 메모리 가드 16종 패치)
- 평가축 §0/§12 양수 commit message 명시
- `Co-Authored-By: Claude Opus 4.7 (1M context)` 포함

## 6. 5대 멈춤 패턴 회피
- 모호 결정 → 보수적 + DECISIONS.md
- 테스트 3회 실패 → SKIPPED.md + 다음
- 자가 디버그 30 iter 한계
- 컨텍스트 한계 → 본 파일 핵심
- 의존성 실패 → 새 의존성 X·오프라인

## 7. 한국어 정책
- PO 프롬프트·응답 = 한국어
- 영어 = 식별자·git commit·API 경로
- KORMARC·KDC·관제 용어 = 한국어
- 단일 식별자 혼용 금지

## 8. 영구 정책 (PO 명령)
- 명령 없을 시 = 자율 모드 default
- 매 사이클 = 사용자_TODO 자동 정리

## 8C. NO offline activities (PO 영구 2026-05-07·ADR 0052)
- PO 명령: "인터뷰 같은 코딩 외 활동 진행 안 할 예정"
- 차단: 사서 인터뷰·카페 글·cold email·외부 미팅·전화·등록 (홈택스·통신판매·정부24)·외부 발사 (Streamlit Cloud·도메인·gh release)·키 발급 외부 청구
- 허용: 코드·테스트·ADR·docs·연구·페르소나 시뮬 (invariant 11 정합)·외부 공개 자료 분석·PO 자관 PILOT (founder fit 자기 검증)
- 매 사이클 끝 "발사 권유"·"인터뷰 권고" 메시지 = 절대 X
- PO가 "발사 시작"·"인터뷰 시작" 명시 시만 발동
- invariant 11 (PMF = 인터뷰 후) = 보류 상태로 유지·PMF 결정 자체를 보류 (자기 검증·시뮬·코드 강화로 갈음)

## 8D. 30 apps portfolio (PO 영구 2026-05-07·ADR 0053)
- PO 명령: 단일 대박 앱 X·**30개 단일 기능 앱 포트폴리오** (인디 검증·MRR $22K·12개월)
- Claude 자율: 1주 1앱 사이클 (Mon spec → Tue~Wed 코드 → Thu UI → Fri ruff → Sat·Sun docs)
- 6 카테고리: A 도서관 (#1~#8) · B 자영업 (#9~#13) · C 모바일 게임 (#14~#16) · D 생산성 (#17~#23) · E 교육 (#24~#26) · F 창작 (#27~#30)
- #1 kormarc-auto = 완성 (v0.7.1·1287 tests) = 유지보수 + #2 부터 신규 자율 사이클
- 발사·홍보·피드백 = ADR 0052 정합 = 보류 (PO 미래 명령 시 활성)
- 평가축: 단일 기능·버그 0·1주 완성·MIT/Apache·한국어·자관 데이터 X (헌법 §14)
- 위치: kormarc-auto 외 = `30-apps/<n>_<한국어_기능>/` 또는 `후보_아이디어/<한국어_앱>/` (Cycle 123 PO 명령·폴더명 = 출시 앱 명·한국어)
- 영문 유지: `_shared/` (sys.path 호환)·`kormarc-auto/` (git history)

## 8L. _shared 정식 패키지 (Cycle 104·ADR 0066·Sandi Metz AHA)
- 5 사용처 도달 = packages/ 승격 시점·정식 Python 패키지화 완료
- 위치: `30-apps/_shared/` (Apache-2.0·v0.1.0·Python 3.11+)
- 4 모듈: payments·auth·email_helper·landing·법적 templates·flow·roadmap
- email → **email_helper rename** (Python 표준 충돌 회피·sys.path 등록 시)
- tests: 9 smoke passing·헌법 §3 (env only)·전자상거래법 §17 정합
- 사용 패턴: `sys.path.insert(0, "../_shared")` + `from landing import ...`
- ROI: 30 앱 누적 시 코드 단축 30~50%·캐시카우 가속

## 8K. 15 요건 페인 평가 매트릭스 (PO 영구 2026-05-08·ADR 0065)
- PO 3 요건: 페인·자동화·수익 (각 0~10·합 30)
- 자율 12 요건: 결제권자=결제자·1인 운영·정부 잠식 X·founder fit·반복·락인·법적 X·한국+글로벌·인디 검증·ADR 0052 정합·헌법 §14·MIT
- 자동 평가: `scripts/evaluate_pain_15.py --demo`·overall = po/30×50 + autonomy/12×50
- 결정: GO ≥75 + no_legal_risk·MAYBE ≥60·NO_GO 그 외
- 매 신규 앱 = ADR 0055 + 0058 + 0065 3중 게이트 의무
- 메모리: feedback_15_criteria_pain_eval.md ⭐⭐⭐⭐
- #31 검증 = overall 85·GO·fail_reasons []

## 8J. Blanket authorization (PO 영구 2026-05-08)
- PO 명령: "여러 허용 안물어봐도 됨·심각한 것 외 다 허용"
- 매 결정 = Claude 자율·PO 묻지 말고 즉시 진행
- 심각 = 차단 (헌법 §3·§14 위반·법적 위험·비가역 액션·ADR 0052 외부 발사·PO STOP)
- 이외 = 모두 자율 (코드·박제·페인 발굴·30 앱·SKILL.md·_shared·가격·라이선스·의존성·비용 가드)
- 매 cycle 끝 절대 X 멘트: "허용 부탁드립니다"·"PO 결정 시 진행"·"확인 후 적용"·"권한 필요"
- 위반 = 즉시 자율 결정으로 전환
- 메모리: feedback_blanket_authorization.md ⭐⭐⭐⭐⭐
- ADR 0064 박제

## 8I. 계획 선행 의무 (PO 영구 2026-05-08)
- PO 명령: "조사 및 앱 제작도 계획이 선행되어야함·스타트업처럼 순서 맞춰서 계획대로 진행"
- 매 신규 앱 = 다음 순서 의무:
  1. ADR 0055 페인 게이트 평가 카드 박제 (시장·캐시카우·Q5)
  2. 통과 시 = `30-apps/_shared/STARTUP_ROADMAP.md` Phase 정합 확인
  3. spec.md (단일 기능 1줄·평가축·의존성)
  4. 코드 (pyproject·LICENSE·src·tests ≥ 15)
  5. README (한국어·차별화 표·면책)
  6. _shared 활용 (payments·legal·landing·email)
  7. 박제 (INDEX·STATUS·learnings)
- 매 cycle = 현재 Phase 진척 + 다음 게이트 체크
- 게이트 미달 = Phase 유지·skip X
- 모든 외부 발사 = ADR 0058 4 조건 + Phase 3 진입 모두 통과 후만

## 8H. Conditional deployment cashcow (PO 영구 2026-05-08·ADR 0058)
- PO 명령: "수익 확실·캐시카우 가능 판단 시 코딩 및 배포 허용"
- 4 조건: 시장 ≥ 75·캐시카우 ≥ 80·벤치마크 1+·Q5 PASS
- 통과 = Streamlit Cloud + 도메인 + 결제 wrapper + ProductHunt·HN 발사 허용
- 미달 = ADR 0052 유지 (코드만)
- 벤치마크 의무: 솔로 인디 사례 인용 (Pieter·Tony·Marc·Daniel·삼쩜삼·Habit Pixel 등)
- 차단 잔존: 사서 인터뷰·자관 데이터 누설·사업자 등록 (PO 외부 작업)
- 통과 앱 (Cycle 89): #31 freelancer-tax-helper (벤치마크 삼쩜삼)·#32 sidehustle-tracker (벤치마크 Habit Pixel)

## 8G. Unstoppable continuous mode (PO 영구 2026-05-08·ADR 0056)
- PO 명령 5건: "야간 무한"·"중간 멈춤 X"·"멈추지 않고 사용"·"무한 자율모드 적용"·"지속해서 일할것"
- 매 응답 = 토큰·시간 최대 사용·중간 멈춤 X·다음 사이클 자동 진행
- 1 응답 = 다중 작업 묶음 (페인 검색 + 평가 + 코딩 + tests + 박제 + 갱신)
- 응답 끝 멘트 절대 X: "다음 권장"·"진행할까요?"·"보고드립니다"·"확인 권고"
- 자동 sunk cost 회피: NO_GO = 즉시 폐기·다음 검색
- GO 페인 = 같은 응답 내 1 cycle 압축 코딩 진행
- 정지 조건 4건만: 헌법 위반·비가역 액션·PO STOP 명시·토큰 한계
- 효율 가드 X·night_cycle_unstoppable·매 사이클 끝 권유 = 모두 무시
- 캐시카우 자동 수익 = 최종 목표 (PO 2026-05-08): 매 응답 = 매출 가능 자산 누적

## 8F. Pain discovery + market + cashcow gate (PO 영구 2026-05-08·ADR 0055)
- PO 명령: "인터넷 검색으로 사람들 페인포인트를 찾아내서 해결하는 간단 앱·시작 전 시장성·캐시카우 조사 후 시행"
- 모든 신규 앱 = 4 단계 게이트 통과 의무 (페인 1h + 시장 30m + 캐시카우 30m + GO/NO-GO 자동)
- 자동 룰: market ≥ 60 + cashcow ≥ 60 + Q5 PASS = GO·미달 = NO_GO (영구 폐기·sunk cost 0)
- WebSearch + 공개 자료 분석 OK·인터뷰·외부 발신 = ADR 0052 차단
- 박제 위치: docs/process·docs/pain-discovery/{candidates,approved,rejected}·docs/adr/0055
- 30 앱 매트릭스 = 본 게이트 통과 시만 추가 (#31+)
- 1차 시연 (Cycle 86): 4 후보 → 2 GO (#31 freelancer-tax-helper·#10 sns_multipost 확장) + 2 NO_GO

## 8E. External research 흡수 (Cycle 85·ADR 0054)
- 17 P-series Light 명령어 + B2C 시장 심층 보고서 박제 = `docs/research/external-2026-05/`
- 인디 패턴 (Pieter Levels 5%·Tony Dinh 6개월·Marc Lou cross-link·Daniel Vassallo small bets) = 손절·archive 정량 룰
- 5명 결제 룰 (D+30·D+60·D+90 마일스톤·archive 추천) = ADR 0053 + P44L 통합
- 페르소나 우선순위 (γ 사서교사 + α 재단 위탁 = Tier 1·δ 기업 = Tier 2·β 작은도서관 = Tier 3·정보누리 잠식)
- KOLAS III 종료 D-238 (2026-12-31)·일본 NDL JAPAN/MARC 80% 호환·MARC 처리 엔진 80% 재활용 가능
- 글로벌 4 트랙 추가 (Chrome 확장·Windows 매크로·GPT 래퍼·KORMARC) = 30 앱 + 4 글로벌 = 34 자산
- monorepo packages/ 승격 = 3번째 사용처 게이트 (Sandi Metz AHA)
- ADR 0052 정합: 9 즉시 자율 + 5 부분 (코드만) + 3 외부 차단 (P34·P39·P40)

## 8B. Plan B 무중단 자율 (ADR 0025·PO 2026-05-03 채택)
- 무중단 자율 사이클 = 7일 단위·P1~P28 큐 (~6.5개월)
- Cycle 1 = per-block disaggregation publish (강제)
- Cycle 2 = T2-1 offline demo finish + v0.6.0 tag (강제)
- Cycle 3+ = T2-2 → ... → T6-6 v1.0.0 release gate
- 자동 머지 차단 게이트 6건: ruff·pytest·binary_assertions 38/38·자관 174 회귀 ≤ 1pp·demo 30초·헌법 0건
- 영구 invariants 2건 (비협상):
  1) 헌법 위반 0: "100% 자동" / raw 확률 / 본문 송신 / 사서 검토 우회 = PR 차단
  2) 자관 데이터 git 누설 0: D:\ commit 시도 = 자율 정지·PO 통보
- "99.82%" 단일 = 폐기·per-block table 인용
- STOP 조건 7건만 자율 정지 (회귀 5사이클·누설·본문 송신·키 commit·큐 소진·PO STOP·동일 P 3사이클 SKIP)

## 자율 작업 가이드

너(Claude)가 자율로 작업할 때:

### 핵심 정책: 한 명령 = 끝까지 완료 (one-shot completion)

PO가 명령을 내리면 그 명령에 포함된 모든 작업을 한 번에 끝까지 처리한다.
- "더 추가할 거 있냐"고 중간에 묻지 말 것
- "다음 단계 진행할까요"로 끊지 말 것
- 명령 시작 시점에 추가로 필요한 것을 먼저 식별한 뒤 그것까지 한 번에 처리
- 단계 분할이 필요하면 분할 사실만 알리고 자동으로 다음 단계 진행
- 응답을 마치는 건 명령에 포함된 모든 작업이 진짜 다 끝났을 때만

예외 (이때만 멈추고 사람 호출):
- unsafe 분류 작업 (결제·DB·인증 자동 변경)
- 5번 시도해도 진척 없음
- 100파일 이상 변경 시도
- 명세 모호해서 추측 위험

### 일반 규칙

1. 변경은 항상 새 브랜치(auto/<timestamp>)에서.
2. 5파일 이상 변경되면 반드시 /pavr 사용.
3. 신규 의존성 추가 시 라이선스가 MIT/Apache/BSD 중 하나여야 함.
4. 실패하면 learnings.md에 패턴을 한 단락 추가하고 사람을 부를 것.
5. 비용을 추적해. 한 작업이 50K 토큰 넘어가면 중단하고 사람에게 보고.

### 무중단 자율 모드 (po_loop.sh 안에서 실행될 때)

매 사이클은 [사이클 N/M] 접두로 시작한다. 이때:
- 이번 사이클의 한 단위 작업만 진행하고 응답 종료 (외부 루프가 다음 사이클 트리거)
- PROGRESS.md를 매 사이클 끝에 갱신
- 모든 작업이 진짜 끝났으면 응답에 COMPLETED만 출력 → 외부 루프가 종료
- 막히면 learnings.md에 기록 후 다음 사이클 시도

## 9. 상세 참조 (agent_docs/·B안 P4)
- KORMARC 필드 → `agent_docs/kormarc_field_reference.md` ★ (신규)
- 평가 측정 → `agent_docs/running_evals.md` ★ (신규)
- 릴리스 절차 → `agent_docs/release_process.md` ★ (신규)
- 구버전 통합 → `agent_docs/CLAUDE-full-2026-05-03.md` (백업)
- 외부 API → `docs/spec.md`
- 테스트 → `docs/test_results.md`
- 헌법 정밀화 → `.claude/rules/{autonomy-gates,kormarc-domain,business-impact-axes}.md`
- 페르소나 자율 → `.claude/rules/personas-autonomy-policy.md`

## 10. 변경 이력
v0.5.0+ (2026-05-03): Part 87~92·600 tests·Champion 4/4 92.5점·CSAP 추상화·정확도 disaggregation. 상세 → `CHANGELOG_NIGHT.md`.
