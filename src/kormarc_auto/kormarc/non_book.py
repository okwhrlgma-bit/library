"""비도서·전자자료 KORMARC 처리.

NL Korea 매뉴얼:
- 「비도서자료용기술규칙」 (DVD·CD·점자도서·교구 등)
- 「온라인자료정리지침」 5종 (전자책·오디오북·전자저널·학위논문·멀티미디어, 2023)

핵심:
- 007 (형태기술) 자동
- 008 (재생속도·녹음·언어 등 자료유형 분기)
- 256 (전자자료 특성)
- 516 (컴퓨터 파일 종류)
- 538 (시스템 사양)
- 856 (URL·전자자원)
"""

from __future__ import annotations

from pymarc import Field, Indicators, Record, Subfield

# 007 자료유형 부호 (KORMARC)
TYPE_007_PREFIX = {
    "ebook": "cr",  # 컴퓨터 파일 (원격)
    "audiobook": "ss",  # 음향자료
    "dvd": "vd",  # 영상자료 (DVD)
    "cd": "co",  # 컴퓨터 파일 (광디스크)
    "music_cd": "sd",  # 음반
    "braille": "ta",  # 점자도서 (텍스트, 무판본)
    "thesis": "ta",  # 학위논문은 일반 텍스트
    "multimedia": "co",
    "ejournal": "cr",
}


def add_007(record: Record, material_type: str) -> None:
    """007 형태기술 필드 자동 추가.

    Args:
        material_type: 'ebook'/'audiobook'/'dvd'/'cd'/'braille'/'thesis'/'multimedia'/'ejournal'
    """
    prefix = TYPE_007_PREFIX.get(material_type)
    if not prefix:
        return
    # 단순 PoC: prefix + 공백으로 길이 맞춤 (실제는 자료유형별 정밀 부호화)
    data = (prefix + " " * 23)[:23]
    record.add_field(Field(tag="007", data=data))


def add_electronic_resource_url(
    record: Record,
    *,
    url: str,
    label: str = "전자자료",
    public_note: str | None = None,
) -> None:
    """856 ▾u URL + ▾y 표시 텍스트 + ▾z 공개주기."""
    if not url:
        return
    subfields = [
        Subfield(code="u", value=url),
        Subfield(code="y", value=label),
    ]
    if public_note:
        subfields.append(Subfield(code="z", value=public_note))
    record.add_field(Field(tag="856", indicators=Indicators("4", "0"), subfields=subfields))


def add_thesis_note(
    record: Record,
    *,
    degree: str,  # 박사학위·석사학위
    institution: str,
    year: str | None = None,
    department: str | None = None,
) -> None:
    """502 학위논문 주기.

    예:
    "박사학위 -- 서울대학교 대학원 문헌정보학과, 2024"
    """
    if not degree or not institution:
        return
    parts = [degree, "--", institution]
    if department:
        parts.append(department + ",")
    if year:
        parts.append(str(year))
    note = " ".join(parts)
    record.add_field(
        Field(
            tag="502",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=note)],
        )
    )


def add_system_requirements(record: Record, requirements: str) -> None:
    """538 시스템 사양 (전자자료·DVD).

    예: "PDF; Adobe Reader 이상" / "DVD; 한국어 더빙"
    """
    if not requirements:
        return
    record.add_field(
        Field(
            tag="538",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value=requirements)],
        )
    )


def add_braille_note(record: Record, *, language: str = "kor") -> None:
    """점자도서 주기 (340 + 546 ▾b).

    340 ▾a 점자, ▾b 매체
    546 ▾a 한국어 점자
    """
    record.add_field(
        Field(
            tag="340",
            indicators=Indicators(" ", " "),
            subfields=[Subfield(code="a", value="점자")],
        )
    )
    record.add_field(
        Field(
            tag="546",
            indicators=Indicators(" ", " "),
            subfields=[
                Subfield(code="a", value="한국어 점자" if language == "kor" else "Braille"),
            ],
        )
    )
