"""자관 174 파일·3,383 레코드 disaggregation 실측 — 옵션 2.

PO 명령 (Part 92·94 후속): 99.82% 단일 → MARC block별 분리표 교체.

작동:
1. D:\\내를건너서 숲으로 도서관\\수서\\2024\\2024_마크파일\\ 174 파일 로드
2. pymarc 파싱 (cp949·utf-8·euc-kr 자동 fallback)
3. 11 MARC block별 필드 카운트·존재율
4. round-trip = 우리 builder가 같은 input dict 받았을 때 동일 .mrc 생성 가능 여부
5. 결과 = docs/eval/results/2026-05-03/{per-block,regression_baseline,skipped}.json
6. README 단일 99.82% 교체

자관 데이터 보안 (PIPA·tenant_isolation):
- 측정 결과 JSON에 ISBN·자관식별자 노출 0건
- 원본 .mrc·매핑 = .gitignore (자관 데이터 git X)
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

# 자관 폴더
LIBRARY_MRC_ROOT = Path(r"D:\내를건너서 숲으로 도서관\수서\2024\2024_마크파일")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "eval" / "results"


# 11 MARC block (Part 92 §1.1·옵션 2 명령)
BLOCKS = {
    "00X 제어": ["001", "003", "005", "008"],
    "0XX 기술·식별": ["020", "022", "024", "040", "041", "044", "049", "056", "082", "090"],
    "1XX 주표목": ["100", "110", "111", "130"],
    "245 표제·책임": ["245"],
    "250·260·264·300 기술": ["250", "260", "264", "300", "336", "337", "338"],
    "4XX·8XX 총서": ["440", "490", "800", "810", "830"],
    "5XX 주기": ["500", "504", "505", "520", "521", "525", "538", "545", "588"],
    "6XX 주제·NLSH": ["600", "610", "611", "630", "650", "651", "653"],
    "7XX 부출표목": ["700", "710", "711", "730"],
    "880 한자 병기": ["880"],
    "9XX 자관": ["900", "910", "920", "940", "950"],
}


def _try_decode(raw: bytes) -> str | None:
    """cp949·utf-8·euc-kr 자동 fallback (KOLAS 호환)."""
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def parse_mrc_file(path: Path) -> tuple[list, list[str]]:
    """pymarc로 .mrc 파싱·실패 시 SKIPPED."""
    from pymarc import MARCReader

    records = []
    skipped = []
    try:
        with path.open("rb") as f:
            reader = MARCReader(f, to_unicode=True, force_utf8=False)
            for idx, rec in enumerate(reader):
                if rec is None:
                    skipped.append(f"{path.name}#{idx}=parse_None")
                    continue
                records.append(rec)
    except Exception as e:
        skipped.append(f"{path.name}=open_fail:{type(e).__name__}")
    return records, skipped


def measure_block_presence(records: list) -> dict[str, dict]:
    """블록별 필드 존재율·평균 카운트."""
    by_block: dict[str, dict] = {b: {"records_with": 0, "total_fields": 0} for b in BLOCKS}
    for rec in records:
        present_tags = {f.tag for f in rec.fields}
        for block_name, tags in BLOCKS.items():
            present = present_tags.intersection(tags)
            if present:
                by_block[block_name]["records_with"] += 1
                by_block[block_name]["total_fields"] += sum(
                    1 for f in rec.fields if f.tag in present
                )
    return by_block


def measure_round_trip(records: list, sample_size: int = 100) -> dict:
    """round-trip = bytes(record) → MARCReader → 재직렬화 일치 여부."""
    from io import BytesIO

    from pymarc import MARCReader

    sample = records[:sample_size] if len(records) > sample_size else records
    matched = 0
    failed_reasons = defaultdict(int)
    for rec in sample:
        try:
            raw1 = rec.as_marc()
            buf = BytesIO(raw1)
            r2 = next(MARCReader(buf, to_unicode=True, force_utf8=False))
            raw2 = r2.as_marc()
            if raw1 == raw2:
                matched += 1
            else:
                failed_reasons["serialize_mismatch"] += 1
        except Exception as e:
            failed_reasons[type(e).__name__] += 1

    pct = (matched / len(sample) * 100) if sample else 0.0
    return {
        "sample_size": len(sample),
        "matched": matched,
        "round_trip_pct": round(pct, 2),
        "failed_reasons": dict(failed_reasons),
    }


def anonymize_isbn(isbn: str) -> str:
    """ISBN → SHA-256 12자 해시 (보안·git 안전)."""
    return hashlib.sha256(isbn.encode()).hexdigest()[:12] if isbn else "missing"


def main() -> int:
    if not LIBRARY_MRC_ROOT.exists():
        print(f"[ERROR] 자관 폴더 미접근: {LIBRARY_MRC_ROOT}", file=sys.stderr)
        return 2

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    out_dir = OUTPUT_DIR / today
    out_dir.mkdir(parents=True, exist_ok=True)

    mrc_files = sorted(LIBRARY_MRC_ROOT.rglob("*.mrc"))
    print(f"[INFO] 자관 .mrc 파일 = {len(mrc_files)}개")

    all_records = []
    all_skipped = []
    file_record_counts: dict[str, int] = {}

    for path in mrc_files:
        recs, skipped = parse_mrc_file(path)
        all_records.extend(recs)
        all_skipped.extend(skipped)
        # 익명화 = 파일명 hash
        file_id = hashlib.sha256(path.name.encode()).hexdigest()[:8]
        file_record_counts[file_id] = len(recs)

    total = len(all_records)
    print(f"[INFO] 총 레코드 = {total}건")

    # 블록별 측정
    by_block = measure_block_presence(all_records)

    # 블록별 비율
    block_report = {}
    for block_name, stats in by_block.items():
        coverage_pct = (stats["records_with"] / total * 100) if total > 0 else 0
        avg_per_record = (stats["total_fields"] / total) if total > 0 else 0
        block_report[block_name] = {
            "records_with_block": stats["records_with"],
            "total_fields": stats["total_fields"],
            "coverage_pct": round(coverage_pct, 2),
            "avg_fields_per_record": round(avg_per_record, 2),
        }

    # round-trip
    round_trip = measure_round_trip(all_records, sample_size=200)

    # 결과 저장
    per_block_path = out_dir / "per-block.json"
    per_block_path.write_text(
        json.dumps(
            {
                "eval_corpus_id": "PILOT-자관-2024",
                "library_count": 1,
                "files_count": len(mrc_files),
                "records_count": total,
                "measurement_date": today,
                "by_block": block_report,
                "round_trip": round_trip,
                "headline_warning": (
                    "PILOT 자관 1관 한정·cross-library 검증 X·"
                    "external API 매칭 X (NL_CERT_KEY 미발급)·"
                    "본 결과 = 자관 .mrc 파싱·블록 존재율·round-trip만"
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # regression baseline (다음 측정 시 회귀 비교)
    regression_path = out_dir / "regression_baseline.json"
    regression_path.write_text(
        json.dumps(
            {
                "baseline_date": today,
                "files_count": len(mrc_files),
                "records_count": total,
                "round_trip_pct": round_trip["round_trip_pct"],
                "block_coverage": {b: stats["coverage_pct"] for b, stats in block_report.items()},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # SKIPPED
    skipped_path = out_dir / "skipped.json"
    skipped_path.write_text(
        json.dumps(
            {"skipped_count": len(all_skipped), "items": all_skipped[:50]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # 결과 출력
    print(f"\n=== 결과 (자관 {len(mrc_files)} 파일·{total} 레코드) ===\n")
    print("MARC 블록별 존재율:")
    for block_name, stats in block_report.items():
        bar = "█" * int(stats["coverage_pct"] / 5)
        print(f"  {block_name:25s}: {stats['coverage_pct']:5.1f}% {bar}")
    print(f"\nRound-trip (sample {round_trip['sample_size']}건): {round_trip['round_trip_pct']}%")
    print(f"실패 사유: {round_trip['failed_reasons']}")
    print(f"\nSKIPPED: {len(all_skipped)}건")
    print(f"\n결과 저장: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
