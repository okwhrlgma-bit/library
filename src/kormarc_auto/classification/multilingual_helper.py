"""다국어 도서 처리 보조 — Part 82+ 페인 #42 정합.

사서 페인:
- 다국어 도서 (영어·중국어·일본어 + 베트남·태국·아랍·몽골) = 처리 부담
- 사서 외국어 한계
- 다문화 도서관 (전국 30+) = 별도 분류

해결: 자동 언어 감지 + KORMARC 008 35-37 언어부호 자동.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# KORMARC 008 35-37 언어부호 (ISO 639-2)
LANGUAGE_CODES = {
    "kor": "한국어",
    "eng": "영어",
    "jpn": "일본어",
    "chi": "중국어",
    "vie": "베트남어",
    "tha": "태국어",
    "ara": "아랍어",
    "mon": "몽골어",
    "rus": "러시아어",
    "fre": "프랑스어",
    "ger": "독일어",
    "spa": "스페인어",
    "ita": "이탈리아어",
}


# 문자 범위 → 언어 매핑 (Phase 1·휴리스틱)
SCRIPT_LANGUAGE_MAP = [
    (r"[가-힣]", "kor"),  # 한글
    (r"[ぁ-ゔゞァ-・ヽヾ゛゜ー]", "jpn"),  # 일본어 가나
    (r"[一-龯]", "chi"),  # 한자 (중국어 / 일본어 / 한국어 한자)
    (r"[А-Яа-я]", "rus"),  # 러시아어
    (r"[ก-๛]", "tha"),  # 태국어
    (r"[ا-ي]", "ara"),  # 아랍어
    (r"[А-я]", "mon"),  # 몽골어 (키릴 문자 변형)
    (r"[À-ſ]", "fre"),  # 프랑스어 (악센트 추정)
    (r"[A-Za-z]", "eng"),  # 영어 (default Latin)
]


@dataclass(frozen=True)
class LanguageDetection:
    """언어 감지 결과."""

    primary_language: str  # ISO 639-2 코드
    secondary_languages: list[str]
    confidence: float


def detect_language(text: str) -> LanguageDetection:
    """텍스트 → 주 언어·보조 언어 감지.

    KORMARC 008 35-37 + 041 다국어 지원.

    Args:
        text: 분석 대상 (제목·저자·요약 결합)

    Returns:
        LanguageDetection
    """
    if not text:
        return LanguageDetection(primary_language="kor", secondary_languages=[], confidence=0.0)

    # 각 언어별 매칭 카운트
    counts = {}
    for pattern, lang in SCRIPT_LANGUAGE_MAP:
        matches = re.findall(pattern, text)
        if matches:
            counts[lang] = counts.get(lang, 0) + len(matches)

    if not counts:
        return LanguageDetection(primary_language="kor", secondary_languages=[], confidence=0.0)

    # 정렬 (count 내림)
    sorted_langs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_langs[0][0]
    primary_count = sorted_langs[0][1]
    total = sum(counts.values())
    confidence = round(primary_count / total, 2) if total else 0

    secondary = [lang for lang, _ in sorted_langs[1:5]]  # 최대 4개

    return LanguageDetection(
        primary_language=primary,
        secondary_languages=secondary,
        confidence=confidence,
    )


def is_translation(book_data: dict) -> bool:
    """번역서 자동 감지 (간단 휴리스틱)."""
    if book_data.get("translator"):
        return True
    title = str(book_data.get("title", ""))
    if "원저" in title or "옮김" in title or "번역" in title:
        return True
    # 원어 정보 = 번역서
    return bool(book_data.get("original_language") and book_data.get("original_language") != "kor")


def build_041_field(book_data: dict) -> dict | None:
    """041 다국어 필드 자동 생성.

    번역서 = ▾a 본문 + ▾h 원어 (KORMARC 표준).
    """
    if not is_translation(book_data):
        return None

    body_lang = book_data.get("language", "kor")
    original_lang = book_data.get("original_language", "")

    subfields = [{"code": "a", "value": body_lang}]
    if original_lang:
        subfields.append({"code": "h", "value": original_lang})

    return {
        "tag": "041",
        "ind1": "1",  # 1 = 번역
        "ind2": " ",
        "subfields": subfields,
    }


__all__ = [
    "LANGUAGE_CODES",
    "LanguageDetection",
    "build_041_field",
    "detect_language",
    "is_translation",
]
