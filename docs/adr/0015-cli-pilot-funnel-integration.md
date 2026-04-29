# ADR-0015: CLI에 prefix-discover·pilot-collect·sales-funnel 통합

## Status
Accepted (2026-04-30)

## Context

scripts/ 디렉토리에 PILOT·영업 측정 도구 3종 모듈로 존재:
- `scripts/validate_real_mrc.py` (자관 .mrc 99.82% 정합)
- `scripts/pilot_collect.py` (PILOT 시연 결과 수집)
- `scripts/sales_funnel.py` (가입→결제 funnel)
- `src/kormarc_auto/librarian_helpers/prefix_discovery.py` (049 prefix 자동)

사용자 (사서·PO) 진입 패턴:
- `kormarc-auto isbn 9788912345678` 같이 단일 entry point 익숙
- `python scripts/X.py` 호출은 외부 path 인지·sys.path 추가 필요

## Decision

3 도구를 CLI 명령으로 통합:
1. `kormarc-auto prefix-discover <dir> [--threshold 1.0]` (5c3ce2b)
2. `kormarc-auto pilot-collect [--persona macro] [--library 자관]` (69f2ec9)
3. `kormarc-auto sales-funnel [--json reports/funnel.json]` (69f2ec9)

구현: `src/kormarc_auto/cli.py`에 cmd_prefix_discover·cmd_pilot_collect·cmd_sales_funnel
- prefix-discover: librarian_helpers.PrefixDiscoverer 직접 호출
- pilot-collect·sales-funnel: subprocess로 scripts/X.py 호출 (코드 중복 회피)

UTF-8 stdout fix (cli.py 시작 시점):
```python
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

## Consequences

### 쉬워지는 것

- 사서 진입 단순화 (1 entry point)
- README CLI 섹션 가시화 (사서 즉시 발견)
- `kormarc-auto info`로 환경 진단 후 즉시 시연
- Windows cp949 환경 한국어 출력 정합 (UTF-8 reconfigure)

### 어려워지는 것

- subprocess 호출 = 약간의 overhead (1~2초)
- 회피: 자주 쓰는 prefix-discover는 직접 import (이미 적용)

### 트레이드오프

- 코드 중복 (subprocess) ↔ 통합 entry point 단순화
- 우리 선택: 사서 친화 단순화 (1인 운영·PILOT 도입 진입 장벽 ↓)

### 후속

- AUTONOMOUS_BACKLOG 1순위 명령 모두 처리
- streamlit_app caption에 prefix-discover GUI 안내 추가 (cfd3424)
- README CLI 섹션 갱신 (a36b429)

## Sources

- 5c3ce2b: prefix-discover CLI + UTF-8 fix
- 69f2ec9: pilot-collect·sales-funnel CLI
- a36b429: README CLI 갱신
- cfd3424: streamlit_app caption 안내
