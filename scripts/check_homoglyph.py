"""KORMARC 사칭 감사 CLI (Cycle 518·#15 V01·founder fit ★★★).

사서 친화 출력·`.mrc` JSON·dict CLI 모두 호환.

Usage:
    python scripts/check_homoglyph.py "245=홍길동전" "100=허균"
    python scripts/check_homoglyph.py --json record.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kormarc_auto.text import build_homoglyph_sanity_report_kr  # noqa: E402


def parse_kv_args(args: list[str]) -> dict:
    record: dict = {}
    for arg in args:
        if "=" not in arg:
            continue
        field, _, text = arg.partition("=")
        record[field.strip()] = text.strip()
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KORMARC 사칭 감사 (사서 친화 한국어 리포트)")
    parser.add_argument("kv", nargs="*", help="필드=텍스트 (예: 245=홍길동전)")
    parser.add_argument("--json", help="record JSON 파일 경로")
    args = parser.parse_args(argv)

    if args.json:
        record = json.loads(Path(args.json).read_text(encoding="utf-8"))
    else:
        record = parse_kv_args(args.kv)

    report = build_homoglyph_sanity_report_kr(record)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(report + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
