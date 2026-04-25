"""BookData → KORMARC 필드 매핑 헬퍼.

008 필드 구성, 발행국부호, 언어부호 등 KORMARC 고유 인코딩 규칙.
상세는 docs/spec.md §KORMARC 필드 매핑 참조.
"""

from __future__ import annotations

from datetime import datetime

# 한국 주요 도시 → 008 발행국부호
PUBLICATION_PLACE_CODES = {
    "서울": "ulk",
    "부산": "ulk",
    "대구": "ulk",
    "인천": "ulk",
    "광주": "ulk",
    "대전": "ulk",
    "울산": "ulk",
    "경기": "ulg",
    "파주": "ulg",
    "수원": "ulg",
    "성남": "ulg",
    "강원": "ulw",
    "충북": "ulj",
    "충남": "ulc",
    "전북": "ulb",
    "전남": "uln",
    "경북": "ulh",
    "경남": "uln",
    "제주": "ulj",
    "세종": "ulj",
}

DEFAULT_LANGUAGE = "kor"


def build_008(
    *,
    publication_year: str | None,
    language: str = DEFAULT_LANGUAGE,
    publication_place: str | None = None,
    publication_status: str = "s",  # s=단일발행, m=다권물, n=출판년불명
    illustration: str = "    ",  # 4자리 (예: "a   "는 삽화)
    target_audience: str = " ",
    form: str = " ",
    nature: str = "    ",
    literary_form: str = "0",
    biography: str = " ",
) -> str:
    """008 필드 (40자리) 문자열 생성.

    위치별 의미 (도서 기준):
        00-05: 입력일자 YYMMDD
        06: 발행상태 (s/m/n/q/t/d)
        07-10: 발행연도1
        11-14: 발행연도2 (단일발행이면 공백 4)
        15-17: 발행국부호 (3자리, 예 'ulk')
        18-21: 삽화 (4자리)
        22: 이용대상자
        23: 자료형태
        24-27: 내용형식
        28: 정부간행물
        29: 회의간행물
        30: 기념회지
        31: 색인
        32: (사용안함)
        33: 문학형식
        34: 전기
        35-37: 언어 (3자리)
        38: 수정레코드
        39: 목록전거 (' '=완전, '7'=최소수준)
    """
    today = datetime.now().strftime("%y%m%d")
    year1 = (publication_year or "    ").ljust(4)[:4]
    year2 = "    "
    place = (PUBLICATION_PLACE_CODES.get((publication_place or "").strip(), "xx ")).ljust(3)[:3]
    lang = language.ljust(3)[:3]

    parts = [
        today,                  # 00-05 (6)
        publication_status,     # 06 (1)
        year1,                  # 07-10 (4)
        year2,                  # 11-14 (4)
        place,                  # 15-17 (3)
        illustration,           # 18-21 (4)
        target_audience,        # 22 (1)
        form,                   # 23 (1)
        nature,                 # 24-27 (4)
        " ",                    # 28 (1)
        " ",                    # 29 (1)
        " ",                    # 30 (1)
        " ",                    # 31 (1)
        " ",                    # 32 (1)
        literary_form,          # 33 (1)
        biography,              # 34 (1)
        lang,                   # 35-37 (3)
        " ",                    # 38 (1)
        " ",                    # 39 (1)
    ]
    result = "".join(parts)
    # 길이 보정
    if len(result) < 40:
        result = result.ljust(40)
    elif len(result) > 40:
        result = result[:40]
    return result


def parse_publication_place(publisher_field: str | None) -> str | None:
    """출판사 정보에서 발행지 도시명 추출.

    예: "파주: 창비, 2014" → "파주"
        "창비" → None
    """
    if not publisher_field:
        return None
    text = publisher_field.strip()
    for city in PUBLICATION_PLACE_CODES:
        if text.startswith(city):
            return city
    return None


def normalize_isbn(isbn: str | None) -> str | None:
    """ISBN을 숫자만 13자리로 정규화."""
    if not isbn:
        return None
    digits = "".join(c for c in isbn if c.isdigit())
    if len(digits) == 13:
        return digits
    if len(digits) == 10:
        # ISBN-10 → ISBN-13 변환 (978 prefix + check digit 재계산)
        prefix = "978" + digits[:9]
        check_sum = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(prefix))
        check = (10 - check_sum % 10) % 10
        return prefix + str(check)
    return None
