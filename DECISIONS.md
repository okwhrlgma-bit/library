# 의사결정 로그 (V2 §4.4·Cycle 21 표준화)

> 작은 결정도 누적·모델이 "왜 X를 쓰는가?" 질문 시 검색 (3-Tier Memory Warm Tier).
> 야간 자율 결정 + 매출/제품 결정 통합. CLAUDE.md 부풀리지 않으면서 일관성 유지.

## 표준 형식 (Cycle 21+)

```
## YYYY-MM-DD — <결정 제목>
**컨텍스트**: <어떤 상황>
**선택**: <무엇을 골랐나>
**대안**: <고려한 다른 옵션>
**이유**: <왜>
**되돌릴 수 있는가**: <쉬운가·어려운가·한 방향인가>
**관련 ADR**: <ADR 번호>
```

---

## 2026-05-06 — Cycle 21: claude-saas-starter 5 영역 차용

**컨텍스트**: 외부 V2 가이드 흡수 후 PO가 starter 폴더 차용 + 삭제 명령
**선택**: refine-claudemd·deploy 슬래시 + 5 hooks (validate-bash·budget-guard·inject-learnings·append-learning·backup-transcript) + 3 automation (router·proposer-critic·supervisor) + 5 docs + 5 scripts
**대안**: 전체 차용·차용 0 (이미 보유로 충분)
**이유**: 핵심 V2 §1·§3·§6.1·§10 마스터 코드 = 검증된 패턴·재발명 X·기존 보유와 비중복
**되돌릴 수 있는가**: 가능 (모듈별 git revert)·하지만 V2 §11 체크리스트 정합 잃음
**관련 ADR**: 0036 PAVR (정합)·차후 ADR 0037 신설 권장

## 2026-05-04 — 결제는 PortOne v2 + NHN KCP Primary

**컨텍스트**: 한국 도서관 100% 세금계산서 요구·B2B 가상계좌 핵심
**선택**: PortOne v2 (Standard Webhooks) + NHN KCP Primary + 토스 V2 Secondary
**대안**: 토스페이먼츠 Primary·Stripe (한국 미지원)
**이유**: KCP 가상계좌 강력·연관리비 면제·B2B 세금계산서 통합·일반과세자 정합
**되돌릴 수 있는가**: 가능하지만 PortOne SDK 0.20.0 마이그레이션 비용 큼·한 방향에 가까움
**관련 ADR**: 0026 한국 SaaS 프로덕션·0035 budget tracker

## 2026-05-03 — Plan B 무중단 자율 채택 (가드레일 ADR 0024 supersede)

**컨텍스트**: 외부 901 출처 4중 진단 인지 후 PO 명시 결정
**선택**: 무중단 자율 + 영구 invariants 2건 (헌법 0건·자관 누설 0건)
**대안**: A안 가드레일 (Mon-Thu·24h hold·5 module/cycle·신규 모듈 X)
**이유**: PO 6개월 v1.0 도달 vs 1주 1 사이클 사이 명시 결정·invariants가 PIPA·헌법 사고 차단
**되돌릴 수 있는가**: PO `STOP` 입력 즉시 가능·하지만 22 사이클 누적 후 큐 재시작 비용
**관련 ADR**: 0025 Plan B 무중단

## 2026-05-04 — eval-corpus = 자관 174 round-trip + 익명 v1

**컨텍스트**: 단일 99.82% 약속 = 외부 901 보고서 거짓 정밀성 진단
**선택**: per-MARC-block disaggregation + round-trip 100% baseline + SHA-256 익명 corpus
**대안**: 99.82% 단일 유지·외부 API ground-truth 비교
**이유**: 정직 60-80% > 숨겨진 99% (Hamel Husain eval 정합)·N=1 한계 명시
**되돌릴 수 있는가**: 어려움 (ADR 0025 Plan B 사이클 1 강제 산출물·헌법 §11 카테고리형 신뢰)
**관련 ADR**: 0025 Plan B + ADR 0030 카테고리형 신뢰

