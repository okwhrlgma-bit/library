"""분류 시스템 추상 인터페이스 — 다국가 진출 대비.

미래에 KDC 외 DDC·NDC·LCC·UDC 등을 끼워넣을 수 있는 베이스.

현재는 KDC만 활성. 다른 시스템은 placeholder.
글로벌 진출 시 (한국 → 일본 → 영어권 순) 단계적 활성.
"""

from __future__ import annotations

from typing import Any, Protocol


class ClassificationScheme(Protocol):
    """분류 시스템 인터페이스."""

    name: str  # "KDC" / "DDC" / "NDC" / "LCC" / "UDC"
    edition: str  # "6판" / "23rd" 등
    marc_field: str  # KORMARC: 056, MARC21: 082(DDC) / 050(LCC)

    def recommend(self, book_data: dict[str, Any]) -> list[dict[str, Any]]:
        """후보 추천 (code/confidence/source/rationale)."""
        ...

    def search_tree(self, query: str) -> list[tuple[str, str]]:
        """키워드로 분류 트리 탐색."""
        ...


# 등록된 분류 시스템 (글로벌 진출 시 확장)
SCHEMES: dict[str, dict[str, Any]] = {
    "KDC": {
        "name": "한국십진분류법",
        "edition": "6판",
        "marc_field_kormarc": "056",
        "marc_field_marc21": "082",  # KDC 표시는 KORMARC 056 또는 MARC21 092
        "country": "KR",
        "active": True,
        "module": "kormarc_auto.classification.kdc_classifier",
    },
    "DDC": {
        "name": "Dewey Decimal Classification",
        "edition": "23rd",
        "marc_field_kormarc": "082",
        "marc_field_marc21": "082",
        "country": "US/Global",
        "active": False,  # 글로벌 진출 2단계
        "license_required": True,  # OCLC WebDewey 라이센스 필요
        "module": None,  # placeholder
    },
    "NDC": {
        "name": "日本十進分類法 (Nippon Decimal Classification)",
        "edition": "10판",
        "marc_field_kormarc": "082",
        "marc_field_marc21": "082",
        "country": "JP",
        "active": False,  # 글로벌 진출 1단계 (일본)
        "module": None,
    },
    "LCC": {
        "name": "Library of Congress Classification",
        "edition": "현행",
        "marc_field_kormarc": None,  # KORMARC에 직접 매핑 없음
        "marc_field_marc21": "050",
        "country": "US",
        "active": False,  # 글로벌 진출 2단계 (대학도서관)
        "module": None,
    },
    "UDC": {
        "name": "Universal Decimal Classification",
        "edition": "현행",
        "marc_field_kormarc": "080",
        "marc_field_marc21": "080",
        "country": "EU/Global",
        "active": False,  # 글로벌 진출 3단계 (유럽·중남미)
        "license_required": True,
        "module": None,
    },
}


def get_active_schemes() -> list[str]:
    """현재 활성된 분류 시스템 키 목록."""
    return [k for k, v in SCHEMES.items() if v.get("active")]


def get_scheme_info(name: str) -> dict[str, Any] | None:
    """시스템명으로 메타정보 조회."""
    return SCHEMES.get(name.upper())
