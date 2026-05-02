"""외부 .mrc / MARCXML 일괄 import — 다른 도서관 시스템에서 갈아탈 때.

KOLASYS-NET / DLS / Koha 등에서 받은 .mrc 파일을 우리 도구의 자관 인덱스로 가져옴.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from kormarc_auto.inventory.library_db import add_record

logger = logging.getLogger(__name__)


def import_mrc_file(path: str | Path) -> list[dict[str, Any]]:
    """.mrc 파일에서 모든 레코드 추출 → 자관 인덱스 추가.

    Returns:
        추가된 레코드 요약 리스트
    """
    from pymarc import MARCReader

    p = Path(path)
    if not p.exists():
        logger.warning("파일 없음: %s", p)
        return []

    out: list[dict[str, Any]] = []
    try:
        with p.open("rb") as f:
            reader = MARCReader(f, force_utf8=True)
            for record in reader:
                if record is None:
                    continue
                book_data = _record_to_book_data(record)
                rid = add_record(book_data, mrc_path=str(p))
                out.append({"id": rid, **book_data})
    except Exception as e:
        logger.warning(".mrc 파싱 실패: %s — %s", p, e)
        return out

    logger.info(".mrc import: %s → %d 레코드", p, len(out))
    return out


def import_marcxml_file(path: str | Path) -> list[dict[str, Any]]:
    """MARCXML 파일 일괄 import."""
    from pymarc import marcxml

    p = Path(path)
    if not p.exists():
        return []

    out: list[dict[str, Any]] = []
    try:
        records = marcxml.parse_xml_to_array(str(p))
        for record in records:
            if record is None:
                continue
            book_data = _record_to_book_data(record)
            rid = add_record(book_data, mrc_path=str(p))
            out.append({"id": rid, **book_data})
    except Exception as e:
        logger.warning("MARCXML 파싱 실패: %s — %s", p, e)
        return out

    return out


def import_directory(directory: str | Path) -> dict[str, Any]:
    """폴더 안 모든 .mrc + .xml 일괄 import."""
    d = Path(directory)
    if not d.is_dir():
        return {"total": 0, "files": []}

    file_results: list[dict[str, Any]] = []
    total = 0
    for mrc in d.glob("*.mrc"):
        records = import_mrc_file(mrc)
        file_results.append({"file": str(mrc), "count": len(records)})
        total += len(records)
    for xml in d.glob("*.xml"):
        records = import_marcxml_file(xml)
        file_results.append({"file": str(xml), "count": len(records)})
        total += len(records)

    return {"total": total, "files": file_results}


def _record_to_book_data(record: Any) -> dict[str, Any]:
    """pymarc.Record → BookData dict."""

    def _sf(tag: str, code: str) -> str | None:
        for f in record.get_fields(tag):
            for sf in f.subfields:
                if sf.code == code:
                    return sf.value
        return None

    return {
        "isbn": _sf("020", "a"),
        "title": _sf("245", "a"),
        "subtitle": _sf("245", "b"),
        "author": _sf("100", "a") or _sf("700", "a"),
        "publisher": _sf("264", "b") or _sf("260", "b"),
        "publication_year": _sf("264", "c") or _sf("260", "c"),
        "kdc": _sf("056", "a"),
        "ddc": _sf("082", "a"),
        "registration_no": _sf("049", "l"),
        "call_number": _sf("049", "a"),
    }