## 2026-05-05 — Founding Member = LTD 금지·연간결제 의무

**컨텍스트**: 외부 매출 보고서 P31 Live Proxies·Freemius LTD 분석 = 지원 티켓 30-40% 증가
**선택**: 영구 50% + 100관 한정 + 2026-06-30 데드라인 + 연간결제 의무 + 가격 영구 동결
**대안**: LTD (평생 라이선스)·25% 할인 표준
**이유**: LTD = 신규 구독 카니발리제이션·25% 초과 = "할인 기다리기" 학습·Recurly 표준
**되돌릴 수 있는가**: 가능·하지만 약속 깨면 신뢰 손실
**관련 ADR**: 0026 §D + ADR 0030 카테고리형 신뢰

## 2026-05-04 — 4 플랜 = 한국도서관법 정합 명명

**컨텍스트**: ALPAS·OCLC·Alma 가격 비공개 = 차별화 무기·도서관법 카테고리 = 사서 즉시 인지
**선택**: 작은도서관 ₩30K / 학교도서관 ₩50K / 공공도서관 ₩150K / 기관 ₩300K~
**대안**: Lite/Standard/Pro/Enterprise (영문 일반)
**이유**: 한국도서관법 = 사서 즉시 자관 카테고리 인지·전환율 ↑
**되돌릴 수 있는가**: 가능·영업 자료·랜딩 페이지 갱신 비용
**관련 ADR**: 0026 §D·ADR 0030 카테고리형 신뢰

## 2026-05-04 — KOLAS III 종료 = 2026-12-31 (1초 변경 = STOP)

**컨텍스트**: 국립중앙도서관 books.nl.go.kr 공식 공지·외부 매출 보고서 §A
**선택**: 2026-12-31 23:59:59 KST = 영구 invariant·테스트 게이트 박제 (test_kolas3_countdown·fact_checker)
**대안**: "약 12월말"·"연말" 모호 표기
**이유**: 골든윈도우 D-day 마케팅·1초 변경 = 영업 자료 전체 회귀·법적 책임
**되돌릴 수 있는가**: 불가 (정부 공식 사실)
**관련 ADR**: ADR 0026 §A·ADR 0036 Failure Replay 등록 권장

## 2026-05-06 — Failure Replay = ~/.kormarc-auto/replays/{date}-{slug}/

**컨텍스트**: V2 §4.3 = 새 모델 자동 업데이트 시 옛 실패 회귀 가능
**선택**: append-only 디렉토리 + input.json/expected.txt/actual.txt 3 파일
**대안**: SQLite·LLM judge·TTL 90일
**이유**: 디렉토리 = git diff·인간 검토 가능·KOLAS3 사실 영구 invariant
**되돌릴 수 있는가**: 가능 (디렉토리 이동)
**관련 ADR**: 0036 PAVR + Failure Replay

---

## 야간 자율 결정 (Cycle 21 이전·자유 형식 보존)


## 2026-04-27 KST — OpenChronicle LLM 도입 (REJECT)

**출처**: PO 제공 https://discuss.pytorch.kr/t/openchronicle-llm/9882

**실체**: 이름과 달리 LLM 모델 아님. 모든 LLM(Claude·GPT·Gemini·Llama)에 영속 메모리를 제공하는 로컬 메모리 인프라 (SQLite FTS5 + Markdown).

**평가축**:
| 차원 | 점수 |
|---|---|
| §0 사서 마크 시간 | 0 (도서관 도메인 무관) |
| §12 매출 의향 | 0 (사서 미노출 인프라) |
| 운영 안전 (ADR 0010) | **−1** (v0.1.0 알파 + macOS only — Windows PO 환경 미지원) |
| 우리 메모리 중복도 | **높음** — 4단 위계 운영 중 (CLAUDE.md·learnings.md·ADR 11+·patterns 26·`~/.claude/projects/.../memory/`) |

