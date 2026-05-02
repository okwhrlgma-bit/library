"""사서 보고서 자동 생성 — 신착 안내문·월간 보고서·검증 리포트.

PO 도서관 자료의 「2024 통계」·「신착도서 목록」·「자료관리대장」 흐름 자동화.

3종 PDF:
1. 신착도서 안내문 (이용자 게시용) — 표제·저자·청구기호·소개
2. 월간 자관 보고서 (상부기관 제출용) — KDC 분포·신착·통계
3. 일괄 검증 리포트 — .mrc 묶음 → 오류·경고 요약
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _ensure_reportlab() -> tuple[bool, str | None]:
    try:
        import reportlab  # noqa: F401

        return True, None
    except ImportError:
        return False, "reportlab 미설치 — `pip install -e .[labels]`로 설치"


def _korean_font(c: Any) -> str:
    """한글 폰트 등록 (Malgun/Apple/Nanum 자동 탐지)."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                pdfmetrics.registerFont(TTFont("KoreanFont", fp))
                return "KoreanFont"
            except Exception:
                continue
    return "Helvetica"


def make_acquisition_announcement(
    items: list[dict[str, Any]],
    *,
    title: str = "신착도서 안내",
    library_name: str = "○○도서관",
    output_path: str | Path | None = None,
) -> Path:
    """이용자 게시용 신착도서 안내문 PDF (A4).

    Args:
        items: BookData dict 리스트 (title·author·publisher·call_number·summary)
        title: 안내문 제목
        library_name: 도서관명
        output_path: 출력 경로

    Returns:
        생성된 PDF 경로
    """
    ok, err = _ensure_reportlab()
    if not ok:
        raise RuntimeError(err)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    out = Path(output_path or os.getenv("KORMARC_REPORT_OUT", "./output/acquisition.pdf"))
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4)
    font = _korean_font(c)
    _page_w, page_h = A4

    today = datetime.now().strftime("%Y-%m-%d")
    margin = 20 * mm
    y = page_h - margin

    # 헤더
    c.setFont(font, 18)
    c.drawString(margin, y, f"📚 {title}")
    y -= 8 * mm
    c.setFont(font, 10)
    c.drawString(margin, y, f"{library_name} · {today} · 총 {len(items)}권")
    y -= 10 * mm

    # 본문
    c.setFont(font, 10)
    for item in items:
        if y < margin + 30 * mm:
            c.showPage()
            font = _korean_font(c)
            c.setFont(font, 10)
            y = page_h - margin

        c.setFont(font, 12)
        title_text = (item.get("title") or "표제 미상")[:60]
        c.drawString(margin, y, f"• {title_text}")
        y -= 6 * mm

        c.setFont(font, 9)
        author = (item.get("author") or "")[:40]
        publisher = (item.get("publisher") or "")[:30]
        year = item.get("publication_year") or ""
        meta = f"  {author} | {publisher} ({year})"
        c.drawString(margin, y, meta[:90])
        y -= 5 * mm

        cn = item.get("call_number") or ""
        if cn:
            c.drawString(margin, y, f"  청구기호: {cn}")
            y -= 5 * mm

        summary = (item.get("summary") or "")[:200]
        if summary:
            c.drawString(margin, y, f"  {summary[:80]}...")
            y -= 5 * mm

        y -= 3 * mm  # 항목 간격

    c.save()
    logger.info("신착도서 안내문 저장: %s (%d권)", out, len(items))
    return out


