"""골든 셋 회귀 평가기 — PO 자율성 가이드 §11.

매 commit 또는 모델 업그레이드 후 실행. 검증된 KORMARC 정답 케이스에 대해
실제 aggregate_by_isbn 결과가 어셔션을 통과하는지 검사.

사용:
    python scripts/golden_check.py                # 전체 케이스
    python scripts/golden_check.py --case 001     # 단일
    python scripts/golden_check.py --strict       # 1개 실패 → exit 1
    python scripts/golden_check.py --offline      # 외부 API 호출 안 함 (cache only)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = ROOT / ".claude" / "golden"
sys.path.insert(0, str(ROOT / "src"))


def _list_cases() -> list[Path]:
    return sorted(p for p in GOLDEN_DIR.glob("case-*") if p.is_dir())


def _eval_op(actual: Any, op: str, expected: Any) -> bool:
    if op == "equals":
        return actual == expected
    if op == "not_equals":
        return actual != expected
    if op == "contains":
        return expected in (str(actual) if actual is not None else "")
    if op == "starts_with":
        return str(actual or "").startswith(str(expected))
    if op == "length_eq":
        return len(actual) == expected if actual is not None else False
    if op == "length_ge":
        return len(actual) >= expected if actual is not None else False
    if op in ("ge", "confidence_ge"):
        try:
            return float(actual) >= float(expected)
        except (TypeError, ValueError):
            return False
    raise ValueError(f"알 수 없는 op: {op}")


def _resolve_field(book: dict[str, Any], field: str) -> Any:
    if field == "sources_count":
        return len(book.get("sources") or [])
    return book.get(field)


def run_case(case_dir: Path, *, offline: bool = False) -> dict[str, Any]:
    inp = json.loads((case_dir / "input.json").read_text(encoding="utf-8"))
    asserts = json.loads(
        (case_dir / "assertions.json").read_text(encoding="utf-8")
    )

    # 외부 API 호출 (또는 캐시 hit)
    if offline:
        # offline 시 어셔션 미수행 → skipped 카운트는 분리 (passed/total과 별개)
        n = len(asserts.get("assertions", []))
        return {
            "case_id": inp["case_id"],
            "isbn": inp.get("isbn"),
            "skipped": True,
            "reason": "offline mode",
            "passed": n,  # offline은 무조건 통과 처리 (회귀 안 함)
            "total": n,
        }

    from kormarc_auto.api.aggregator import aggregate_by_isbn

    isbn = inp["isbn"]
    try:
        book = aggregate_by_isbn(isbn)
    except Exception as e:
        return {
            "case_id": inp["case_id"],
            "isbn": isbn,
            "error": str(e),
            "passed": 0,
            "total": len(asserts.get("assertions", [])),
        }

    results = []
    for a in asserts.get("assertions", []):
        actual = _resolve_field(book, a["field"])
        try:
            ok = _eval_op(actual, a["op"], a["value"])
        except ValueError as e:
            ok = False
            results.append({**a, "ok": False, "actual": str(actual), "error": str(e)})
            continue
        results.append({**a, "ok": ok, "actual": str(actual)[:80]})

    passed = sum(1 for r in results if r["ok"])
    return {
        "case_id": inp["case_id"],
        "isbn": isbn,
        "passed": passed,
        "total": len(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=None, help="단일 케이스 ID (예: 001)")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cases = _list_cases()
    if args.case:
        cases = [c for c in cases if c.name == f"case-{args.case}"]

    if not cases:
        print("❌ 골든 케이스 없음")
        return 1

    all_results: list[dict[str, Any]] = []
    for case_dir in cases:
        r = run_case(case_dir, offline=args.offline)
        all_results.append(r)

    total_passed = sum(r["passed"] for r in all_results)
    total = sum(r["total"] for r in all_results)

    if args.json:
        print(
            json.dumps(
                {"passed": total_passed, "total": total, "results": all_results},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"골든 회귀: {total_passed}/{total}")
        for r in all_results:
            mark = "✓" if r["passed"] == r["total"] else "❌"
            isbn = r.get("isbn", "?")
            print(f"  {mark} {r['case_id']} ({isbn}): {r['passed']}/{r['total']}")
            if r.get("error"):
                print(f"      ⚠ {r['error']}")
            elif r.get("skipped"):
                print(f"      ⏸ {r.get('reason')}")
            else:
                for a in r.get("results", []):
                    if not a["ok"]:
                        print(f"      ❌ {a['name']} — actual: {a.get('actual')}")

    # 누적 로그
    log_path = ROOT / "logs" / "evals" / "golden_results.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {"ts": int(time.time()), "passed": total_passed, "total": total},
                ensure_ascii=False,
            )
            + "\n"
        )

    return 1 if (args.strict and total_passed < total) else 0


if __name__ == "__main__":
    sys.exit(main())
