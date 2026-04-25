"""실제 도서관 신착 .xlsx 분석 → 골든 데이터셋 후보 + KDC 분포.

PO 자료 폴더의 신착 .xlsx (예: 240701~240731 배가된 신착 도서 목록)를
스캔해 ISBN 후보 추출·KDC 분포 시각화.

사용:
    python scripts/analyze_real_acquisitions.py path/to/신착.xlsx
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent


def analyze(xlsx_path: Path) -> dict[str, Any]:
    """신착 .xlsx → 통계 dict."""
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 3:
        return {"error": "행 수 부족"}

    # 헤더 위치 추정 (등록번호·청구기호 키워드)
    header_idx = 0
    for i, r in enumerate(rows[:5]):
        if r and any("등록" in str(c) or "청구" in str(c) for c in r if c):
            header_idx = i
            break

    data_rows = rows[header_idx + 1 :]
    total = sum(1 for r in data_rows if r and any(c is not None for c in r))

    # 청구기호에서 KDC 분포
    kdc_dist: dict[str, int] = {}
    publishers: Counter[str] = Counter()
    titles: list[str] = []
    for r in data_rows:
        if not r:
            continue
        # 청구기호는 보통 4번째 필드
        for cell in r:
            s = str(cell or "")
            if "-" in s and any(s[:1].isdigit() for c in s) and len(s) < 20:
                kdc_part = s.split("-")[0].strip()
                if kdc_part[:1].isdigit():
                    main = kdc_part[:1] + "00"
                    kdc_dist[main] = kdc_dist.get(main, 0) + 1
                    break
        # 출판사·표제 후보
        non_empty = [str(c) for c in r if c is not None and str(c).strip()]
        if len(non_empty) >= 5:
            publishers[non_empty[-2][:30]] = publishers.get(non_empty[-2][:30], 0) + 1
            titles.append(non_empty[-4][:60])

    return {
        "file": str(xlsx_path.name),
        "total_records": total,
        "kdc_main_distribution": dict(sorted(kdc_dist.items())),
        "top_publishers": publishers.most_common(10),
        "sample_titles": titles[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="실 도서관 신착 .xlsx 분석")
    parser.add_argument("xlsx", help=".xlsx 파일 경로")
    parser.add_argument("--output", default=None, help="결과 JSON 저장")
    args = parser.parse_args()

    p = Path(args.xlsx)
    if not p.exists():
        print(f"❌ 파일 없음: {p}")
        return 1

    print(f"📚 분석: {p.name}")
    result = analyze(p)
    print()
    print(f"총 레코드: {result.get('total_records', 0)}")
    print()
    print("KDC 주류 분포:")
    for k, v in result.get("kdc_main_distribution", {}).items():
        print(f"  {k}: {v}")
    print()
    print("출판사 TOP 10:")
    for pub, cnt in result.get("top_publishers", []):
        print(f"  {cnt:3d}  {pub}")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n결과 저장: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
