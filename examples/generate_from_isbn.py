"""CLI 예제: ISBN → KORMARC .mrc 파일 생성.

사용법:
    python examples/generate_from_isbn.py 9788936434120
    python examples/generate_from_isbn.py 9788936434120 --output-dir ./my_output
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# src 경로 추가 (개발 시 pip install -e . 안 한 상태에서도 동작)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.api.aggregator import aggregate_by_isbn  # noqa: E402
from kormarc_auto.classification.kdc_classifier import recommend_kdc  # noqa: E402
from kormarc_auto.kormarc.builder import build_kormarc_record  # noqa: E402
from kormarc_auto.kormarc.validator import validate_record  # noqa: E402
from kormarc_auto.output.kolas_writer import write_kolas_mrc  # noqa: E402
from kormarc_auto.vernacular.field_880 import add_880_pairs  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="ISBN → KORMARC .mrc 생성")
    parser.add_argument("isbn", help="13자리 ISBN")
    parser.add_argument("--output-dir", help="출력 폴더", default=None)
    parser.add_argument(
        "--cataloging-agency",
        default="OURLIB",
        help="040 ▾a 우리 도서관 부호 (기관 설정)",
    )
    args = parser.parse_args()

    load_dotenv()

    isbn = args.isbn.replace("-", "").strip()
    print(f"\n[1/5] ISBN {isbn}로 외부 API 조회...")
    book_data = aggregate_by_isbn(isbn)

    if not book_data.get("sources"):
        print(f"  ❌ 모든 소스에서 ISBN {isbn} 조회 실패", file=sys.stderr)
        return 1

    print(f"  ✓ 소스: {', '.join(book_data['sources'])}")
    print(f"  ✓ 표제: {book_data.get('title')}")
    print(f"  ✓ 저자: {book_data.get('author')}")
    print(f"  ✓ 출판사: {book_data.get('publisher')}")
    print(f"  ✓ 발행연도: {book_data.get('publication_year')}")
    print(f"  ✓ 신뢰도: {book_data.get('confidence', 0):.2f}")

    print("\n[2/5] KDC 분류 추천...")
    kdc_candidates = recommend_kdc(book_data)
    if kdc_candidates:
        top_kdc = kdc_candidates[0]
        print(f"  ✓ {top_kdc['code']} (신뢰도 {top_kdc['confidence']:.2f}, {top_kdc['source']})")
        if not book_data.get("kdc"):
            book_data["kdc"] = top_kdc["code"]

    print("\n[3/5] KORMARC 레코드 빌드...")
    record = build_kormarc_record(book_data, cataloging_agency=args.cataloging_agency)
    print(f"  ✓ 필드 수: {len(record.fields)}")

    print("\n[4/5] 880 한자 병기 페어 생성...")
    pair_count = add_880_pairs(record)
    print(f"  ✓ 추가된 880 페어: {pair_count}개")

    print("\n[5/5] 검증 + .mrc 저장...")
    errors = validate_record(record)
    if errors:
        print("  ⚠ 검증 경고:")
        for err in errors:
            print(f"    - {err}")
    else:
        print("  ✓ 검증 통과")

    out_path = write_kolas_mrc(record, isbn, output_dir=args.output_dir)
    file_size = out_path.stat().st_size
    print(f"  ✓ 저장: {out_path} ({file_size} bytes)")

    if book_data.get("attributions"):
        print("\n[출처 표시 의무]")
        for attribution in book_data["attributions"]:
            print(f"  - {attribution}")

    print(f"\n✅ 완료. KOLAS 자동 반입 폴더에 {out_path.name} 두면 자동 인식됩니다.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
