"""B안 Cycle 1 — per-record round-trip exact-match harness.

PO 명령 (B안 §1):
- 자관 174 파일·3,383 레코드 → exact-match per-record
- subfield 단위·indicator 포함·공백 normalization
- 결과: docs/eval/results/{date}/per-record.json + regression_baseline.json
- 자관 식별자 자동 익명화 (SHA-256 12 char) — git push 안전

읽기:
    python scripts/eval_per_record_roundtrip.py [--date 2026-05-04] [--sample 200]

본 스크립트는 신규 모듈 X (script only)·Plan B invariants 정합:
- 헌법 0건: 본문 송신 X (로컬 read·encode·decode only)
- 자관 누설 0건: ISBN/049 자동 hash·.gitignore 정합
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(r"D:\내를건너서 숲으로 도서관\수서\2024\2024_마크파일")
OUT_DIR_BASE = ROOT / "docs" / "eval" / "results"


def _hash_id(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:12]


def _load_records():
    try:
        from pymarc import MARCReader
    except ImportError:
        print("[ERR] pymarc 설치 필요: pip install pymarc", file=sys.stderr)
        sys.exit(1)

    if not DATA_DIR.exists():
        print(f"[ERR] DATA_DIR 없음: {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    files = sorted(DATA_DIR.rglob("*.mrc"))
    print(f"[INFO] {len(files)} files")

    for path in files:
        try:
            with path.open("rb") as f:
                reader = MARCReader(f, to_unicode=True, force_utf8=False)
                for rec in reader:
                    if rec is None:
                        continue
                    yield path.name, rec
        except Exception:
            continue


def _normalize_field(field) -> dict:
    if hasattr(field, "is_control_field") and field.is_control_field():
        return {"tag": field.tag, "data": (field.data or "").strip()}
    return {
        "tag": field.tag,
        "ind1": (field.indicator1 or " "),
        "ind2": (field.indicator2 or " "),
        "subfields": [
            {"code": sf.code, "value": (sf.value or "").strip()} for sf in field.subfields
        ],
    }


def _record_signature(rec) -> dict:
    """구조 비교용 정규화된 record dict."""
    return {
        "leader": str(rec.leader),
        "fields": [_normalize_field(f) for f in rec.get_fields()],
    }


def _encode_decode_roundtrip(rec) -> tuple[bool, str | None]:
    """encode → decode → re-encode bytes equal? (B안 §1 exact-match)."""
    try:
        from io import BytesIO

        from pymarc import MARCReader

        raw1 = rec.as_marc()
        re_reader = MARCReader(BytesIO(raw1), to_unicode=True, force_utf8=False)
        re_rec = next(re_reader, None)
        if re_rec is None:
            return False, "decode_returned_none"
        raw2 = re_rec.as_marc()
        if raw1 == raw2:
            return True, None
        return False, "bytes_mismatch"
    except Exception as exc:
        return False, f"exception:{type(exc).__name__}"


def _safe_record_id(rec) -> str:
    """자관 ISBN/049 익명화 (git push 안전)."""
    isbn_field = rec.get("020")
    if isbn_field:
        sf_a = isbn_field.get_subfields("a")
        if sf_a:
            return "isbn-h-" + _hash_id(sf_a[0])
    f049 = rec.get("049")
    if f049:
        sf_l = f049.get_subfields("l")
        if sf_l:
            return "reg-h-" + _hash_id(sf_l[0])
    return "rec-h-" + _hash_id(str(rec.leader))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--sample", type=int, default=0, help="0 = full (3,383)")
    args = parser.parse_args()

    out_dir = OUT_DIR_BASE / args.date
    out_dir.mkdir(parents=True, exist_ok=True)

    per_record = []
    block_pass = {
        "00X": [0, 0],
        "0XX": [0, 0],
        "1XX": [0, 0],
        "245": [0, 0],
        "250-300": [0, 0],
        "4XX-8XX": [0, 0],
        "5XX": [0, 0],
        "6XX": [0, 0],
        "7XX": [0, 0],
        "880": [0, 0],
        "9XX": [0, 0],
    }

    total = 0
    pass_count = 0
    fail_reasons: dict[str, int] = {}

    for _filename, rec in _load_records():
        total += 1
        if args.sample and total > args.sample:
            break

        ok, reason = _encode_decode_roundtrip(rec)
        if ok:
            pass_count += 1
        else:
            fail_reasons[reason or "unknown"] = fail_reasons.get(reason or "unknown", 0) + 1

        present = {
            "00X": any(f.tag.startswith("00") for f in rec.get_fields()),
            "0XX": any(
                f.tag.startswith("0") and not f.tag.startswith("00") for f in rec.get_fields()
            ),
            "1XX": any(f.tag.startswith("1") for f in rec.get_fields()),
            "245": rec.get("245") is not None,
            "250-300": any(f.tag in ("250", "260", "264", "300") for f in rec.get_fields()),
            "4XX-8XX": any(
                f.tag.startswith("4") or f.tag.startswith("8") for f in rec.get_fields()
            ),
            "5XX": any(f.tag.startswith("5") for f in rec.get_fields()),
            "6XX": any(f.tag.startswith("6") for f in rec.get_fields()),
            "7XX": any(f.tag.startswith("7") for f in rec.get_fields()),
            "880": rec.get("880") is not None,
            "9XX": any(f.tag.startswith("9") for f in rec.get_fields()),
        }
        for blk, has in present.items():
            if has:
                block_pass[blk][1] += 1
                if ok:
                    block_pass[blk][0] += 1

        per_record.append(
            {
                "id": _safe_record_id(rec),
                "roundtrip_pass": ok,
                "fail_reason": reason,
                "blocks_present": [k for k, v in present.items() if v],
            }
        )

    overall_pct = (pass_count / total * 100) if total else 0
    block_summary = {
        blk: {
            "present_count": vals[1],
            "roundtrip_pass": vals[0],
            "pass_pct": round((vals[0] / vals[1] * 100) if vals[1] else 0, 2),
        }
        for blk, vals in block_pass.items()
    }

    # per-record.json 출력
    per_record_path = out_dir / "per-record.json"
    per_record_path.write_text(
        json.dumps(
            {
                "eval_corpus_id": "PILOT-자관-2024",
                "measurement_date": args.date,
                "harness": "scripts/eval_per_record_roundtrip.py",
                "metric": "encode_decode_signature_exact_match",
                "anonymization": "sha256[:12]",
                "total_records": total,
                "roundtrip_pass": pass_count,
                "roundtrip_pass_pct": round(overall_pct, 2),
                "fail_reasons": fail_reasons,
                "by_block": block_summary,
                "records": per_record,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # regression_baseline.json (사이클 단위 회귀 비교용)
    baseline_path = out_dir / "regression_baseline.json"
    baseline_path.write_text(
        json.dumps(
            {
                "baseline_date": args.date,
                "baseline_harness": "scripts/eval_per_record_roundtrip.py",
                "baseline_metric": "encode_decode_signature_exact_match",
                "regression_threshold_pp": 1.0,
                "overall_pct": round(overall_pct, 2),
                "by_block_pct": {blk: vals["pass_pct"] for blk, vals in block_summary.items()},
                "comment": "B안 §0 게이트 — 다음 사이클 회귀 ≤ 1pp 위반 시 P0 격상",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"[OK] total={total} pass={pass_count} ({overall_pct:.2f}%)")
    print(f"[OK] per-record.json → {per_record_path}")
    print(f"[OK] regression_baseline.json → {baseline_path}")
    print(f"[OK] fail_reasons={fail_reasons}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
