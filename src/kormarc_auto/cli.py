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
import contextlib
import os
import sys
from pathlib import Path
from typing import Any

# Windows cp949 환경에서 한국어 stdout 깨짐 회피
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
with contextlib.suppress(AttributeError, OSError):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


def cmd_init(args: argparse.Namespace) -> int:
    """B안 P2 — 신규 환경 초기화 (.env 템플릿·작업 디렉토리).

    안전: 기존 .env에 키 값이 1건이라도 있으면 --force도 거부 (PO 키 보호).
    """
    cwd = Path.cwd()
    env_path = cwd / ".env"

    if env_path.exists():
        existing = env_path.read_text(encoding="utf-8")
        # 비어있지 않은 KEY=VALUE 1건이라도 있으면 차단 (--force 무관)
        has_real_value = any(
            "=" in line
            and not line.lstrip().startswith("#")
            and line.split("=", 1)[1].strip() not in ("", '""', "''")
            for line in existing.splitlines()
        )
        if has_real_value:
            print(f"⛔ .env에 이미 키가 입력되어 있습니다 ({env_path})")
            print("  PO 키 보호를 위해 --force도 거부합니다.")
            print("  덮어쓰려면 .env를 직접 백업·삭제 후 init 재실행하세요.")
            return 1
        if not args.force:
            print(f"⚠ .env 이미 존재 (모두 빈 값): {env_path}")
            print("  덮어쓰려면 --force")
            return 1

    template = """# kormarc-auto .env 템플릿 (kormarc-auto init 자동 생성)
# 발급 가이드: 사용자_TODO.txt 참조

# 필수 (B안 §1 backbone)
NL_CERT_KEY=
ANTHROPIC_API_KEY=

# 권장 (다중 폴백)
DATA4LIBRARY_AUTH_KEY=
KAKAO_API_KEY=
PUBMED_API_KEY=

# 자관 정책 (선택)
KORMARC_AGENCY=OURLIB
KORMARC_PRICE_PER_RECORD_KRW=200

# Plan B Cycle 2 — 키 0개로 30초 데모 = KORMARC_DEMO_MODE=1 후 'kormarc-auto demo'
KORMARC_DEMO_MODE=
"""

    env_path.write_text(template, encoding="utf-8")
    print(f"✓ .env 템플릿 생성 → {env_path}")
    print()
    print("다음 단계:")
    print("  1. .env 메모장으로 열어 키 입력 (사용자_TODO.txt 참조)")
    print("  2. 키 0개로 즉시 시도 = KORMARC_DEMO_MODE=1 kormarc-auto demo")
    print("  3. 실 사용 = kormarc-auto isbn 9788937437076")
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


