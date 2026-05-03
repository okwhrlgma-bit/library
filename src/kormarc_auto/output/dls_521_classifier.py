"""독서로DLS 521 자료유형 자동 분기 — 페르소나 01 100점 (사서교사).

KERIS DLS / 독서로DLS 521 자료유형 코드 (5 카테고리):
- BK: 단행본 (도서)
- SR: 연속간행물 (잡지·신문)
- NB: 비도서 (CD·DVD·키트)
- LR: 장학자료 (학습 보조)
- ET: 기타

DLS 반입 시 521 ▾a 자동 채움 = 사서교사 작업 시간 단축 (기존 수동 입력).
12,200 학교도서관·86% 자원봉사 = 자동화 가치 ↑.

작동:
1. KORMARC LDR + 008 + 245 + KDC → DLS 521 자동 추론
2. 자신없는 경우 = 사서 검토용 후보 3개 반환
3. 사서교사 1클릭 선택
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

DlsCategory = Literal["BK", "SR", "NB", "LR", "ET"]


# 카테고리 메타
DLS_521_CATEGORIES: dict[DlsCategory, str] = {
    "BK": "단행본 (Book)",
    "SR": "연속간행물 (Serial)",
    "NB": "비도서 (Non-Book·CD·DVD·키트)",
    "LR": "장학자료 (Learning Resource)",
    "ET": "기타 (Etc.)",
}

# KORMARC 자료유형 → DLS 521 매핑 (Phase 1.5 17 subtype 기준)
KORMARC_TO_DLS_521: dict[str, DlsCategory] = {
    "book_single": "BK",
    "book_multi": "BK",
    "book_part": "BK",
    "thesis": "BK",
    "rare_book": "BK",
    "ebook": "BK",  # DLS = 전자책도 BK 처리 (별도 NB 가능)
    "braille": "LR",  # 학습 보조
    "serial_current": "SR",
    "serial_ceased": "SR",
    "ejournal": "SR",
    "audiobook": "NB",
    "dvd": "NB",
    "multimedia": "NB",
    "music_cd": "NB",
    "map": "NB",
    "kit": "LR",  # 학습 키트
    "non_book": "NB",
}


@dataclass(frozen=True)
class Dls521Result:
    """DLS 521 분류 결과."""

    primary: DlsCategory
    confidence: float  # 0.0~1.0
    candidates: list[DlsCategory]  # 사서 검토용 후보 (최대 3)
    reason: str  # 분류 근거
    requires_review: bool = False  # confidence < 0.7 = 사서 검토 권장


def classify_dls_521(book_data: dict[str, Any]) -> Dls521Result:
    """KORMARC book_data → DLS 521 자동 분류.

    Args:
        book_data: aggregator 결과 + material_type 필드

    Returns:
        Dls521Result (primary·confidence·candidates·reason)
    """
    material = book_data.get("material_type", "")
    title = str(book_data.get("title", "")).lower()
    kdc = str(book_data.get("kdc", ""))
    summary = str(book_data.get("summary", "") or "").lower()

    # 1차: material_type 직접 매핑 (가장 강한 신호)
    if material and material in KORMARC_TO_DLS_521:
        primary = KORMARC_TO_DLS_521[material]
        return Dls521Result(
            primary=primary,
            confidence=0.95,
            candidates=[primary],
            reason=f"material_type={material} → DLS {primary}",
        )

    # 2차: KDC 기반 추론
    if kdc:
        kdc_main = kdc[0] if kdc[:1].isdigit() else ""
        if kdc_main == "0":  # 총류 = 사전·연감
            return Dls521Result("LR", 0.7, ["LR", "BK"], f"KDC {kdc_main} (총류) → 장학자료")
        if kdc_main in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            # 일반 분류 = BK
            primary = "BK"
            return Dls521Result(primary, 0.85, ["BK"], f"KDC {kdc_main} → 단행본")

    # 3차: 제목 키워드
    if any(kw in title for kw in ["dvd", "cd", "음반", "영상", "오디오"]):
        return Dls521Result(
            "NB",
            0.8,
            ["NB"],
            "제목 비도서 키워드 매칭",
        )
    if any(kw in title for kw in ["월간", "주간", "계간", "저널", "잡지"]):
        return Dls521Result("SR", 0.85, ["SR"], "제목 연속간행물 키워드")
    if any(kw in title for kw in ["워크북", "교재", "문제집", "참고서", "사전"]):
        return Dls521Result("LR", 0.8, ["LR", "BK"], "제목 학습 자료 키워드")

    # 4차: summary 키워드
    if any(kw in summary for kw in ["dvd", "cd", "음반", "영상"]):
        return Dls521Result("NB", 0.7, ["NB", "BK"], "summary 비도서 키워드")

    # 기본: BK + 사서 검토
    return Dls521Result(
        primary="BK",
        confidence=0.5,
        candidates=["BK", "LR", "ET"],
        reason="명확한 신호 없음·기본 BK + 사서 검토 권장",
        requires_review=True,
    )


def add_dls_521_to_book_data(book_data: dict[str, Any]) -> dict[str, Any]:
    """book_data에 DLS 521 ▾a 자동 추가.

    Returns:
        enriched book_data (dls_521 필드 포함)
    """
    result = classify_dls_521(book_data)
    enriched = dict(book_data)
    enriched["dls_521"] = result.primary
    enriched["dls_521_confidence"] = result.confidence
    enriched["dls_521_candidates"] = result.candidates
    enriched["dls_521_requires_review"] = result.requires_review
    return enriched


__all__ = [
    "DLS_521_CATEGORIES",
    "KORMARC_TO_DLS_521",
    "Dls521Result",
    "DlsCategory",
    "add_dls_521_to_book_data",
    "classify_dls_521",
]
