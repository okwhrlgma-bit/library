"""시리즈·권차·통일표제 — Part 74 정합.

KORMARC 4XX (시리즈사항) + 8XX (시리즈 부출표목) 자동.
같은 시리즈 = 자동 그룹화·권차 자동.

사서 페인 (Part 74·E1):
- 시리즈물 = 권차 수동·통일표제 X
- 사서 = 시리즈마다 별도 처리

해결: 자동 4XX + 8XX·권차 자동 추출.
"""
from __future__ import annotations

import re
from typing import Any

from pymarc import Field, Record, Subfield


def add_series_fields(book_data: dict[str, Any], record: Record) -> Record:
    """시리즈·권차·통일표제 자동.

    Args:
        book_data:
            - series·series_title: 시리즈명
            - volume·volume_no: 권차 (예: 3, "3권", "v.3")
            - uniform_title: 통일표제
        record: pymarc.Record

    Returns:
        record (in-place)
    """
    series = book_data.get("series") or book_data.get("series_title")
    volume = book_data.get("volume") or book_data.get("volume_no")

    if not series:
        return record

    # 권차 정규화 (3, "3권", "v.3" → "v.3")
    vol_str = _normalize_volume(volume) if volume else ""

    # 490 시리즈사항 (인쇄형)
    series_subfields = [Subfield(code="a", value=series)]
    if vol_str:
        series_subfields.append(Subfield(code="v", value=vol_str))
    record.add_field(
        Field(tag="490", indicators=["0", " "], subfields=series_subfields)
    )

    # 830 시리즈 부출표목 (검색 가능 통일표제)
    uniform_subfields = [Subfield(code="a", value=series)]
    if vol_str:
        uniform_subfields.append(Subfield(code="v", value=vol_str))
    record.add_field(
        Field(tag="830", indicators=[" ", "0"], subfields=uniform_subfields)
    )

    return record


def _normalize_volume(volume: Any) -> str:
    """권차 정규화 → 'v.N' 형식."""
    if isinstance(volume, int):
        return f"v.{volume}"

    text = str(volume).strip()
    # "3권"·"제3권"·"v.3"·"3" 모두 처리
    match = re.search(r"(\d+)", text)
    if match:
        return f"v.{match.group(1)}"
    return text


__all__ = ["add_series_fields"]