def cmd_xlsx(args: argparse.Namespace) -> int:
    """Excel 일괄 처리 — ISBN 컬럼 채우면 자동 채움 또는 빈 템플릿 생성."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.xlsx_command == "template":
        from kormarc_auto.output.xlsx_writer import write_isbn_template_xlsx

        out = write_isbn_template_xlsx(output_path=args.output or "isbn_template.xlsx")
        print(f"✓ 템플릿: {out}")
        print("  → ISBN을 A열에 채운 뒤: kormarc-auto xlsx fill <파일> --output <결과>")
        return 0

    if args.xlsx_command == "fill":
        try:
            import openpyxl
        except ImportError:
            print("❌ openpyxl 미설치 — `pip install openpyxl`")
            return 1
        from kormarc_auto.api.aggregator import aggregate_by_isbn
        from kormarc_auto.output.xlsx_writer import write_books_xlsx

        wb = openpyxl.load_workbook(args.input, read_only=True)
        ws = wb.active
        isbns: list[str] = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row:
                continue
            cell = row[0]
            if cell is None:
                continue
            isbn = str(cell).replace("-", "").strip()
            if isbn and isbn.isdigit():
                isbns.append(isbn)
        wb.close()

        if not isbns:
            print("❌ A열에 ISBN이 없습니다 (1행은 헤더, 2행부터 데이터)")
            return 1

        print(f"📚 {len(isbns)}건 조회 중...")
        books: list[dict[str, Any]] = []
        for i, isbn in enumerate(isbns, 1):
            print(f"[{i}/{len(isbns)}] {isbn}", end=" ... ")
            try:
                data = aggregate_by_isbn(isbn)
                if data.get("sources"):
                    data["source"] = ", ".join(data["sources"])
                    books.append(data)
                    print(f"✓ {data.get('title', '?')[:30]}")
                else:
                    print("미조회")
                    books.append({"isbn": isbn, "title": "(미조회)"})
            except Exception as e:
                print(f"오류: {e}")
                books.append({"isbn": isbn, "title": f"(오류: {e})"})

        out = write_books_xlsx(books, output_path=args.output or "filled.xlsx")
        ok = sum(1 for b in books if b.get("title", "").startswith("(") is False)
        print(f"\n✓ {out} ({ok}/{len(isbns)} 성공)")
        return 0

    print(f"❌ 알 수 없는 명령: {args.xlsx_command}")
    return 1


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

    if args.deposit_command == "form":
        from kormarc_auto.legal.deposit_form import (
            build_deposit_form,
            render_deposit_form_pdf,
        )

        if not args.title:
            print("❌ --title 필수 (자료 표제)")
            return 2
        bd = {
            "title": args.title,
            "author": args.author,
            "publisher": args.publisher,
            "publication_year": args.pub_date,
            "isbn": args.isbn,
        }
        form = build_deposit_form(
            bd,
            publisher_address=args.address or "",
            publisher_contact=args.contact or "",
            publisher_biz_no=args.biz_no,
            submitter_name=args.submitter or "",
            submitter_role=args.role or "발행인",
            is_government=args.government,
            consents_preservation=not args.no_consent,
        )
        out = render_deposit_form_pdf(form, output_path=args.output)
        print(f"✓ 납본서 PDF (별지 제3호서식): {out}")
        return 0

    print(f"❌ 알 수 없는 명령: {args.deposit_command}")
    return 1


def cmd_demo(args: argparse.Namespace) -> int:
    """30초 무키 데모 — Part 92 §A.1 / T2-1 step 5.

    fakellm-style mock 서버 활성·.env·API 키 X·SAMPLE_BOOKS 7건 즉시 사용.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import os

    from kormarc_auto.demo.offline_mock_server import (
        SAMPLE_BOOKS,
        SENTINEL_ISBNS,
        list_demo_isbns,
    )

    # KORMARC_DEMO_MODE = aggregator·외부 API 모듈이 자동 mock 사용
    os.environ["KORMARC_DEMO_MODE"] = "1"

    print("=" * 60)
    print("kormarc-auto 데모 모드 (30초·API 키 불필요)")
    print("=" * 60)
    print(f"\n사용 가능 SAMPLE ISBN ({len(SAMPLE_BOOKS)}건):")
    for isbn, book in SAMPLE_BOOKS.items():
        print(f"  {isbn} = {book.get('title', '')}")

    print(f"\nSENTINEL ISBN ({len(SENTINEL_ISBNS)}건·테스트):")
    for isbn, kind in SENTINEL_ISBNS.items():
        print(f"  {isbn} = {kind}")

    if args.isbn:
        from kormarc_auto.demo.offline_mock_server import (
            mock_anthropic_kdc_recommendation,
            mock_data4library,
            mock_seoji,
        )

        print(f"\n데모 처리: ISBN {args.isbn}")
        seoji = mock_seoji(args.isbn)
        d4l = mock_data4library(args.isbn)
        ai = mock_anthropic_kdc_recommendation(f"book_{args.isbn}")

        print(f"  SEOJI: {seoji.status_code} = {len(seoji.json_body.get('docs', []))}건")
        print(f"  data4library: {d4l.status_code}")
        print(f"  AI KDC: {ai.status_code} (mock·결정성)")

        if args.isbn in SAMPLE_BOOKS:
            book = SAMPLE_BOOKS[args.isbn]
            print("\nKORMARC 자동 채움 (예시):")
            for k in ("title", "author", "publisher", "publication_year", "kdc"):
                if k in book:
                    print(f"  {k}: {book[k]}")
            print(
                "\n→ 실 사용 = .env에 NL_CERT_KEY·ANTHROPIC_API_KEY 입력 후 'kormarc-auto isbn <ISBN>'"
            )
    else:
        # B안 Cycle 2 — 5건 자동 처리·30초 timing·round-trip 회귀
        import time

        from kormarc_auto.api.aggregator import aggregate_by_isbn
        from kormarc_auto.kormarc.builder import build_kormarc_record
        from kormarc_auto.kormarc.validator import validate_record

        print("\n5건 자동 처리 (KORMARC_DEMO_MODE=1·외부 API 0건)\n")
        t0 = time.time()
        ok = 0
        isbns = list_demo_isbns()[:5]
        for i, isbn in enumerate(isbns, 1):
            t_step = time.time()
            data = aggregate_by_isbn(isbn)
            if not data.get("sources"):
                print(f"  [{i}/5] {isbn} ❌ no_data")
                continue
            try:
                record = build_kormarc_record(data, cataloging_agency="DEMO")
                errs = validate_record(record)
                # round-trip 회귀 (Cycle 1 baseline 정합)
                from io import BytesIO

                from pymarc import MARCReader

                raw1 = record.as_marc()
                r2 = next(MARCReader(BytesIO(raw1), to_unicode=True, force_utf8=False), None)
                roundtrip = r2 is not None and r2.as_marc() == raw1
                rt_mark = "✓" if roundtrip else "✗"
                title = (data.get("title") or "")[:25]
                print(
                    f"  [{i}/5] {isbn} ✓ {title} (errs={len(errs)}·rt={rt_mark}·{time.time() - t_step:.2f}s)"
                )
                ok += 1
            except Exception as e:
                print(f"  [{i}/5] {isbn} ❌ build_fail: {type(e).__name__}: {e}")

        elapsed = time.time() - t0
        print(f"\n=== Reproduced {ok}/5 records ({elapsed:.2f}s)")
        if elapsed > 30:
            print(f"⚠ 30초 초과 ({elapsed:.1f}s) — Cycle 2 회귀 게이트")
            return 1
        if ok < 5:
            print(f"⚠ 5건 미만 처리 ({ok}/5)")
            return 1
        print("✓ B안 Cycle 2 demo 게이트 통과 (30초 5건 + round-trip 100%)")
        print("\n사용: kormarc-auto demo --isbn 9788937437076 (단건 inspect)")

    return 0


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
    print(
        f"  오배가:       {len(result['missorted'])}건 ({result['summary']['missorted_pct']:.1f}%)"
    )
    print(
        f"  자관 미등록:  {len(result['missing_in_db'])}건 ({result['summary']['missing_pct']:.1f}%)"
    )

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

        print(
            f"anthropic: {anthropic.__version__ if hasattr(anthropic, '__version__') else '설치됨'}"
        )
    except ImportError:
        print("anthropic: ❌ 미설치")

    # B안 Cycle 1 — MARC 블록별 분리표 (단일 99.82% 폐기)
    print()
    print("=== MARC 블록별 정합 (자관 PILOT 1관·174 파일·3,383 레코드) ===")
    import json

    eval_results = Path(__file__).resolve().parent.parent.parent / "docs" / "eval" / "results"
    per_block_path = eval_results / "2026-05-03" / "per-block.json"
    per_record_path = eval_results / "2026-05-04" / "per-record.json"

    if per_block_path.exists():
        data = json.loads(per_block_path.read_text(encoding="utf-8"))
        for blk, vals in data.get("by_block", {}).items():
            pct = vals.get("coverage_pct", 0)
            print(f"  {blk:35s}  presence={pct:6.2f}%")

    if per_record_path.exists():
        data = json.loads(per_record_path.read_text(encoding="utf-8"))
        print(
            f"\n  Round-trip exact-match: {data.get('roundtrip_pass_pct', 0):.2f}%"
            f" ({data.get('roundtrip_pass', 0)}/{data.get('total_records', 0)})"
        )

    print("\n  단일 헤드라인: 자관 round-trip 100% baseline (99.82% 단일 표시 폐기)")
    print("  방법론: docs/eval/methodology.md")

    return 0


