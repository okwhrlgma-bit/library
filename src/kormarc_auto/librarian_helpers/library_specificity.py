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
    "seoul_gangnam", "seoul_songpa", "seoul_seocho", "seoul_nowon", "seoul_eunpyeong",
    "seoul_other", "gyeonggi", "incheon", "busan", "daegu", "gwangju", "daejeon",
    "ulsan", "sejong", "gangwon", "chungbuk", "chungnam", "jeonbuk", "jeonnam",
    "gyeongbuk", "gyeongnam", "jeju",
]


@dataclass(frozen=True)
class LibrarySpecificity:
    """도서관 특이성 (자관별)."""

    library_id: str
    library_name: str
    library_type: str  # public·school·academic·small·special
    hierarchy: str    # metropolitan_main·regional_central·branch_main·branch·small_library
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

    # 1. 자관 등록번호 prefix 자동
    if library.sasagwan_prefix:
        enriched["registration_no_prefix"] = library.sasagwan_prefix

    # 2. 청구기호 형식 자동
    enriched["call_number_format"] = library.call_number_format

    # 3. 별치 자동 추천
    title = str(book_data.get("title", "")).lower()
    for category in library.shelf_categories:
        if category in title or category in book_data.get("subject_keywords", []):
            enriched["shelf_category"] = category
            break

    # 4. 040 ▾a 우리 도서관 부호
    enriched["cataloging_agency"] = library.library_id

    # 5. 지역 정책 메타
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
    "LibrarySpecificity",
    "RegionalGovernment",
    "REGIONAL_POLICIES",
    "get_regional_policy",
    "auto_apply_specificity",
    "detect_library_pattern",
]
