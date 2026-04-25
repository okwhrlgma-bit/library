"""kormarc-auto CLI 진입점.

설치 후 `kormarc-auto` 명령으로 호출 가능 (pyproject.toml의 [project.scripts]).

사용 예:
    kormarc-auto isbn 9788936434120
    kormarc-auto isbn 9788936434120 --output-dir D:/KOLAS/Import
    kormarc-auto batch tests/sample_isbns.txt
    kormarc-auto photo cover.jpg copyright.jpg
    kormarc-auto validate output/9788936434120.mrc
    kormarc-auto info
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from kormarc_auto import __version__
from kormarc_auto.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def cmd_isbn(args: argparse.Namespace) -> int:
    """단일 ISBN → KORMARC."""
    from kormarc_auto.api.aggregator import aggregate_by_isbn
    from kormarc_auto.classification.kdc_classifier import recommend_kdc
    from kormarc_auto.kormarc.builder import build_kormarc_record
    from kormarc_auto.kormarc.validator import validate_record
    from kormarc_auto.output.kolas_writer import write_kolas_mrc
    from kormarc_auto.vernacular.field_880 import add_880_pairs

    isbn = args.isbn.replace("-", "").strip()
    print(f"[1/5] {isbn} 외부 API 조회...")
    book_data = aggregate_by_isbn(isbn)

    if not book_data.get("sources"):
        print("  ❌ 모든 소스 실패", file=sys.stderr)
        return 1

    print(f"  ✓ 소스: {', '.join(book_data['sources'])}")
    print(f"  ✓ 표제: {book_data.get('title')}")
    print(f"  ✓ 저자: {book_data.get('author')}")
    print(f"  ✓ 신뢰도: {book_data.get('confidence', 0):.2f}")

    print("\n[2/5] KDC 분류 추천...")
    candidates = recommend_kdc(book_data)
    if candidates:
        top = candidates[0]
        print(f"  ✓ {top['code']} ({top['source']}, conf={top['confidence']:.2f})")
        if not book_data.get("kdc"):
            book_data["kdc"] = top["code"]

    print("\n[3/5] KORMARC 빌드...")
    record = build_kormarc_record(book_data, cataloging_agency=args.agency)
    print(f"  ✓ 필드 수: {len(record.fields)}")

    print("\n[4/5] 880 페어 + 검증...")
    pair_count = add_880_pairs(record)
    print(f"  ✓ 880 페어: {pair_count}개")
    errors = validate_record(record)
    if errors:
        print("  ⚠ 검증 경고:")
        for e in errors:
            print(f"    - {e}")
    else:
        print("  ✓ 검증 통과")

    print("\n[5/5] .mrc 저장...")
    out_path = write_kolas_mrc(record, isbn, output_dir=args.output_dir)
    print(f"  ✓ {out_path} ({out_path.stat().st_size} bytes)")

    if book_data.get("attributions"):
        print("\n[출처 표시]")
        for a in book_data["attributions"]:
            print(f"  - {a}")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """배치 처리 — ISBN 목록 파일 → 다수 .mrc."""
    from kormarc_auto.api.aggregator import aggregate_by_isbn
    from kormarc_auto.classification.kdc_classifier import recommend_kdc
    from kormarc_auto.kormarc.builder import build_kormarc_record
    from kormarc_auto.kormarc.validator import validate_record
    from kormarc_auto.output.kolas_writer import write_kolas_mrc
    from kormarc_auto.vernacular.field_880 import add_880_pairs

    isbn_file = Path(args.file)
    if not isbn_file.exists():
        print(f"❌ 파일 없음: {isbn_file}", file=sys.stderr)
        return 1

    isbns = [
        line.strip().replace("-", "")
        for line in isbn_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    print(f"📚 {len(isbns)}건 배치 처리 시작\n")

    results: list[dict] = []
    for i, isbn in enumerate(isbns, 1):
        print(f"[{i}/{len(isbns)}] {isbn}", end=" ... ")
        try:
            data = aggregate_by_isbn(isbn)
            if not data.get("sources"):
                print("❌ 미조회")
                results.append({"isbn": isbn, "ok": False, "reason": "no_data"})
                continue
            kdc = recommend_kdc(data)
            if kdc and not data.get("kdc"):
                data["kdc"] = kdc[0]["code"]
            record = build_kormarc_record(data, cataloging_agency=args.agency)
            add_880_pairs(record)
            errors = validate_record(record)
            out_path = write_kolas_mrc(record, isbn, output_dir=args.output_dir)
            print(
                f"✓ {data.get('title', '?')[:30]} "
                f"(conf={data.get('confidence', 0):.2f}, errs={len(errors)})"
            )
            results.append({"isbn": isbn, "ok": True, "path": str(out_path), "errors": errors})
        except Exception as e:
            print(f"❌ 오류: {e}")
            results.append({"isbn": isbn, "ok": False, "reason": str(e)})

    ok = sum(1 for r in results if r["ok"])
    print(f"\n📊 결과: {ok}/{len(isbns)} 성공 ({ok / len(isbns) * 100:.0f}%)")
    return 0 if ok == len(isbns) else 1


def cmd_photo(args: argparse.Namespace) -> int:
    """책 사진 → KORMARC."""
    from kormarc_auto.kormarc.builder import build_kormarc_record
    from kormarc_auto.kormarc.validator import validate_record
    from kormarc_auto.output.kolas_writer import write_kolas_mrc
    from kormarc_auto.vernacular.field_880 import add_880_pairs
    from kormarc_auto.vision.photo_pipeline import photo_to_book_data

    print(f"📷 {len(args.images)}장 분석...")
    book_data = photo_to_book_data(args.images)

    if book_data.get("vision_only") and not book_data.get("vision_isbn"):
        print(f"❌ 추출 실패: {book_data.get('error')}", file=sys.stderr)
        return 1

    record = build_kormarc_record(book_data)
    add_880_pairs(record)
    validate_record(record)
    isbn = book_data.get("isbn", "unknown")
    out_path = write_kolas_mrc(record, isbn, output_dir=args.output_dir)
    print(f"✓ {out_path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """기존 .mrc 파일 검증."""
    from pymarc import MARCReader

    from kormarc_auto.kormarc.validator import validate_record

    path = Path(args.file)
    if not path.exists():
        print(f"❌ 파일 없음: {path}", file=sys.stderr)
        return 1

    with path.open("rb") as f:
        reader = MARCReader(f, force_utf8=True)
        for i, record in enumerate(reader, 1):
            if record is None:
                print(f"  레코드 {i}: 파싱 실패")
                continue
            errors = validate_record(record)
            status = "✓ 통과" if not errors else f"⚠ {len(errors)} 경고"
            print(f"  레코드 {i}: {status}")
            for e in errors:
                print(f"    - {e}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """키워드/표제/저자로 검색."""
    from kormarc_auto.api.search import search_by_query

    print(f"🔍 검색: {args.query}")
    candidates = search_by_query(args.query, limit=args.limit)
    if not candidates:
        print("  ❌ 결과 없음")
        return 1

    print(f"\n  {len(candidates)}건 발견:\n")
    for i, c in enumerate(candidates, 1):
        print(
            f"  [{i:2d}] {c.get('title', '?')[:40]} / {c.get('author', '?')[:20]} "
            f"({c.get('publication_year', '?')}) ISBN={c.get('isbn', '?')} "
            f"src={c.get('source', '?')} conf={c.get('confidence', 0):.2f}"
        )
    print("\n  → 사용: kormarc-auto isbn <ISBN>")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """FastAPI 서버 실행."""
    from kormarc_auto.server.app import run

    if args.host:
        os.environ["KORMARC_HOST"] = args.host
    if args.port:
        os.environ["KORMARC_PORT"] = str(args.port)
    print(f"🚀 kormarc-auto 서버 시작 (host={args.host}, port={args.port})")
    run()
    return 0


def cmd_ui(args: argparse.Namespace) -> int:
    """Streamlit UI 실행."""
    from kormarc_auto.ui.streamlit_app import run

    if args.port:
        os.environ["KORMARC_UI_PORT"] = str(args.port)
    print(f"🖥  Streamlit UI 시작 (port={args.port})")
    run()
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """프로젝트·환경 진단."""
    import os

    print(f"kormarc-auto v{__version__}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"작업 폴더: {Path.cwd()}")
    print()
    print("환경변수 점검:")
    for key in ["NL_CERT_KEY", "ALADIN_TTB_KEY", "KAKAO_API_KEY", "ANTHROPIC_API_KEY"]:
        val = os.getenv(key)
        status = "✓ 설정됨" if val else "❌ 미설정"
        masked = f" ({val[:6]}***)" if val else ""
        print(f"  {key}: {status}{masked}")

    try:
        import pymarc

        print(f"\npymarc: {pymarc.__version__ if hasattr(pymarc, '__version__') else '설치됨'}")
    except ImportError:
        print("\npymarc: ❌ 미설치")

    try:
        import anthropic

        print(f"anthropic: {anthropic.__version__ if hasattr(anthropic, '__version__') else '설치됨'}")
    except ImportError:
        print("anthropic: ❌ 미설치")

    return 0


def build_parser() -> argparse.ArgumentParser:
    """argparse 트리 구성."""
    parser = argparse.ArgumentParser(
        prog="kormarc-auto",
        description="한국 도서관용 KORMARC 자동 생성 도구",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verbose", "-v", action="store_true", help="DEBUG 로그 출력")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # isbn
    p_isbn = sub.add_parser("isbn", help="단일 ISBN → KORMARC")
    p_isbn.add_argument("isbn", help="13자리 ISBN")
    p_isbn.add_argument("--output-dir", default=None, help="출력 폴더 (기본: ./output)")
    p_isbn.add_argument("--agency", default="OURLIB", help="040 ▾a 우리 도서관 부호")
    p_isbn.set_defaults(func=cmd_isbn)

    # batch
    p_batch = sub.add_parser("batch", help="ISBN 목록 파일 일괄 처리")
    p_batch.add_argument("file", help="ISBN 목록 텍스트 파일 (한 줄에 하나)")
    p_batch.add_argument("--output-dir", default=None)
    p_batch.add_argument("--agency", default="OURLIB")
    p_batch.set_defaults(func=cmd_batch)

    # photo
    p_photo = sub.add_parser("photo", help="책 사진 → KORMARC")
    p_photo.add_argument("images", nargs="+", help="이미지 파일 1~3장")
    p_photo.add_argument("--output-dir", default=None)
    p_photo.set_defaults(func=cmd_photo)

    # validate
    p_val = sub.add_parser("validate", help="기존 .mrc 파일 검증")
    p_val.add_argument("file", help=".mrc 파일 경로")
    p_val.set_defaults(func=cmd_validate)

    # search
    p_search = sub.add_parser("search", help="키워드/표제/저자로 검색")
    p_search.add_argument("query", help="검색어")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.set_defaults(func=cmd_search)

    # serve
    p_serve = sub.add_parser("serve", help="FastAPI REST 서버 실행")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.set_defaults(func=cmd_serve)

    # ui
    p_ui = sub.add_parser("ui", help="Streamlit UI 실행 (모바일 반응형)")
    p_ui.add_argument("--port", type=int, default=8501)
    p_ui.set_defaults(func=cmd_ui)

    # info
    p_info = sub.add_parser("info", help="환경·설치 상태 진단")
    p_info.set_defaults(func=cmd_info)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 진입점."""
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(level="DEBUG" if args.verbose else "INFO")
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