**결정**: REJECT — 평가축 양축 0 + 운영 안전 음수. 우리 학습 영속 인프라가 이미 충분.

**보수적 회피**: ADR 미작성 (도입 안 하므로 ADR 과잉). 본 항목으로 결정 영속.

**재검토 트리거**: (1) v1.0 GA + Windows 지원, (2) 우리 메모리 시스템에서 검색·검사 한계 발생.

## 2026-04-27 KST — streamlit-authenticator 도입 (ACCEPT, 6차원 +7)

**근거**: PO 마스터 명령서 Part G Step 2 + PO 답변 (2026-04-27).

**6차원 안전 평가**:
| 차원 | 점수 | 근거 |
|---|---:|---|
| OS 호환성 | **+1** | pure Python, Windows·macOS·Linux 모두 동작 |
| 데이터 거버넌스 | **+1** | 로컬 `.streamlit/auth_config.yaml`만 사용, PII 외부 송신 0 |
| 보안 | **+2** | bcrypt 해싱·세션 쿠키·timing-safe 비교·CSRF 가드 검증된 OWASP 패턴 |
| 의존성 | **+1** | mkhorasani 활발 유지보수, GitHub 1.7k stars, 안정 메이저 버전 0.4.2 |
| 롤백 | **+2** | `pip uninstall streamlit-authenticator` 단일 명령, app.py 인증 import 제거 |
| 관측 가능성 | **0** | 기본 Python logging만, 별도 메트릭/트레이싱 없음 |
| **합계** | **+7** | **ACCEPT** (≥ +6 + 모든 차원 ≥ 0) |

**의존성 정확 버전 핀** (PO 마스터 명령서 부록 A 일치):
- `streamlit-authenticator==0.4.2`
- `bcrypt==4.3.0` (streamlit-authenticator transitive 의존이지만 명시 핀)
- `PyYAML==6.0.2` (이미 transitive 가능성 — 명시 핀으로 재현성 보장)

**도입 사유**:
- `cloudflared trycloudflare.com` 종료(Part G Step 1) 후 Streamlit 127.0.0.1만 listening = 외부 노출 0 보장
- 다음 cloudflared 재기동 전에 인증 도입 의무
- 자체 password 체크 (옵션 A)는 임시 코드의 보안 결함 위험 + 마이그레이션 비용 → PO B 선택

**롤백 절차**:
1. `pip uninstall streamlit-authenticator bcrypt`
2. `app.py`의 `authenticator.login()` 블록 제거
3. `.streamlit/auth_config.yaml` 삭제 (gitignore이라 git 영향 없음)
4. `requirements.txt`·`pyproject.toml`에서 3 패키지 제거
5. git revert (Commit 1)

**장기 마이그레이션** (Week 2 이후):
- 도메인 구매 + Cloudflare Zero Trust + Google OAuth 셋업 후
- Streamlit 1.46+ 네이티브 `st.user.is_logged_in` + Cloudflare Access 조합으로 전환
- streamlit-authenticator 폐기 (해당 시점 ADR로 명시)

**검증 트리거**: `streamlit run` 후 인증 없이 접근 시 401 또는 redirect → 인증 후만 200 응답.

## 2026-04-27 21:03 KST — PermissionDenied: Bash
- 입력: `git push --force`
- 사유: irreversible-guard
- 우회: 다음 단계로 진행 (자율 게이트 §자동 우회)

---

## 2026-05-06 — Cycle 60: UI/UX 통합 (헌법 §12 doc → 코드 100%)

