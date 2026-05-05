"""갈래 B Cycle 22 (P51·V2 §6.4) — Progressive Trust 5단계.

승격 규칙:
1. 자동화 항목별 Level 1 시작
2. 30회 연속 성공 = 다음 Level 승격 PR 자동 생성
3. PR = PO 승인 필수 (자동 머지 X·V2 §11)
4. 1회 실패 = 카운터 reset (보수적)
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

TrustLevel = Literal[1, 2, 3, 4, 5]

# Level별 허용 도구 (V2 §6.4 정합)
PROGRESSIVE_TRUST_LEVELS: dict[int, list[str]] = {
    1: ["Read"],
    2: ["Read", "Edit"],
    3: ["Read", "Edit", "Write", "Bash(npm:*)", "Bash(uv:*)", "Bash(pip:*)"],
    4: ["Read", "Edit", "Write", "Bash(*)"],  # deny list 적용
    5: ["Read", "Edit", "Write", "Bash(*)", "MCP-write"],
}

SUCCESS_THRESHOLD: int = 30


def resolve_trust_dir() -> Path:
    env = os.getenv("KORMARC_TRUST_DIR")
    if env:
        return Path(env)
    return Path.home() / ".kormarc-auto" / "trust"


@dataclass(frozen=True)
class AutomationRecord:
    """자동화 항목 1 실행 결과."""

    automation_id: str  # "router-code-edit"·"daily-autonomy" 등
    success: bool
    level_at_run: int
    timestamp: str  # ISO 8601 UTC
    note: str = ""

    @classmethod
    def now(cls, **kwargs: Any) -> AutomationRecord:
        kwargs.setdefault("timestamp", datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"))
        return cls(**kwargs)


@dataclass
class TrustState:
    """자동화 항목별 신뢰 상태."""

    automation_id: str
    current_level: TrustLevel = 1
    consecutive_successes: int = 0
    total_runs: int = 0
    total_successes: int = 0
    total_failures: int = 0
    last_updated: str = field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def to_dict(self) -> dict:
        return asdict(self)


def _state_file(automation_id: str) -> Path:
    base = resolve_trust_dir()
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{automation_id}.json"


def _load_state(automation_id: str) -> TrustState:
    path = _state_file(automation_id)
    if not path.exists():
        return TrustState(automation_id=automation_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    return TrustState(**data)


def _save_state(state: TrustState) -> None:
    state.last_updated = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = _state_file(state.automation_id)
    path.write_text(
        json.dumps(asdict(state), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )


def record_automation_outcome(*, automation_id: str, success: bool, note: str = "") -> TrustState:
    """자동화 실행 결과 기록 + 카운터 갱신."""
    state = _load_state(automation_id)
    state.total_runs += 1
    if success:
        state.total_successes += 1
        state.consecutive_successes += 1
    else:
        state.total_failures += 1
        state.consecutive_successes = 0  # 1회 실패 = reset (보수적)

    _save_state(state)
    return state


def can_promote(state: TrustState) -> bool:
    """다음 Level 승격 가능 여부 (30회 연속 성공)."""
    if state.current_level >= 5:
        return False  # 최대 Level
    return state.consecutive_successes >= SUCCESS_THRESHOLD


def suggest_next_level(state: TrustState) -> dict[str, Any]:
    """승격 PR 본문용 dict (V2 §6.4 정합)."""
    if not can_promote(state):
        remaining = SUCCESS_THRESHOLD - state.consecutive_successes
        return {
            "promotion_eligible": False,
            "current_level": state.current_level,
            "consecutive_successes": state.consecutive_successes,
            "threshold": SUCCESS_THRESHOLD,
            "remaining_until_eligible": max(0, remaining),
            "note": f"승격 대기 = {remaining}회 더 연속 성공 필요",
        }

    next_level = state.current_level + 1
    return {
        "promotion_eligible": True,
        "current_level": state.current_level,
        "next_level": next_level,
        "consecutive_successes": state.consecutive_successes,
        "current_tools": PROGRESSIVE_TRUST_LEVELS[state.current_level],
        "next_tools": PROGRESSIVE_TRUST_LEVELS[next_level],
        "pr_required": True,
        "auto_merge_blocked": True,  # V2 §11 자기 안전장치 풀지 X
        "pr_template": (
            f"# Progressive Trust 승격 제안: {state.automation_id}\n\n"
            f"현재 Level: {state.current_level}\n"
            f"제안 Level: {next_level}\n"
            f"연속 성공: {state.consecutive_successes}/{SUCCESS_THRESHOLD}\n"
            f"총 실행: {state.total_runs}건 (성공 {state.total_successes}·실패 {state.total_failures})\n\n"
            f"## 추가 도구\n\n"
            f"```\n"
            f"{set(PROGRESSIVE_TRUST_LEVELS[next_level]) - set(PROGRESSIVE_TRUST_LEVELS[state.current_level])}\n"
            f"```\n\n"
            f"## PO 승인 후 settings.json 업데이트 필요\n\n"
            f"⚠️ 자동 머지 절대 금지 (V2 §11·헌법 §0)"
        ),
        "note": "🟢 승격 가능·PR 자동 생성 후 PO 승인 필수",
    }


def iter_states() -> Iterator[TrustState]:
    """모든 자동화 항목 상태 순회 (관측·옵저버빌리티)."""
    base = resolve_trust_dir()
    if not base.exists():
        return
    for f in sorted(base.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            yield TrustState(**data)
        except (json.JSONDecodeError, TypeError):
            continue
