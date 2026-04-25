"""독서로DLS (학교도서관) 호환 출력.

DLS는 MARC 반입 기능 보유. 자료유형 자동 판단 (단행본/연속간행물/비도서/장학자료/기타).
DLS 추가 권장 필드:
- 521 ▾a 추천 학년·이용 대상 (있으면)
- 526 ▾a 교과 연계 (학습참고서)
- 049 ▾l 등록번호 (학교는 학교별 규칙)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from pymarc import Field, Indicators, Record, Subfield

logger = logging.getLogger(__name__)


def write_dls_mrc(
    record: Record,
    isbn: str,
    *,
    output_dir: str | Path | None = None,
    target_grade: str | None = None,
) -> Path:
    """DLS 호환 .mrc 출력.

    Args:
        record: pymarc.Record
        isbn: 13자리 ISBN (파일명)
        output_dir: 출력 폴더 (기본 KORMARC_DLS_OUTPUT_DIR 또는 ./output/dls)
        target_grade: "초3-6" / "중1-3" / "고1-3" 등. 있으면 521 필드 자동 추가.

    Returns:
        생성된 .mrc 경로
    """
    isbn_clean = "".join(c for c in isbn if c.isdigit())
    if len(isbn_clean) != 13:
        raise ValueError(f"ISBN은 13자리여야 합니다 (입력: {isbn})")

    if target_grade and not record.get_fields("521"):
        record.add_field(
            Field(
                tag="521",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=target_grade)],
            )
        )

    out_dir = Path(output_dir or os.getenv("KORMARC_DLS_OUTPUT_DIR", "./output/dls"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{isbn_clean}.mrc"

    binary = record.as_marc()
    out_path.write_bytes(binary)
    logger.info("DLS KORMARC .mrc 저장: %s (%d bytes)", out_path, len(binary))
    return out_path