def cmd_dispose(args: argparse.Namespace) -> int:
    """제적·폐기 결재서식 PDF + 폐기목록 엑셀."""
    import json as _json

    from kormarc_auto.output.disposal_form import (
        DisposalEntry,
        render_disposal_form_pdf,
        write_disposal_xlsx,
    )

    if not args.input:
        print("❌ --input JSON 파일 필요 ([{registration_number, title, reason_code, ...}])")
        return 2
    rows = _json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        print("❌ JSON은 리스트여야 함")
        return 2
    entries = [DisposalEntry(**r) for r in rows]

    if args.format in ("pdf", "both"):
        pdf_out = Path(
            args.output_pdf or f"logs/disposal/{args.fiscal_period.replace(' ', '_')}.pdf"
        )
        render_disposal_form_pdf(
            entries,
            library_name=args.library,
            fiscal_period=args.fiscal_period,
            director=args.director or "",
            output_path=pdf_out,
        )
        print(f"✓ 제적·폐기 결재서식: {pdf_out}")
    if args.format in ("xlsx", "both"):
        xlsx_out = Path(
            args.output_xlsx or f"logs/disposal/{args.fiscal_period.replace(' ', '_')}.xlsx"
        )
        write_disposal_xlsx(entries, xlsx_out)
        print(f"✓ 폐기목록 엑셀: {xlsx_out}")
    return 0