def make_monthly_report(
    *,
    library_name: str = "○○도서관",
    year: int,
    month: int,
    output_path: str | Path | None = None,
) -> Path:
    """월간 자관 운영 보고서 (상부기관 제출용).

    inventory/library_db에서 자관 통계 자동 추출 + 월별 신착·KDC 분포.
    """
    ok, err = _ensure_reportlab()
    if not ok:
        raise RuntimeError(err)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    from kormarc_auto.inventory.library_db import stats

    out = Path(
        output_path or os.getenv("KORMARC_REPORT_OUT", f"./output/monthly_{year}_{month:02d}.pdf")
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    s = stats()

    c = canvas.Canvas(str(out), pagesize=A4)
    font = _korean_font(c)
    _page_w, page_h = A4

    margin = 20 * mm
    y = page_h - margin

    c.setFont(font, 20)
    c.drawString(margin, y, f"{library_name} 월간 운영 보고서")
    y -= 8 * mm
    c.setFont(font, 12)
    c.drawString(margin, y, f"{year}년 {month}월")
    y -= 12 * mm

    # 1. 종합 지표
    c.setFont(font, 14)
    c.drawString(margin, y, "1. 종합 지표")
    y -= 8 * mm
    c.setFont(font, 11)
    c.drawString(margin + 5 * mm, y, f"• 자관 총 등록 자료: {s['total']:,}건")
    y -= 6 * mm

    # 2. KDC 주류 분포
    y -= 4 * mm
    c.setFont(font, 14)
    c.drawString(margin, y, "2. KDC 주류 분포")
    y -= 8 * mm
    c.setFont(font, 11)
    for kdc, count in s.get("by_kdc_main", {}).items():
        pct = (count / max(s["total"], 1)) * 100
        c.drawString(margin + 5 * mm, y, f"• {kdc}: {count:>5}건 ({pct:.1f}%)")
        y -= 6 * mm

    # 3. 발행연도 분포 (최근 10년)
    y -= 4 * mm
    if y < 60 * mm:
        c.showPage()
        font = _korean_font(c)
        y = page_h - margin

    c.setFont(font, 14)
    c.drawString(margin, y, "3. 발행연도 분포 (상위 10)")
    y -= 8 * mm
    c.setFont(font, 11)
    for yr, count in list(s.get("by_year", {}).items())[:10]:
        c.drawString(margin + 5 * mm, y, f"• {yr}년: {count}건")
        y -= 6 * mm

    # 푸터
    c.setFont(font, 8)
    c.drawString(
        margin, margin, f"생성: kormarc-auto · {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    c.save()
    logger.info("월간 보고서 저장: %s", out)
    return out


def make_validation_report(
    mrc_paths: list[str | Path],
    *,
    output_path: str | Path | None = None,
) -> Path:
    """일괄 .mrc 검증 리포트 — KOLAS 반입 전 사전 점검.

    Returns:
        생성된 PDF 경로
    """
    ok, err = _ensure_reportlab()
    if not ok:
        raise RuntimeError(err)

    from pymarc import MARCReader
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    from kormarc_auto.kormarc.kolas_validator import kolas_strict_validate

    out = Path(output_path or os.getenv("KORMARC_REPORT_OUT", "./output/validation_report.pdf"))
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4)
    font = _korean_font(c)
    _page_w, page_h = A4

    margin = 20 * mm
    y = page_h - margin

    c.setFont(font, 18)
    c.drawString(margin, y, "KORMARC 일괄 검증 리포트")
    y -= 10 * mm

    total_errors = 0
    total_warnings = 0

    for path in mrc_paths:
        p = Path(path)
        if not p.exists():
            continue
        if y < margin + 30 * mm:
            c.showPage()
            font = _korean_font(c)
            y = page_h - margin

        with p.open("rb") as f:
            reader = MARCReader(f, force_utf8=True)
            for record in reader:
                if record is None:
                    continue
                strict = kolas_strict_validate(record)
                errors = strict.get("errors", [])
                warns = strict.get("warnings", [])
                total_errors += len(errors)
                total_warnings += len(warns)

                c.setFont(font, 11)
                status = "✓" if not errors else "❌"
                c.drawString(margin, y, f"{status} {p.name}")
                y -= 6 * mm
                c.setFont(font, 9)
                c.drawString(margin + 5 * mm, y, f"오류: {len(errors)} / 경고: {len(warns)}")
                y -= 5 * mm

                for e in errors[:3]:
                    c.drawString(margin + 10 * mm, y, f"x {e[:60]}")
                    y -= 4 * mm
                y -= 2 * mm

    # 요약
    if y < 30 * mm:
        c.showPage()
        font = _korean_font(c)
        y = page_h - margin

    y -= 5 * mm
    c.setFont(font, 12)
    c.drawString(
        margin, y, f"종합: 파일 {len(mrc_paths)}개 · 오류 {total_errors} · 경고 {total_warnings}"
    )

    c.save()
    logger.info("검증 리포트 저장: %s", out)
    return out
