"""도서관·지역 특이성 자동 인식·정합 시스템 — PO 명령 2026-05-03.

PO 통찰: "각 도서관마다 다른 특징·지역구마다 다른 정책·양식 등 특이성 확인 필수"

도서관 특이성 차원:
1. 도서관 유형 (광역대표·지역중앙·거점·분관·작은도서관)
2. 지역 (서울 25구·경기 31시군·6 광역시·9 도)
3. 자관 정책 (prefix·청구기호·KDC 변형·별치)
4. 결재 양식 (자치구별·시도별·교육청별)
5. 운영 시간·휴관일
6. 회원 정책 (책이음·자관·시도 통합 카드)
7. 예산 사이클 (1월·3월·연·분기)
8. 평가 기준 (KOLAS·KLA·문체부·자치구 자체)

해결: 자관 config + 지역 매트릭스 + 양식 자동 매핑.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

RegionalGovernment = Literal[
    "seoul_gangnam",
    "seoul_songpa",
    "seoul_seocho",
    "seoul_nowon",
    "seoul_eunpyeong",
    "seoul_other",
    "gyeonggi",
    "incheon",
    "busan",
    "daegu",
    "gwangju",
    "daejeon",
    "ulsan",
    "sejong",
    "gangwon",
    "chungbuk",
    "chungnam",
    "jeonbuk",
    "jeonnam",
    "gyeongbuk",
    "gyeongnam",
    "jeju",
]


@dataclass(frozen=True)
class LibrarySpecificity:
    """도서관 특이성 (자관별)."""

    library_id: str
    library_name: str
    library_type: str  # public·school·academic·small·special
    hierarchy: str  # metropolitan_main·regional_central·branch_main·branch·small_library
    region: RegionalGovernment
    sasagwan_prefix: str  # EQ·CQ·WQ 등
    call_number_format: str  # "{KDC}/{이재철}"
    shelf_categories: list[str] = field(default_factory=list)  # 별치 (시문학·아동·향토)
    operation_hours: str = "09:00-18:00"
    closing_days: list[str] = field(default_factory=list)  # 휴관일
    membership_systems: list[str] = field(default_factory=list)  # 책이음·책두레·자관
    fiscal_year_start: int = 1  # 1=1월·3=3월
    evaluation_criteria: list[str] = field(default_factory=list)


# 지역별 표준 양식·정책 (자치구 25관·경기 31시군·광역시·도)
REGIONAL_POLICIES = {
    "seoul_gangnam": {
        "fiscal_year": 1,
        "approval_form": "강남구 도서관 운영 결재 양식",
        "evaluation": ["문체부 23 지표", "강남구 자체 KPI"],
        "membership": ["서울시민카드", "책이음"],
        "budget_cycle": "1월 시작·3월 추경·11월 결산",
    },
    "seoul_eunpyeong": {
        "fiscal_year": 1,
        "approval_form": "은평구 도서관 운영 결재 양식",
        "evaluation": ["문체부 23 지표", "은평구 평가"],
        "membership": ["서울시민카드", "책이음", "책단비"],  # 책단비 = 은평구 한정
        "budget_cycle": "1월 시작",
    },
    "gyeonggi": {
        "fiscal_year": 1,
        "approval_form": "경기도 도서관 운영 결재 (시군별 차등)",
        "evaluation": ["문체부", "경기도 자체"],
        "membership": ["경기도 통합", "책이음"],
        "budget_cycle": "1월 시작",
    },
    "busan": {
        "fiscal_year": 1,
        "approval_form": "부산시립 도서관 운영",
        "evaluation": ["문체부", "부산시 평가"],
        "membership": ["부산시민카드", "책이음"],
        "budget_cycle": "1월 시작",
    },
    "jeonnam": {
        "fiscal_year": 3,  # 학교 = 3월
        "approval_form": "전남교육청 학교도서관 결재",
        "evaluation": ["KERIS DLS", "전남교육청"],
        "membership": ["DLS 통합"],
        "budget_cycle": "3월 시작",
        "note": "순회사서 482개교 29명 (P15 정합)",
    },
}


def get_regional_policy(region: RegionalGovernment) -> dict:
    """지역별 정책·양식 자동 조회."""
    return REGIONAL_POLICIES.get(region, REGIONAL_POLICIES.get("seoul_other", {}))


# 별치 시소러스 (사서 일과 사이클 어휘 정합)
SHELF_KEYWORD_MAP: dict[str, tuple[str, ...]] = {
    "시문학": ("시", "시집", "시선집", "운문", "시인", "노래시"),
    "아동": ("어린이", "동화", "유아", "그림책", "초등", "유년", "키즈"),
    "청소년": ("청소년", "YA", "10대", "중학", "고교"),
    "향토": ("지역", "고향", "향토사", "지방사"),
    "고서": ("고서", "한적", "조선", "조선왕조"),
    "참고": ("사전", "백과", "연감", "편람", "핸드북"),
    "외국어": ("english", "japanese", "原書", "원서"),
    "정기간행물": ("저널", "잡지", "월간", "주간", "계간"),
}


def _match_shelf_category(title: str, category: str, subject_keywords: list[str]) -> bool:
    """별치 매칭 — 직접 + 시소러스 양방향."""
    title_lc = title.lower()
    if category in title or category in subject_keywords:
        return True
    for keyword in SHELF_KEYWORD_MAP.get(category, ()):
        if keyword in title_lc or keyword in title:
            return True
    return False


def auto_apply_specificity(
    book_data: dict,
    library: LibrarySpecificity,
) -> dict:
    """자관 특이성 자동 적용.

    Args:
        book_data: ISBN·제목 등 기본
        library: 자관 특이성

    Returns:
        도서관별 정합 데이터 (자관 prefix + 청구기호 + 별치 등)
    """
    enriched = dict(book_data)

    if library.sasagwan_prefix:
        enriched["registration_no_prefix"] = library.sasagwan_prefix

    enriched["call_number_format"] = library.call_number_format

    title = str(book_data.get("title", ""))
    subject_keywords = book_data.get("subject_keywords") or []
    for category in library.shelf_categories:
        if _match_shelf_category(title, category, subject_keywords):
            enriched["shelf_category"] = category
            break

    enriched["cataloging_agency"] = library.library_id
    enriched["regional_policy"] = get_regional_policy(library.region)

    return enriched


def detect_library_pattern(history: list[dict]) -> dict:
    """자관 history → 패턴 자동 감지 (Mem0 대비).

    3~5건 누적 = 자관 prefix·청구기호·별치 패턴 자동 인식.
    """
    if not history:
        return {}

    prefixes = [h.get("registration_no", "")[:2] for h in history if h.get("registration_no")]
    common_prefix = max(set(prefixes), key=prefixes.count) if prefixes else ""

    shelf_cats = [h.get("shelf_category", "") for h in history if h.get("shelf_category")]
    common_shelves = list(set(shelf_cats))

    return {
        "detected_prefix": common_prefix,
        "detected_shelves": common_shelves,
        "sample_size": len(history),
        "confidence": min(len(history) / 5, 1.0),
    }


__all__ = [
    "REGIONAL_POLICIES",
    "SHELF_KEYWORD_MAP",
    "LibrarySpecificity",
    "RegionalGovernment",
    "auto_apply_specificity",
    "detect_library_pattern",
    "get_regional_policy",
]
