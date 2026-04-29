"""KORMARC 2023.12 적용 수준 (M/A/O) 자동 판정.

KS X 6006-0:2023.12 (NLK 2차 개정) 정합. 9 자료유형별 필드 적용 수준 분기.

- M (Mandatory): 누락 시 4단 검증 fail
- A (Mandatory if applicable): 조건 충족 시 필수
- O (Optional): 사서 자유

출처: docs/research/part2-kormarc-implementation.md §1.3
"""

from __future__ import annotations

from typing import Any

from kormarc_auto.vernacular.hanja_converter import has_hanja

# KORMARC 2023.12 + 한국 실무 (KOLAS) 정합 — 모든 자료유형 공통 필수
# 주의: 260/264 둘 중 하나, 049/056/090 중 하나는 있어야 함 (validate에서 OR 처리)
M_FIELDS: frozenset[str] = frozenset({
    "005", "008", "020", "245", "300",
})

# OR 관계 필드 그룹 (그룹 내 1개 이상 있으면 정합)
M_FIELD_GROUPS: tuple[tuple[str, ...], ...] = (
    ("260", "264"),  # 발행사항 (옛 260 또는 RDA 264)
    ("049", "056", "090"),  # 분류·자관 청구기호 (1 이상)
    ("007", "008"),  # 통제 (008은 위 M에도 있어 중복 보장)
)

# A 관계 OR 그룹 — 시리즈 표시는 440 또는 490 둘 다 가능
A_FIELD_GROUPS: dict[str, tuple[str, ...]] = {
    "series": ("440", "490"),
}


def _has_hanja_anywhere(book_data: dict[str, Any]) -> bool:
    """본표제·부표제·저자명·시리즈명 어디에든 한자 존재 여부."""
    fields = ("title", "subtitle", "author", "series_title", "publisher")
    return any(has_hanja(str(book_data.get(f) or "")) for f in fields)


def determine_application_level(
    field_tag: str,
    book_data: dict[str, Any],
    material_type: str,
) -> str:
    """필드별 적용 수준 자동 결정.

    Args:
        field_tag: KORMARC 필드 태그 (예: "245", "880").
        book_data: 외부 API에서 통합한 서지 dict.
        material_type: `kormarc.material_type` 키 (예: "book_single", "thesis").

    Returns:
        "M" | "A" | "O".
    """
    if field_tag in M_FIELDS:
        return "M"

    # 한국 KOLAS 실무 정합 — 336/337/338 (RDA)는 표준 권장이나 실측 0% 적용,
    # 자관 PILOT에서 strict 모드 별도 검증. default = False.
    a_rules: dict[str, bool] = {
        "022": material_type.startswith("serial"),
        "041": len(book_data.get("languages") or []) > 1,
        "082": bool(book_data.get("ddc")),
        "336": False,  # RDA 매체 (한국 실무 미적용)
        "337": False,  # RDA 내용
        "338": False,  # RDA 전달
        # 시리즈 표시 — 440 또는 490 둘 다 가능 (validate에서 OR 처리)
        "440": bool(book_data.get("series_title")),
        "490": bool(book_data.get("series_title")),
        "538": material_type in {"ebook", "audiobook", "dvd", "music_cd"},
        "502": material_type == "thesis",
        "880": _has_hanja_anywhere(book_data),
    }
    if field_tag in a_rules:
        return "A" if a_rules[field_tag] else "O"
    return "O"


def validate_application_level(
    present_tags: set[str],
    book_data: dict[str, Any],
    material_type: str,
) -> list[tuple[str, str, str]]:
    """레코드 내 존재 필드 집합 vs M/A/O 정합 검증.

    Args:
        present_tags: 레코드에 실제 존재하는 필드 태그 집합.
        book_data: 외부 API에서 통합한 서지 dict.
        material_type: `kormarc.material_type` 키.

    Returns:
        위반 목록 `[(tag, level, reason)]`. 비어 있으면 정합.
    """
    issues: list[tuple[str, str, str]] = []

    for tag in M_FIELDS:
        if tag not in present_tags:
            issues.append((tag, "M", f"필수 필드 누락 ({material_type})"))

    for group in M_FIELD_GROUPS:
        if not any(tag in present_tags for tag in group):
            issues.append(
                ("/".join(group), "M", f"OR 그룹 모두 누락 ({material_type})")
            )

    # 단일 A 후보 (OR 그룹 외)
    single_a_candidates = ("022", "041", "082", "336", "337", "338", "538", "502", "880")
    for tag in single_a_candidates:
        level = determine_application_level(tag, book_data, material_type)
        if level == "A" and tag not in present_tags:
            issues.append((tag, "A", f"적용 조건 충족 but 누락 ({material_type})"))

    # A OR 그룹 (시리즈는 440 또는 490 중 1개 있으면 OK)
    if book_data.get("series_title") and not any(
        tag in present_tags for tag in A_FIELD_GROUPS["series"]
    ):
        issues.append(
            ("/".join(A_FIELD_GROUPS["series"]), "A",
             f"시리즈 표시 OR 그룹 모두 누락 ({material_type})"),
        )

    return issues
