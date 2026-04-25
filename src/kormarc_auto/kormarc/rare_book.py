"""고서 KORMARC 처리 — NL Korea 「고서용기술규칙」 기반.

고서 = 1900년 이전 한국·중국·일본 전적 등.
한국 도서관계는 KORMARC 고서용 별도 형식 사용.

핵심 차이 (단행본 대비):
- 008 06 = 'a' (모노그래프) 같으나 28 (정부간행물 부호) 다름
- 245 표제는 한자 그대로 + ▾a 한자, ▾h [필사본]/[목판본] 등 형식
- 246 한글 변형표제 자동
- 250 판차 (간행본·필사본·중인본 등)
- 260 ▾a 발행지 + ▾b 출판자 + ▾c 발행연도 (干支 가능)
- 300 ▾a 葉(엽) 또는 권수 + ▾c 크기
- 500 일반주기 (장정·서지 정보)
- 561 소장이력 (구장자)
- 740 분출표목 (편명·자호 등)
"""

from __future__ import annotations

from pymarc import Field, Indicators, Record, Subfield

# 고서 형식 매체 부호
RARE_FORMATS = {
    "wood_print": "[목판본]",
    "movable_type_metal": "[금속활자본]",
    "movable_type_wood": "[목활자본]",
    "manuscript": "[필사본]",
    "lithograph": "[석판본]",
    "rubbing": "[탁본]",
    "modern_reprint": "[영인본]",
}


def add_rare_book_title(
    record: Record,
    *,
    title_hanja: str,
    title_korean: str | None = None,
    format_type: str | None = None,
) -> None:
    """245 고서 표제 + 246 한글 변형표제.

    Args:
        title_hanja: 한자 본표제 (예: '論語')
        title_korean: 한글 변형 (예: '논어')
        format_type: 'wood_print', 'manuscript' 등 (▾h 형식)
    """
    if not title_hanja:
        return

    sf_245 = [Subfield(code="a", value=title_hanja)]
    if format_type and format_type in RARE_FORMATS:
        sf_245.append(Subfield(code="h", value=RARE_FORMATS[format_type]))

    record.add_field(
        Field(tag="245", indicators=Indicators("0", "0"), subfields=sf_245)
    )

    # 246 한글 변형표제
    if title_korean:
        record.add_field(
            Field(
                tag="246",
                indicators=Indicators("3", " "),
                subfields=[Subfield(code="a", value=title_korean)],
            )
        )


def add_rare_book_publication(
    record: Record,
    *,
    place: str | None = None,
    publisher: str | None = None,
    year: str | None = None,
    ganji: str | None = None,  # 干支 (갑자·을축 등)
) -> None:
    """260 고서 발행사항 — 간지 지원.

    예: 260 ▾a한양 :▾b出版社, ▾c崇禎四丁丑 (1697)
    """
    sf = []
    if place:
        sf.append(Subfield(code="a", value=f"{place} :"))
    if publisher:
        sf.append(Subfield(code="b", value=f"{publisher},"))

    year_str = ""
    if ganji and year:
        year_str = f"{ganji} ({year})"
    elif ganji:
        year_str = ganji
    elif year:
        year_str = str(year)
    if year_str:
        sf.append(Subfield(code="c", value=year_str))

    if sf:
        record.add_field(Field(tag="260", indicators=Indicators(" ", " "), subfields=sf))


def add_provenance(record: Record, owner_history: str) -> None:
    """561 ▾a 소장이력 (구장자·인장 등).

    예: '561 ▾a홍길동 구장 → 1950년 김철수 기증'
    """
    if not owner_history:
        return
    record.add_field(
        Field(
            tag="561",
            indicators=Indicators("1", " "),
            subfields=[Subfield(code="a", value=owner_history)],
        )
    )


def add_extent_yeop(record: Record, *, leaves: int | str, size_cm: str) -> None:
    """300 고서 형태사항 — 葉(엽) 단위.

    한국 고서는 페이지 대신 '엽'(=한 장 양면) 단위.
    """
    sf = [
        Subfield(code="a", value=f"{leaves} 葉"),
        Subfield(code="c", value=size_cm),
    ]
    record.add_field(Field(tag="300", indicators=Indicators(" ", " "), subfields=sf))