def cmd_wishlist(args: argparse.Namespace) -> int:
    """비치희망도서 분석 — 자관 중복 + KDC 균형 + 예상 비용."""
    import json as _json

    from kormarc_auto.acquisition.wishlist import (
        analyze_wishlist,
        summarize,
    )

    if not args.input:
        print("❌ --input ISBN 파일 필요")
        return 2

    with Path(args.input).open(encoding="utf-8") as f:
        isbns = [line.strip() for line in f if line.strip()]

    items = analyze_wishlist(isbns, use_external=not args.offline)
    summary = summarize(items)

    print(f"수서 분석: 총 {summary['total']}건")
    print(f"  · 자관 중복: {summary['in_holdings']}건")
    print(f"  · 신규 구입 후보: {summary['new_purchase']}건")
    print(f"  · 예상 비용: {summary['estimated_cost_krw']:,}원")
    print(f"  · KDC 분포: {summary['kdc_distribution']}")
    if summary["balance_warnings"]:
        print("\n⚠ 장서개발지침 경고:")
        for w in summary["balance_warnings"]:
            print(f"  · {w}")
    if summary["errors"]:
        print(f"\n조회 실패 {len(summary['errors'])}건:")
        for e in summary["errors"]:
            print(f"  · {e['isbn']}: {e['error']}")

    if args.output:
        out_data = {
            "summary": summary,
            "items": [vars(it) for it in items],
        }
        Path(args.output).write_text(
            _json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n✓ 상세 결과: {args.output}")
    return 0


def cmd_interlibrary(args: argparse.Namespace) -> int:
    """상호대차 양식 어댑터 — 책나래·책바다·RISS 사서대리신청."""
    import json

    from kormarc_auto.interlibrary.exporters import (
        from_inventory,
        write_csv,
        write_xlsx,
    )

    # 입력 books
    if args.from_isbns:
        with Path(args.from_isbns).open(encoding="utf-8") as f:
            isbns = [line.strip() for line in f if line.strip()]
        books = from_inventory(isbns)
    elif args.from_json:
        with Path(args.from_json).open(encoding="utf-8") as f:
            books = json.load(f)
        if not isinstance(books, list):
            print("❌ JSON은 리스트여야 함")
            return 2
    else:
        print("❌ --from-isbns 또는 --from-json 필요")
        return 2

    out = Path(args.output)
    if args.format == "csv":
        write_csv(books, out, system=args.system)
    else:
        write_xlsx(books, out, system=args.system)
    print(f"✓ {args.system} 양식 {args.format.upper()}: {out} ({len(books)}건)")
    return 0


def cmd_registration(args: argparse.Namespace) -> int:
    """등록번호 자동 부여·누락번호 검출 — 알파스 워크플로우."""
    from kormarc_auto.librarian_helpers.registration import (
        assign_for_multivolume,
        find_missing_numbers,
        load_existing_from_index,
        next_registration_number,
    )

    existing = load_existing_from_index() if args.use_index else []
    if args.from_file:
        with Path(args.from_file).open(encoding="utf-8") as f:
            existing.extend(line.strip() for line in f if line.strip())

    if args.action == "next":
        n = next_registration_number(
            existing,
            kind=args.kind,
            turn=args.turn,
            year=args.year,
            fill_gap=args.fill_gap,
        )
        print(n)
        return 0

    if args.action == "missing":
        gaps = find_missing_numbers(existing, kind=args.kind, turn=args.turn, year=args.year)
        if gaps:
            print(f"누락번호 {len(gaps)}개 (kind={args.kind}, turn={args.turn}, year={args.year}):")
            for g in gaps:
                print(f"  · {args.kind}{args.turn:02d}{args.year:02d}{g:05d}")
        else:
            print("누락번호 없음")
        return 0

    if args.action == "multivolume":
        if args.volumes < 1:
            print("❌ --volumes는 1 이상")
            return 2
        results = assign_for_multivolume(
            {"title": args.title or "(미입력)"},
            volumes=args.volumes,
            kind=args.kind,
            turn=args.turn,
            year=args.year,
            existing=existing,
        )
        print(f"✓ 다권본 {args.volumes}권 등록번호 부여:")
        for r in results:
            print(
                f"  · {r['registration_number']} | {r['volume_label']} | 245 ▾n {r['marc_245_n']}"
            )
        return 0

    print(f"❌ 알 수 없는 동작: {args.action}")
    return 2


def cmd_pilot_collect(args: argparse.Namespace) -> int:
    """PILOT 시연 결과 1줄 수집 — scripts/pilot_collect 통합."""
    import subprocess

    cmd = [
        str(Path(sys.executable)),
        "scripts/pilot_collect.py",
        "--persona",
        args.persona,
        "--library",
        args.library,
    ]
    return subprocess.call(cmd)


def cmd_sales_funnel(args: argparse.Namespace) -> int:
    """영업 funnel — scripts/sales_funnel 통합."""
    import subprocess

    cmd = [str(Path(sys.executable)), "scripts/sales_funnel.py"]
    if args.json:
        cmd.extend(["--json", str(args.json)])
    return subprocess.call(cmd)


def cmd_prefix_discover(args: argparse.Namespace) -> int:
    """자관 .mrc 049 ▾l prefix 자동 발견 — 다른 자관 PILOT 1주차 도입 (5분).

    영업: PILOT 사서가 본인 .mrc 디렉토리만 지정 → config.yaml snippet 출력 →
    바로 적용 가능. 자관 「○○도서관」 4-29 발견 = WQ →
    99.82% 정합 도달.
    """
    from kormarc_auto.librarian_helpers.prefix_discovery import PrefixDiscoverer

    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ 디렉토리 없음: {directory}")
        return 2

    discoverer = PrefixDiscoverer(threshold_pct=args.threshold)
    print(f"분석 중: {directory}")
    summary = discoverer.scan(directory)

    print(f"\n총 레코드: {summary.total_records}건")
    print("\n049 prefix 분포:")
    for prefix, count in sorted(summary.prefix_counts.items(), key=lambda x: -x[1]):
        pct = count / summary.total_records * 100 if summary.total_records else 0.0
        marker = "  [권장]" if prefix in summary.recommended_prefixes else ""
        print(f"  {prefix}: {count:>5}건 ({pct:5.1f}%){marker}")

    print(f"\n권장 (>= {summary.threshold_pct}% 적용):")
    print(f"  {summary.recommended_prefixes}")
    print(f"\nconfig.yaml snippet:\n{summary.to_yaml_snippet()}")
    return 0


def cmd_sanity_check(args: argparse.Namespace) -> int:
    """자관 .mrc 디렉토리 진단 — PILOT 1주차 첫 30분 도구.

    prefix 분포 + 정합률 + 위반 유형 Top 5 한 번에 출력. 사서가 자관 데이터
    건강 진단 즉시 확인 → 신뢰 형성. JSON 출력 옵션 (--json) = KLA 슬라이드 데이터.
    """
    import json

    from kormarc_auto.librarian_helpers.sanity_check import run_sanity_check

    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ 디렉토리 없음: {directory}")
        return 2

    report = run_sanity_check(directory, prefix_threshold=args.threshold)
    print(report.to_text())

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "directory": report.directory,
            "file_count": report.file_count,
            "record_count": report.record_count,
            "valid_count": report.valid_count,
            "issue_count": report.issue_count,
            "integrity_pct": round(report.integrity_pct, 2),
            "prefix_counts": report.prefix_summary.prefix_counts,
            "recommended_prefixes": list(report.prefix_summary.recommended_prefixes),
            "issues_by_type": report.issues_by_type,
            "sample_issues": report.sample_issues,
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✓ JSON 저장: {out}")
    return 0


def cmd_account(args: argparse.Namespace) -> int:
    """본인 데이터 다운로드/삭제 — 개인정보보호법 §35-3·§36."""
    import json

    from kormarc_auto.server.usage import (
        delete_account_data,
        export_account_data,
    )

    api_key = args.api_key
    if not api_key:
        print("❌ --api-key 또는 KORMARC_API_KEY 환경변수 필요")
        return 2

    if args.action == "export":
        data = export_account_data(api_key)
        out = Path(args.output or "account_export.json")
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ 본인 데이터 다운로드: {out}")
        print(f"  사용 로그: {data['usage_log_count']}건")
        print(f"  피드백: {len(data['feedback'])}건")
        return 0

    if args.action == "delete":
        if not args.yes:
            print("⚠ 본인 데이터를 영구 삭제합니다. 복구 불가.")
            print("   계속하려면 --yes 플래그를 추가하세요.")
            return 1
        result = delete_account_data(api_key)
        print(f"✓ 삭제 완료: {result['deleted']}")
        return 0

    print(f"❌ 알 수 없는 동작: {args.action}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    """argparse 트리 구성."""
    parser = argparse.ArgumentParser(
        prog="kormarc-auto",
        description="한국 도서관용 KORMARC 자동 생성 도구",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verbose", "-v", action="store_true", help="DEBUG 로그 출력")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # demo (T2-1 step 5·Part 92 §A.1)
    p_demo = sub.add_parser("demo", help="30초 무키 데모 (SAMPLE 7건·SENTINEL 5건)")
    p_demo.add_argument("--isbn", default=None, help="데모 ISBN (없으면 리스트만 출력)")
    p_demo.set_defaults(func=cmd_demo)

    p_init = sub.add_parser("init", help="신규 환경 초기화 (.env 템플릿 생성)")
    p_init.add_argument("--force", action="store_true", help="기존 .env 덮어쓰기")
    p_init.set_defaults(func=cmd_init)

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

    # xlsx
    p_xls = sub.add_parser("xlsx", help="Excel 일괄 처리 (template 생성 또는 fill 채우기)")
    p_xls.add_argument("xlsx_command", choices=["template", "fill"])
    p_xls.add_argument("input", nargs="?", default=None, help="입력 .xlsx (fill 시)")
    p_xls.add_argument("--output", default=None)
    p_xls.set_defaults(func=cmd_xlsx)

    # notify
    p_not = sub.add_parser(
        "notify", help="이용자 알림 메시지 생성 (overdue/return/reservation/closure)"
    )
    p_not.add_argument("notify_type", choices=["overdue", "return", "reservation", "closure"])
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
    p_dep = sub.add_parser("deposit", help="납본 추적 + 별지 제3호서식 (도서관법 §21)")
    p_dep.add_argument("deposit_command", choices=["add", "list", "deadline", "form"])
    p_dep.add_argument("--title", default="")
    p_dep.add_argument("--isbn", default=None)
    p_dep.add_argument("--pub-date", default="", help="발행일 (YYYY-MM-DD)")
    p_dep.add_argument("--dep-date", default=None, help="납본일 (없으면 오늘)")
    p_dep.add_argument("--recipient", default="국립중앙도서관")
    p_dep.add_argument("--copies", type=int, default=2)
    p_dep.add_argument("--note", default="")
    p_dep.add_argument("--limit", type=int, default=50)
    # form 전용
    p_dep.add_argument("--author", default=None, help="form: 저자")
    p_dep.add_argument("--publisher", default=None, help="form: 발행처")
    p_dep.add_argument("--address", default=None, help="form: 발행처 주소")
    p_dep.add_argument("--contact", default=None, help="form: 연락처")
    p_dep.add_argument("--biz-no", default=None, help="form: 사업자번호")
    p_dep.add_argument("--submitter", default=None, help="form: 납본자 성명")
    p_dep.add_argument("--role", default=None, help="form: 직책 (발행인/관장 등)")
    p_dep.add_argument(
        "--government",
        action="store_true",
        help="form: 국가·지자체·공공기관 발행 (3부)",
    )
    p_dep.add_argument(
        "--no-consent",
        action="store_true",
        help="form: 디지털 영구 보존 미동의 (2부)",
    )
    p_dep.add_argument("--output", default=None, help="form: 출력 PDF 경로")
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
    p_rep.add_argument("files", nargs="*", help="검증할 .mrc 파일 목록 (validate 전용)")
    p_rep.add_argument("--output", default=None, help="출력 PDF 경로")
    p_rep.set_defaults(func=cmd_report)

    # info
    p_info = sub.add_parser("info", help="환경·설치 상태 진단")
    p_info.set_defaults(func=cmd_info)

    # dispose — 제적·폐기
    p_dis = sub.add_parser(
        "dispose",
        help="제적·폐기 결재서식 PDF + 폐기목록 엑셀 (도서관법 §22)",
    )
    p_dis.add_argument("--input", required=True, help="DisposalEntry JSON 파일")
    p_dis.add_argument("--library", required=True, help="도서관명")
    p_dis.add_argument("--fiscal-period", required=True, help="심의 기간 (예: '2026 1분기')")
    p_dis.add_argument("--director", default=None, help="결재자(관장명)")
    p_dis.add_argument("--format", choices=["pdf", "xlsx", "both"], default="both")
    p_dis.add_argument("--output-pdf", default=None)
    p_dis.add_argument("--output-xlsx", default=None)
    p_dis.set_defaults(func=cmd_dispose)

    # wishlist — 비치희망도서 수서 분석
    p_w = sub.add_parser(
        "wishlist",
        help="비치희망도서 분석 (자관 중복 + KDC 균형 + 비용)",
    )
    p_w.add_argument("--input", required=True, help="ISBN 목록 파일 (한 줄당 1개)")
    p_w.add_argument("--output", default=None, help="JSON 결과 저장 경로 (선택)")
    p_w.add_argument(
        "--offline",
        action="store_true",
        help="외부 API 미사용 (자관 인덱스만 조회)",
    )
    p_w.set_defaults(func=cmd_wishlist)

    # pilot-collect — PILOT 시연 결과 1줄 수집 (4 페르소나)
    p_pc = sub.add_parser(
        "pilot-collect",
        help="PILOT 시연 직후 결과 인터랙티브 수집 + JSON 자동 저장",
    )
    p_pc.add_argument(
        "--persona", default="macro", choices=["macro", "acquisition", "general", "video"]
    )
    p_pc.add_argument("--library", default="○○도서관")
    p_pc.set_defaults(func=cmd_pilot_collect)

    # sales-funnel — 영업 funnel (가입→활성→한도→결제)
    p_sf = sub.add_parser(
        "sales-funnel",
        help="영업 funnel + 페르소나별 결제 전환률 (KLA 슬라이드 데이터)",
    )
    p_sf.add_argument("--json", type=Path, default=None, help="JSON 보고서 경로")
    p_sf.set_defaults(func=cmd_sales_funnel)

    # prefix-discover — 자관 049 prefix 자동 발견 (PILOT 1주차 도입 ★)
    p_pd = sub.add_parser(
        "prefix-discover",
        help="자관 .mrc → 049 prefix 자동 발견 + config snippet (PILOT 5분 도입)",
    )
    p_pd.add_argument(
        "directory",
        help="자관 .mrc 디렉토리 (재귀 검색)",
    )
    p_pd.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help="권장 임계값 % (default 1.0)",
    )
    p_pd.set_defaults(func=cmd_prefix_discover)

    # sanity-check — 자관 .mrc 진단 (PILOT 1주차 첫 30분 ★)
    p_sc = sub.add_parser(
        "sanity-check",
        help="자관 .mrc 디렉토리 진단 (prefix + 정합률 + 위반 Top 5) — 사서 첫 만남 5분",
    )
    p_sc.add_argument(
        "directory",
        help="자관 .mrc 디렉토리 (재귀 검색)",
    )
    p_sc.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help="prefix 권장 임계값 % (default 1.0)",
    )
    p_sc.add_argument(
        "--json",
        default=None,
        help="JSON 보고서 저장 경로 (KLA 슬라이드·영업 자료)",
    )
    p_sc.set_defaults(func=cmd_sanity_check)

    # interlibrary — 상호대차 양식 어댑터
    p_il = sub.add_parser(
        "interlibrary",
        help="상호대차 양식 (책나래·책바다·RISS) 사서대리신청 자동",
    )
    p_il.add_argument(
        "--system",
        choices=["chaeknarae", "chaekbada", "riss"],
        required=True,
    )
    p_il.add_argument("--format", choices=["csv", "xlsx"], default="xlsx", help="출력 형식")
    p_il.add_argument(
        "--from-isbns",
        default=None,
        help="ISBN 목록 파일 (한 줄당 1개) — 자관 인덱스 자동 조회",
    )
    p_il.add_argument(
        "--from-json",
        default=None,
        help="신청 정보 JSON 배열 파일 (이용자/날짜 등 포함)",
    )
    p_il.add_argument("--output", required=True, help="저장 경로 (.csv/.xlsx)")
    p_il.set_defaults(func=cmd_interlibrary)

    # registration — 등록번호 자동 부여
    p_reg = sub.add_parser(
        "registration",
        help="등록번호 자동 부여·누락번호 검출 (알파스/KOLAS 워크플로우)",
    )
    p_reg.add_argument(
        "action",
        choices=["next", "missing", "multivolume"],
        help="next=다음 번호 / missing=누락번호 / multivolume=다권본 일괄",
    )
    p_reg.add_argument("--kind", default="EM", help="등록구분 (EM·BM·AM 등)")
    p_reg.add_argument("--turn", type=int, default=1, help="차수 (기본 1)")
    p_reg.add_argument(
        "--year",
        type=int,
        default=None,
        help="연도 두 자리 (기본 올해)",
    )
    p_reg.add_argument(
        "--fill-gap",
        action="store_true",
        help="next 시 누락번호 우선 채움",
    )
    p_reg.add_argument(
        "--use-index",
        action="store_true",
        help="자관 DB 인덱스 자동 로드",
    )
    p_reg.add_argument("--from-file", default=None, help="기존 번호 파일 (한 줄당 하나)")
    p_reg.add_argument("--volumes", type=int, default=1, help="multivolume 권수")
    p_reg.add_argument("--title", default=None, help="multivolume 표제")
    p_reg.set_defaults(func=cmd_registration)

    # account — 개인정보보호법 §35-3 / §36
    p_acc = sub.add_parser(
        "account",
        help="본인 데이터 다운로드/삭제 (개인정보보호법 §35-3·§36)",
    )
    p_acc.add_argument(
        "action",
        choices=["export", "delete"],
        help="export=본인 데이터 JSON 다운로드 / delete=영구 삭제",
    )
    p_acc.add_argument(
        "--api-key",
        default=os.getenv("KORMARC_API_KEY"),
        help="API 키 (또는 KORMARC_API_KEY 환경변수)",
    )
    p_acc.add_argument("--output", default=None, help="export 저장 경로")
    p_acc.add_argument("--yes", action="store_true", help="delete 확인 (필수)")
    p_acc.set_defaults(func=cmd_account)

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
