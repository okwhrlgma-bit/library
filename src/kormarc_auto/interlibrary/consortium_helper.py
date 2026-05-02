"""도서관 협력·컨소시엄 보조 — Part 82+ 페인 #49 정합.

사서 페인:
- 전국적 협력 체계 부족 (KCI 학술 검증)
- 학교-공공 연계 약함
- 책이음 가맹 = 사서 이해도 낮음

해결: 협력 통합 라우팅 + 가맹 도서관 검색·정보 자동.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ConsortiumType = Literal[
    "chaek_ieum",  # 책이음 (KOLAS III 통합 회원증)
    "chaek_dure",  # 책두레 (KOLAS III 모듈)
    "kolisnet",  # KOLISNET 종합목록
    "school_public",  # 학교-공공 연계
    "academic",  # 대학도서관 컨소시엄 (KORIBLE·CCL)
    "regional",  # 지역 도서관 협의회 (자치구·시도)
]


@dataclass(frozen=True)
class Consortium:
    """협력 체계 정보."""

    type: ConsortiumType
    name: str
    operator: str
    member_count: int = 0
    description: str = ""
    join_url: str = ""


CONSORTIUM_DATABASE = {
    "chaek_ieum": Consortium(
        type="chaek_ieum",
        name="책이음",
        operator="국립중앙도서관 (NLK)",
        member_count=1300,
        description="전국 단일 대출증 = 1장으로 가맹 도서관 모두 이용",
        join_url="https://books.nl.go.kr/PU/contents/P20201000000.do",
    ),
    "chaek_dure": Consortium(
        type="chaek_dure",
        name="책두레",
        operator="국립중앙도서관 (KOLAS III 모듈)",
        member_count=600,
        description="자관 회원 = 책두레 모듈 가맹 도서관 상호대차",
    ),
    "kolisnet": Consortium(
        type="kolisnet",
        name="KOLISNET 종합목록",
        operator="국립중앙도서관",
        member_count=2000,
        description="전국 2,000+ 도서관 통합 목록·서지 검색",
    ),
    "school_public": Consortium(
        type="school_public",
        name="학교-공공 연계",
        operator="문체부·교육부",
        description="학교도서관 ↔ 공공도서관 자료·서비스 협력",
    ),
    "academic": Consortium(
        type="academic",
        name="대학도서관 컨소시엄 (KORIBLE)",
        operator="한국교육학술정보원 (KERIS)",
        description="대학도서관 학술자료 통합·상호대차",
    ),
    "regional": Consortium(
        type="regional",
        name="지역 도서관 협의회",
        operator="자치구·시도 (지역별)",
        description="자치구 도서관 컨소시엄 (예: 두드림 600관)",
    ),
}


def recommend_consortium_join(
    *,
    library_type: str,  # "public·school·academic·small·special"
    region: str = "",
    has_kolas: bool = True,
) -> list[Consortium]:
    """자관 유형·지역 → 권장 가맹 컨소시엄.

    Args:
        library_type: 자관 유형
        region: 지역 (자치구·시도)
        has_kolas: KOLAS 사용 여부

    Returns:
        list[Consortium] (우선순위 정렬)
    """
    recommendations = []

    # 1. 책이음 = 모든 공공·작은도서관 (KOLAS 가맹 시)
    if has_kolas and library_type in ("public", "small"):
        recommendations.append(CONSORTIUM_DATABASE["chaek_ieum"])

    # 2. 책두레 = KOLAS III 모듈 도서관
    if has_kolas:
        recommendations.append(CONSORTIUM_DATABASE["chaek_dure"])

    # 3. KOLISNET = 모든 도서관
    recommendations.append(CONSORTIUM_DATABASE["kolisnet"])

    # 4. 학교-공공 연계
    if library_type in ("school", "public"):
        recommendations.append(CONSORTIUM_DATABASE["school_public"])

    # 5. 대학 컨소시엄
    if library_type == "academic":
        recommendations.append(CONSORTIUM_DATABASE["academic"])

    # 6. 지역 협의회
    if region:
        recommendations.append(CONSORTIUM_DATABASE["regional"])

    return recommendations


def get_consortium_info(consortium_type: ConsortiumType) -> Consortium:
    """컨소시엄 정보 조회."""
    return CONSORTIUM_DATABASE[consortium_type]


__all__ = [
    "CONSORTIUM_DATABASE",
    "Consortium",
    "ConsortiumType",
    "get_consortium_info",
    "recommend_consortium_join",
]
