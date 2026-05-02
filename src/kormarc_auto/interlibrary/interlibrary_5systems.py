"""상호대차 5 시스템 통합 — Part 70 갭 7 정합.

5 상호대차 시스템 (헌법 §2 정합):
- 책바다 (NLK·5,200원·전국)
- 책나래 (NLD·무료·장애인) — Part 71 정합
- 책이음 (KOLAS III·통합 회원증)
- 책두레 (KOLAS III 모듈)
- 책단비 (은평구·자관 정합)

사서 페인 (Part 70):
- 사서 일과 30% = 상호대차 = 별도 작업
- 5 시스템 = 매번 별도 처리 = 부담

해결: 통합 라우팅·우선순위·자동 신청.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class System(StrEnum):
    """5 상호대차 시스템."""

    CHAEK_BADA = "chaek_bada"     # 책바다·NLK·5,200원·전국
    CHAEK_NARAE = "chaek_narae"   # 책나래·NLD·무료·장애인
    CHAEK_IEUM = "chaek_ieum"     # 책이음·KOLAS·통합 회원증
    CHAEK_DURE = "chaek_dure"     # 책두레·KOLAS 모듈
    CHAEK_DANBI = "chaek_danbi"   # 책단비·은평구·자관


@dataclass(frozen=True)
class SystemInfo:
    """상호대차 시스템 정보."""

    name: str
    operator: str  # 운영 기관
    cost_won: int  # 0=무료
    coverage: str  # 적용 범위
    target: str  # 대상
    api_url: str = ""  # 통합 API URL (Phase 2)


SYSTEM_DATABASE: dict[System, SystemInfo] = {
    System.CHAEK_BADA: SystemInfo(
        name="책바다",
        operator="국립중앙도서관 (NLK)",
        cost_won=5200,
        coverage="전국 공공도서관",
        target="모든 이용자",
    ),
    System.CHAEK_NARAE: SystemInfo(
        name="책나래",
        operator="국립장애인도서관 (NLD)",
        cost_won=0,
        coverage="전국",
        target="시각·청각·지체장애인 (Part 71)",
    ),
    System.CHAEK_IEUM: SystemInfo(
        name="책이음",
        operator="국립중앙도서관 (KOLAS III 통합)",
        cost_won=0,
        coverage="KOLAS III 가입 도서관",
        target="통합 회원증 사용자",
    ),
    System.CHAEK_DURE: SystemInfo(
        name="책두레",
        operator="국립중앙도서관 (KOLAS III 모듈)",
        cost_won=0,
        coverage="KOLAS III 모듈 가입",
        target="자관 회원",
    ),
    System.CHAEK_DANBI: SystemInfo(
        name="책단비",
        operator="은평구",
        cost_won=0,
        coverage="은평구 공공·작은도서관",
        target="은평구민",
    ),
}


def recommend_system(
    *,
    is_disabled_user: bool = False,
    is_eunpyeong_user: bool = False,
    is_kolas_member: bool = True,
    prefer_free: bool = True,
) -> list[System]:
    """이용자·요청 조건 → 적합 시스템 우선순위 추천.

    예시:
        - 장애인 = [책나래, 책바다]
        - 은평구민 + KOLAS 회원 = [책단비, 책이음, 책두레, 책바다]
        - 일반 + KOLAS 회원 + 무료 우선 = [책이음, 책두레, 책나래, 책바다]
    """
    candidates: list[System] = []

    # 1. 장애인 = 책나래 무료 우선
    if is_disabled_user:
        candidates.append(System.CHAEK_NARAE)

    # 2. 은평구민 = 책단비 우선
    if is_eunpyeong_user:
        candidates.append(System.CHAEK_DANBI)

    # 3. KOLAS 회원 = 통합 무료 시스템 우선
    if is_kolas_member:
        if System.CHAEK_IEUM not in candidates:
            candidates.append(System.CHAEK_IEUM)
        if System.CHAEK_DURE not in candidates:
            candidates.append(System.CHAEK_DURE)

    # 4. 책바다 = 전국·일반 (유료 = 마지막)
    if not prefer_free or not candidates:
        candidates.append(System.CHAEK_BADA)
    else:
        candidates.append(System.CHAEK_BADA)  # fallback

    # 중복 제거 (순서 보존)
    seen: set[System] = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def get_info(system: System) -> SystemInfo:
    """시스템 정보 조회."""
    return SYSTEM_DATABASE[system]


__all__ = ["SYSTEM_DATABASE", "System", "SystemInfo", "get_info", "recommend_system"]
