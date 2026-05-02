"""049 청구기호 자동/반자동 구성.

KORMARC 049 (한국 특수):
    ▾l 등록번호
    ▾c 복본기호 (c.1, c.2)
    ▾f 별치기호 (L=장학자료, K=향토, GO=고서, R=참고도서, Y=청소년, J=어린이 등)
    ▾v 권차기호 (다권물)

도서관별 규칙은 `library_rules.json`로 외부화 (도서관마다 다름).

전형 청구기호 형태:
    813.7 한31ㅈ c.1
    [KDC 분류] [저자기호] [서명기호] [복본]

저자기호: 한국식 저자기호표(이재철 등) — 본 모듈은 단순화된 휴리스틱만 제공.
사서가 표준 저자기호표 적용한 전체 자동화는 외부 라이브러리(없음) 필요.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pymarc import Field, Indicators, Record, Subfield

logger = logging.getLogger(__name__)


# 별치기호 (도서관 표준)
SHELVING_CODES = {
    "general": "",  # 일반서가
    "reference": "R",  # 참고도서
    "youth": "Y",  # 청소년
    "child": "J",  # 어린이
    "rare": "GO",  # 고서
    "local": "K",  # 향토
    "scholarship": "L",  # 장학자료
    "ebook": "EB",  # 전자책
    "audiobook": "AB",  # 오디오북
}


def load_library_rules(path: str | Path) -> dict[str, Any]:
    """도서관별 청구기호 규칙 JSON 로드.

    JSON 예시:
    {
      "agency_code": "OURLIB",
      "registration_prefix": "K",      // 등록번호 접두 (K000001)
      "registration_padding": 6,       // 자릿수
      "next_registration_no": 1234,    // 다음 발급 번호
      "kdc_to_shelving": {             // KDC 시작 → 자동 별치
         "8": "general",
         "813": "general",
         "375": "scholarship"
      },
      "default_shelving": "general"
    }
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


def suggest_shelving(book_data: dict[str, Any], rules: dict[str, Any] | None = None) -> str:
    """KDC와 메타데이터로 별치기호 추천.

    Args:
        book_data: BookData dict
        rules: load_library_rules 결과 (있으면 우선)

    Returns:
        별치기호 (없으면 빈 문자열)
    """
    kdc = str(book_data.get("kdc") or "")
    add_code = str(book_data.get("additional_code") or "")

    if rules and kdc:
        kdc_map = rules.get("kdc_to_shelving", {})
        for prefix, shelf_key in sorted(kdc_map.items(), key=lambda x: -len(x[0])):
            if kdc.startswith(prefix):
                return SHELVING_CODES.get(shelf_key, "")

    # 휴리스틱: ISBN 부가기호 첫 자리
    if add_code:
        first = add_code[0]
        if first == "7":  # 아동
            return SHELVING_CODES["child"]
        if first == "4":  # 청소년
            return SHELVING_CODES["youth"]
        if first in ("5", "6", "8"):  # 학습참고
            return SHELVING_CODES["scholarship"]

    if rules:
        return SHELVING_CODES.get(rules.get("default_shelving", "general"), "")
    return ""


def make_author_mark(author: str, title: str = "") -> str:
    """이재철 한국 도서기호법 근사 — 저자기호 자동.

    이재철식 형식: [성씨 1자] + [2자리 숫자] + [표제 첫 글자]
    예: '한강' + '작별하지 않는다' → '한31ㅈ'

    정확한 표는 KLA 종이책 (1만원). 본 함수는 휴리스틱이며
    사서 수기 검토 권장. GitHub에 한국 저자기호 오픈 코드 부재 (2026-04 기준).

    Args:
        author: 저자명 (예: '한강', '김영하')
        title: 표제 (없으면 무시)

    Returns:
        저자기호 문자열 (3~5자 한글+숫자)
    """
    if not author:
        return ""

    # 성씨 1자 추출 (한국 성씨 = 1자 이상)
    first_char = author[0]

    # 두 번째 글자(이름 첫 자) 자모 분해 → 이재철식 숫자 매핑
    rest = author[1:2] if len(author) > 1 else ""
    mark = first_char

    if rest:
        # 한글 자모 분해: 초성·중성·종성
        # 이재철 표는 초성+중성 조합으로 11~99 매핑
        try:
            code = ord(rest) - 0xAC00  # 한글 시작점
            if 0 <= code < 11172:
                cho = code // 588  # 초성 (0~18)
                jung = (code % 588) // 28  # 중성 (0~20)
                # 이재철 근사: 초성·중성 가중 합
                num = (cho * 5 + jung) % 89 + 11  # 11~99 범위
                mark += f"{num:02d}"
            else:
                # 한글 외 문자: ord 기반 단순 매핑
                num = (ord(rest) % 89) + 11
                mark += f"{num:02d}"
        except TypeError:
            pass

    # 표제 첫 글자 첨자
    if title:
        first_title = title.strip()[0] if title.strip() else ""
        if first_title:
            mark += first_title

    return mark


def issue_registration_no(rules: dict[str, Any]) -> str:
    """다음 등록번호 발급 (rules dict in-place 갱신).

    호출 후 rules는 next_registration_no가 +1 됨 — 호출자가 저장 책임.
    """
    prefix = rules.get("registration_prefix", "")
    padding = int(rules.get("registration_padding", 6))
    n = int(rules.get("next_registration_no", 1))
    rules["next_registration_no"] = n + 1
    return f"{prefix}{n:0{padding}d}"


def add_call_number_field(
    record: Record,
    book_data: dict[str, Any],
    *,
    rules: dict[str, Any] | None = None,
    registration_no: str | None = None,
    copy_no: int = 1,
    volume_no: str | None = None,
) -> None:
    """049 청구기호 필드를 record에 in-place 추가.

    Args:
        record: pymarc.Record (수정됨)
        book_data: BookData dict
        rules: load_library_rules 결과 (없으면 휴리스틱)
        registration_no: 명시 등록번호 (없으면 rules로 자동 발급)
        copy_no: 복본 번호 (1=원본)
        volume_no: 권차 (있을 때)
    """
    subfields: list[Subfield] = []

    if registration_no is None and rules is not None:
        registration_no = issue_registration_no(rules)
    if registration_no:
        subfields.append(Subfield(code="l", value=registration_no))

    if copy_no > 1:
        subfields.append(Subfield(code="c", value=f"c.{copy_no}"))

    shelving = suggest_shelving(book_data, rules)
    if shelving:
        subfields.append(Subfield(code="f", value=shelving))

    if volume_no:
        subfields.append(Subfield(code="v", value=str(volume_no)))

    if not subfields:
        return

    record.add_field(Field(tag="049", indicators=Indicators("0", " "), subfields=subfields))
    logger.info("049 청구기호 추가: %s", subfields)
