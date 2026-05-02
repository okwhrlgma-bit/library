"""KORMARC 멀티미디어 (multimedia) 빌더 — Phase 1.5.

KORMARC 2023.12 8번째 자료유형 (시청각자료·DVD·CD·블루레이·온라인 영상):
- LDR 06=g (시청각자료)
- LDR 07=m (단행본 단위)
- 008 06=s (단일발행) 또는 m (다권물)
- 008 33-34 자료특성 부호 (v=비디오, c=오디오, k=정지영상 등)
- 007 ▾a v ▾b d (DVD) ▾b f (블루레이) ▾b z (스트리밍)
- 300 ▾a 매체 단위 + ▾b 종류 + ▾c 크기 (예: "DVD 1매 ▾b 컬러·유성 ▾c 12 cm")
- 306 ▾a 재생시간 (HHMMSS, 예: "010500" = 1시간 5분)
- 538 ▾a 매체·재생 시스템 (예: "NTSC·Region 3·돌비 5.1")
- 856 ▾u URL (스트리밍·OTT)
"""

from __future__ import annotations

from typing import Any

from pymarc import Field, Indicators, Subfield

# 008 33 카테고리 부호 (시청각)
MEDIA_TYPE_CODES: dict[str, str] = {
    "video": "v",  # 비디오 (영화·드라마)
    "motion_picture": "m",  # 영화 필름
    "slide": "s",  # 슬라이드
    "photo": "k",  # 정지영상·사진
    "graphic": "i",  # 그래픽
    "kit": "b",  # 키트 (복합)
}


def build_multimedia_fields(media_data: dict[str, Any]) -> list[Field]:
    """멀티미디어 특화 필드 (007·300·306·538·856) → Field 리스트.

    Args:
        media_data: 통합 dict (`format`·`runtime`·`region`·`color`·`url`·`unit_count`)

    Returns:
        007·300·306·538·856 필드 리스트.
    """
    fields: list[Field] = []

    # 007 — 매체 부호 (비디오 v + 매체 종류)
    media_format = media_data.get("format", "DVD").upper()
    media_byte = {
        "DVD": "vd",
        "BLURAY": "vd",
        "BD": "vd",
        "VHS": "vf",
        "스트리밍": "vz",
        "STREAM": "vz",
    }.get(media_format, "vd")
    fields.append(Field(tag="007", data=media_byte))

    # 300 — 형태사항 (매체 단위·종류·크기)
    unit_count = media_data.get("unit_count", 1)
    color = media_data.get("color", "컬러")
    size = media_data.get("size_cm", "12 cm")
    sound = media_data.get("sound", "유성")
    subfields_300 = [
        Subfield(code="a", value=f"{media_format} {unit_count}매"),
        Subfield(code="b", value=f"{color}·{sound}"),
        Subfield(code="c", value=size),
    ]
    fields.append(
        Field(
            tag="300",
            indicators=Indicators(" ", " "),
            subfields=subfields_300,
        )
    )

    # 306 — 재생시간 (HHMMSS)
    if runtime := media_data.get("runtime"):
        fields.append(
            Field(
                tag="306",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value=_normalize_runtime(runtime))],
            )
        )

    # 538 — 매체 사양 (NTSC·Region·돌비)
    spec_parts: list[str] = []
    if signal := media_data.get("signal"):  # NTSC·PAL·SECAM
        spec_parts.append(signal)
    if region := media_data.get("region"):
        spec_parts.append(f"Region {region}")
    if audio := media_data.get("audio_spec"):
        spec_parts.append(audio)
    if spec_parts:
        fields.append(
            Field(
                tag="538",
                indicators=Indicators(" ", " "),
                subfields=[Subfield(code="a", value="·".join(spec_parts))],
            )
        )

    # 856 — URL (스트리밍·OTT)
    if url := media_data.get("url"):
        fields.append(
            Field(
                tag="856",
                indicators=Indicators("4", "0"),
                subfields=[Subfield(code="u", value=url)],
            )
        )

    return fields


def _normalize_runtime(runtime: str | int) -> str:
    """재생시간 → HHMMSS 6자리.

    수용 입력: 90 (분 정수) · "90분" · "1:30:00" · "010500" (이미 정규형)
    """
    if isinstance(runtime, int):
        hours = runtime // 60
        minutes = runtime % 60
        return f"{hours:02d}{minutes:02d}00"

    s = str(runtime).strip()
    if len(s) == 6 and s.isdigit():
        return s
    if s.endswith("분") and s[:-1].strip().isdigit():
        total_min = int(s[:-1].strip())
        hours, minutes = divmod(total_min, 60)
        return f"{hours:02d}{minutes:02d}00"
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            h, m, sec = (int(p) for p in parts)
            return f"{h:02d}{m:02d}{sec:02d}"
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            h, m = (int(p) for p in parts)
            return f"{h:02d}{m:02d}00"
    return "000000"


def derive_008_33(media_type: str) -> str:
    """008 33 자료특성 부호 (1자리)."""
    return MEDIA_TYPE_CODES.get(media_type, " ")


__all__ = [
    "MEDIA_TYPE_CODES",
    "build_multimedia_fields",
    "derive_008_33",
]
