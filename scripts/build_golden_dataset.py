"""골든 데이터셋 자동 수집 — 국립중앙도서관/KOLIS-NET 응답을 정답 KORMARC로 저장.

PO 통찰: 정답은 국립중앙도서관·각 도서관 검색 결과가 곧 사서들이 검증한 것.

사용:
    python scripts/build_golden_dataset.py             # 기본 시드 ISBN 50건
    python scripts/build_golden_dataset.py --isbns my_list.txt
    python scripts/build_golden_dataset.py --output tests/samples/golden

저장:
    tests/samples/golden/{ISBN}.mrc          # KORMARC binary
    tests/samples/golden/{ISBN}.json         # 정규화된 BookData 원본
    tests/samples/golden/_index.csv          # 수집 결과 요약

NL Korea API 키(NL_CERT_KEY)가 필요합니다.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from kormarc_auto.api import nl_korea  # noqa: E402
from kormarc_auto.api.kolisnet_compare import (  # noqa: E402
    fetch_other_libraries,
    summarize_classification,
)
from kormarc_auto.kormarc.builder import build_kormarc_record  # noqa: E402
from kormarc_auto.kormarc.kolas_validator import kolas_strict_validate  # noqa: E402
from kormarc_auto.kormarc.validator import validate_record  # noqa: E402
from kormarc_auto.logging_config import setup_logging  # noqa: E402
from kormarc_auto.output.kolas_writer import write_kolas_mrc  # noqa: E402
from kormarc_auto.vernacular.field_880 import add_880_pairs  # noqa: E402

logger = logging.getLogger(__name__)


# 다양한 KDC 분포 시드 ISBN 50건 (한국 주요 출판사·다 분야)
# 실제 수집 시 NL Korea가 응답하지 않으면 자동 스킵
SEED_ISBNS = [
    # 800 한국문학 (소설)
    "9788936434120",  # 한강, 작별하지 않는다
    "9788932020789",  # 김영하, 작별인사
    "9788937834790",  # 정유정, 28
    "9788954692410",
    "9788954645003",
    "9788954656405",
    "9788932473673",
    "9788937462788",
    # 320 경제·경영
    "9791186560977",
    "9788934942467",
    "9788970127194",
    "9791160506235",
    # 100 철학
    "9788937462252",
    "9788932466682",
    "9788932474236",
    # 230 기독교 / 220 불교
    "9788958101888",
    "9788960517813",
    # 370 교육
    "9791160682526",
    "9788983956347",
    # 400 자연과학
    "9788960863125",
    "9788984524873",
    "9791185402116",
    # 500 기술과학
    "9791185751870",
    "9788970887944",
    "9788960777859",
    # 600 예술
    "9788937836404",
    "9788970127545",
    # 700 언어
    "9791160506631",
    "9788983955784",
    # 911 한국사
    "9788970698434",
    "9788984318892",
    "9788937835971",
    # 813 아동·청소년 (부가기호 7)
    "9788958365211",
    "9788972876236",
    "9788963170091",
    "9788989654346",
    # 020 문헌정보학 (사서 본업)
    "9788957333020",
    "9788960512924",
    # 잡종 — 자비출판/소형 (NL 응답 없을 가능성 — 스킵 정상)
    "9788998374010",
    "9791186650998",
    "9791155424827",
    # 시집·수필 (811·814)
    "9788932020277",
    "9788954650595",
    "9788932020796",
    "9788937473661",
    # 추가 일반 서적
    "9788936472047",
    "9788937479359",
    "9788932025902",
    "9788970125985",
    "9788960517431",
    "9788983716576",
]


def collect_one(isbn: str, *, output_dir: Path) -> dict[str, Any]:
    """ISBN 한 건 → NL Korea + KOLIS-NET 정답 수집·저장.

    Returns:
        결과 dict (ok/skip/error 상태 + 메타)
    """
    started = time.time()
    record_summary: dict[str, Any] = {"isbn": isbn, "elapsed_ms": 0}

    try:
        nl_data = nl_korea.fetch_by_isbn(isbn)
    except nl_korea.NLKoreaAPIError as e:
        record_summary["status"] = "nl_error"
        record_summary["error"] = str(e)
        record_summary["elapsed_ms"] = int((time.time() - started) * 1000)
        return record_summary

    if not nl_data:
        record_summary["status"] = "not_found"
        record_summary["elapsed_ms"] = int((time.time() - started) * 1000)
        return record_summary

    # NL Korea 정답 데이터 → KORMARC 빌드
    book_data = dict(nl_data)
    book_data["isbn"] = isbn
    book_data["sources"] = ["nl_korea"]
    book_data["source_map"] = {k: "nl_korea" for k in nl_data}
    book_data["confidence"] = nl_data.get("confidence", 0.95)
    book_data["attributions"] = [nl_data["attribution"]] if nl_data.get("attribution") else []

    # KOLIS-NET에서 다른 도서관 분류 비교 (선택적, 실패해도 계속)
    try:
        peers = fetch_other_libraries(isbn, limit=10)
        if peers:
            summary = summarize_classification(peers)
            record_summary["peer_libraries"] = summary["total_libraries"]
            record_summary["peer_kdc_top"] = summary.get("most_common_kdc")
    except Exception as e:
        logger.debug("KOLIS-NET %s 실패 (계속): %s", isbn, e)

    record = build_kormarc_record(book_data)
    add_880_pairs(record)

    basic_errors = validate_record(record)
    strict = kolas_strict_validate(record)
    record_summary["validation_errors"] = len(basic_errors)
    record_summary["kolas_strict_ok"] = strict["ok"]
    record_summary["kolas_strict_errors"] = len(strict["errors"])
    record_summary["kolas_strict_warnings"] = len(strict["warnings"])

    # .mrc 저장
    mrc_path = write_kolas_mrc(record, isbn, output_dir=str(output_dir))
    record_summary["mrc_path"] = str(mrc_path.relative_to(ROOT))
    record_summary["mrc_size_bytes"] = mrc_path.stat().st_size

    # 정규화된 BookData 원본 (raw 제외 — 너무 큼)
    json_path = output_dir / f"{isbn}.json"
    payload = {k: v for k, v in book_data.items() if k != "raw"}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    record_summary["json_path"] = str(json_path.relative_to(ROOT))

    record_summary["title"] = nl_data.get("title")
    record_summary["author"] = nl_data.get("author")
    record_summary["kdc"] = nl_data.get("kdc")
    record_summary["status"] = "ok"
    record_summary["elapsed_ms"] = int((time.time() - started) * 1000)
    return record_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="골든 데이터셋 자동 수집")
    parser.add_argument(
        "--isbns",
        type=str,
        default=None,
        help="ISBN 목록 텍스트 파일 (한 줄에 하나, # 주석). 미지정 시 SEED 50건 사용",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tests/samples/golden",
        help="저장 폴더 (기본 tests/samples/golden)",
    )
    parser.add_argument("--limit", type=int, default=0, help="최대 수집 개수 (0=무제한)")
    args = parser.parse_args()

    load_dotenv()
    setup_logging(level="WARNING")

    if args.isbns:
        isbns = [
            line.strip().replace("-", "")
            for line in Path(args.isbns).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    else:
        isbns = SEED_ISBNS

    if args.limit > 0:
        isbns = isbns[: args.limit]

    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)

    print(f"📚 골든 데이터셋 수집 — 대상 {len(isbns)}건 → {out.relative_to(ROOT)}")
    print("   소스: 국립중앙도서관 (정답) + KOLIS-NET 비교")
    print("=" * 70)

    results: list[dict[str, Any]] = []
    for i, isbn in enumerate(isbns, 1):
        print(f"[{i:2d}/{len(isbns)}] {isbn} ...", end=" ", flush=True)
        result = collect_one(isbn, output_dir=out)
        results.append(result)

        status = result.get("status")
        if status == "ok":
            print(
                f"✓ {(result.get('title') or '?')[:30]} | "
                f"KDC {result.get('kdc') or '-'} | "
                f"{result.get('mrc_size_bytes', 0)} bytes | "
                f"{result.get('elapsed_ms', 0)}ms"
            )
        elif status == "not_found":
            print("⊝ 미등록 (스킵)")
        else:
            print(f"❌ {status}: {result.get('error', '')[:40]}")

    # 인덱스 CSV 저장
    index_path = out / "_index.csv"
    if results:
        with index_path.open("w", encoding="utf-8-sig", newline="") as f:
            fields = [
                "isbn", "status", "title", "author", "kdc",
                "validation_errors", "kolas_strict_ok",
                "kolas_strict_errors", "kolas_strict_warnings",
                "peer_libraries", "peer_kdc_top",
                "mrc_path", "json_path", "mrc_size_bytes", "elapsed_ms", "error",
            ]
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)

    ok = sum(1 for r in results if r.get("status") == "ok")
    not_found = sum(1 for r in results if r.get("status") == "not_found")
    errors = len(results) - ok - not_found

    print("=" * 70)
    print(f"📊 종합: {ok} 성공 / {not_found} 미등록 / {errors} 오류")
    print(f"   → 인덱스: {index_path.relative_to(ROOT)}")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
