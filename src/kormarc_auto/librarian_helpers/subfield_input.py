"""사서 빠른 입력 — 식별기호(▾) 자동 변환.

사서가 평소 키보드로 ▾ 직접 치기 어려움. 다음 표기를 자동 변환:
- $a, $b, ... → ▾a, ▾b, ... (MARC 21 표기법)
- //a, //b, ... → ▾a, ▾b, ... (단축)
- ‡a (LC 식별기호) → ▾a

또한 자주 쓰는 필드 패턴 자동 추가:
- "245 작별하지 않는다" → 245 ▾a작별하지 않는다
- "100 한강" → 100 ▾a한강

웹 UI(Streamlit)·CLI 양쪽에서 활용.
"""

from __future__ import annotations

import re
from typing import Any


# 식별기호 변환 패턴 (우선순위 순)
_SUBFIELD_PATTERNS = [
    # $a, $b, ... → ▾a, ▾b
    (re.compile(r"\$([a-z0-9])"), r"▾\1"),
    # //a, //b, ... → ▾a, ▾b
    (re.compile(r"/{2}([a-z0-9])"), r"▾\1"),
    # ‡a (LC) → ▾a
    (re.compile(r"‡([a-z0-9])"), r"▾\1"),
]


def expand_subfield_codes(text: str) -> str:
    """텍스트의 $a·//a·‡a 표기를 ▾a로 변환.

    예:
    - "245 $a작별하지 않는다 $c/ 한강" → "245 ▾a작별하지 않는다 ▾c/ 한강"
    - "100 //a한강 //d1970-" → "100 ▾a한강 ▾d1970-"
    """
    if not text:
        return text
    out = text
    for pattern, replacement in _SUBFIELD_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def parse_field_line(line: str) -> dict[str, Any] | None:
    """필드 한 줄 파싱.

    형식: "TAG [ind1 ind2] ▾a값1 ▾b값2 ..."
    예:
    - "245 10 ▾a작별하지 않는다 ▾c/ 한강"
    - "020 ▾a9788936434120"
    - "100 1 ▾a한강 ▾d1970-"

    Returns:
        {"tag": "245", "ind1": "1", "ind2": "0", "subfields": [("a", "..."), ("c", "...")]}
        또는 파싱 실패 시 None
    """
    line = expand_subfield_codes(line.strip())
    if not line:
        return None

    # 첫 토큰이 3자리 태그
    m = re.match(r"^(\d{3})\s*", line)
    if not m:
        return None
    tag = m.group(1)
    rest = line[m.end():].strip()

    # 지시기호 (옵션, 0~2 char)
    ind1, ind2 = " ", " "
    ind_match = re.match(r"^([0-9 \\#])([0-9 \\#])\s+(?=▾)", rest)
    if ind_match:
        ind1 = ind_match.group(1).replace("\\", " ").replace("#", " ")
        ind2 = ind_match.group(2).replace("\\", " ").replace("#", " ")
        rest = rest[ind_match.end():]

    # 서브필드 추출
    subfields: list[tuple[str, str]] = []
    for sf_match in re.finditer(r"▾([a-z0-9])([^▾]*)", rest):
        code = sf_match.group(1)
        value = sf_match.group(2).strip()
        if value:
            subfields.append((code, value))

    if not subfields:
        return None

    return {"tag": tag, "ind1": ind1, "ind2": ind2, "subfields": subfields}


def common_subfield_hint(tag: str) -> str:
    """필드 태그별 자주 쓰는 식별기호 힌트.

    UI 툴팁용.
    """
    hints = {
        "020": "▾a ISBN, ▾g 부가기호, ▾c 가격",
        "040": "▾a 우리도서관, ▾b 사용언어, ▾c 편목기관",
        "041": "▾a 본문언어 (반복)",
        "049": "▾l 등록번호, ▾c 복본, ▾f 별치, ▾v 권차",
        "056": "▾a KDC, ▾2 6 (6판)",
        "082": "▾a DDC",
        "100": "▾a 저자명, ▾d 생몰년, ▾e 역할",
        "245": "▾a 본표제, ▾b 부표제, ▾c 책임표시",
        "246": "▾a 변형표제",
        "250": "▾a 판차",
        "264": "▾a 발행지, ▾b 발행처, ▾c 발행연도",
        "300": "▾a 페이지, ▾c 크기, ▾b 기타",
        "490": "▾a 총서명, ▾v 권차",
        "500": "▾a 일반주기",
        "504": "▾a 서지·색인 주기",
        "505": "▾a 내용주기",
        "520": "▾a 요약·초록",
        "521": "▾a 이용대상 (DLS 추천학년)",
        "650": "▾a 주제, ▾2 8 (NLSH)",
        "653": "▾a 비통제 키워드 (반복)",
        "700": "▾a 부저자명, ▾e 역할",
        "856": "▾u URL, ▾y 표시 텍스트",
        "950": "▾b 가격",
    }
    return hints.get(tag, "▾a 주 서브필드")
