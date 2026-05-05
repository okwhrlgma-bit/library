"""Cycle 24 — 자관 회귀 자동 비교 (영구 invariant 게이트).

실행:
    python scripts/regression_check.py            # 최신 vs baseline (≤ 1pp)
    python scripts/regression_check.py --strict   # exit 1 on regression

원칙 (Plan B §0 자동 머지 게이트 #4):
- baseline = docs/eval/results/2026-05-04/regression_baseline.json (round-trip 100%)
- 회귀 ≤ 1pp = 통과·> 1pp = 즉시 STOP·P0 격상

자관 D:\ 미접근 환경 = SKIPPED·CI 통과 (회귀 게이트는 D:\ 접근 환경에서만).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

# Windows cp949 환경에서 한국어 stdout 깨짐 회피
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = ROOT / "docs" / "eval" / "results"
BASELINE_FILE = EVAL_DIR / "2026-05-04" / "regression_baseline.json"
DATA_DIR = Path(r"D:\내를건너서 숲으로 도서관\수서\2024\2024_마크파일")


def load_baseline() -> dict:
    if not BASELINE_FILE.exists():
        print(f"[ERR] baseline 없음: {BASELINE_FILE}", file=sys.stderr)
        sys.exit(2)
    return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))


def measure_current(sample: int = 200) -> dict | None:
    r"""현재 round-trip 측정. D:\ 미접근 시 None (CI skip)."""
    if not DATA_DIR.exists():
        return None

    try:
        from io import BytesIO

        from pymarc import MARCReader
    except ImportError:
        print("[ERR] pymarc 필요", file=sys.stderr)
        sys.exit(2)

    files = sorted(DATA_DIR.rglob("*.mrc"))
    total = 0
    pass_count = 0
    fail_reasons: dict[str, int] = {}

    for path in files:
        if total >= sample:
            break
        try:
            with path.open("rb") as f:
                reader = MARCReader(f, to_unicode=True, force_utf8=False)
                for rec in reader:
                    if rec is None or total >= sample:
                        continue
                    total += 1
                    try:
                        raw1 = rec.as_marc()
                        re_rec = next(
                            MARCReader(BytesIO(raw1), to_unicode=True, force_utf8=False),
                            None,
                        )
                        if re_rec is not None and re_rec.as_marc() == raw1:
                            pass_count += 1
                        else:
                            fail_reasons["bytes_mismatch"] = (
                                fail_reasons.get("bytes_mismatch", 0) + 1
                            )
                    except Exception as exc:
                        key = f"exception:{type(exc).__name__}"
                        fail_reasons[key] = fail_reasons.get(key, 0) + 1
        except Exception:
            continue

    overall_pct = (pass_count / total * 100) if total else 0
    return {
        "total": total,
        "pass": pass_count,
        "overall_pct": round(overall_pct, 2),
        "fail_reasons": fail_reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="회귀 시 exit 1")
    parser.add_argument("--sample", type=int, default=200)
    parser.add_argument("--threshold-pp", type=float, default=1.0)
    args = parser.parse_args()

    baseline = load_baseline()
    baseline_pct = baseline.get("overall_pct", 100.0)
    threshold = args.threshold_pp

    current = measure_current(sample=args.sample)
    if current is None:
        print(f"[SKIP] D:\\ 미접근·CI 환경 = baseline 비교 생략 (baseline={baseline_pct}%)")
        print(f"baseline: {BASELINE_FILE}")
        return 0

    delta = current["overall_pct"] - baseline_pct
    print(
        f"[CURRENT] {current['pass']}/{current['total']} = "
        f"{current['overall_pct']:.2f}% (baseline {baseline_pct:.2f}%·Δ {delta:+.2f}pp)"
    )
    if current["fail_reasons"]:
        print(f"[FAIL] {current['fail_reasons']}")

    if delta < -threshold:
        print(
            f"⛔ REGRESSION = {-delta:.2f}pp 하락 (임계 {threshold}pp 초과)·P0 격상·자율 사이클 STOP",
            file=sys.stderr,
        )
        return 1 if args.strict else 0

    print(f"✓ 회귀 게이트 통과 (Δ {delta:+.2f}pp ≤ {threshold}pp)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
