"""배치 결과 CSV 요약 출력.

배치 처리 결과(여러 ISBN의 변환 성공/실패 + 메타)를 한 CSV로 정리해
사서가 Excel/한글에서 확인·정리하기 쉽게 한다.
"""

from __future__ import annotations

import csv
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


CSV_FIELDS = [
    "isbn",
    "ok",
    "title",
    "author",
    "publisher",
    "publication_year",
    "kdc",
    "confidence",
    "field_count",
    "validation_errors",
    "sources",
    "out_path",
    "reason",
]


def write_batch_csv(
    rows: list[dict[str, Any]],
    *,
    output_path: str | Path | None = None,
) -> Path:
    """배치 결과를 CSV로 저장.

    Args:
        rows: 각 ISBN의 처리 결과 dict 리스트.
              필요 키: isbn, ok, (성공 시) title/author/publisher/publication_year/kdc/
              confidence/field_count/validation_errors/sources/out_path,
              (실패 시) reason
        output_path: 출력 파일 경로 (기본 ./output/batch_summary.csv)

    Returns:
        생성된 CSV 파일 경로 (Excel 호환 utf-8-sig)
    """
    out = Path(output_path or os.getenv("KORMARC_CSV_OUT", "./output/batch_summary.csv"))
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            normalized = dict(row)
            if isinstance(normalized.get("validation_errors"), list):
                normalized["validation_errors"] = "; ".join(normalized["validation_errors"])
            if isinstance(normalized.get("sources"), list):
                normalized["sources"] = ",".join(normalized["sources"])
            writer.writerow(normalized)

    logger.info("배치 CSV 저장: %s (%d rows)", out, len(rows))
    return out


# KOLASYS-NET / 일반 도서관 시스템 CSV 일괄 업로드 형식
# 사서가 "Excel 파일로 모은 후 한꺼번에 자기 시스템에 업로드"하는 흐름 지원
KOLASYS_FIELDS = [
    "ISBN",
    "표제",
    "부표제",
    "저자",
    "역자_부저자",
    "출판사",
    "발행지",
    "발행연도",
    "페이지",
    "크기",
    "정가",
    "KDC",
    "DDC",
    "주제명",
    "총서명",
    "권차",
    "요약",
    "출처",
]


def write_kolasys_csv(
    book_data_list: list[dict[str, Any]],
    *,
    output_path: str | Path | None = None,
) -> Path:
    """KOLASYS-NET·일반 도서관 시스템에 일괄 업로드 가능한 CSV.

    사서가 한 번에 30~100권을 자기 도서관 시스템에 들여올 때 사용.
    Excel/한글에서 열어 검토 → 본인 시스템 가져오기 메뉴로 업로드.

    Args:
        book_data_list: aggregator 결과 dict 리스트
        output_path: 출력 경로 (기본 ./output/kolasys_upload.csv)

    Returns:
        utf-8-sig CSV 경로 (Excel 한글 호환)
    """
    out = Path(output_path or os.getenv("KORMARC_KOLASYS_OUT", "./output/kolasys_upload.csv"))
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KOLASYS_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for bd in book_data_list:
            authors = (bd.get("author") or "").strip()
            primary, additional = authors.split(";", 1) if ";" in authors else (authors, "")
            row = {
                "ISBN": bd.get("isbn") or "",
                "표제": bd.get("title") or "",
                "부표제": bd.get("subtitle") or "",
                "저자": primary.strip(),
                "역자_부저자": additional.strip().lstrip(";").strip(),
                "출판사": bd.get("publisher") or "",
                "발행지": bd.get("publication_place") or "",
                "발행연도": bd.get("publication_year") or "",
                "페이지": bd.get("pages") or "",
                "크기": bd.get("book_size") or "",
                "정가": bd.get("price") or "",
                "KDC": bd.get("kdc") or "",
                "DDC": bd.get("ddc") or "",
                "주제명": ", ".join(bd.get("keywords", [])) if bd.get("keywords") else "",
                "총서명": bd.get("series_title") or "",
                "권차": bd.get("series_no") or "",
                "요약": (bd.get("summary") or "")[:500],
                "출처": ",".join(bd.get("sources", [])),
            }
            writer.writerow(row)

    logger.info("KOLASYS CSV 저장: %s (%d rows)", out, len(book_data_list))
    return out
