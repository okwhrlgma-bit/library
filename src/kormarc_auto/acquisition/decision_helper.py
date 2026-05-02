"""수서 결정 지원 (Acquisition Decision Helper) — Part 74 §A 정합.

사서 페인 (Part 74·B):
- 신간 추천·선정 = 5h/주 (사서 일과)
- 출판사·서점 가격 비교 = 2h/주
- 정치·종교 중립성 부담 = 권당 5분 (Part 80·페인 21)
- 이용자 요청 vs 예산 vs 장서 구성 = 3중 고려

해결: AI 균형 추천 + 가격 비교 + 중립성 자동 검증.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PoliticalReligiousFlag = Literal["neutral", "political", "religious", "controversial"]


@dataclass(frozen=True)
class AcquisitionRecommendation:
    """수서 추천 1건."""

    isbn: str
    title: str
    author: str
    publisher: str
    price_won: int
    kdc: str
    rating: float = 0.0  # 0~5 (별점·평점)
    reviews_count: int = 0
    flag: PoliticalReligiousFlag = "neutral"
    user_requests: int = 0  # 이용자 요청 건수
    decision_score: float = 0.0  # 0~100
    reason: str = ""


def evaluate_neutrality(book_data: dict) -> PoliticalReligiousFlag:
    """정치·종교 중립성 자동 검증 (Part 80·페인 21).

    AI1 윤리 검증 + 키워드 기반.
    """
    text = " ".join(
        str(book_data.get(k, ""))
        for k in ["title", "subject_keywords", "description"]
    ).lower()

    political_kw = ["보수", "진보", "여당", "야당", "좌파", "우파", "이재명", "윤석열", "정당"]
    religious_kw = ["기독교 우월", "이단", "사이비", "종교 비방"]
    controversial_kw = ["혐오", "차별", "음모론"]

    if any(kw in text for kw in controversial_kw):
        return "controversial"
    if any(kw in text for kw in political_kw):
        return "political"
    if any(kw in text for kw in religious_kw):
        return "religious"
    return "neutral"


def calculate_decision_score(
    *,
    rating: float = 0.0,
    user_requests: int = 0,
    publisher_reputation: float = 0.5,  # 0~1
    budget_remaining_ratio: float = 1.0,  # 0~1
    is_neutral: bool = True,
) -> float:
    """수서 결정 점수 (0~100).

    가중치 (사서 일과 정합):
        - 평점 (rating × 5 = 25)
        - 이용자 요청 (≥5건 = 20)
        - 출판사 신뢰 (× 15 = 15)
        - 예산 잔여 (× 10 = 10)
        - 중립성 통과 (30 또는 0)
    """
    score = 0.0
    score += min(rating * 5, 25)
    score += min(user_requests * 4, 20)
    score += publisher_reputation * 15
    score += budget_remaining_ratio * 10
    score += 30 if is_neutral else 0
    return min(score, 100)


def recommend_books(
    candidates: list[dict],
    *,
    budget_remaining_won: int = 1_000_000,
    avg_book_price: int = 18_000,
    max_recommendations: int = 20,
) -> list[AcquisitionRecommendation]:
    """후보 도서 → 수서 추천 우선순위.

    Args:
        candidates: list[dict(isbn·title·author·publisher·price_won·kdc·rating·user_requests)]
        budget_remaining_won: 자관 예산 잔여
        avg_book_price: 평균 도서 가격
        max_recommendations: 최대 추천 (기본 20)

    Returns:
        list[AcquisitionRecommendation] (점수 내림차순)
    """
    budget_ratio = min(budget_remaining_won / max(avg_book_price * 100, 1), 1.0)

    recs = []
    for book in candidates:
        flag = evaluate_neutrality(book)
        is_neutral = flag == "neutral"
        score = calculate_decision_score(
            rating=book.get("rating", 0.0),
            user_requests=book.get("user_requests", 0),
            publisher_reputation=book.get("publisher_reputation", 0.5),
            budget_remaining_ratio=budget_ratio,
            is_neutral=is_neutral,
        )

        reason_parts = []
        if book.get("rating", 0) >= 4.0:
            reason_parts.append("높은 평점")
        if book.get("user_requests", 0) >= 5:
            reason_parts.append(f"이용자 요청 {book['user_requests']}건")
        if not is_neutral:
            reason_parts.append(f"중립성 검토 필요 ({flag})")

        recs.append(
            AcquisitionRecommendation(
                isbn=book.get("isbn", ""),
                title=book.get("title", ""),
                author=book.get("author", ""),
                publisher=book.get("publisher", ""),
                price_won=book.get("price_won", 0),
                kdc=book.get("kdc", ""),
                rating=book.get("rating", 0.0),
                reviews_count=book.get("reviews_count", 0),
                flag=flag,
                user_requests=book.get("user_requests", 0),
                decision_score=score,
                reason=" / ".join(reason_parts),
            )
        )

    recs.sort(key=lambda r: r.decision_score, reverse=True)
    return recs[:max_recommendations]


__all__ = [
    "AcquisitionRecommendation",
    "PoliticalReligiousFlag",
    "calculate_decision_score",
    "evaluate_neutrality",
    "recommend_books",
]
