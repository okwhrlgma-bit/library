"""CLI 예제: 책 사진 → KORMARC .mrc.

사용법:
    python examples/generate_from_photo.py cover.jpg copyright.jpg toc.jpg
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.kormarc.builder import build_kormarc_record  # noqa: E402
from kormarc_auto.kormarc.validator import validate_record  # noqa: E402
from kormarc_auto.output.kolas_writer import write_kolas_mrc  # noqa: E402
from kormarc_auto.vernacular.field_880 import add_880_pairs  # noqa: E402
from kormarc_auto.vision.photo_pipeline import photo_to_book_data  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(description="책 사진 → KORMARC .mrc 생성")
    parser.add_argument("images", nargs="+", help="이미지 파일 경로 (1~3장)")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    load_dotenv()

    print(f"\n[1/4] {len(args.images)}장 사진 분석...")
    book_data = photo_to_book_data(args.images)

    if book_data.get("vision_only") and not book_data.get("vision_isbn"):
        print(f"  ❌ 사진에서 정보 추출 실패: {book_data.get('error')}", file=sys.stderr)
        return 1

    print(f"  ✓ ISBN: {book_data.get('isbn')}")
    print(f"  ✓ 신뢰도: {book_data.get('confidence', 0):.2f}")

    print("\n[2/4] KORMARC 빌드...")
    record = build_kormarc_record(book_data)
    print(f"  ✓ 필드 수: {len(record.fields)}")

    print("\n[3/4] 880 페어 + 검증...")
    add_880_pairs(record)
    errors = validate_record(record)
    if errors:
        print(f"  ⚠ 검증 경고: {errors}")

    print("\n[4/4] .mrc 저장...")
    isbn = book_data.get("isbn", "unknown")
    out_path = write_kolas_mrc(record, isbn, output_dir=args.output_dir)
    print(f"  ✓ {out_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
