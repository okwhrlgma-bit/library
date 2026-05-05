"""갈래 B Cycle 20B (P48·V2 §4) — Failure Replay 시스템.

원칙 (V2 §4.3 정합):
- 실패 = 재현 가능한 input + output + context 묶음
- 위치: ~/.kormarc-auto/replays/{slug}/
- 새 모델/프롬프트 변경 시 = 모든 replay 회귀 검사
"""

from kormarc_auto.replay.store import (
    FailureReplay,
    ReplayResult,
    create_replay,
    iter_replays,
    load_replay,
    resolve_replays_dir,
    run_regression,
)

__all__ = [
    "FailureReplay",
    "ReplayResult",
    "create_replay",
    "iter_replays",
    "load_replay",
    "resolve_replays_dir",
    "run_regression",
]
