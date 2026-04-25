"""KORMARC 전거 데이터 처리 — 100/110/111 표목 정밀.

근거: 「국립중앙도서관 전거데이터 기술 지침_개인명(2018)」, 「단체명(2018)」.

100 (개인저자):
  ▾a 개인명
  ▾d 생몰년 (1970-, 1923-1989)
  ▾e 역할 (편자, 역자, 서문 등)
  ▾f 역조 (조선, 고려, 신라 — 한국·중국 특유)
  ▾g 세기 (17세기 등)

110 (단체저자):
  ▾a 단체명
  ▾b 하위단위
  ▾d 회의일자·소재지

111 (회의저자):
  ▾a 회의명
  ▾d 일자
  ▾c 장소
  ▾n 회차
"""

from __future__ import annotations

import re
from typing import Any

from pymarc import Field, Indicators, Record, Subfield


def add_personal_author_field(
    record: Record,
    *,
    name: str,
    birth_year: int | str | None = None,
    death_year: int | str | None = None,
    role: str | None = None,
    dynasty: str | None = None,  # 조선·고려·신라 등
    century: str | None = None,
    is_main: bool = True,
) -> None:
    """100 (주표목) 또는 700 (부출표목) 추가.

    Args:
        record: pymarc.Record (in-place)
        name: 개인명
        birth_year, death_year: 생몰년 (있으면 ▾d)
        role: 역할 (편자/역자 등, ▾e)
        dynasty: 역조 (한국·중국 특유, ▾f)
        century: 세기 (▾g)
        is_main: True면 100, False면 700
    """
    if not name:
        return

    tag = "100" if is_main else "700"
    subfields = [Subfield(code="a", value=name)]

    if birth_year is not None or death_year is not None:
        b = str(birth_year) if birth_year else ""
        d = str(death_year) if death_year else ""
        if b and d:
            subfields.append(Subfield(code="d", value=f"{b}-{d}"))
        elif b:
            subfields.append(Subfield(code="d", value=f"{b}-"))
        elif d:
            subfields.append(Subfield(code="d", value=f"-{d}"))

    if role:
        subfields.append(Subfield(code="e", value=role))
    if dynasty:
        subfields.append(Subfield(code="f", value=dynasty))
    if century:
        subfields.append(Subfield(code="g", value=century))

    # 1지시기호: 0=이름순(서양), 1=성,이름(한국)
    ind1 = "1" if _looks_korean_name(name) else "0"
    record.add_field(
        Field(tag=tag, indicators=Indicators(ind1, " "), subfields=subfields)
    )


def add_corporate_author_field(
    record: Record,
    *,
    name: str,
    subordinate: str | None = None,
    location: str | None = None,
    is_main: bool = True,
) -> None:
    """110 (단체저자, 주표목) 또는 710 (부출).

    Args:
        name: 단체명 (예: '한국도서관협회')
        subordinate: 하위단위 (▾b, 예: '편집부')
        location: 소재지 (▾d)
        is_main: True면 110
    """
    if not name:
        return
    tag = "110" if is_main else "710"
    subfields = [Subfield(code="a", value=name)]
    if subordinate:
        subfields.append(Subfield(code="b", value=subordinate))
    if location:
        subfields.append(Subfield(code="d", value=location))

    # 1지시기호: 0=역순, 1=관할권, 2=직접
    record.add_field(
        Field(tag=tag, indicators=Indicators("2", " "), subfields=subfields)
    )


def add_meeting_author_field(
    record: Record,
    *,
    name: str,
    date: str | None = None,
    place: str | None = None,
    number: str | None = None,
    is_main: bool = True,
) -> None:
    """111 (회의저자, 주표목) 또는 711 (부출).

    Args:
        name: 회의명
        date: 일자 (▾d)
        place: 장소 (▾c)
        number: 회차 (▾n, 예: '제5회')
        is_main: True면 111
    """
    if not name:
        return
    tag = "111" if is_main else "711"
    subfields = [Subfield(code="a", value=name)]
    if number:
        subfields.append(Subfield(code="n", value=number))
    if date:
        subfields.append(Subfield(code="d", value=date))
    if place:
        subfields.append(Subfield(code="c", value=place))

    record.add_field(
        Field(tag=tag, indicators=Indicators("2", " "), subfields=subfields)
    )


def parse_author_string_full(value: str) -> dict[str, Any]:
    """저자 문자열 → 풍부한 분석.

    "한강 (1970-)"  → {name: "한강", birth_year: "1970", death_year: None}
    "이순신 (조선)" → {name: "이순신", dynasty: "조선"}
    "홍길동 ; 김철수 외" → {primary, additional}
    """
    if not value:
        return {"name": "", "additional": []}

    s = value.strip()

    # 생몰년 추출 (4자리-4자리 또는 4자리-)
    year_match = re.search(r"\((\d{4})\s*[-~]\s*(\d{4})?\)", s)
    birth = death = None
    if year_match:
        birth = year_match.group(1)
        death = year_match.group(2)
        s = s[: year_match.start()].strip() + s[year_match.end():].strip()

    # 역조 추출 (조선·고려·신라·삼국·고구려·백제·발해·중국 왕조)
    dynasty = None
    for dyn in ["조선", "고려", "신라", "삼국", "고구려", "백제", "발해", "당", "송", "원", "명", "청"]:
        if f"({dyn})" in s:
            dynasty = dyn
            s = s.replace(f"({dyn})", "").strip()
            break

    # 부저자 분리
    s = re.sub(r"\s*외\s*\d*$", "", s)
    parts = re.split(r"[;,]", s)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        return {"name": "", "additional": []}

    return {
        "name": parts[0],
        "birth_year": birth,
        "death_year": death,
        "dynasty": dynasty,
        "additional": parts[1:4],
    }


def _looks_korean_name(name: str) -> bool:
    """한국 이름 (성+이름 1자 + 1~2자) 형태인지."""
    if not name:
        return False
    return bool(re.match(r"^[가-힣]{2,4}$", name.strip()))
