"""도서관법 §21·시행규칙 §4 — 납본 별지 제3호서식 PDF 자동 생성.

근거 법령:
- 도서관법(법률 제19592호) §21: 발행자는 발행일로부터 30일 이내에 국립중앙도서관에
  자료 2부 이상 납본 의무 (보존동의 시 1부 가능, 국가·지자체·공공기관은 3부)
- 도서관법 시행령(대통령령 제34533호) §15: 자료 종류별 부수
- 도서관법 시행규칙(문화체육관광부령 제496호) §4 별지 제3호서식: 납본서
  (별지 제4호서식은 납본증명서 — NL이 발급, 우리가 만드는 것 아님)

PO 사서 워크플로우:
1. 작은도서관·출판사가 자체 발간한 자료(소식지·문집·자료집) 납본 의무
2. 발행 30일 이내 별지 제3호서식 작성 + KORMARC 초안 첨부 + NL Korea 우편 발송
3. NL이 별지 제4호 납본증명서 회신 → 도서관 보관

매출 영향: PO 사업화 플레이북 §7.8 "소형 출판사 납본 MARC 초안" 건당 5,000~15,000원
대행 모델. 본 모듈로 그 대행을 자동화.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DepositForm:
    """납본 신청 정보 — 별지 제3호서식 입력 필드."""

    title: str
    author: str | None
    publisher: str
    publication_date: str  # ISO YYYY-MM-DD
    isbn: str | None = None
    issn: str | None = None
    material_type: str = "도서"  # 도서·연속간행물·악보·지도·전자자료·기타
    pages: str | None = None
    price_krw: int | None = None
    publisher_address: str = ""
    publisher_contact: str = ""
    publisher_biz_no: str | None = None
    is_government: bool = False  # 국가·지자체·공공기관 발행
    consents_preservation: bool = True  # 디지털 영구보존 동의 여부
    submitter_name: str = ""  # 납본자 성명
    submitter_role: str = "발행인"  # 발행인·편집인·관장 등


# 시행령 §15 부수 산정
def required_copies(form: DepositForm) -> int:
    """납본 부수 산정 — 도서관법 시행령 §15 + 시행규칙 §4.

    - 국가·지자체·공공기관 발행: 3부
    - 보존동의: 1부 (디지털 보존)
    - 그 외: 2부
    """
    if form.is_government:
        return 3
    if form.consents_preservation:
        return 1
    return 2


def deposit_deadline(publication_date: str | date) -> date:
    """발행일 + 30일."""
    if isinstance(publication_date, str):
        publication_date = date.fromisoformat(publication_date)
    return publication_date + timedelta(days=30)


def build_deposit_form(
    book_data: dict[str, Any],
    *,
    publisher_address: str = "",
    publisher_contact: str = "",
    publisher_biz_no: str | None = None,
    submitter_name: str = "",
    submitter_role: str = "발행인",
    is_government: bool = False,
    consents_preservation: bool = True,
) -> DepositForm:
    """KORMARC book_data → DepositForm.

    book_data는 aggregator 결과 또는 사서 수동 입력 dict.
    """
    title = str(book_data.get("title", "")).strip()
    if not title:
        raise ValueError("title 필수 (별지 제3호서식 §자료의 표제)")

    pub_date = str(
        book_data.get("publication_date")
        or book_data.get("publication_year")
        or date.today().isoformat()
    )
    # 연도만 들어온 경우 1월 1일로
    if len(pub_date) == 4 and pub_date.isdigit():
        pub_date = f"{pub_date}-01-01"

    return DepositForm(
        title=title,
        author=str(book_data.get("author") or "") or None,
        publisher=str(book_data.get("publisher") or "(미등록)"),
        publication_date=pub_date,
        isbn=str(book_data.get("isbn") or "") or None,
        issn=str(book_data.get("issn") or "") or None,
        material_type=str(book_data.get("material_type") or "도서"),
        pages=str(book_data.get("pages") or "") or None,
        price_krw=int(book_data["price_krw"]) if book_data.get("price_krw") else None,
        publisher_address=publisher_address,
        publisher_contact=publisher_contact,
        publisher_biz_no=publisher_biz_no,
        is_government=is_government,
        consents_preservation=consents_preservation,
        submitter_name=submitter_name,
        submitter_role=submitter_role,
    )


def render_deposit_form_pdf(
    form: DepositForm,
    *,
    output_path: str | Path | None = None,
) -> Path:
    """납본 별지 제3호서식 PDF 생성.

    형식은 시행규칙 별지 제3호의 항목을 모두 포함하되, 정부 공식 양식
    (한글 hwp)과 100% 동일하지는 않음. PO·발행자가 인쇄 후 서명·도장만
    추가하면 NL Korea에 우편 발송 가능.

    NL Korea가 정식 양식을 요구하면 본 PDF + 한글 별지 제3호 hwp 출력 병행.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
    except ImportError as e:
        raise RuntimeError("reportlab 미설치 — `pip install reportlab`") from e

    from kormarc_auto.output.reports import _korean_font

    out = Path(
        output_path or f"logs/deposit_forms/deposit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4)
    font = _korean_font(c)
    _w, page_h = A4
    margin = 22 * mm
    y = page_h - margin

    # 표제
    c.setFont(font, 16)
    c.drawString(margin, y, "[별지 제3호서식]")
    y -= 8 * mm
    c.setFont(font, 18)
    c.drawString(margin, y, "납  본  서")
    y -= 6 * mm
    c.setFont(font, 9)
    c.drawString(margin, y, "(도서관법 제21조 및 같은 법 시행규칙 제4조)")
    y -= 10 * mm

    # 1. 자료 정보
    c.setFont(font, 12)
    c.drawString(margin, y, "1. 자료의 표시")
    y -= 7 * mm
    c.setFont(font, 11)
    fields = [
        ("자료의 표제", form.title),
        ("저자(발행인)", form.author or "-"),
        ("발행처", form.publisher),
        ("발행연월일", form.publication_date),
        ("자료 종별", form.material_type),
        ("ISBN", form.isbn or "-"),
        ("ISSN", form.issn or "-"),
        ("쪽수·면수", form.pages or "-"),
        ("정가", f"{form.price_krw:,}원" if form.price_krw else "-"),
    ]
    for label, value in fields:
        c.drawString(margin + 5 * mm, y, f"· {label}: {value}")
        y -= 6 * mm

    # 2. 납본자 정보
    y -= 4 * mm
    c.setFont(font, 12)
    c.drawString(margin, y, "2. 납본자")
    y -= 7 * mm
    c.setFont(font, 11)
    submitter_fields = [
        ("성명·직책", f"{form.submitter_name} ({form.submitter_role})"),
        ("발행처 주소", form.publisher_address or "-"),
        ("연락처", form.publisher_contact or "-"),
        ("사업자등록번호", form.publisher_biz_no or "-"),
    ]
    for label, value in submitter_fields:
        c.drawString(margin + 5 * mm, y, f"· {label}: {value}")
        y -= 6 * mm

    # 3. 납본 부수·보존 동의
    y -= 4 * mm
    c.setFont(font, 12)
    c.drawString(margin, y, "3. 납본 부수")
    y -= 7 * mm
    c.setFont(font, 11)
    copies = required_copies(form)
    why = (
        "국가·지자체·공공기관 발행"
        if form.is_government
        else ("디지털 보존 동의" if form.consents_preservation else "표준")
    )
    c.drawString(margin + 5 * mm, y, f"· 납본 부수: {copies}부  ({why})")
    y -= 6 * mm
    consent_mark = "☑" if form.consents_preservation else "☐"
    c.drawString(
        margin + 5 * mm,
        y,
        f"· {consent_mark} 디지털 영구 보존 동의 (도서관법 시행령 §15)",
    )
    y -= 10 * mm

    # 4. 마감일
    deadline = deposit_deadline(form.publication_date)
    c.setFont(font, 11)
    c.drawString(
        margin,
        y,
        f"※ 납본 마감일: {deadline.isoformat()} (발행일 + 30일, 도서관법 §21)",
    )
    y -= 12 * mm

    # 서명
    c.setFont(font, 11)
    c.drawString(margin, y, f"발행일: {form.publication_date}")
    y -= 7 * mm
    today = date.today().isoformat()
    c.drawString(margin, y, f"제출일: {today}")
    y -= 14 * mm
    c.drawString(margin, y, "납본자 서명·도장: ____________________  (인)")
    y -= 12 * mm

    # 수신자
    c.setFont(font, 11)
    c.drawString(margin, y, "수신: 국립중앙도서관장")
    y -= 6 * mm
    c.setFont(font, 9)
    c.drawString(
        margin,
        y,
        "주소: 06579 서울특별시 서초구 반포대로 201 국립중앙도서관 자료수집과",
    )
    y -= 5 * mm
    c.drawString(margin, y, "전화: 02-3483-3333  /  https://www.nl.go.kr")

    # 푸터
    c.setFont(font, 8)
    c.drawString(
        margin,
        margin,
        f"발행: kormarc-auto · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 사서가 직접 검토·수정 후 사용",
    )
    c.save()
    logger.info("납본서 PDF 저장: %s", out)
    return out


__all__ = [
    "DepositForm",
    "build_deposit_form",
    "deposit_deadline",
    "render_deposit_form_pdf",
    "required_copies",
]