**컨텍스트**: 28 사이클 동안 헌법 §12 (KWCAG 2.2 + KRDS + Pretendard) = doc 박제·코드 적용 0건
**선택**: `.streamlit/config.toml` + `a11y_inject.py` + `librarian_ux.py` 신설·모든 Streamlit 진입점 1회 호출
**대안**: 페이지별 inject (중복)·Streamlit components-html (iframe 격리·키보드 흐름 단절)
**이유**: KWCAG 2.2 9 항목 (1.3.1·1.4.3·1.4.4·1.4.13·2.3.3·2.4.1·2.4.7·2.5.5)·헌법 §12 invariant 영구 게이트
**되돌릴 수 있는가**: 가능 (모듈 단위 git revert)
**관련 ADR**: 0044

## 2026-05-06 — Cycle 61: 8 ICP 페르소나 + 상업성/SEO/AEO/GEO + invariant 11

**컨텍스트**: PO "사서 페르소나가 이거 돈 내고 살까?"·외부 자료 종합·인터뷰 0건
**선택**: 8 ICP 페르소나 (P1~P8) × 5 영역 매트릭스·정직 헤더 영구 (invariant 11·ADR 0046)
**대안**: 시뮬 결과로 PMF 결정 (외부 901 진단 4중 패턴 위험)·인터뷰만 (1주 시간)
**이유**: 결제 의향 ≠ 결제 권한 분리 통찰·8/8 권당 200원 모델 적합·시간 절감 5/8만 정합
**되돌릴 수 있는가**: 어려움 (CLAUDE.md §13 헌법 박제·invariant 11)
**관련 ADR**: 0045·0046

## 2026-05-06 — Cycle 62: 마케팅 30+ 갭 (콜드 메일 5 페르소나)

**컨텍스트**: PO "검색·노출 잘되게"·SEO/AEO/GEO 모듈 박제·발행 0건
**선택**: 5 영역 30+ 갭 매트릭스 박제·콜드 메일 5 페르소나 시드·콘텐츠 캘린더 90일·press kit·MOU 8
**대안**: 발행까지 (도메인 필요)·매트릭스만 (Cycle 16 이미 박제·중복)
**이유**: 페르소나별 메시지 분기 (5/8 시간 절감 + 3 다른 동기) 사전 박제·인터뷰 후 v2
**되돌릴 수 있는가**: 가능 (시드 markdown 단위)
**관련 ADR**: 0045 §B (영업 시기) + ADR 0046 (정직 헤더)

## 2026-05-06 — Cycle 63: 신경 0 배포 stack (₩0/월·도메인 X) + E-E-A-T

**컨텍스트**: PO "도메인 필수? 돈 안 들이고 신경끄는 구조"
**선택**: GitHub Pages + Streamlit Community Cloud + GitHub Actions + GitHub Releases
**대안**: AWS Lightsail (₩7K/월 Cycle 26)·자체 도메인 (₩30K/년)·CSAP NCP (₩50K+/월)
**이유**: PO Phase 1 (사용자 0명) = ₩0 stack 충분·15분 외부 작업으로 활성·git push 자동
**되돌릴 수 있는가**: 가능·매출 후 AWS Lightsail로 이전 (외부 858 보고서 정합)
**관련 ADR**: 0026 §E (인프라)·도메인 = Phase 2 권장

## 2026-05-06 — Cycle 63: E-E-A-T 4 신호 (검색·LLM 신뢰도)

**컨텍스트**: PO "신뢰도 영향 간다고 하던데"·Google 2022 EEAT update + LLM 인용 정합
**선택**: About 페이지·Schema Person/Organization·통계 박스·5 권위 인용 (NLK·KAIT·MCST·KLA·KLMA)
**대안**: 자체 평판 신호만 (외부 인용 X)·MOU만 (사업자 등록 후·시간 ↑)
**이유**: 코드만으로 즉시 가능·도메인 0원·인터뷰 + 사업자 후 = MOU 추가 가능
**되돌릴 수 있는가**: 가능 (markdown·landing 단위)
**관련 ADR**: 0044 (UI/UX)·0046 (정직)·press-kit-2026-05.md 통합

