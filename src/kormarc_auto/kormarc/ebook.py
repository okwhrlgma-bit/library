"""KORMARC 전자책 (ebook) 빌더 — Phase 1.5.

KORMARC 2023.12 5번째 자료유형 (전자책):
- LDR 06=m (컴퓨터 파일·전자책)
- LDR 07=m (단행본 단위)
- 008 06=s (단일발행) 또는 m (다권물)
- 008 23=o (온라인) 또는 q (직접 접근·USB·CD)
- 856 ▾u URL·▾y 안내 (필수)
- 538 ▾a 시스템 사양·요구 (예: "PDF·EPUB")
- 020 ▾a ISBN-13 또는 ISBN-A (전자책 별도 ISBN)

자관 사례: 「○○도서관」은 전자책 직접 소장 X (책이음 통합)
→ 본 모듈은 다른 자관 PILOT (대학·사립·공공) 시 활용.
"""

from __future__ import annotations

from typing import Any

from pymarc import Field, Indicators, Subfield


def build_ebook_fields(book_data: dict[str, Any]) -> list[Field]:
    """전자책 특화 필드 (008 보강·538·856) → Field 리스트.

    Args:
        book_data: 통합 dict (`isbn`·`title`·`url`·`format`·`access_type`)

    Returns:
        856 (URL)·538 (시스템) 필드 리스트.
    """
    fields: list[Field] = []

    # 856 — 전자 자원 위치 (필수)
    if url := book_data.get("url"):
        subfields = [Subfield(code="u", value=url)]
        if guide := book_data.get("url_guide"):
            subfields.append(Subfield(code="y", value=guide))
        fields.append(
            Field(
                tag="856",
                indicators=Indicators("4", "0"),  # HTTP·자원 자체
                subfields=subfields,
            )
        )

    # 538 — 시스템 사양 (PDF·EPUB·앱 등)
    if fmt := book_data.get("format"):
        fields.append(
            Field(
                tag="538",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=f"{fmt} 형식")],
            )
        )

    return fields


def derive_008_23(access_type: str) -> str:
    """008 23번째 자리 (자료형태) — 전자책 분기.

    Args:
        access_type: "online" | "offline" (USB·CD·DVD)

    Returns:
        "o" (온라인) | "q" (직접 접근·미디어).
    """
    return "o" if access_type == "online" else "q"


__all__ = ["build_ebook_fields", "derive_008_23"]
