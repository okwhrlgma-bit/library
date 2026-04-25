"""BookData → KORMARC 필드 매핑 헬퍼.

008 필드 구성, 발행국부호, 언어부호 등 KORMARC 고유 인코딩 규칙.
상세는 docs/spec.md §KORMARC 필드 매핑 참조.
"""

from __future__ import annotations

from datetime import datetime

# 한국 도서관 관행상 사용되는 국내 발행국부호 + LC MARC Country Codes 외국분.
# 한국 코드는 KS X 6006-0 (KORMARC) Annex 발행국부호표 기준이지만,
# 도서관마다 차이 있어 자관 표준 우선. 외국 코드는 https://www.loc.gov/marc/countries/
PUBLICATION_PLACE_CODES = {
    # === 대한민국 (시도별, KORMARC 관행) ===
    "서울": "ulk",
    "서울특별시": "ulk",
    "seoul": "ulk",
    "부산": "bnk",
    "부산광역시": "bnk",
    "busan": "bnk",
    "대구": "tgk",
    "대구광역시": "tgk",
    "daegu": "tgk",
    "인천": "ick",
    "인천광역시": "ick",
    "incheon": "ick",
    "광주": "kjk",
    "광주광역시": "kjk",
    "gwangju": "kjk",
    "대전": "tjk",
    "대전광역시": "tjk",
    "daejeon": "tjk",
    "울산": "usk",
    "울산광역시": "usk",
    "ulsan": "usk",
    "세종": "sjk",
    "세종특별자치시": "sjk",
    "sejong": "sjk",
    "경기": "ggk",
    "경기도": "ggk",
    "파주": "ggk",
    "수원": "ggk",
    "성남": "ggk",
    "고양": "ggk",
    "용인": "ggk",
    "안양": "ggk",
    "부천": "ggk",
    "gyeonggi": "ggk",
    "강원": "kwk",
    "강원도": "kwk",
    "강원특별자치도": "kwk",
    "춘천": "kwk",
    "원주": "kwk",
    "강릉": "kwk",
    "gangwon": "kwk",
    "충북": "ccb",
    "충청북도": "ccb",
    "청주": "ccb",
    "chungbuk": "ccb",
    "충남": "ccn",
    "충청남도": "ccn",
    "천안": "ccn",
    "chungnam": "ccn",
    "전북": "jbk",
    "전라북도": "jbk",
    "전북특별자치도": "jbk",
    "전주": "jbk",
    "jeonbuk": "jbk",
    "전남": "jnk",
    "전라남도": "jnk",
    "목포": "jnk",
    "여수": "jnk",
    "jeonnam": "jnk",
    "경북": "kbk",
    "경상북도": "kbk",
    "포항": "kbk",
    "안동": "kbk",
    "gyeongbuk": "kbk",
    "경남": "knk",
    "경상남도": "knk",
    "창원": "knk",
    "진주": "knk",
    "gyeongnam": "knk",
    "제주": "jjk",
    "제주특별자치도": "jjk",
    "jeju": "jjk",
    # === 북한 ===
    "평양": "ko ",
    "북한": "ko ",
    "조선": "ko ",
    # === 외국 (LC MARC Country Codes) ===
    "미국": "xxu",
    "usa": "xxu",
    "united states": "xxu",
    "뉴욕": "nyu",
    "new york": "nyu",
    "캘리포니아": "cau",
    "california": "cau",
    "워싱턴": "dcu",
    "washington": "dcu",
    "보스턴": "mau",
    "일본": "ja ",
    "japan": "ja ",
    "도쿄": "ja ",
    "tokyo": "ja ",
    "오사카": "ja ",
    "osaka": "ja ",
    "중국": "cc ",
    "china": "cc ",
    "베이징": "cc ",
    "beijing": "cc ",
    "상하이": "cc ",
    "shanghai": "cc ",
    "홍콩": "cc ",
    "hong kong": "cc ",
    "타이완": "ch ",
    "대만": "ch ",
    "taiwan": "ch ",
    "타이베이": "ch ",
    "영국": "enk",
    "uk": "enk",
    "england": "enk",
    "런던": "enk",
    "london": "enk",
    "프랑스": "fr ",
    "france": "fr ",
    "파리": "fr ",
    "paris": "fr ",
    "독일": "gw ",
    "germany": "gw ",
    "베를린": "gw ",
    "berlin": "gw ",
    "이탈리아": "it ",
    "italy": "it ",
    "로마": "it ",
    "rome": "it ",
    "스페인": "sp ",
    "spain": "sp ",
    "마드리드": "sp ",
    "포르투갈": "po ",
    "portugal": "po ",
    "네덜란드": "ne ",
    "netherlands": "ne ",
    "벨기에": "be ",
    "belgium": "be ",
    "스위스": "sz ",
    "switzerland": "sz ",
    "오스트리아": "au ",
    "austria": "au ",
    "스웨덴": "sw ",
    "sweden": "sw ",
    "노르웨이": "no ",
    "norway": "no ",
    "덴마크": "dk ",
    "denmark": "dk ",
    "핀란드": "fi ",
    "finland": "fi ",
    "러시아": "ru ",
    "russia": "ru ",
    "모스크바": "ru ",
    "moscow": "ru ",
    "캐나다": "xxc",
    "canada": "xxc",
    "토론토": "onc",
    "toronto": "onc",
    "오스트레일리아": "at ",
    "호주": "at ",
    "australia": "at ",
    "뉴질랜드": "nz ",
    "new zealand": "nz ",
    "인도": "ii ",
    "india": "ii ",
    "베트남": "vm ",
    "vietnam": "vm ",
    "태국": "th ",
    "thailand": "th ",
    "싱가포르": "si ",
    "singapore": "si ",
    "말레이시아": "my ",
    "malaysia": "my ",
    "필리핀": "ph ",
    "philippines": "ph ",
    "인도네시아": "io ",
    "indonesia": "io ",
    "이집트": "ua ",
    "egypt": "ua ",
    "이스라엘": "is ",
    "israel": "is ",
    "터키": "tu ",
    "turkey": "tu ",
    "튀르키예": "tu ",
    "브라질": "bl ",
    "brazil": "bl ",
    "아르헨티나": "ag ",
    "argentina": "ag ",
    "멕시코": "mx ",
    "mexico": "mx ",
}

DEFAULT_LANGUAGE = "kor"


def lookup_publication_country(place: str | None) -> str:
    """발행지 문자열 → 008 발행국부호 (3자리, 미상이면 'xx ').

    매칭 우선순위:
    1. 정확 일치 (소문자 변환 후)
    2. 부분 포함 — '서울특별시 종로구' → 'ulk'
    3. 미상 → 'xx '
    """
    if not place:
        return "xx "
    key = place.strip().lower()
    if key in PUBLICATION_PLACE_CODES:
        return PUBLICATION_PLACE_CODES[key]
    for known, code in PUBLICATION_PLACE_CODES.items():
        if known in key or key.startswith(known):
            return code
    return "xx "


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
    place = lookup_publication_country(publication_place).ljust(3)[:3]
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
