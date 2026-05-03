# 인증 회전 런북 — Streamlit auth_config.yaml 90일 갱신

> **출처**: PO 답변 (2026-04-27) — auth_setup.py 보존 결정 재고. 평문 비밀번호 처리 코드는 working tree 상시 보존 X. git history에만 보존.
> **참조**: ADR 0011 (Part G Step 2 streamlit-authenticator), DECISIONS 6dim+7 (2026-04-27).
> **주기**: 90일 (PO 마스터 §G.5 정기 보안 감사) + 노트북 도난·악성코드 의심 시 즉시.

## 위협 모델 (왜 working tree 보존 X)

| 위협 | 시나리오 | 회피 |
|---|---|---|
| 메모리 덤프 | `getpass.getpass()` → bcrypt 해시 사이 평문이 RSS에 잔존 | 스크립트 실행 시간 최소화 + 즉시 삭제 |
| 스왑 파일 | Windows pagefile.sys에 메모리 페이지 기록 | 동일 (실행 빈도 최소화) |
| 노트북 도난 + 디버거 attach | 누구든 `python scripts/auth_setup.py` 실행 → 새 비밀번호로 덮어쓰기 → 우회 | working tree 상시 보존 X |
| 악성코드 실행 (RCE 등) | Claude Code 외부 프로세스가 auth_setup.py 호출 → silent 비밀번호 변경 | 동일 |
| git history 노출 | git log·git show로 누구나 코드 복원 가능 | **이 런북의 trade-off** — 회전 절차 완료 후 working tree에는 없음 |

## 회전 절차 (90일마다)

### 1) git history에서 일시 복원

```bash
cd "C:\Users\kormarc-auto\OneDrive\바탕 화면\클로드 코드 활동용\kormarc-auto"

# 최근 auth_setup.py가 있던 commit 검색 (지난 회전 또는 최초 도입)
git log --diff-filter=AD --pretty=format:"%h %ad %s" --date=short -- scripts/auth_setup.py | head -5

# 첫 번째 결과 SHA를 사용 (예: abc1234)
git show <SHA>:scripts/auth_setup.py > scripts/auth_setup.py
```

### 2) 인터랙티브 실행

```bash
.venv/Scripts/python.exe scripts/auth_setup.py
```

화면 안내:
- 새 비밀번호 입력 (12자 이상, 비밀번호 매니저에 보관 — 종이·평문파일 X)
- 재입력 확인
- bcrypt 해시 + 새 cookie key 자동 생성 → `.streamlit/auth_config.yaml` 덮어씀

### 3) 즉시 삭제 (working tree 정리)

```bash
rm scripts/auth_setup.py
```

`auth_config.yaml`은 `.gitignore` 보호 중이라 git 영향 없음. `auth_setup.py` 삭제도 git status에 표시되지 않음 (이미 git history에만 존재).

### 4) 검증

```bash
# 4-1) 기존 streamlit 종료 (이전 cookie key 무효화)
taskkill //F //IM streamlit.exe 2>/dev/null
# 또는 PID 직접 종료

# 4-2) 새 streamlit 기동
.venv/Scripts/python.exe -m streamlit run src/kormarc_auto/ui/streamlit_app.py

# 4-3) 브라우저 검증 3종
# (a) 로그아웃 상태 → KORMARC UI 차단 (로그인 화면만 노출)
# (b) 잘못된 비밀번호 → "로그인 실패" 메시지
# (c) 새 비밀번호 → 본 UI 노출
```

### 5) 모든 기기에서 재로그인

cookie key 회전으로 기존 세션 모두 무효화됨. PO 폰·다른 PC에서 재로그인 필요 — 정상 동작.

## 비상 회전 (도난·RCE 의심 시)

위 1)~5) 동일하되:

- 새 비밀번호 + 새 cookie key 즉시 생성 (24시간 내)
- Streamlit 외부 노출 (cloudflared) **즉시 종료**:
  ```bash
  taskkill //F //IM cloudflared.exe
  ```
- Cloudflare Zero Trust 도입 후라면 Access Application의 session cookie 강제 회전 (Cloudflare Dashboard → Access → Sessions → Revoke All)
- `~/.cloudflared/<UUID>.json` 자격증명 파일 회전 검토 (`cloudflared tunnel rotate`)

## auth_setup.py 코드 위치 (참조용)

```
git history:
- 도입 commit: 3440d34 (2026-04-27, Part G Step 2 streamlit-authenticator 인증 도입)
- 삭제 commit: <Commit 2 이후>

실 코드 보기 (working tree 손대지 않음):
git show 3440d34:scripts/auth_setup.py
```

## 6차원 안전 평가 (auth_setup.py git history-only 보존)

| 차원 | 점수 | 근거 |
|---|---:|---|
| OS 호환성 | +1 | git 모든 OS 동일 |
| 데이터 거버넌스 | +2 | 평문 비밀번호 working tree 0초 잔존 |
| 보안 | **+2** | 노트북 도난·RCE 우회 가능성 0 (재인증 강제) |
| 의존성 | +1 | git만 사용 (이미 의존) |
| 롤백 | +2 | git revert 1 commit |
| 관측 가능성 | 0 | git log로 회전 이력 추적 가능 |
| **합계** | **+8** | **ACCEPT** |

## 변경 이력

- 2026-04-27 — 신규 (PO 답변 정정 — Commit 1 보존 결정 재고)
