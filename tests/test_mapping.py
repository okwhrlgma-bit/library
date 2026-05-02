"""KORMARC 008 발행국부호 + 008 빌드 단위 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.kormarc.mapping import (  # noqa: E402
    PUBLICATION_PLACE_CODES,
    build_008,
    lookup_publication_country,
)


def test_korean_capital_codes():
    assert lookup_publication_country("서울") == "ulk"
    assert lookup_publication_country("서울특별시") == "ulk"
    assert lookup_publication_country("Seoul") == "ulk"


def test_korean_metro_distinct_codes():
    """광역시별 코드가 서로 다른지 — 이전엔 모두 'ulk' 였던 버그 회귀 방지."""
    assert lookup_publication_country("부산") == "bnk"
    assert lookup_publication_country("대구") == "tgk"
    assert lookup_publication_country("인천") == "ick"
    assert lookup_publication_country("광주") == "kjk"
    assert lookup_publication_country("대전") == "tjk"
    assert lookup_publication_country("울산") == "usk"
    # 모두 다른 값이어야 함
    codes = {
        lookup_publication_country(p) for p in ["부산", "대구", "인천", "광주", "대전", "울산"]
    }
    assert len(codes) == 6


def test_partial_match():
    """'서울특별시 종로구' → 'ulk' (부분 매칭)."""
    assert lookup_publication_country("서울특별시 종로구 사직로") == "ulk"
    assert lookup_publication_country("경기도 파주시 회동길") == "ggk"


def test_foreign_codes():
    assert lookup_publication_country("미국") == "xxu"
    assert lookup_publication_country("일본") == "ja "
    assert lookup_publication_country("Tokyo") == "ja "
    assert lookup_publication_country("New York") == "nyu"
    assert lookup_publication_country("프랑스") == "fr "
    assert lookup_publication_country("독일") == "gw "


def test_unknown_returns_xx():
    assert lookup_publication_country("화성") == "xx "
    assert lookup_publication_country("") == "xx "
    assert lookup_publication_country(None) == "xx "


def test_build_008_length():
    """008은 정확히 40자리."""
    s = build_008(publication_year="2024", publication_place="서울")
    assert len(s) == 40


def test_build_008_country_position():
    """발행국부호는 15-17 위치 (3자리)."""
    s = build_008(publication_year="2024", publication_place="부산")
    assert s[15:18] == "bnk"

    s2 = build_008(publication_year="2024", publication_place="Tokyo")
    assert s2[15:18] == "ja "


def test_publication_place_codes_table_size():
    """매핑 테이블 충분히 커졌는지 — 회귀 방지."""
    assert len(PUBLICATION_PLACE_CODES) >= 80, (
        "발행국부호 매핑 테이블이 너무 작습니다 (한국 시도 + 외국 주요국 포함 필요)"
    )
