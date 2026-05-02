"""도서관 위계·분류 (광역대표·지역중앙·거점·분관) — 페인 #53 정합.

문체부 2022·2024 공공도서관 매뉴얼 정합.
지역 분류 (도시·도농복합·농어촌) + 위계 (광역대표·지역중앙·거점·분관).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LibraryHierarchy = Literal[
    "metropolitan_main",  # 광역대표 (시도 1관)
    "regional_central",   # 지역중앙 (시군구 1관)
    "branch_main",        # 거점도서관
    "branch",             # 분관
    "small_library",      # 작은도서관
]

RegionalType = Literal[
    "urban",              # 도시형 (인구 ↑)
    "urban_rural_mixed",  # 도농복합형
    "rural_fishing",      # 농어촌형
]


@dataclass(frozen=True)
class LibraryClassification:
    """도서관 위계·지역 분류."""

    hierarchy: LibraryHierarchy
    regional_type: RegionalType
    avg_users_per_librarian: int = 0
    avg_books: int = 0
    consortium_priority: list[str] = None  # 권장 컨소시엄


HIERARCHY_INFO = {
    "metropolitan_main": {
        "name": "광역대표도서관",
        "examples": "서울도서관·부산도서관·인천대표도서관",
        "role": "시도 단위 정책·디지털 중앙·지역 협력",
    },
    "regional_central": {
        "name": "지역중앙도서관",
        "examples": "자치구·시군구 단위 중앙",
        "role": "자치구 정책·분관 관리",
    },
    "branch_main": {
        "name": "거점도서관",
        "examples": "지역 중심 분관 (보통 1만 권+)",
        "role": "지역 거점·종합 서비스",
    },
    "branch": {
        "name": "분관",
        "examples": "동단위 분관 (5천 권+)",
        "role": "지역 밀착·일상 서비스",
    },
    "small_library": {
        "name": "작은도서관",
        "examples": "마을·아파트·종교·민간 작은도서관",
        "role": "최소 단위·자원봉사·1인 사서",
    },
}

REGIONAL_INFO = {
    "urban": {
        "name": "도시형",
        "characteristics": "인구 ↑·도서관 ↑·예산 ↑",
        "examples": "서울 25 자치구·부산·대구·인천",
    },
    "urban_rural_mixed": {
        "name": "도농복합형",
        "characteristics": "도시 + 농촌 혼합·중간 예산",
        "examples": "수원·청주·전주·천안",
    },
    "rural_fishing": {
        "name": "농어촌형",
        "characteristics": "인구 ↓·도서관 ↓·정부 지원 의존",
        "examples": "강원·전남·경북 군 단위",
    },
}


def recommend_strategy(classification: LibraryClassification) -> dict:
    """위계·지역 → 영업·운영 전략 자동.

    Returns:
        dict (영업 우선·가격 정합·페르소나 매칭)
    """
    hier = classification.hierarchy
    region = classification.regional_type

    # 가격 권장 (Part 64 정합)
    if hier == "metropolitan_main":
        price_tier = "Enterprise"
        discount = "협의"
    elif hier == "regional_central":
        price_tier = "B2B-Pro 또는 Enterprise"
        discount = "30% (자치구 25관 일괄)"
    elif hier == "branch_main":
        price_tier = "B2B-Starter 또는 B2B-Pro"
        discount = "20% (10~24관)"
    elif hier == "branch":
        price_tier = "B2B-Starter"
        discount = "0~15%"
    else:  # small_library
        price_tier = "Personal (사서 자비)"
        discount = "무료 + Personal 9,900"

    # 페르소나 매칭
    if hier == "small_library":
        personas = ["P3 자원봉가", "P19 사서 0명", "C5b 작은도서관 1인"]
    elif hier == "branch":
        personas = ["P1 매크로", "P4 1년 계약직", "P14 야간"]
    elif hier == "branch_main":
        personas = ["P1 매크로", "P9 Reference"]
    else:  # central·metropolitan
        personas = ["P1 매크로", "P9 Reference", "관장"]

    # 정부 자금 권장
    if region == "rural_fishing":
        funding = "농어촌 도서관 보급 사업·정부 지원 80%"
    elif region == "urban_rural_mixed":
        funding = "AI 바우처·디지털 바우처"
    else:
        funding = "AI 바우처·디딤돌·자치구 예산"

    return {
        "price_tier": price_tier,
        "discount": discount,
        "personas": personas,
        "funding_recommendation": funding,
        "hierarchy_role": HIERARCHY_INFO[hier]["role"],
        "regional_characteristics": REGIONAL_INFO[region]["characteristics"],
    }


__all__ = [
    "LibraryHierarchy",
    "RegionalType",
    "LibraryClassification",
    "HIERARCHY_INFO",
    "REGIONAL_INFO",
    "recommend_strategy",
]
