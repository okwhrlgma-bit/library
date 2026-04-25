"""등록번호 자동 부여 + 누락번호 검출 — 알파스/KOLAS 사서 워크플로우 흡수.

근거 (PO 제공 알파스 단행 V 1.0 매뉴얼 + KOLAS III 매뉴얼):
- 등록구분: EM(일반)·BM(별치)·AM(아동)·CM(연속간행물) 등 도서관별 자유
- 등록번호 형식: 등록구분(2~3자) + 차수(2자) + 연도(2자) + 일련번호(5자) = 10~12자
- 누락번호: 폐기·분실로 등록 누락된 번호를 찾아 다음 신규 등록에 재활용
  → 알파스 매뉴얼 p72 "등록 누락번호 적용" 사서가 매주 점검
- 다권본: 전 5권 동시 등록 시 권별 일련번호 (245 ▾n + 091/090 ▾c 자동)

KORMARC 049 ▾l 에 들어감. 복본기호(▾c), 별치기호(▾f), 권차(▾v)는 별도.

PO 페인포인트: 매일 신착 + 분기 누락번호 점검을 수동으로. 본 모듈로 자동화.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)


# 알파스 표준 12자리: <등록구분 3자리><차수 2자리><연도 2자리><일련번호 5자리>
# 예: EM01260012345 = 일반 1차 2026년 12345번째
DEFAULT_KIND = "EM"  # 일반(Each Material) 등록
DEFAULT_TURN = 1  # 1차 등록 (재고 정리 등 N차)
DEFAULT_SERIAL_DIGITS = 5  # 일련번호 자릿수
DEFAULT_KIND_DIGITS = 2  # 등록구분 자릿수
DEFAULT_TURN_DIGITS = 2  # 차수 자릿수
DEFAULT_YEAR_DIGITS = 2  # 연도 자릿수 (마지막 두 자리)


REG_PATTERN = re.compile(
    r"^(?P<kind>[A-Z]{2,3})"
    r"(?P<turn>\d{2})"
    r"(?P<year>\d{2})"
    r"(?P<serial>\d{4,6})$"
)


@dataclass
class RegistrationNumber:
    """파싱된 등록번호 구성요소."""

    raw: str
    kind: str
    turn: int
    year: int  # 두 자리 (예: 26 = 2026)
    serial: int

    def render(
        self,
        *,
        serial_digits: int = DEFAULT_SERIAL_DIGITS,
    ) -> str:
        return (
            f"{self.kind}{self.turn:02d}{self.year:02d}"
            f"{self.serial:0{serial_digits}d}"
        )


def parse_registration_number(reg_no: str) -> RegistrationNumber:
    """문자열 등록번호 → RegistrationNumber.

    Raises:
        ValueError: 형식 위반 (사서가 손으로 입력한 비표준은 거부)
    """
    s = reg_no.strip().upper()
    m = REG_PATTERN.match(s)
    if not m:
        raise ValueError(f"등록번호 형식 오류: {reg_no!r}")
    return RegistrationNumber(
        raw=s,
        kind=m["kind"],
        turn=int(m["turn"]),
        year=int(m["year"]),
        serial=int(m["serial"]),
    )


def next_registration_number(
    existing: Iterable[str],
    *,
    kind: str = DEFAULT_KIND,
    turn: int = DEFAULT_TURN,
    year: int | None = None,
    fill_gap: bool = False,
    serial_digits: int = DEFAULT_SERIAL_DIGITS,
) -> str:
    """다음 신규 등록번호.

    Args:
        existing: 기존 등록번호 iterable (자관 DB)
        kind/turn/year: 부여할 (kind, turn, year)
        fill_gap: True면 누락번호를 우선 채움 (사서 매주 작업).
                  False면 가장 큰 일련번호 +1.
        serial_digits: 일련번호 자릿수 (기본 5 → 99999까지)
    """
    if year is None:
        year = date.today().year % 100

    matching: list[int] = []
    for raw in existing:
        try:
            r = parse_registration_number(raw)
        except ValueError:
            continue
        if r.kind == kind and r.turn == turn and r.year == year:
            matching.append(r.serial)

    if not matching:
        return RegistrationNumber(
            raw="",
            kind=kind,
            turn=turn,
            year=year,
            serial=1,
        ).render(serial_digits=serial_digits)

    matching_set = set(matching)
    if fill_gap:
        for n in range(1, max(matching) + 1):
            if n not in matching_set:
                return RegistrationNumber(
                    raw="",
                    kind=kind,
                    turn=turn,
                    year=year,
                    serial=n,
                ).render(serial_digits=serial_digits)

    return RegistrationNumber(
        raw="",
        kind=kind,
        turn=turn,
        year=year,
        serial=max(matching) + 1,
    ).render(serial_digits=serial_digits)


def find_missing_numbers(
    existing: Iterable[str],
    *,
    kind: str = DEFAULT_KIND,
    turn: int = DEFAULT_TURN,
    year: int | None = None,
) -> list[int]:
    """등록 누락번호 목록 — 사서 분기 점검용.

    예: 1, 3, 5, 9가 등록되어 있으면 [2, 4, 6, 7, 8] 반환.
    """
    if year is None:
        year = date.today().year % 100

    serials: list[int] = []
    for raw in existing:
        try:
            r = parse_registration_number(raw)
        except ValueError:
            continue
        if r.kind == kind and r.turn == turn and r.year == year:
            serials.append(r.serial)

    if not serials:
        return []
    serial_set = set(serials)
    return [n for n in range(1, max(serials) + 1) if n not in serial_set]


def assign_for_multivolume(
    base: dict,
    *,
    volumes: int,
    kind: str = DEFAULT_KIND,
    turn: int = DEFAULT_TURN,
    year: int | None = None,
    existing: Iterable[str] = (),
) -> list[dict]:
    """다권본 일괄 등록 — 권별 등록번호·권차 자동.

    예: 5권짜리 전집 → EM0126[00100..00104] + 245 ▾n "v.1"~"v.5"

    Returns:
        [{**base, "registration_number": "...", "volume_index": 1, "volume_label": "v.1"}, ...]
    """
    if year is None:
        year = date.today().year % 100

    existing_list = list(existing)
    results: list[dict] = []
    for i in range(1, volumes + 1):
        next_no = next_registration_number(
            existing_list,
            kind=kind,
            turn=turn,
            year=year,
            fill_gap=False,
        )
        existing_list.append(next_no)
        results.append(
            {
                **base,
                "registration_number": next_no,
                "volume_index": i,
                "volume_label": f"v.{i}",
                "marc_245_n": f"v.{i}",  # KORMARC 245 ▾n 후보
                "marc_490_v": str(i),  # 491/490 ▾v 권차
            }
        )
    return results


def load_existing_from_index(library_db_path: str | Path | None = None) -> list[str]:
    """자관 DB 인덱스에서 기존 등록번호 모두 로드.

    inventory/library_db.py와 협력. 없으면 빈 리스트.
    """
    try:
        from kormarc_auto.inventory.library_db import iter_records
    except ImportError:
        return []

    out: list[str] = []
    for rec in iter_records():
        rn = rec.get("registration_number") or rec.get("reg_no")
        if rn:
            out.append(str(rn))
    _ = library_db_path  # 향후 경로 인자 활용 시
    return out


__all__ = [
    "DEFAULT_KIND",
    "DEFAULT_TURN",
    "REG_PATTERN",
    "RegistrationNumber",
    "assign_for_multivolume",
    "find_missing_numbers",
    "load_existing_from_index",
    "next_registration_number",
    "parse_registration_number",
]
