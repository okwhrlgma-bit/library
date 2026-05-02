"""OPAC 검색 향상 — Part 82+ 페인 #37 정합.

이용자 페인 (Part 82+):
- 자료 검색 난이도 3.67/5
- 키워드 부족 3.11
- 주제 탐색 실패율 ↑ → 서명·저자만 사용

해결: 자동 키워드·주제어·동의어 확장 → OPAC 검색 정확도 ↑.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# 사서·이용자 동의어 매핑 (사서 응용 부담 ↓)
SYNONYM_MAP = {
    # 일상 용어 ↔ 학술 용어
    "AI": ["인공지능", "기계학습", "딥러닝"],
    "인공지능": ["AI", "기계학습", "딥러닝"],
    "코딩": ["프로그래밍", "소프트웨어 개발"],
    "프로그래밍": ["코딩", "소프트웨어 개발"],
    "투자": ["주식", "자산관리", "재테크"],
    "재테크": ["투자", "주식", "자산관리"],
    "다이어트": ["체중감량", "건강", "식이요법"],
    "요리": ["음식", "조리법", "레시피"],
    "여행": ["관광", "기행"],
    "영어": ["English", "어학", "외국어"],
    "한자": ["漢字", "한문"],
    "역사": ["사학", "한국사", "세계사"],
}


@dataclass(frozen=True)
class EnhancedSearch:
    """향상된 검색 1건."""

    original_query: str
    expanded_keywords: list[str] = field(default_factory=list)
    suggested_subjects: list[str] = field(default_factory=list)
    search_tips: list[str] = field(default_factory=list)


def expand_query(query: str) -> EnhancedSearch:
    """이용자 검색어 → 자동 확장 (동의어·관련어).

    Args:
        query: 이용자 입력 (예: "AI 책 찾아주세요")

    Returns:
        EnhancedSearch (확장 키워드·주제어·팁)
    """
    expanded = [query]
    subjects = []
    tips = []

    # 동의어 확장
    for word in query.split():
        clean = word.strip(".,!?")
        if clean in SYNONYM_MAP:
            expanded.extend(SYNONYM_MAP[clean])
            subjects.extend(SYNONYM_MAP[clean])

    # 검색 팁
    if len(query) < 2:
        tips.append("검색어가 짧습니다. 2글자 이상 입력해주세요.")
    if " " not in query and len(query) > 10:
        tips.append("긴 검색어는 띄어쓰기로 분리해주세요.")
    if query.isdigit():
        tips.append("숫자만 입력 = ISBN 검색 시도. 도서명·저자명도 함께 검색해보세요.")

    # 중복 제거 (순서 보존)
    seen = set()
    unique_expanded = []
    for kw in expanded:
        if kw not in seen:
            seen.add(kw)
            unique_expanded.append(kw)

    return EnhancedSearch(
        original_query=query,
        expanded_keywords=unique_expanded,
        suggested_subjects=list(set(subjects)),
        search_tips=tips,
    )


def suggest_alternative_search(
    failed_query: str,
    *,
    max_suggestions: int = 5,
) -> list[str]:
    """검색 실패 시 대안 제안.

    Args:
        failed_query: 결과 X 검색어
        max_suggestions: 최대 대안 수

    Returns:
        list[str] (대안 검색어)
    """
    suggestions = []

    # 1. 동의어 활용
    if failed_query in SYNONYM_MAP:
        suggestions.extend(SYNONYM_MAP[failed_query])

    # 2. 부분 검색 (앞부분만)
    if len(failed_query) > 4:
        suggestions.append(failed_query[: len(failed_query) - 1])
        suggestions.append(failed_query[: len(failed_query) - 2])

    # 3. 띄어쓰기 추가·제거
    if " " in failed_query:
        suggestions.append(failed_query.replace(" ", ""))
    else:
        # 단순 분리 (Phase 1·실제는 형태소 분석 필요)
        if len(failed_query) > 4:
            mid = len(failed_query) // 2
            suggestions.append(f"{failed_query[:mid]} {failed_query[mid:]}")

    return suggestions[:max_suggestions]


__all__ = ["SYNONYM_MAP", "EnhancedSearch", "expand_query", "suggest_alternative_search"]
