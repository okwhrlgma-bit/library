"""정확도 자체 검증 스크립트 — 알려진 ISBN 5건으로 회귀 측정.

사용:
    python scripts/accuracy_check.py
    python scripts/accuracy_check.py --output reports/accuracy_2026-04-25.json

기대 결과:
- 외부 API에서 표제·저자가 정상 반환되는가
- KDC가 부여되거나 AI 후보가 나오는가
- KORMARC 빌드·검증 통과하는가
- .mrc 파일이 정상 생성되는가
- KOLAS 사전 검증 ERRORS=0 인가

PO·사서가 "이거 진짜 되는 건가?" 의심할 때 답변 가능하게 만든 도구.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.api.aggregator import aggregate_by_isbn  # noqa: E402
from kormarc_auto.classification.kdc_classifier import recommend_kdc  # noqa: E402
from kormarc_auto.classification.subject_recommender import recommend_subjects  # noqa: E402
from kormarc_auto.kormarc.builder import build_kormarc_record  # noqa: E402
from kormarc_auto.kormarc.kolas_validator import kolas_strict_validate  # noqa: E402
from kormarc_auto.kormarc.validator import validate_record  # noqa: E402
from kormarc_auto.logging_config import setup_logging  # noqa: E402
from kormarc_auto.output.kolas_writer import write_kolas_mrc  # noqa: E402
from kormarc_auto.vernacular.field_880 import add_880_pairs  # noqa: E402

logger = logging.getLogger(__name__)


# 검증용 ISBN 5건 — 한국 자료, 다양한 분류
TEST_ISBNS = [
    {"isbn": "9788936434120", "expected_title_contains": "작별", "expected_kdc_prefix": "81"},
    {"isbn": "9788932020789", "expected_title_contains": "작별", "expected_kdc_prefix": "81"},
    {"isbn": "9788937834790", "expected_title_contains": "28", "expected_kdc_prefix": "81"},
    {"isbn": "9788954692410", "expected_title_contains": None, "expected_kdc_prefix": None},
    {"isbn": "9788972752310", "expected_title_contains": None, "expected_kdc_prefix": None},
]


def run_one(isbn: str, *, expected_title_contains: str | None, expected_kdc_prefix: str | None) -> dict[str, Any]:
    """단일 ISBN 회귀 — 메타·KDC·KORMARC·검증·.mrc 모두 체크."""
    started = time.time()
    result: dict[str, Any] = {
        "isbn": isbn,
        "expected_title_contains": expected_title_contains,
        "expected_kdc_prefix": expected_kdc_prefix,
        "checks": {},
    }

    try:
        book_data = aggregate_by_isbn(isbn)
    except Exception as e:
        result["error"] = f"aggregate failed: {e}"
        result["elapsed_ms"] = int((time.time() - started) * 1000)
        return result

    sources = book_data.get("sources", [])
    title = book_data.get("title")
    result["checks"]["external_api_returned"] = bool(sources)
    result["checks"]["title_present"] = bool(title)
    result["title"] = title
    result["sources"] = sources
    result["confidence"] = book_data.get("confidence")

    if expected_title_contains and title:
        result["checks"]["title_matches_expectation"] = expected_title_contains in title

    candidates = recommend_kdc(book_data)
    if candidates:
        top = candidates[0]
        result["kdc"] = top["code"]
        result["kdc_source"] = top["source"]
        result["checks"]["kdc_present"] = True
        if expected_kdc_prefix:
            result["checks"]["kdc_matches_expectation"] = top["code"].startswith(expected_kdc_prefix)
        if not book_data.get("kdc"):
            book_data["kdc"] = top["code"]

    subjects = recommend_subjects(book_data)
    result["subject_count"] = len(subjects)

    record = build_kormarc_record(book_data)
    add_880_pairs(record)
    basic_errors = validate_record(record)
    strict = kolas_strict_validate(record)
    result["checks"]["build_ok"] = bool(record.fields)
    result["field_count"] = len(record.fields)
    result["basic_validation_errors"] = basic_errors
    result["kolas_strict"] = {
        "ok": strict["ok"],
        "errors": strict["errors"],
        "warnings_count": len(strict["warnings"]),
    }
    result["checks"]["kolas_strict_ok"] = strict["ok"]

    out_dir = Path(os.getenv("ACCURACY_OUTPUT_DIR", ".cache/kormarc-auto/accuracy"))
    try:
        path = write_kolas_mrc(record, isbn, output_dir=str(out_dir))
        result["checks"]["mrc_written"] = path.exists() and path.stat().st_size > 100
        result["mrc_size_bytes"] = path.stat().st_size if path.exists() else 0
    except Exception as e:
        result["checks"]["mrc_written"] = False
        result["mrc_error"] = str(e)

    result["elapsed_ms"] = int((time.time() - started) * 1000)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="kormarc-auto 정확도 자체 검증")
    parser.add_argument("--output", default=None, help="결과 JSON 저장 경로 (옵션)")
    args = parser.parse_args()

    setup_logging(level="WARNING")  # 로그 노이즈 줄임

    print("kormarc-auto 정확도 회귀 — 5건 ISBN")
    print("=" * 60)

    summary: list[dict[str, Any]] = []
    pass_count = 0
    total_checks = 0
    passed_checks = 0

    for case in TEST_ISBNS:
        print(f"\n[{case['isbn']}] 처리...")
        result = run_one(
            case["isbn"],
            expected_title_contains=case.get("expected_title_contains"),
            expected_kdc_prefix=case.get("expected_kdc_prefix"),
        )
        summary.append(result)

        if "error" in result:
            print(f"  ❌ {result['error']}")
            continue

        checks = result["checks"]
        total_checks += len(checks)
        case_passed = sum(1 for v in checks.values() if v)
        passed_checks += case_passed

        status = "✓" if all(checks.values()) else "⚠"
        if all(checks.values()):
            pass_count += 1
        print(
            f"  {status} {result.get('title', '?')[:40]} | "
            f"KDC={result.get('kdc', '-')} ({result.get('kdc_source', '-')}) | "
            f"필드 {result.get('field_count', 0)} | "
            f"{result.get('elapsed_ms', 0)}ms | "
            f"{case_passed}/{len(checks)} 체크 통과"
        )
        if not all(checks.values()):
            failed = [k for k, v in checks.items() if not v]
            print(f"      실패: {', '.join(failed)}")

    print("\n" + "=" * 60)
    print(f"종합: {pass_count}/{len(TEST_ISBNS)} 케이스 전체 통과")
    print(f"체크: {passed_checks}/{total_checks} 통과 ({passed_checks/max(total_checks,1)*100:.0f}%)")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "summary": {
                        "case_pass_rate": pass_count / len(TEST_ISBNS),
                        "check_pass_rate": passed_checks / max(total_checks, 1),
                        "total_cases": len(TEST_ISBNS),
                        "total_checks": total_checks,
                    },
                    "results": summary,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\n결과 저장: {out_path}")

    return 0 if pass_count == len(TEST_ISBNS) else 1


if __name__ == "__main__":
    sys.exit(main())
