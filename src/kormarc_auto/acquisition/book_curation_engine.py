"""북큐레이션 엔진 — Part 82+ 페인 #40 정합.

학교도서관 사서교사 페인:
- 사서교사 12.1% 배치 (11,785관 중 1,432명)
- 큐레이션 = 정보·전문성·자원·경영·홍보·마케팅 5축 부담
- 학생 = 큐레이션 응답 = 필요

해결: 자동 큐레이션 (계절·테마·연령·분야).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

CURATION_THEMES = {
    "spring": ["봄·새출발", "신학기", "봄꽃", "환경의 날"],
    "summer": ["여름·바다", "방학", "독서 챌린지", "더위 식히기"],
    "autumn": ["가을·독서의 계절", "단풍", "독서주간"],
    "winter": ["겨울·연말", "방학", "신년 계획", "회고"],
    "library_week": ["도서관주간", "도서관의 날 4/12"],
    "exam_period": ["시험 대비", "학습법", "동기부여"],
    "new_semester": ["신학기", "선후배", "교과 연계"],
    "vacation": ["방학 추천", "장편 도전", "독서 일기"],
}


AGE_GROUPS = {
    "kindergarten": "유치원 (5~7세)",
    "elementary_low": "초등 저학년 (1~3)",
    "elementary_high": "초등 고학년 (4~6)",
    "middle": "중학생",
    "high": "고등학생",
    "adult": "성인",
    "senior": "노인",
}


@dataclass(frozen=True)
class CurationCriteria:
    """큐레이션 기준 1건."""

    theme: str
    age_group: str
    kdc_focus: list[str] = field(default_factory=list)  # 강조 KDC
    max_books: int = 10


@dataclass(frozen=True)
class CurationResult:
    """큐레이션 결과."""

    theme: str
    age_group: str
    selected_books: list[dict]
    poster_title: str
    description: str


def auto_select_theme(today: date | None = None) -> str:
    """오늘 날짜 → 자동 테마 추천."""
    today = today or date.today()
    month = today.month
    if month in (3, 4):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "autumn"
    else:
        return "winter"


def curate_books(
    candidates: list[dict],
    criteria: CurationCriteria,
) -> CurationResult:
    """후보 도서 → 자동 큐레이션.

    Args:
        candidates: list[dict(isbn·title·author·kdc·age_target)]
        criteria: 기준

    Returns:
        CurationResult (큐레이션 + 자동 포스터 제목·설명)
    """
    # 1. 연령 필터
    filtered = [
        b for b in candidates
        if b.get("age_target", criteria.age_group) == criteria.age_group
        or not b.get("age_target")
    ]

    # 2. KDC 우선순위
    if criteria.kdc_focus:
        focused = [
            b for b in filtered
            if any(b.get("kdc", "").startswith(k) for k in criteria.kdc_focus)
        ]
        # 강조 + 일반 결합
        filtered = focused + [b for b in filtered if b not in focused]

    selected = filtered[: criteria.max_books]

    # 3. 자동 포스터 텍스트
    age_label = AGE_GROUPS.get(criteria.age_group, "전체")
    theme_keywords = CURATION_THEMES.get(criteria.theme, [criteria.theme])

    poster_title = f"{theme_keywords[0]} 추천 도서 {len(selected)}선"
    description = (
        f"{age_label}을 위한 {theme_keywords[0]} 테마 큐레이션입니다. "
        f"사서가 직접 골랐어요."
    )

    return CurationResult(
        theme=criteria.theme,
        age_group=criteria.age_group,
        selected_books=selected,
        poster_title=poster_title,
        description=description,
    )


def generate_curation_markdown(result: CurationResult) -> str:
    """큐레이션 결과 markdown (도서관 게시판·블로그·SNS 가능)."""
    lines = [
        f"# {result.poster_title}",
        "",
        f"> {result.description}",
        f"> 대상: {AGE_GROUPS.get(result.age_group, '전체')} · 테마: {result.theme}",
        "",
        "## 추천 도서",
        "",
    ]
    for i, book in enumerate(result.selected_books, 1):
        title = book.get("title", "")
        author = book.get("author", "")
        kdc = book.get("kdc", "")
        lines.append(f"{i}. **{title}** — {author} (KDC {kdc})")

    return "\n".join(lines)


__all__ = [
    "AGE_GROUPS",
    "CURATION_THEMES",
    "CurationCriteria",
    "CurationResult",
    "auto_select_theme",
    "curate_books",
    "generate_curation_markdown",
]
