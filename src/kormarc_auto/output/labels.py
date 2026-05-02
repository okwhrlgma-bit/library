"""청구기호·바코드 라벨 PDF 출력 (A4 Avery 호환).

사서가 신착도서에 붙이는 라벨 자동 생성:
- 청구기호 라벨 (책등용, 25mm x 38mm 권장)
- 바코드 라벨 (Code 128 또는 EAN-13, 책 안쪽 표지용)
- 도서 카드 (구식이지만 일부 도서관 사용)

A4 21장 (3x7) Avery L7160 호환 / 24장 (3x8) L7159 호환.
"""

from __future__ import annotations

import io
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def _ensure_libs() -> tuple[bool, str | None]:
    try:
        import barcode  # noqa: F401
        import reportlab  # noqa: F401

        return True, None
    except ImportError as e:
        return False, f"라이브러리 미설치: {e}. `pip install -e .[labels]`로 설치."


def make_barcode_image(value: str, *, format: str = "code128") -> bytes:
    """바코드 PNG 이미지 생성.

    Args:
        value: 등록번호 또는 ISBN
        format: "code128" / "ean13"

    Returns:
        PNG 바이트
    """
    ok, err = _ensure_libs()
    if not ok:
        raise RuntimeError(err)

    import barcode
    from barcode.writer import ImageWriter

    cls = barcode.get_barcode_class(format)
    code = cls(value, writer=ImageWriter())
    buf = io.BytesIO()
    code.write(buf, options={"write_text": True, "module_height": 8.0})
    return buf.getvalue()


def make_label_pdf(
    items: list[dict[str, str]],
    *,
    output_path: str | Path | None = None,
    layout: str = "L7160",  # A4 21장
) -> Path:
    """라벨 PDF 생성.

    Args:
        items: [{"call_number": "813.7 한31ㅈ", "registration_no": "K000123", "title": "작별..."}]
        output_path: 기본 ./output/labels.pdf
        layout: "L7160" (3x7=21) / "L7159" (3x8=24) / "A4_one"

    Returns:
        생성된 PDF 경로
    """
    ok, err = _ensure_libs()
    if not ok:
        raise RuntimeError(err)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    out = Path(output_path or os.getenv("KORMARC_LABEL_OUT", "./output/labels.pdf"))
    out.parent.mkdir(parents=True, exist_ok=True)

    # 한글 폰트 (Windows 기본 Malgun Gothic)
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/MalgunGothic.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]
    font_name = "Helvetica"
    for fp in font_paths:
        if Path(fp).exists():
            try:
                pdfmetrics.registerFont(TTFont("KoreanFont", fp))
                font_name = "KoreanFont"
                break
            except Exception:
                continue

    c = canvas.Canvas(str(out), pagesize=A4)
    page_w, page_h = A4

    if layout == "L7160":  # 63.5 x 38.1 mm, 3 col x 7 row
        cols, rows = 3, 7
        cell_w = 63.5 * mm
        cell_h = 38.1 * mm
        margin_left = 7.2 * mm
        margin_top = 15.15 * mm
    elif layout == "L7159":  # 63.5 x 33.9 mm, 3 col x 8 row
        cols, rows = 3, 8
        cell_w = 63.5 * mm
        cell_h = 33.9 * mm
        margin_left = 7.2 * mm
        margin_top = 13.3 * mm
    else:  # A4 한 장에 큰 라벨 1개 (검토용)
        cols, rows = 1, 1
        cell_w = page_w - 40 * mm
        cell_h = page_h - 40 * mm
        margin_left = 20 * mm
        margin_top = 20 * mm

    per_page = cols * rows
    for i, item in enumerate(items):
        if i > 0 and i % per_page == 0:
            c.showPage()

        idx = i % per_page
        col = idx % cols
        row = idx // cols

        x = margin_left + col * cell_w
        y = page_h - margin_top - (row + 1) * cell_h

        # 외곽선 (점선, 절단 가이드)
        c.setDash(2, 2)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(x, y, cell_w, cell_h)
        c.setDash()

        # 청구기호 (큰 글자)
        call = item.get("call_number", "")
        if call:
            c.setFont(font_name, 14)
            c.drawString(x + 5 * mm, y + cell_h - 8 * mm, call)

        # 등록번호
        reg = item.get("registration_no", "")
        if reg:
            c.setFont(font_name, 9)
            c.drawString(x + 5 * mm, y + cell_h - 14 * mm, reg)

        # 표제 (잘려도 OK, 30자 컷)
        title = item.get("title", "")[:30]
        if title:
            c.setFont(font_name, 8)
            c.drawString(x + 5 * mm, y + 5 * mm, title)

        # 바코드 (등록번호 또는 ISBN)
        bc_value = item.get("barcode_value") or reg
        if bc_value:
            try:
                bc_png = make_barcode_image(bc_value, format="code128")
                from reportlab.lib.utils import ImageReader

                img = ImageReader(io.BytesIO(bc_png))
                bc_w = cell_w - 10 * mm
                bc_h = 12 * mm
                c.drawImage(
                    img,
                    x + 5 * mm,
                    y + cell_h / 2 - bc_h / 2,
                    width=bc_w,
                    height=bc_h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                logger.warning("바코드 생성 실패: %s — %s", bc_value, e)

    c.save()
    logger.info("라벨 PDF 저장: %s (%d items, layout=%s)", out, len(items), layout)
    return out
