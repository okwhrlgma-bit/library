"""이용자 개인화 추천 — Part 82+ 페인 #47 정합.

도서관 정보나루 빅데이터 = 운영 중·개인화 부족.

해결: 협업 필터링 + KDC 기반 + 자관 history + Mem0 학습.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class UserPreference:
    """이용자 선호."""

    user_id: str
    age_group: str  # AGE_GROUPS (book_curation_engine)
    favorite_kdc: list[str]  # 선호 KDC 대분류
    loan_history: list[str]  # ISBN 누적
    avg_books_per_month: int = 0


@dataclass(frozen=True)
class Recommendation:
    """개인화 추천 1건."""

    book: dict
    score: float  # 0~100
    reason: str


def analyze_user_preference(loan_history: list[dict]) -> dict:
    """대출 이력 → 선호 분석.

    Args:
        loan_history: list[dict(kdc·age_target·isbn)]

    Returns:
        선호 dict (favorite_kdc·avg_per_month·patterns)
    """
    kdcs = Counter()
    for book in loan_history:
        kdc = str(book.get("kdc", ""))
        if kdc:
            major = kdc[0] + "00" if kdc[0].isdigit() else "000"
            kdcs[major] += 1

    favorites = [k for k, _ in kdcs.most_common(3)]
    return {
        "favorite_kdc": favorites,
        "total_loans": len(loan_history),
        "diversity_score": len(kdcs) / 10,  # 10 KDC 대분류 중 활용 비율
    }


def recommend_for_user(
    candidates: list[dict],
    user_preference: dict,
    *,
    max_recommendations: int = 5,
) -> list[Recommendation]:
    """이용자 선호 → 자동 추천.

    Args:
        candidates: list[dict(isbn·title·kdc·rating)]
        user_preference: analyze_user_preference 결과
        max_recommendations: 최대 추천 수

    Returns:
        list[Recommendation] (점수 내림순)
    """
    favorites = user_preference.get("favorite_kdc", [])
    recs = []

    for book in candidates:
        # 이미 대출한 책 제외 (history 기반)
        if book.get("isbn") in [b.get("isbn") for b in user_preference.get("loan_history", [])]:
            continue

        kdc = str(book.get("kdc", ""))
        major = kdc[0] + "00" if kdc and kdc[0].isdigit() else ""

        score = 0
        reason_parts = []

        # 1. 선호 KDC 일치 (50점)
        if major in favorites:
            score += 50
            reason_parts.append(f"선호 분야 {major}")

        # 2. 평점 (25점)
        rating = book.get("rating", 0)
        score += min(rating * 5, 25)
        if rating >= 4.0:
            reason_parts.append(f"높은 평점 {rating}")

        # 3. 다양성 보너스 (25점) — 미선호 분야도 일부
        if major not in favorites and user_preference.get("diversity_score", 0) > 0.5:
            score += 15
            reason_parts.append("다양성 확장")

        recs.append(
            Recommendation(
                book=book,
                score=score,
                reason=" / ".join(reason_parts) or "기본 추천",
            )
        )

    recs.sort(key=lambda r: r.score, reverse=True)
    return recs[:max_recommendations]


def collaborative_filter(
    target_user_history: list[str],
    *,
    similar_users_history: dict[str, list[str]],
    max_recommendations: int = 5,
) -> list[str]:
    """협업 필터링 (간단 Phase 1).

    "당신과 비슷한 이용자들이 빌린 책".

    Args:
        target_user_history: 대상 사용자 ISBN 누적
        similar_users_history: dict[user_id, list[ISBN]]
        max_recommendations: 최대 추천 ISBN 수

    Returns:
        list[ISBN] (추천)
    """
    target_set = set(target_user_history)

    # 유사 사용자별 = 공통 책 ↑ + 비대상 책 누적
    candidate_counts = Counter()
    for _user_id, history in similar_users_history.items():
        history_set = set(history)
        # 공통도 (Jaccard)
        common = target_set & history_set
        if len(common) < 2:
            continue
        # 비대상 책 = 추천 후보
        for isbn in history_set - target_set:
            candidate_counts[isbn] += len(common)

    return [isbn for isbn, _ in candidate_counts.most_common(max_recommendations)]


__all__ = [
    "Recommendation",
    "UserPreference",
    "analyze_user_preference",
    "collaborative_filter",
    "recommend_for_user",
]
