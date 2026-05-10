"""KORMARC homoglyph 사칭 감사 CLI entry_point (Cycle 648·pyproject.toml console_scripts).

Usage (pip install kormarc-auto 후):
    check-homoglyph "245=홍길동전" "100=허균"
    check-homoglyph --json record.json

founder fit ★★★·CLAUDE.md §15 정합·사서 1줄 명령.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kormarc_auto.text import build_homoglyph_sanity_report_kr


def parse_kv_args(args: list[str]) -> dict:
    record: dict = {}
    for arg in args:
        if "=" not in arg:
            continue
        field, _, text = arg.partition("=")
        record[field.strip()] = text.strip()
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="KORMARC 사칭 감사 (사서 친화 한국어 리포트·1줄 명령)",
        prog="check-homoglyph",
    )
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
