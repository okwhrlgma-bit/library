"""KOLAS III 호환 .mrc 출력.

KOLAS III 자동 반입 규칙: 파일명이 ISBN과 동일하면 자동 인식.
인코딩: UTF-8 (KOLAS III는 유니코드 3.0 기반).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from pymarc import Record

logger = logging.getLogger(__name__)


def write_kolas_mrc(
    record: Record,
    isbn: str,
    *,
    output_dir: str | Path | None = None,
) -> Path:
    """KORMARC 레코드를 KOLAS 자동 반입 형식의 .mrc 파일로 저장.

    Args:
        record: pymarc.Record
        isbn: 13자리 ISBN (파일명으로 사용 — KOLAS 자동 인식 규칙)
        output_dir: 출력 폴더. 미지정 시 KORMARC_OUTPUT_DIR 환경변수 또는 ./output

    Returns:
        생성된 파일 경로

    Raises:
        ValueError: ISBN 형식 오류
        OSError: 파일 쓰기 실패
    """
    isbn_clean = "".join(c for c in isbn if c.isdigit())
    if len(isbn_clean) != 13:
        raise ValueError(f"ISBN은 13자리여야 합니다 (입력: {isbn})")

    out_dir = Path(output_dir or os.getenv("KORMARC_OUTPUT_DIR", "./output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{isbn_clean}.mrc"

    binary = record.as_marc()  # ISO 2709 binary
    out_path.write_bytes(binary)

    logger.info("KORMARC .mrc 저장: %s (%d bytes)", out_path, len(binary))
    return out_path
