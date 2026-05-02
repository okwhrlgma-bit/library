"""정확도 측정 — 우리 풀 파이프라인 결과 vs 골든 데이터셋(NL Korea 직답) 필드별 비교.

전제: scripts/build_golden_dataset.py 가 이미 실행돼 tests/samples/golden/ 채움.

흐름:
  golden/{ISBN}.json  ← NL Korea 응답으로 만든 "정답" BookData
  golden/{ISBN}.mrc   ← 그 정답으로 빌드된 KORMARC

  우리 풀 파이프라인 (aggregator → 모든 소스 + AI):
  aggregate_by_isbn(ISBN) + recommend_kdc + builder + 880 → 우리 결과 .mrc

  필드별로 정답과 비교:
    020 ▾a  (ISBN)
    245 ▾a  (본표제)
    100 ▾a  (저자)
    264 ▾b  (출판사)
    056 ▾a  (KDC)
    008 (40자리)

  필드별 일치율 + 종합 정확도 출력.

사용:
    python scripts/accuracy_compare.py
    python scripts/accuracy_compare.py --output reports/accuracy.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from pymarc import MARCReader, Record

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from kormarc_auto.api.aggregator import aggregate_by_isbn  # noqa: E402
from kormarc_auto.classification.kdc_classifier import recommend_kdc  # noqa: E402
from kormarc_auto.kormarc.builder import build_kormarc_record  # noqa: E402
from kormarc_auto.logging_config import setup_logging  # noqa: E402
from kormarc_auto.vernacular.field_880 import add_880_pairs  # noqa: E402

logger = logging.getLogger(__name__)


# 비교할 필드·서브필드 (KORMARC 핵심)
COMPARE_FIELDS = [
    ("020", "a", "ISBN"),
    ("245", "a", "본표제"),
    ("100", "a", "저자"),
    ("264", "b", "출판사"),
    ("056", "a", "KDC"),
]


def _read_record(path: Path) -> Record | None:
    """첫 레코드 읽기 (없거나 깨졌으면 None)."""
    if not path.exists():
        return None
    with path.open("rb") as f:
        reader = MARCReader(f, force_utf8=True)
        for record in reader:
            if record is not None:
                return record
    return None


def _get_subfield(record: Record, tag: str, code: str) -> str | None:
    """첫 발견 서브필드 값."""
    for field in record.get_fields(tag):
        for sf in field.subfields:
            if sf.code == code:
                return sf.value.strip()
    return None


def _normalize(value: str | None) -> str:
    """비교용 정규화 — 공백·구두점 제거, 소문자."""
    if not value:
        return ""
    return "".join(c for c in value.lower() if c.isalnum())


def _match(a: str | None, b: str | None) -> str:
    """일치 판정 — exact / partial / mismatch / both_empty / one_empty."""
    na, nb = _normalize(a), _normalize(b)
    if not na and not nb:
        return "both_empty"
    if not na or not nb:
        return "one_empty"
    if na == nb:
        return "exact"
    if na in nb or nb in na:
        return "partial"
    return "mismatch"


def compare_one(isbn: str, golden_dir: Path) -> dict[str, Any]:
    """단일 ISBN — 골든 vs 우리 결과 비교."""
    golden_mrc = golden_dir / f"{isbn}.mrc"
    golden_record = _read_record(golden_mrc)
    if golden_record is None:
        return {"isbn": isbn, "status": "no_golden"}

    # 우리 풀 파이프라인 (모든 외부 API + AI 후보)
    try:
        book_data = aggregate_by_isbn(isbn)
    except Exception as e:
        return {"isbn": isbn, "status": "aggregate_error", "error": str(e)}

    if not book_data.get("sources"):
        return {"isbn": isbn, "status": "aggregate_empty"}

    candidates = recommend_kdc(book_data)
    if candidates and not book_data.get("kdc"):
        book_data["kdc"] = candidates[0]["code"]

    our_record = build_kormarc_record(book_data)
    add_880_pairs(our_record)

    field_results: dict[str, Any] = {}
    for tag, code, label in COMPARE_FIELDS:
        gv = _get_subfield(golden_record, tag, code)
        ov = _get_subfield(our_record, tag, code)
        field_results[f"{tag}{code}_{label}"] = {
            "golden": gv,
            "ours": ov,
            "match": _match(gv, ov),
        }

    return {
        "isbn": isbn,
        "status": "ok",
        "fields": field_results,
        "our_sources": book_data.get("sources", []),
        "our_confidence": book_data.get("confidence"),
        "kdc_source": candidates[0]["source"] if candidates else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="정확도 측정 — 골든 vs 우리 결과")
    parser.add_argument(
        "--golden",
        type=str,
        default="tests/samples/golden",
        help="골든 데이터 폴더 (기본: tests/samples/golden)",
    )
    parser.add_argument("--output", type=str, default=None, help="결과 JSON 저장 경로")
    parser.add_argument("--limit", type=int, default=0, help="최대 비교 건수")
    args = parser.parse_args()

    load_dotenv()
    setup_logging(level="WARNING")

    golden_dir = ROOT / args.golden
    isbns = [p.stem for p in golden_dir.glob("*.mrc")]
    if not isbns:
        print(f"❌ 골든 .mrc 파일 없음: {golden_dir}")
        print("   먼저 실행: python scripts/build_golden_dataset.py")
        return 1

    if args.limit > 0:
        isbns = isbns[: args.limit]

    print(f"🎯 정확도 측정 — 골든 {len(isbns)}건 vs 풀 파이프라인 결과")
    print("=" * 75)

    results: list[dict[str, Any]] = []
    field_match_counter: Counter[tuple[str, str]] = Counter()  # (label, match_type)

    for i, isbn in enumerate(isbns, 1):
        print(f"[{i:2d}/{len(isbns)}] {isbn} ...", end=" ", flush=True)
        r = compare_one(isbn, golden_dir)
        results.append(r)

        if r["status"] != "ok":
            print(f"❌ {r['status']}")
            continue

        # 케이스별 일치 카운트
        line_summary = []
        for key, fr in r["fields"].items():
            label = key.split("_", 1)[1]
            field_match_counter[(label, fr["match"])] += 1
            mark = {
                "exact": "✓",
                "partial": "≈",
                "mismatch": "✗",
                "both_empty": "·",
                "one_empty": "○",
            }[fr["match"]]
            line_summary.append(f"{label}{mark}")
        print(" ".join(line_summary))

    # 필드별 종합
    print("\n" + "=" * 75)
    print(f"📊 필드별 일치율 (총 {len(isbns)}건)")
    print("-" * 75)
    print(
        f"{'필드':<14} {'exact':>7} {'partial':>9} {'mismatch':>9} {'one_empty':>11} {'both_empty':>11}"
    )
    for _tag, _code, label in COMPARE_FIELDS:
        exact = field_match_counter.get((label, "exact"), 0)
        partial = field_match_counter.get((label, "partial"), 0)
        mismatch = field_match_counter.get((label, "mismatch"), 0)
        one_empty = field_match_counter.get((label, "one_empty"), 0)
        both_empty = field_match_counter.get((label, "both_empty"), 0)
        total_compared = exact + partial + mismatch + one_empty
        accuracy = (exact + partial * 0.5) / total_compared if total_compared else 0
        print(
            f"{label:<14} {exact:>7} {partial:>9} {mismatch:>9} {one_empty:>11} {both_empty:>11}"
            f"   ({accuracy * 100:.0f}%)"
        )

    if args.output:
        out = ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(
                {
                    "summary": {
                        f"{tag}{code}_{label}": {
                            "exact": field_match_counter.get((label, "exact"), 0),
                            "partial": field_match_counter.get((label, "partial"), 0),
                            "mismatch": field_match_counter.get((label, "mismatch"), 0),
                            "one_empty": field_match_counter.get((label, "one_empty"), 0),
                            "both_empty": field_match_counter.get((label, "both_empty"), 0),
                        }
                        for tag, code, label in COMPARE_FIELDS
                    },
                    "results": results,
                    "total_cases": len(isbns),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\n결과 저장: {out.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
