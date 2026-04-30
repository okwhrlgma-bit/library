"""책단비 (은평구 한정) 상호대차 라벨 자동 생성기 — Phase 1.5+.

자관 5년 1,328건 (거의 매일 1건 수동) → 자동화. ROI 1순위 (`docs/sales/INDEX.md`).

핵심 설계 (ADR-0020):
1. python-hwpx 선택 의존성 (try/except). 미설치 시 .txt 폴백.
2. KORMARC dict → ChaekdanbiLabel dataclass → hwpx 또는 txt.
3. 라벨 양식 변경에 강함 — generate_label_text() 한 함수가 텍스트 청사진 생성.

사용 예 (사서 PILOT 1주차):
    label = ChaekdanbiLabel(
        title="작별하지 않는다",
        author="한강",
        isbn="9788936434120",
        registration_no="EQ012345",
        call_number="813.7-한31ㅈ",
        target_library="은평구립도서관",
        request_date="2026-05-01",
    )
    out = generate_label(label, Path("출력/책단비_20260501.hwpx"))
    # out.hwpx 또는 out.txt (의존성에 따라)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


# python-hwpx는 선택 의존성 — 미설치 시 .txt 폴백
try:
    import hwpx  # type: ignore[import-not-found]

    HAS_HWPX = True
except ImportError:
    HAS_HWPX = False


@dataclass(frozen=True)
class ChaekdanbiLabel:
    """책단비 상호대차 라벨 한 장."""

    title: str
    author: str
    isbn: str
    registration_no: str
    call_number: str
    target_library: str
    request_date: str
    return_date: str = ""
    note: str = ""
    source_library: str = "내를건너서 숲으로 도서관"
    extra: dict[str, str] = field(default_factory=dict)


def from_kormarc_dict(record: dict, *, target_library: str, request_date: str) -> ChaekdanbiLabel:
    """KORMARC 통합 dict → ChaekdanbiLabel.

    Args:
        record: aggregator.aggregate_by_isbn() 결과 또는 호환 dict.
        target_library: 책단비 회원관 (예: "은평구립도서관").
        request_date: 신청일 (YYYY-MM-DD).

    Returns:
        ChaekdanbiLabel 인스턴스.
    """
    return ChaekdanbiLabel(
        title=record.get("title", ""),
        author=record.get("author", ""),
        isbn=record.get("isbn", ""),
        registration_no=record.get("registration_no", record.get("reg_no", "")),
        call_number=record.get("call_number", ""),
        target_library=target_library,
        request_date=request_date,
    )


def generate_label_text(label: ChaekdanbiLabel) -> str:
    """라벨 청사진 (텍스트). hwpx·txt 양쪽이 공유하는 단일 진실 소스."""
    lines = [
        "─" * 40,
        "책단비 상호대차 신청서",
        "─" * 40,
        f"신청일자  : {label.request_date}",
        f"반납예정  : {label.return_date or '(미정)'}",
        f"제공도서관: {label.source_library}",
        f"요청도서관: {label.target_library}",
        "─" * 40,
        f"표  제   : {label.title}",
        f"저  자   : {label.author}",
        f"ISBN     : {label.isbn}",
        f"청구기호  : {label.call_number}",
        f"등록번호  : {label.registration_no}",
    ]
    if label.note:
        lines.extend(["─" * 40, f"비  고   : {label.note}"])
    if label.extra:
        lines.append("─" * 40)
        lines.extend(f"{k:9}: {v}" for k, v in label.extra.items())
    lines.append("─" * 40)
    return "\n".join(lines) + "\n"


def generate_label(label: ChaekdanbiLabel, output_path: Path) -> Path:
    """책단비 라벨 1장 생성 → 파일 경로 반환.

    python-hwpx 설치 시 .hwpx 생성. 미설치 시 같은 이름의 .txt 폴백.
    사서가 직접 hwp로 열어 출력 또는 .txt를 hwp에 붙여넣기.

    Args:
        label: ChaekdanbiLabel 인스턴스.
        output_path: 원하는 출력 경로 (.hwpx 권장).

    Returns:
        실제 작성된 파일 경로 (의존성 미충족 시 .txt 변경됨).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = generate_label_text(label)

    if HAS_HWPX:
        try:
            return _write_hwpx(text, output_path)
        except Exception as e:
            logger.warning("hwpx 작성 실패 — .txt 폴백: %s", e)

    txt_path = output_path.with_suffix(".txt")
    txt_path.write_text(text, encoding="utf-8")
    return txt_path


def _write_hwpx(text: str, output_path: Path) -> Path:
    """python-hwpx로 .hwpx 작성 (HAS_HWPX=True 시에만 호출).

    실제 hwpx API는 라이브러리 버전에 따라 변할 수 있어 좁은 어댑터 1곳에
    캡슐화. 미지원 케이스는 호출부가 .txt 폴백 처리.
    """
    if not HAS_HWPX:  # pragma: no cover — 호출부 가드
        raise RuntimeError("python-hwpx 미설치")
    doc = hwpx.HwpxDocument()  # type: ignore[attr-defined]
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(str(output_path))
    return output_path


__all__ = [
    "HAS_HWPX",
    "ChaekdanbiLabel",
    "from_kormarc_dict",
    "generate_label",
    "generate_label_text",
]
