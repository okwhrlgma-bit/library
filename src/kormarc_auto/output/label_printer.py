"""라벨 프린터 PDF 출력 (Brother QL·Avery 호환) — Part 69 정합.

사서 페인 (Part 69·갭 2):
- 사서 70% = Brother QL·Avery 라벨 사용
- 청구기호 라벨 = 사서 수동 = 권당 5분 = 1관 1만권 = 800시간 낭비

해결: 청구기호 + 바코드 + 자관명 = PDF 자동.

Phase 1 = 단순 ReportLab PDF (의존성: reportlab).
의존성 없을 시 = HTML/CSS print preview fallback.
"""
from __future__ import annotations

from typing import Literal

LabelFormat = Literal[
    "brother_ql_dk_22205",  # 62×100mm 연속
    "brother_ql_dk_11202",  # 62×29mm 주소
    "avery_l7160",          # 21장/A4 (63.5×38.1mm)
    "avery_l7163",          # 14장/A4 (99.1×38.1mm)
]

LABEL_DIMENSIONS_MM = {
    "brother_ql_dk_22205": (62, 100),
    "brother_ql_dk_11202": (62, 29),
    "avery_l7160": (63.5, 38.1),
    "avery_l7163": (99.1, 38.1),
}


def render_label_html(
    *,
    call_number: str,
    barcode_value: str,
    library_name: str,
    label_format: LabelFormat = "avery_l7160",
) -> str:
    """라벨 HTML 자동 생성 (브라우저 print 가능).

    의존성 X (Phase 1).
    Phase 2 = ReportLab PDF (의존성 추가 시).

    Args:
        call_number: 청구기호 (예: "시문학811.7/ㅇ676ㅁ")
        barcode_value: 바코드 값 (예: "EQ20260001")
        library_name: 자관명 (예: "○○도서관")
        label_format: 라벨 포맷

    Returns:
        HTML string (브라우저에서 print 가능)
    """
    width_mm, height_mm = LABEL_DIMENSIONS_MM[label_format]

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>도서 라벨 — {library_name}</title>
<style>
@page {{ size: A4; margin: 10mm; }}
body {{ font-family: 'Pretendard', 'Noto Sans KR', sans-serif; margin: 0; padding: 0; }}
.label {{
  width: {width_mm}mm;
  height: {height_mm}mm;
  border: 1px solid #999;
  display: inline-block;
  padding: 3mm;
  box-sizing: border-box;
  page-break-inside: avoid;
  margin: 1mm;
  text-align: center;
}}
.library {{ font-size: 8pt; color: #666; margin-bottom: 1mm; }}
.call-number {{ font-size: 14pt; font-weight: bold; margin: 2mm 0; }}
.barcode {{
  font-family: 'Libre Barcode 128', monospace;
  font-size: 36pt;
  letter-spacing: 0;
  line-height: 1;
}}
.barcode-text {{ font-size: 9pt; margin-top: 1mm; }}
@media print {{
  .label {{ border: none; }}
}}
</style>
</head>
<body>
  <div class="label">
    <div class="library">{library_name}</div>
    <div class="call-number">{call_number}</div>
    <div class="barcode">*{barcode_value}*</div>
    <div class="barcode-text">{barcode_value}</div>
  </div>
</body>
</html>"""


def render_label_batch_html(
    items: list[dict],
    *,
    library_name: str,
    label_format: LabelFormat = "avery_l7160",
) -> str:
    """일괄 라벨 (1만권+ A4 시트).

    Args:
        items: list[dict(call_number, barcode_value)]
        library_name: 자관명
        label_format: 라벨 포맷

    Returns:
        HTML (모든 라벨)
    """
    width_mm, height_mm = LABEL_DIMENSIONS_MM[label_format]
    label_html = []
    for item in items:
        label_html.append(f"""
    <div class="label">
      <div class="library">{library_name}</div>
      <div class="call-number">{item.get('call_number', '')}</div>
      <div class="barcode">*{item.get('barcode_value', '')}*</div>
      <div class="barcode-text">{item.get('barcode_value', '')}</div>
    </div>""")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>일괄 도서 라벨 — {library_name} ({len(items)}건)</title>
<style>
@page {{ size: A4; margin: 10mm; }}
body {{ font-family: 'Pretendard', 'Noto Sans KR', sans-serif; }}
.label {{
  width: {width_mm}mm; height: {height_mm}mm;
  border: 1px solid #999;
  display: inline-block;
  padding: 3mm; box-sizing: border-box;
  page-break-inside: avoid; margin: 1mm; text-align: center;
}}
.library {{ font-size: 8pt; color: #666; }}
.call-number {{ font-size: 14pt; font-weight: bold; margin: 2mm 0; }}
.barcode {{ font-family: 'Libre Barcode 128', monospace; font-size: 36pt; }}
.barcode-text {{ font-size: 9pt; }}
@media print {{ .label {{ border: none; }} }}
</style>
</head>
<body>
{"".join(label_html)}
</body>
</html>"""


__all__ = ["LABEL_DIMENSIONS_MM", "LabelFormat", "render_label_batch_html", "render_label_html"]
