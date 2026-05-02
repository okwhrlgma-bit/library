"""KDC 신주제 자동 학습 — Part 77 (P17) 정합.

사서 페인 (Part 77):
- KDC 분류 = 응용력 필요 (단순 암기 X)
- 신주제 (AI·계량정보학·블록체인·메타버스) = KDC 미반영
- 자관마다 다른 분류 = 종합목록 혼란

해결: 신주제 자동 감지 + AI 응용 추천 + 자관별 결정 누적.
"""

from __future__ import annotations

from dataclasses import dataclass

# 신주제 키워드 매핑 (KDC 6판 미반영 분야)
NEW_SUBJECTS_KDC = {
    # AI·머신러닝
    "ai": "004.7",  # 인공지능 → 컴퓨터과학·정보처리
    "인공지능": "004.7",
    "머신러닝": "004.7",
    "딥러닝": "004.7",
    "생성형": "004.7",
    "ChatGPT": "004.7",
    "LLM": "004.7",
    # 블록체인·암호화
    "블록체인": "005.8",  # 컴퓨터 보안·암호
    "암호화폐": "327.5",  # 통화·금융
    "비트코인": "327.5",
    "NFT": "005.8",
    # 메타버스·VR/AR
    "메타버스": "004.79",
    "VR": "004.79",
    "AR": "004.79",
    "가상현실": "004.79",
    "증강현실": "004.79",
    # 데이터 과학
    "데이터 과학": "005.7",
    "빅데이터": "005.7",
    "계량정보학": "020.7",  # 도서관학·정보학 분야 (KCI 검증)
    # ESG·지속가능성
    "ESG": "338.9",
    "지속가능": "338.9",
    "탄소 중립": "539.91",
    "기후 변화": "539.91",
    # 핀테크·디지털 금융
    "핀테크": "327.5",
    "디지털 금융": "327.5",
    "마이데이터": "005.7",
}


@dataclass(frozen=True)
class SubjectRecommendation:
    """신주제 분류 추천."""

    keyword: str
    kdc_code: str
    confidence: float  # 0.0~1.0
    needs_review: bool = True  # 사서 검토 필수


def detect_new_subject(book_data: dict) -> list[SubjectRecommendation]:
    """책 정보 → 신주제 자동 감지·KDC 추천.

    Args:
        book_data: title·subject_keywords·description 포함

    Returns:
        list[SubjectRecommendation] (정확도 ≥0.5)
    """
    text = " ".join(
        str(book_data.get(k, "")) for k in ["title", "subject_keywords", "description", "summary"]
    ).lower()

    recommendations = []
    for keyword, kdc in NEW_SUBJECTS_KDC.items():
        if keyword.lower() in text:
            confidence = 0.85 if keyword in text else 0.65
            recommendations.append(
                SubjectRecommendation(
                    keyword=keyword,
                    kdc_code=kdc,
                    confidence=confidence,
                    needs_review=True,  # 신주제 = 항상 사서 검토
                )
            )

    # 정확도 순 정렬·상위 3건
    recommendations.sort(key=lambda r: r.confidence, reverse=True)
    return recommendations[:3]


def is_new_subject_book(book_data: dict) -> bool:
    """신주제 책 여부 (자동 감지)."""
    return len(detect_new_subject(book_data)) > 0


__all__ = [
    "NEW_SUBJECTS_KDC",
    "SubjectRecommendation",
    "detect_new_subject",
    "is_new_subject_book",
]
