# 야간 자율 결정 로그

> 모호한 지점에서 더 안전·보수적 옵션을 선택한 근거.

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
