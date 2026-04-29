"""KORMARC 오디오북 (audiobook) 빌더 — Phase 1.5.

KORMARC 2023.12 7번째 자료유형 (오디오북·낭독):
- LDR 06=i (음향자료·낭독·강연)
- LDR 07=m (단행본 단위)
- 008 06=s (단일발행) 또는 m (다권물)
- 008 23=o (온라인) 또는 s (음향 매체·MP3·CD)
- 007 ▾a s (음향) ▾b s (스트리밍) 등
- 538 ▾a 음향 매체·재생 시스템 (예: "MP3·64kbps·총 8시간")
- 856 ▾u URL (스트리밍 시)
- 511 ▾a 낭독자 (예: "낭독: 김연아")
"""

from __future__ import annotations

from typing import Any

from pymarc import Field, Indicators, Subfield


def build_audiobook_fields(audio_data: dict[str, Any]) -> list[Field]:
    """오디오북 특화 필드 (007·538·511·856) → Field 리스트.

    Args:
        audio_data: 통합 dict (`isbn`·`title`·`narrator`·`duration`·`format`·`url`)

    Returns:
        007·538·511·856 필드 리스트.
    """
    fields: list[Field] = []

    # 007 — 자료 매체 부호 (음향)
    fields.append(
        Field(tag="007", data="ss"),  # s=음향·s=스트리밍 (단순)
    )

    # 538 — 매체·재생 시스템
    spec_parts: list[str] = []
    if fmt := audio_data.get("format"):
        spec_parts.append(fmt)
    if duration := audio_data.get("duration"):
        spec_parts.append(f"총 {duration}")
    if spec_parts:
        fields.append(
            Field(
                tag="538",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value="·".join(spec_parts))],
            )
        )

    # 511 — 낭독자·연주자 정보
    if narrator := audio_data.get("narrator"):
        fields.append(
            Field(
                tag="511",
                indicators=Indicators("0", " "),  # 일반 낭독자
                subfields=[Subfield(code="a", value=f"낭독: {narrator}")],
            )
        )

    # 856 — URL (스트리밍)
    if url := audio_data.get("url"):
        fields.append(
            Field(
                tag="856",
                indicators=Indicators("4", "0"),
                subfields=[Subfield(code="u", value=url)],
            )
        )

    return fields


def derive_008_23(access_type: str) -> str:
    """008 23번째 자리 (자료형태) — 오디오북 분기.

    Args:
        access_type: "online" (스트리밍) | "offline" (CD·MP3 파일)

    Returns:
        "o" (온라인) | "s" (음향 매체).
    """
    return "o" if access_type == "online" else "s"


__all__ = ["build_audiobook_fields", "derive_008_23"]
