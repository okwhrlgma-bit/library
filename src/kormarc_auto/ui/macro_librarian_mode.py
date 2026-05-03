"""사서 E 매크로 사서 모드 — 5-1 (1순위 ICP·전국 1,500~2,500명).

PO 명령 (12-섹션 §5.1): "기존 매크로 5종이 한 번에"
사서 E (Excel 매크로 자작) = 가장 큰 매출 잠재력 (월 5만원 × 1,500명).

작동:
- 한 화면 = 큰 ISBN 입력창 + "마크 만들기" 버튼
- 출력 = 4 산출물 동시:
  1. .mrc (KOLAS·DLS 반입)
  2. 책단비 hwp (interlibrary/exporters)
  3. 등록번호 12자리 라벨 (output/label_printer)
  4. 월간 보고 한 줄 (output/annual_statistics)
- 클릭 3회 이내 = 첫 화면 → 첫 .mrc
- 5권마다 NPS 1문항 (인라인 피드백)

목표: 사서 E NPS 50+ 수집 (PILOT 검증 후 영업 자료).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class MacroOutputs:
    """매크로 사서 모드 4 산출물."""

    isbn: str
    library_name: str
    mrc_bytes: bytes | None = None
    chaekdanbi_hwp_path: str | None = None
    label_pdf_path: str | None = None
    monthly_report_line: str | None = None
    nps_prompt_due: bool = False  # 5권마다 True
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class MacroSessionStats:
    """세션 누적 통계 (NPS 트리거)."""

    books_processed: int = 0
    nps_responses: list[int] = field(default_factory=list)

    def should_prompt_nps(self) -> bool:
        """5권마다 NPS 프롬프트."""
        return self.books_processed > 0 and self.books_processed % 5 == 0


def process_one_book(
    isbn: str,
    library_name: str,
    *,
    session: MacroSessionStats | None = None,
    builder=None,
    chaekdanbi_writer=None,
    label_printer=None,
    monthly_aggregator=None,
) -> MacroOutputs:
    """1권 ISBN → 4 산출물 동시 생성.

    Args:
        isbn: 13자리
        library_name: 자관명 (라벨·hwp 헤더)
        session: 누적 통계 (NPS 트리거용)
        builder: build_kormarc_record (DI·테스트 mock 가능)
        chaekdanbi_writer: 책단비 hwp 생성 함수
        label_printer: 라벨 PDF 생성 함수
        monthly_aggregator: 월간 통계 함수

    Returns:
        MacroOutputs (4 산출물 경로/바이트)
    """
    session = session or MacroSessionStats()

    # 1. .mrc (실제 builder 호출 = 외부 DI)
    mrc_bytes: bytes | None = None
    if builder is not None:
        try:
            record = builder({"isbn": isbn, "library": library_name})
            mrc_bytes = bytes(record) if record else None
        except Exception:
            mrc_bytes = None

    # 2. 책단비 hwp
    chaekdanbi_path: str | None = None
    if chaekdanbi_writer is not None:
        try:
            chaekdanbi_path = chaekdanbi_writer(isbn=isbn, library=library_name)
        except Exception:
            chaekdanbi_path = None

    # 3. 라벨 PDF
    label_path: str | None = None
    if label_printer is not None:
        try:
            label_path = label_printer(isbn=isbn, library=library_name)
        except Exception:
            label_path = None

    # 4. 월간 보고 한 줄
    monthly_line: str | None = None
    if monthly_aggregator is not None:
        try:
            monthly_line = monthly_aggregator(isbn=isbn, library=library_name)
        except Exception:
            monthly_line = None

    session.books_processed += 1
    nps_due = session.should_prompt_nps()

    return MacroOutputs(
        isbn=isbn,
        library_name=library_name,
        mrc_bytes=mrc_bytes,
        chaekdanbi_hwp_path=chaekdanbi_path,
        label_pdf_path=label_path,
        monthly_report_line=monthly_line,
        nps_prompt_due=nps_due,
    )


def render_one_screen_html(library_name: str, last_outputs: MacroOutputs | None = None) -> str:
    """매크로 사서 모드 한 화면 HTML (Streamlit 컴포넌트 대체용·HTML 자동).

    클릭 3회 이내 = ISBN 입력 → 마크 만들기 → 결과 확인.
    """
    last_section = ""
    if last_outputs:
        last_section = f"""
        <div class="last-result">
          <h3>지난 산출물 (ISBN {last_outputs.isbn})</h3>
          <ul>
            <li>📄 .mrc: {"✅" if last_outputs.mrc_bytes else "❌"}</li>
            <li>📋 책단비 hwp: {last_outputs.chaekdanbi_hwp_path or "❌"}</li>
            <li>🏷 라벨 PDF: {last_outputs.label_pdf_path or "❌"}</li>
            <li>📊 월간 보고: {last_outputs.monthly_report_line or "대기"}</li>
          </ul>
          {"<p>📊 5권 완료 — NPS 응답 부탁드립니다 (1~10)</p>" if last_outputs.nps_prompt_due else ""}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>매크로 사서 모드 — {library_name}</title>
<style>
  body {{ font-family: 'Pretendard', sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
  h1 {{ font-size: 24pt; color: #333; }}
  .input-area {{ margin: 30px 0; }}
  input[type="text"] {{ width: 100%; padding: 16pt; font-size: 18pt; border: 2px solid #555; border-radius: 8px; }}
  button {{ width: 100%; padding: 16pt; font-size: 16pt; background: #2c5; color: white; border: none; border-radius: 8px; cursor: pointer; margin-top: 10pt; }}
  button:hover {{ background: #1a3; }}
  .last-result {{ margin-top: 30px; padding: 15pt; background: #f5f5f5; border-radius: 8px; }}
  .last-result h3 {{ margin-top: 0; }}
  .pitch {{ color: #c00; font-weight: bold; font-size: 14pt; }}
</style>
</head>
<body>
  <h1>📚 매크로 사서 모드 — {library_name}</h1>
  <p class="pitch">기존 Excel 매크로 5종이 한 번에 = 클릭 3회 = 4 산출물 동시</p>

  <div class="input-area">
    <input type="text" id="isbn" placeholder="ISBN 13자리 입력 후 Enter" autofocus>
    <button onclick="processBook()">마크 만들기 (.mrc + hwp + 라벨 + 보고)</button>
  </div>

  {last_section}

  <script>
    document.getElementById('isbn').addEventListener('keypress', (e) => {{
      if (e.key === 'Enter') processBook();
    }});
    function processBook() {{
      const isbn = document.getElementById('isbn').value.trim();
      if (!isbn || isbn.length !== 13) {{
        alert('13자리 ISBN을 입력해주세요');
        return;
      }}
      window.location.href = `/macro/process?isbn=${{isbn}}`;
    }}
  </script>
</body>
</html>
"""


def aggregate_session_nps(session: MacroSessionStats) -> dict:
    """세션 NPS 응답 집계."""
    if not session.nps_responses:
        return {"count": 0, "avg": 0, "promoters": 0, "detractors": 0, "nps": 0}

    promoters = sum(1 for s in session.nps_responses if s >= 9)
    detractors = sum(1 for s in session.nps_responses if s <= 6)
    total = len(session.nps_responses)
    nps = round((promoters - detractors) / total * 100)

    return {
        "count": total,
        "avg": round(sum(session.nps_responses) / total, 2),
        "promoters": promoters,
        "detractors": detractors,
        "nps": nps,
    }


__all__ = [
    "MacroOutputs",
    "MacroSessionStats",
    "aggregate_session_nps",
    "process_one_book",
    "render_one_screen_html",
]
