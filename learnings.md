# learnings.md — kormarc-auto 자율 학습 누적

> **목적**: PO 자율성 가이드 레벨 2 — 세션을 넘는 학습.
> **사용**: 매 commit 직후 새로운 통찰 추가. 다음 세션이 자동 로드 (CLAUDE.md에서 참조).
> **원칙**: 사실 + 근거 + 적용 방법. 추측은 ⚠ 표시.

---

## 2026-04-26 — v0.4.x 자율 디벨롭 18 commit

### 사서 도메인
- **KOLAS III 종료(2026-12-31)**는 6,900곳 도서관에 단일 가장 강력한 영업 트리거. 모든 1차 메일·시연 첫 줄에 명시.
- **학교도서관 95% 마크 외주** (2023 뉴시스). 도서납품업체 B2B(/batch-vendor) 채널이 학교 직접 영업보다 빠름 — 1대 다수.
- **알파스 등록번호 12자리** = 등록구분(2~3자) + 차수(2자) + 연도(2자) + 일련(4~6자). 사서가 매주 누락번호 점검.
- **책나래는 "도서명", 책바다는 "서명"** — 같은 의미 다른 컬럼명. 어댑터 분리 필수.
- **도서관법 §21 납본 부수**: 정부 3부 / 보존동의 1부 / 표준 2부. 시행규칙 별지 제3호서식이 정식.
- **장서개발지침 §2 KDC 분포**: 문학(8) 권장 20~30%. 사서가 수서 결정 시 분포 편중을 가장 먼저 점검.

### 코드 패턴
- **`from kormarc_auto.inventory.library_db import iter_records` 함수 없음** — `search_local("", limit=N)` 호출이 정확.
- Python `from typing import Iterable`은 ruff에서 deprecated → `from collections.abc import Iterable`.
- ruff 자동 수정으로 import 정렬 가능: `ruff check --fix`.
- Streamlit st.success / st.error / st.warning은 자체 아이콘 표시함. 텍스트에 ✓/⚠ 추가는 강조 시에만.
- pymarc Record 변환 시 항상 8/UTF-8 인코딩 명시.

### Hooks·자율성
- Windows 환경에는 jq 미설치 — hook 명령에 jq 의존 금지. `.venv/Scripts/python.exe` 직접 호출이 안전.
- PostToolUse(Edit/Write) hook은 `async: true`로 설정해야 편집 흐름 차단 안 함.
- settings.json watcher는 세션 시작 시 watch 시작한 디렉토리만 봄. 새로 추가한 hook은 다음 세션에서 완전 적용.
- Claude Code Remote Control은 `remoteControlAtStartup: true` 설정으로 PC 새로 켤 때마다 자동 — `/rc` 입력 불필요.

### 매출 영향 우선순위 (높음 → 낮음)
1. **컨소시엄 단체 영업** (1대 30) — 영업 시간당 매출 30배
2. **/batch-vendor B2B** — 도서납품업체 마진 700~1,400원/권
3. **KOLAS 마이그레이션 5세그먼트 메일** — 종료 8개월 전 압박
4. **사서 5분 시연 체크리스트** — 시연 직후 가입 전환
5. **잔여 무료 자동 표시** — 결제 임박 시점 자연 노출
6. 카카오 자동응답 + 베타 인터뷰 템플릿 — 24시간 SLA

### PO 선호 (관찰)
- 매 commit 작은 단위 + 자세한 근거 명시 (PR 분리 안 함)
- "디벨롭 할 게 없다" 판단 자체 금지 — 항상 다음 가치 찾기
- 매 흡수에 "사서 매출 의향 + 마크 시간 단축" 평가축 적용
- PO는 "보기·사용하기 좋은" UX 강조 — 차분한 톤·16px·여백·명확한 다음 단계
- 답변은 한국어, 짧고 즉시 행동 가능한 문장 선호

### 실수·고친 것
- `next_registration_number` 첫 테스트에서 `"EM010" + "00001"` 라고 잘못 어셔션. 실제는 `EM` + 차수`01` + 연도`26` + 일련`00001` = `"EM012600001"`.
- `_holdings_by_isbn` 헬퍼를 추가 후 mock target 변경 — 모듈 내부 import는 mock 경로가 모듈 내부여야.
- Edit 도구가 trailing whitespace 자동 strip — 그 부분 어셔션 시 주의.

---

## 다음 세션 시작 시 자동 적용 체크
- [ ] 모든 .py 편집 후 PostToolUse hook이 ruff fix 자동 — 메모리에 위반 사례 추가 시 즉시 반영
- [ ] 새 모듈 추가 시 단위 테스트 ≥3건 (정상·경계·에러) — `feedback_user_friendly.md §8` 명시
- [ ] commit 메시지 끝에 항상 Co-Authored-By: Claude Opus 4.7 (1M context) 트레일러
- [ ] PO 자료 폴더 `자료/` 신규 파일 발견 시 즉시 흡수 (max_autonomy 메모리)

