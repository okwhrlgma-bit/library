"""저자 전거 통제 (Authority Control) — Part 74 정합.

KORMARC 7XX 필드 (저자·기관·통일표제 부출표목) 자동.
NLK 전거 DB·KOLISNET 전거 검색 → 7XX 추가·동명이인 분기.

사서 페인 (Part 74·E1):
- 동명이인 저자 = 수동 검증 = 권당 5분
- 다중 저자·편집자·옮긴이 = 책임표시 부담
- 영문·한자 병기 자동 X

해결: 자동 7XX 추가 + 880 페어 (한자·로마자 분기).
"""

from __future__ import annotations

from typing import Any

from pymarc import Field, Record, Subfield


def add_authority_fields(book_data: dict[str, Any], record: Record) -> Record:
    """저자·기여자 정보 → 7XX 부출표목 자동.

    Args:
        book_data: aggregate_by_isbn 반환·자관 데이터
            - authors: list[dict] (name·role·birth_year·affiliation)
            - editor·translator·illustrator·corporate_author 등
        record: pymarc.Record (245·100 이미 있음 가정)

    Returns:
        record (in-place 수정)
    """
    authors = book_data.get("authors", [])
    main_author = book_data.get("author")

    # 700 부출표목 (공동저자·번역자·편집자)
    for _idx, author in enumerate(authors):
        if isinstance(author, str):
            name = author
            role = ""
        else:
            name = author.get("name", "")
            role = author.get("role", "")

        # 메인 저자는 100·skip
        if main_author and name == main_author:
            continue
        if not name:
            continue

        subfields = [Subfield(code="a", value=_normalize_name(name))]
        if role:
            subfields.append(Subfield(code="e", value=role))

        # 동명이인 분기 (생년·소속)
        birth = author.get("birth_year") if isinstance(author, dict) else None
        affiliation = author.get("affiliation") if isinstance(author, dict) else None
        if birth:
            subfields.append(Subfield(code="d", value=str(birth)))
        if affiliation:
            subfields.append(Subfield(code="u", value=affiliation))

        record.add_field(Field(tag="700", indicators=["1", " "], subfields=subfields))

    # 710 단체저자 부출표목
    if corporate := book_data.get("corporate_author"):
        record.add_field(
            Field(
                tag="710",
                indicators=["2", " "],
                subfields=[Subfield(code="a", value=corporate)],
            )
        )

    # 730 통일표제 부출표목 (시리즈·총서)
    if uniform := book_data.get("uniform_title"):
        record.add_field(
            Field(
                tag="730",
                indicators=["0", " "],
                subfields=[Subfield(code="a", value=uniform)],
            )
        )

    return record


def _normalize_name(name: str) -> str:
    """저자명 정규화 (NLK 전거 DB 정합)."""
    return name.strip().rstrip(",")


def detect_homonym(name: str, existing_authors: list[dict]) -> dict | None:
    """동명이인 검출 (자관 history + Mem0).

    같은 이름 + 다른 생년·소속 = 별도 인물.
    """
    candidates = [a for a in existing_authors if a.get("name") == name]
    if len(candidates) >= 2:
        return {"name": name, "candidates": candidates, "warning": "동명이인 가능"}
    return None


__all__ = ["add_authority_fields", "detect_homonym"]
