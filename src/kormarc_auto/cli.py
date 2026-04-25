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


def cmd_romanize(args: argparse.Namespace) -> int:
    """한글 → 로마자 (RR/ALA-LC)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from kormarc_auto.librarian_helpers.romanization import hangul_to_alalc, hangul_to_rr

    print(f"입력: {args.text}")
    print(f"RR (정부 표준):    {hangul_to_rr(args.text)}")
    print(f"ALA-LC (학술):     {hangul_to_alalc(args.text)}")
    return 0


def cmd_label(args: argparse.Namespace) -> int:
    """청구기호·바코드 라벨 PDF (A4 Avery)."""
    from kormarc_auto.output.labels import make_label_pdf

    items = []
    for line in Path(args.csv).read_text(encoding="utf-8").splitlines()[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            items.append(
                {
                    "call_number": parts[0],
                    "registration_no": parts[1],
                    "title": parts[2],
                    "barcode_value": parts[1],
                }
            )

    if not items:
        print("❌ 입력 CSV가 비어있음 (헤더 + 데이터 필요)")
        return 1

    out = make_label_pdf(items, output_path=args.output, layout=args.layout)
    print(f"✓ {out} ({len(items)} 라벨)")
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    """자관 장서 검색·통계."""
    from kormarc_auto.inventory.library_db import search_local, stats

    if args.command == "search":
        results = search_local(args.query, kdc_prefix=args.kdc, limit=args.limit)
        print(f"  {len(results)}건:")
        for r in results:
            print(
                f"  {r.get('isbn', '?')} | {r.get('title', '?')[:40]} | "
                f"{r.get('author', '?')[:20]} | KDC {r.get('kdc', '-')}"
            )
    elif args.command == "stats":
        s = stats()
        print(f"총 레코드: {s['total']}")
        print("KDC 주류 분포:")
        for k, v in s.get("by_kdc_main", {}).items():
            print(f"  {k}: {v}")
    return 0


def cmd_notify(args: argparse.Namespace) -> int:
    """이용자 알림 메시지 생성 (overdue/return/reservation/closure)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from kormarc_auto.librarian_helpers import notifications

    if args.notify_type == "overdue":
        msg = notifications.overdue_notice(
            user_name=args.user,
            book_title=args.book,
            due_date=args.due,
            overdue_days=args.days or notifications.calculate_overdue_days(args.due),
            library_name=args.library,
            fine_per_day=args.fine_per_day,
        )
    elif args.notify_type == "return":
        msg = notifications.return_reminder(
            user_name=args.user,
            book_title=args.book,
            due_date=args.due,
            library_name=args.library,
            days_before=args.days or 3,
        )
    elif args.notify_type == "reservation":
        msg = notifications.reservation_ready(
            user_name=args.user,
            book_title=args.book,
            pickup_deadline=args.due,
            library_name=args.library,
        )
    elif args.notify_type == "closure":
        msg = notifications.closure_notice(
            library_name=args.library,
            closure_dates=(args.dates or "").split(","),
            reason=args.reason or "정기 휴관",
        )
    else:
        print(f"❌ 알 수 없는 알림 유형: {args.notify_type}")
        return 1

    print("\n[SMS]")
    print(msg.get("sms", ""))
    print("\n[LMS]")
    print(msg.get("lms", ""))
    print("\n[email subject]")
    print(msg.get("email_subject", ""))
    return 0