---

## 2026-04-26 — PO 자율성 가이드 흡수 (Anthropic·외부 9가지)

### 즉시 적용
- **CLAUDE.md §11 변경 이력** (이미 적용 — 매 commit 동기화)
- **learnings.md** (이 파일 — 이번 세션 신규)
- **PostToolUse hook** (Edit/Write 후 ruff fix 자동) — `.claude/settings.json`
- **Remote Control 자동 활성** — `~/.claude/settings.json`
- **바이너리 어셔션 12종** — `scripts/binary_assertions.py` (12/12 100%)
- **종료 게이트**: pytest 통과 + ruff 0 + commit 완료 (명시 토큰 대신)

### 향후 적용 검토 (도입 우선순위 순)
1. **모델 라우팅**: agents frontmatter에 `model: haiku|sonnet|opus` 명시 — 분류는 haiku, 깊은 추론은 opus. 비용 대비 처리량 향상.
2. **Stop hook + 완료 토큰**: 자율 commit 직전 `<promise>COMPLETE</promise>` 패턴. 미흡 시 같은 작업 반복.
3. **Fork (베스트 오브 N)**: 같은 컨텍스트 3개 분기 → 다른 시드/접근 → 결과 비교 → 최선 선택. 큰 결정에 활용.
4. **DSPy/GEPA 프롬프트 최적화**: 자주 쓰는 KDC 분류·주제명 추천 프롬프트를 골든셋 + 메트릭으로 자동 진화. MATH 67%→93% 사례.
5. **Routines (Anthropic 클라우드)**: Pro 5회/일·Max 15회/일. 야간 의존성 업데이트 PR·문서 드리프트 점검에 적합.
6. **Computer Use 시각 회귀**: Streamlit UI 변경 후 스크린샷 비교 자동. 사서 친화 UI 검증에 결정적.
7. **/loop 명령**: 인터벌 생략 시 동적 대기. 빌드 점검·PR 리뷰 자동.
8. **에이전트별 hook**: `.claude/agents/X.md` frontmatter에 hook 직접 박기 (전역 hook 분리).
9. **Channels (옵저버빌리티)**: 모든 잡 메트릭 push → 자율 우선순위 입력.

### 적용 안 할 것 (블래스트 반경 통제)
- `--dangerously-skip-permissions` 무한 루프 — 샌드박스 외에서는 절대 금지
- 비가역 액션 (DB drop·force push·결제) — hook으로 명시 차단
- 무한 루프 → `--max-iterations 30` + 토큰 예산 + 종료 토큰 3중 게이트

## 2026-04-26 — 야간 자동 재시도·재개 셋업 (PO 가이드)

### 도구 후보
- **claude-auto-retry** (npm) — `npm i -g claude-auto-retry`. Claude Code 죽으면 자동 재실행
- **claude-auto-resume** (셸 스크립트) — 한도 도달·세션 만료 시 자동 재개
- 둘 다 `--dangerously-skip-permissions` 빈번 사용 → 반드시 deny 규칙 동반 필수

### 권장 야간 셋업
1. `tmux new -s kormarc` 또는 PowerShell 백그라운드 잡 안에서 Claude Code 실행
2. `~/.claude/settings.json`·`.claude/settings.json` 양쪽 deny 강화 (이미 적용 — 38종)
3. 한도 도달 시 `/rate-limit-options` → 3번 (자동 재개)
4. 작업을 작은 todo로 분할 — 한 번에 1개 commit 단위, 중간 재시작 혼란 최소화
5. `scripts/binary_assertions.py` 매 commit 후 자동 실행 (Stop hook으로 강제 가능)

### 위험 신호 (즉시 중단)
- 어셔션 통과율 80% 미만으로 떨어짐 → 자동 commit 중단
- ruff 위반 누적 → hook이 막지 못한 회귀
- git log에 `--no-verify` 또는 `--force` 등장 → 정책 우회 시도

### 남은 적용 후보
- Stop hook으로 commit 직후 `binary_assertions.py --strict` 자동 실행 — 미통과 시 commit revert
- `tmux` 미설치 환경에서는 PowerShell `Start-Job` 또는 Windows Task Scheduler 활용
- 매출·테스트·어셔션 메트릭을 `.claude/golden/dashboard.md`로 매일 자동 갱신

---

## 추가 양식 (다음 학습 추가 시 그대로 사용)

```
## YYYY-MM-DD — 작업 요약

### 영역
- 사실 (출처: 파일명·줄번호)
- ⚠ 추측 (확실하지 않음)

### 코드 패턴
- 발견한 함정 + 회피 방법

### 매출 영향
- HIGH/MID/LOW + 근거
```
