"""Cycle 53 (V3 Block 5·외부 256 출처) — router.py AST 자동 패치 + 백업.

V3 §4.5 정합:
- 카테고리별 BLOCKED 비율 분석 (1주 + 1개월 누적)
- 임계 초과 = "unsafe"·복구 = "auto"·중간 = "human"
- 정규식 X·AST 패치 + 백업 (.py.bak.{timestamp})
- 자동 머지 X·PR 생성만 (V2 §6.1 자기 수정 정합)

활성: audit.jsonl 30일+ 누적 후 (n>=20 per category).
지금은 scaffold·dry-run·--apply 시 PR 브랜치 생성.

실행:
    python automation/router_patcher.py --dry-run    # 권고만
    python automation/router_patcher.py --apply      # PR 브랜치 생성
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Windows cp949 환경 = utf-8 강제 (이모지·한국어 stdout)
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
ROUTER = ROOT / "automation" / "router.py"
AUDIT = ROOT / "audit.jsonl"
DECISIONS = ROOT / "decisions.md"

# V3 §4.5 임계
WINDOW_DAYS = 30
UNSAFE_RATE = 0.40  # 40% BLOCKED = router unsafe 승격
RECOVER_RATE = 0.10  # 10% 미만 + n>=20 = router auto 복귀
MIN_SAMPLES = 20  # 통계 의미 최소


@dataclass(frozen=True)
class CategoryStats:
    category: str
    n: int
    blocked: int
    block_rate: float


@dataclass(frozen=True)
class RouterUpdate:
    category: str
    old_policy: str
    new_policy: str
    stats: CategoryStats
    reason: str


def load_audit_window(days: int = WINDOW_DAYS) -> list[dict]:
    """최근 N일 audit.jsonl·cycle_end 이벤트만."""
    if not AUDIT.exists():
        return []
    cutoff = datetime.now(UTC) - timedelta(days=days)
    rows = []
    with AUDIT.open(encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("event") != "cycle_end":
                continue
            ts_str = r.get("ts", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue
            if ts < cutoff:
                continue
            rows.append(r)
    return rows


def category_block_rates(rows: list[dict]) -> list[CategoryStats]:
    """카테고리별 BLOCKED 비율·MIN_SAMPLES 미달 = 제외."""
    stats: dict[str, list[str]] = {}
    for r in rows:
        cat = r.get("category", "unknown")
        status = r.get("status", "")
        stats.setdefault(cat, []).append(status)

    result = []
    for cat, statuses in stats.items():
        n = len(statuses)
        if n < MIN_SAMPLES:
            continue
        blocked = sum(1 for s in statuses if s == "BLOCKED")
        result.append(
            CategoryStats(
                category=cat,
                n=n,
                blocked=blocked,
                block_rate=blocked / n,
            )
        )
    return sorted(result, key=lambda x: -x.block_rate)


def get_current_policies() -> dict[str, str]:
    """router.py CATEGORY_POLICY dict 추출 (AST·정규식 X)."""
    if not ROUTER.exists():
        return {}
    try:
        src = ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return {}

    policies: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (
                    isinstance(tgt, ast.Name)
                    and tgt.id == "CATEGORY_POLICY"
                    and isinstance(node.value, ast.Dict)
                ):
                    for k, v in zip(node.value.keys, node.value.values, strict=False):
                        if (
                            isinstance(k, ast.Constant)
                            and isinstance(v, ast.Constant)
                            and isinstance(k.value, str)
                            and isinstance(v.value, str)
                        ):
                            policies[k.value] = v.value
    return policies


def compute_updates(stats: list[CategoryStats]) -> list[RouterUpdate]:
    """카테고리 stats → 권고 업데이트 리스트."""
    current = get_current_policies()
    updates = []
    for s in stats:
        old = current.get(s.category, "human")
        new = old
        reason = ""
        if s.block_rate >= UNSAFE_RATE:
            new = "unsafe"
            reason = f"BLOCKED 비율 {s.block_rate:.0%} >= {UNSAFE_RATE:.0%} (n={s.n})"
        elif s.block_rate <= RECOVER_RATE and s.n >= MIN_SAMPLES:
            new = "auto"
            reason = f"BLOCKED 비율 {s.block_rate:.0%} <= {RECOVER_RATE:.0%} (n={s.n})"
        if new != old:
            updates.append(
                RouterUpdate(
                    category=s.category,
                    old_policy=old,
                    new_policy=new,
                    stats=s,
                    reason=reason,
                )
            )
    return updates


def patch_router(updates: list[RouterUpdate]) -> bool:
    """AST 패치·.py.bak.{timestamp} 백업 (V3 §4.5 정합)."""
    if not updates or not ROUTER.exists():
        return False
    src = ROUTER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    update_map = {u.category: u.new_policy for u in updates}
    changed = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (
                    isinstance(tgt, ast.Name)
                    and tgt.id == "CATEGORY_POLICY"
                    and isinstance(node.value, ast.Dict)
                ):
                    for i, k in enumerate(node.value.keys):
                        if isinstance(k, ast.Constant) and k.value in update_map:
                            node.value.values[i] = ast.Constant(value=update_map[k.value])
                            changed = True

    if changed:
        ts = int(datetime.now(UTC).timestamp())
        backup = ROUTER.with_suffix(f".py.bak.{ts}")
        shutil.copy(ROUTER, backup)
        ROUTER.write_text(ast.unparse(tree), encoding="utf-8")
    return changed


def append_decision(updates: list[RouterUpdate]) -> None:
    """decisions.md에 V2 §4.4 표준 형식 append."""
    if not updates:
        return
    today = datetime.now(UTC).date().isoformat()
    lines = [f"\n## {today} — Auto-Router Update (V3 Block 5·Cycle 53)\n"]
    lines.append("**컨텍스트**: 30일 audit.jsonl 통계·BLOCKED 비율 임계 초과/회복")
    lines.append("**선택**:")
    for u in updates:
        lines.append(
            f"- `{u.category}` `{u.old_policy}` → **`{u.new_policy}`** "
            f"(n={u.stats.n}, block_rate={u.stats.block_rate:.1%})"
        )
    lines.append("**대안**: 임계 변경·수동 라우팅·범위 축소")
    lines.append("**이유**: V3 §4.5 30일 데이터 정합·통계 결정적·LLM 호출 0")
    lines.append("**되돌릴 수 있는가**: 가능 (.py.bak 백업·git revert)")
    lines.append("**관련 ADR**: 0042 V3 Block 4·5 통합")
    DECISIONS.write_text(
        DECISIONS.read_text(encoding="utf-8") + "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def create_pr_branch(updates: list[RouterUpdate]) -> str | None:
    """V2 §6.1 정합 = PR 브랜치만 생성·자동 머지 X."""
    if not updates:
        return None
    branch = f"auto/router-patch-{int(datetime.now(UTC).timestamp())}"
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch],
            cwd=ROOT,
            check=True,
            capture_output=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return branch


def main() -> int:
    ap = argparse.ArgumentParser(description="V3 Block 5 router_patcher (Cycle 53 scaffold)")
    ap.add_argument("--dry-run", action="store_true", default=True, help="권고만 (기본)")
    ap.add_argument("--apply", action="store_true", help="실제 패치 + PR 브랜치 생성")
    ap.add_argument("--days", type=int, default=WINDOW_DAYS, help="audit 윈도우 일수")
    args = ap.parse_args()

    rows = load_audit_window(days=args.days)
    if not rows:
        print(
            f"📊 audit.jsonl {args.days}일 데이터 부족·Cycle 43 audit-log.sh hook 활성 후 누적 필요"
        )
        return 0

    stats = category_block_rates(rows)
    if not stats:
        print(f"📊 카테고리당 MIN_SAMPLES={MIN_SAMPLES} 미달·관찰 계속")
        return 0

    print(f"=== {args.days}일 audit 분석 (총 {len(rows)} cycle) ===")
    for s in stats:
        print(f"  {s.category:20s} n={s.n:3d} blocked={s.blocked:3d} rate={s.block_rate:.1%}")

    updates = compute_updates(stats)
    if not updates:
        print("\n✅ 변경 없음 (모든 카테고리 임계 정합)")
        return 0

    print(f"\n=== 권고 업데이트 ({len(updates)}건) ===")
    for u in updates:
        print(f"  {u.category:20s} {u.old_policy} → {u.new_policy}  ({u.reason})")

    if not args.apply:
        print("\n→ --apply 시 .py.bak 백업 + AST 패치 + PR 브랜치 생성·자동 머지 X")
        return 0

    if patch_router(updates):
        append_decision(updates)
        branch = create_pr_branch(updates)
        print(f"\n✓ router.py 패치 완료·decisions.md append·PR 브랜치 = {branch}")
        print("  자동 머지 X = PO 검토 + gh pr create 수동")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