def cmd_deposit(args: argparse.Namespace) -> int:
    """납본(legal deposit) 추적 — 도서관법 제20조."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from kormarc_auto.librarian_helpers import deposit

    if args.deposit_command == "add":
        entry = deposit.record_deposit(
            title=args.title,
            isbn=args.isbn,
            publication_date=args.pub_date,
            deposit_date=args.dep_date,
            recipient=args.recipient or "국립중앙도서관",
            copies=args.copies,
            note=args.note or "",
        )
        print(f"✓ 납본 기록: {entry['id']} | {entry['title']} ({entry['deposit_date']})")
        return 0

    if args.deposit_command == "list":
        items = deposit.list_deposits(limit=args.limit)
        print(f"전체 {len(items)}건:")
        for e in items:
            print(
                f"  {e['deposit_date']} | {e.get('title', '?')[:30]} | "
                f"ISBN {e.get('isbn', '-')} | {e['recipient']} {e['copies']}부"
            )
        return 0

    if args.deposit_command == "deadline":
        d = deposit.deposit_deadline(args.pub_date)
        print(f"발행일 {args.pub_date} → 납본 마감일: {d.isoformat()}")
        return 0

    print(f"❌ 알 수 없는 명령: {args.deposit_command}")
    return 1


def cmd_inspect(args: argparse.Namespace) -> int:
    """책장 사진 OCR → 자관 DB 대조 (장서 점검)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from kormarc_auto.inventory.inspection import inspect_shelf_images

    kdc_range: tuple[str, str] | None = None
    if args.kdc_range:
        parts = [p.strip() for p in args.kdc_range.split("-", 1)]
        if len(parts) == 2:
            kdc_range = (parts[0], parts[1])

    print(f"📷 {len(args.images)}장 책장 사진 점검...")
    result = inspect_shelf_images(args.images, expected_kdc_range=kdc_range)

    print("\n📊 결과:")
    print(f"  검출 청구기호: {result['detected_count']}건")
    print(f"  자관 일치:    {len(result['matched'])}건 ({result['summary']['matched_pct']:.1f}%)")
    print(f"  오배가:       {len(result['missorted'])}건 ({result['summary']['missorted_pct']:.1f}%)")
    print(f"  자관 미등록:  {len(result['missing_in_db'])}건 ({result['summary']['missing_pct']:.1f}%)")

    if result["missorted"]:
        print("\n  [오배가 후보]")
        for cn in result["missorted"][:10]:
            print(f"    - {cn}")
    if result["missing_in_db"]:
        print("\n  [미등록 후보]")
        for cn in result["missing_in_db"][:10]:
            print(f"    - {cn}")
    if result["warnings"]:
        print("\n  [경고]")
        for w in result["warnings"][:5]:
            print(f"    ! {w}")

    if args.csv:
        from kormarc_auto.inventory.inspection import write_inspection_csv

        csv_path = write_inspection_csv(result, output_path=args.csv)
        print(f"\n✓ CSV 저장: {csv_path}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """PDF 보고서 생성 (announcement/monthly/validate)."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from kormarc_auto.output.reports import (
        make_acquisition_announcement,
        make_monthly_report,
        make_validation_report,
    )

    if args.report_type == "announcement":
        from kormarc_auto.inventory.library_db import search_local

        items = search_local(query="", limit=args.limit)
        if not items:
            print("❌ 자관 인덱스에 항목이 없습니다 — 먼저 isbn/photo로 .mrc를 생성하세요.")
            return 1
        out = make_acquisition_announcement(
            items,
            title=args.title or "신착도서 안내",
            library_name=args.library or "○○도서관",
            output_path=args.output,
        )
        print(f"✓ 신착 안내문: {out} ({len(items)}권)")
        return 0

    if args.report_type == "monthly":
        from datetime import datetime as _dt

        now = _dt.now()
        out = make_monthly_report(
            library_name=args.library or "○○도서관",
            year=args.year or now.year,
            month=args.month or now.month,
            output_path=args.output,
        )
        print(f"✓ 월간 보고서: {out}")
        return 0

    if args.report_type == "validate":
        if not args.files:
            print("❌ .mrc 파일 경로를 1개 이상 입력하세요.")
            return 1
        out = make_validation_report(args.files, output_path=args.output)
        print(f"✓ 검증 리포트: {out} ({len(args.files)}개 파일)")
        return 0

    print(f"❌ 알 수 없는 보고서 유형: {args.report_type}")
    return 1


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

    # romanize
    p_rom = sub.add_parser("romanize", help="한글 → 로마자 (RR/ALA-LC)")
    p_rom.add_argument("text", help="한글 텍스트")
    p_rom.set_defaults(func=cmd_romanize)

    # label
    p_lbl = sub.add_parser("label", help="청구기호·바코드 라벨 PDF")
    p_lbl.add_argument("csv", help="청구기호,등록번호,표제 CSV")
    p_lbl.add_argument("--output", default=None)
    p_lbl.add_argument("--layout", default="L7160", choices=["L7160", "L7159", "A4_one"])
    p_lbl.set_defaults(func=cmd_label)

    # inventory
    p_inv = sub.add_parser("inventory", help="자관 장서 검색·통계")
    p_inv.add_argument("command", choices=["search", "stats"])
    p_inv.add_argument("query", nargs="?", default="")
    p_inv.add_argument("--kdc", default=None, help="KDC prefix 필터")
    p_inv.add_argument("--limit", type=int, default=20)
    p_inv.set_defaults(func=cmd_inventory)

    # notify
    p_not = sub.add_parser("notify", help="이용자 알림 메시지 생성 (overdue/return/reservation/closure)")
    p_not.add_argument(
        "notify_type", choices=["overdue", "return", "reservation", "closure"]
    )
    p_not.add_argument("--user", default="이용자", help="이용자명")
    p_not.add_argument("--book", default="", help="도서명")
    p_not.add_argument("--due", default="", help="만기/수령기한 (YYYY-MM-DD)")
    p_not.add_argument("--days", type=int, default=0, help="연체 일수 또는 사전 알림 일수")
    p_not.add_argument("--library", default="○○도서관", help="도서관명")
    p_not.add_argument("--fine-per-day", type=int, default=0, help="일 연체료 (원)")
    p_not.add_argument("--dates", default="", help="휴관일 (콤마 구분, closure 전용)")
    p_not.add_argument("--reason", default="", help="휴관 사유 (closure 전용)")
    p_not.set_defaults(func=cmd_notify)

    # deposit
    p_dep = sub.add_parser("deposit", help="납본 추적 (도서관법 제20조)")
    p_dep.add_argument("deposit_command", choices=["add", "list", "deadline"])
    p_dep.add_argument("--title", default="")
    p_dep.add_argument("--isbn", default=None)
    p_dep.add_argument("--pub-date", default="", help="발행일 (YYYY-MM-DD)")
    p_dep.add_argument("--dep-date", default=None, help="납본일 (없으면 오늘)")
    p_dep.add_argument("--recipient", default="국립중앙도서관")
    p_dep.add_argument("--copies", type=int, default=2)
    p_dep.add_argument("--note", default="")
    p_dep.add_argument("--limit", type=int, default=50)
    p_dep.set_defaults(func=cmd_deposit)

    # inspect
    p_insp = sub.add_parser("inspect", help="책장 사진 OCR로 장서 점검 (오배가·미등록)")
    p_insp.add_argument("images", nargs="+", help="책장 사진 1장 이상")
    p_insp.add_argument(
        "--kdc-range",
        default=None,
        help="이 책장의 예상 KDC 범위, 예: '810-820'",
    )
    p_insp.add_argument(
        "--csv",
        default=None,
        help="결과를 CSV로 저장할 경로 (사서 공유용)",
    )
    p_insp.set_defaults(func=cmd_inspect)

    # report
    p_rep = sub.add_parser("report", help="PDF 보고서 (신착 안내·월간·검증)")
    p_rep.add_argument(
        "report_type",
        choices=["announcement", "monthly", "validate"],
        help="보고서 유형",
    )
    p_rep.add_argument("--library", default=None, help="도서관명 (announcement·monthly)")
    p_rep.add_argument("--title", default=None, help="안내문 제목 (announcement)")
    p_rep.add_argument("--year", type=int, default=None, help="연도 (monthly)")
    p_rep.add_argument("--month", type=int, default=None, help="월 (monthly)")
    p_rep.add_argument("--limit", type=int, default=30, help="안내 게재 권수 (announcement)")
    p_rep.add_argument(
        "files", nargs="*", help="검증할 .mrc 파일 목록 (validate 전용)"
    )
    p_rep.add_argument("--output", default=None, help="출력 PDF 경로")
    p_rep.set_defaults(func=cmd_report)

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
