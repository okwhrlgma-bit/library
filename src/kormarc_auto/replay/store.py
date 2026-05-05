"""갈래 B Cycle 20B (P48) — Failure Replay 저장소.

저장 (V2 §4.3 정합):
~/.kormarc-auto/replays/{YYYY-MM-DD}-{slug}/
├── input.json         # 프롬프트·옵션·model·timestamp
├── repro.sh           # 환경 재현 (선택)
├── expected.txt       # 기대 행동
└── actual.txt         # 실제 출력 (실패 당시)

ENV: KORMARC_REPLAYS_DIR (default = ~/.kormarc-auto/replays)
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


def resolve_replays_dir() -> Path:
    env = os.getenv("KORMARC_REPLAYS_DIR")
    if env:
        return Path(env)
    return Path.home() / ".kormarc-auto" / "replays"


@dataclass(frozen=True)
class FailureReplay:
    """1 실패 = 1 replay 디렉토리."""

    slug: str  # "kolas3-d-day-mismatch"·dir name용
    title: str
    failure_kind: str  # "regression"·"crash"·"wrong_output"·"injection"
    failed_at: str  # ISO 8601 UTC
    prompt: str
    expected: str
    actual: str
    model: str = ""
    options: dict[str, Any] = field(default_factory=dict)
    note: str = ""
    fixed_at: str | None = None
    fix_commit: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ReplayResult:
    """회귀 검사 결과."""

    replay_slug: str
    is_passing: bool  # True = 기대대로 동작 (실패 재현 X = 픽스 유지)
    actual_output: str
    diff_summary: str
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def _slugify(s: str) -> str:
    """파일 시스템 안전 slug."""
    s = s.lower().strip()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9가-힣\-]", "", s)
    return s[:60]


def _replay_dir(replay: FailureReplay) -> Path:
    base = resolve_replays_dir()
    date_part = replay.failed_at[:10]  # YYYY-MM-DD
    return base / f"{date_part}-{replay.slug}"


def create_replay(
    *,
    title: str,
    failure_kind: str,
    prompt: str,
    expected: str,
    actual: str,
    model: str = "",
    options: dict[str, Any] | None = None,
    note: str = "",
    failed_at: datetime | None = None,
) -> FailureReplay:
    """실패 1건 등록 → 디스크 저장."""
    if failed_at is None:
        failed_at = datetime.now(UTC)
    elif failed_at.tzinfo is None:
        failed_at = failed_at.replace(tzinfo=UTC)

    slug = _slugify(title)
    if not slug:
        slug = f"replay-{int(failed_at.timestamp())}"

    replay = FailureReplay(
        slug=slug,
        title=title,
        failure_kind=failure_kind,
        failed_at=failed_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        prompt=prompt,
        expected=expected,
        actual=actual,
        model=model,
        options=options or {},
        note=note,
    )

    rdir = _replay_dir(replay)
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / "input.json").write_text(
        json.dumps(replay.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (rdir / "expected.txt").write_text(expected, encoding="utf-8")
    (rdir / "actual.txt").write_text(actual, encoding="utf-8")
    return replay


def load_replay(slug: str, *, dated_dir_name: str | None = None) -> FailureReplay:
    """slug → FailureReplay 로드 (가장 최근 우선)."""
    base = resolve_replays_dir()
    if dated_dir_name:
        target = base / dated_dir_name / "input.json"
        if not target.exists():
            raise FileNotFoundError(f"replay 없음: {dated_dir_name}")
        return FailureReplay(**json.loads(target.read_text(encoding="utf-8")))

    # 최신 우선 검색
    matches = sorted(base.glob(f"*-{slug}"), reverse=True)
    if not matches:
        raise FileNotFoundError(f"slug '{slug}' 매칭 replay 없음")
    target = matches[0] / "input.json"
    return FailureReplay(**json.loads(target.read_text(encoding="utf-8")))


def iter_replays(*, since: date | None = None) -> Iterator[FailureReplay]:
    """모든 replay 순회 (since 이후만)."""
    base = resolve_replays_dir()
    if not base.exists():
        return
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        try:
            when = date.fromisoformat(d.name[:10])
        except ValueError:
            continue
        if since and when < since:
            continue
        input_file = d / "input.json"
        if not input_file.exists():
            continue
        try:
            yield FailureReplay(**json.loads(input_file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError):
            continue


def run_regression(replay: FailureReplay, actual_now: str) -> ReplayResult:
    """기대 vs 현재 출력 비교 (V2 §4.3 회귀 검사).

    Args:
        replay: 등록된 실패
        actual_now: 새 모델/프롬프트로 다시 돌려본 결과

    Returns:
        ReplayResult (is_passing = expected와 매칭하면 True)
    """
    # 단순 substring 매칭 (정확한 비교는 도메인별 적용)
    expected_norm = replay.expected.strip()
    actual_norm = actual_now.strip()

    if expected_norm == actual_norm:
        passing = True
        note = "✓ 정확히 일치 = 회귀 X"
        diff = "(no diff)"
    elif expected_norm in actual_norm:
        passing = True
        note = "✓ 기대 substring 포함 = 회귀 X"
        diff = f"+actual은 expected를 포함 (extra {len(actual_norm) - len(expected_norm)} chars)"
    else:
        passing = False
        note = "🔴 회귀 발생 = 실패 재현됨 또는 새로운 차이"
        # 첫 100자 차이 요약
        max_show = 200
        diff = (
            f"-expected (first {max_show}): {expected_norm[:max_show]}\n"
            f"+actual   (first {max_show}): {actual_norm[:max_show]}"
        )

    return ReplayResult(
        replay_slug=replay.slug,
        is_passing=passing,
        actual_output=actual_now,
        diff_summary=diff,
        note=note,
    )
