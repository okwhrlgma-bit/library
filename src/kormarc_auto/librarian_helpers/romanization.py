"""한글 → 로마자 표기 (글로벌 진출 자산).

근거: 국립중앙도서관 「서지데이터 로마자 표기 지침」(2021).
한국 표준 = 문체부 고시 「국어의 로마자 표기법」(2014-42).

미국·유럽 도서관 한국학 컬렉션은 ALA-LC (McCune-Reischauer) 사용.
한국 정부는 RR (Revised Romanization) 권장.
두 방식 모두 지원 — 도서관별 선택.

주요 차이:
  김치: RR='gimchi', ALA-LC='kimch''i'
  서울: RR='Seoul', ALA-LC='Sŏul'
  한강: RR='Han Gang', ALA-LC='Han Kang'

본 모듈은 단순화된 RR (Revised Romanization) 우선.
ALA-LC는 PDF 지침의 모든 규칙(약 200쪽) 적용 시 정확. PoC 수준.
"""

from __future__ import annotations

import re

# 자모 → RR 매핑 (단순화)
_INITIAL_RR = {
    "ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt",
    "ㄹ": "r", "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s",
    "ㅆ": "ss", "ㅇ": "", "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch",
    "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}

_VOWEL_RR = {
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae",
    "ㅓ": "eo", "ㅔ": "e", "ㅕ": "yeo", "ㅖ": "ye",
    "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe",
    "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we",
    "ㅟ": "wi", "ㅠ": "yu", "ㅡ": "eu", "ㅢ": "ui",
    "ㅣ": "i",
}

_FINAL_RR = {
    "": "", "ㄱ": "k", "ㄲ": "k", "ㄳ": "k", "ㄴ": "n", "ㄵ": "n",
    "ㄶ": "n", "ㄷ": "t", "ㄹ": "l", "ㄺ": "k", "ㄻ": "m",
    "ㄼ": "l", "ㄽ": "l", "ㄾ": "l", "ㄿ": "p", "ㅀ": "l",
    "ㅁ": "m", "ㅂ": "p", "ㅄ": "p", "ㅅ": "t", "ㅆ": "t",
    "ㅇ": "ng", "ㅈ": "t", "ㅊ": "t", "ㅋ": "k", "ㅌ": "t",
    "ㅍ": "p", "ㅎ": "t",
}

_INITIAL_LIST = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
_VOWEL_LIST = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
_FINAL_LIST = ["", *list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")]


def _decompose(syl: str) -> tuple[str, str, str] | None:
    """한글 음절 → (초성·중성·종성) 자모."""
    code = ord(syl) - 0xAC00
    if not 0 <= code < 11172:
        return None
    cho = code // 588
    jung = (code % 588) // 28
    jong = code % 28
    return _INITIAL_LIST[cho], _VOWEL_LIST[jung], _FINAL_LIST[jong]


def hangul_to_rr(text: str, *, capitalize_proper: bool = True) -> str:
    """한글 → RR (Revised Romanization, 정부 표준).

    Args:
        text: 한글 입력
        capitalize_proper: True면 단어 첫 자 대문자 (인명·고유명사)

    Returns:
        RR 로마자 문자열

    예:
        "한강" → "Han Gang"
        "서울특별시" → "Seoul Teukbyeolsi"
        "김영하" → "Kim Yeongha"
    """
    if not text:
        return ""

    out_parts: list[str] = []
    word_buf: list[str] = []

    def _flush() -> None:
        if not word_buf:
            return
        word = "".join(word_buf)
        if capitalize_proper and word:
            word = word[0].upper() + word[1:]
        out_parts.append(word)
        word_buf.clear()

    for ch in text:
        decomp = _decompose(ch)
        if decomp is None:
            _flush()
            if ch.strip() or out_parts:
                out_parts.append(ch)
            continue
        cho, jung, jong = decomp
        word_buf.append(_INITIAL_RR.get(cho, "") + _VOWEL_RR.get(jung, "") + _FINAL_RR.get(jong, ""))

    _flush()
    return " ".join(p for p in out_parts if p).strip()


def hangul_to_alalc(text: str) -> str:
    """한글 → ALA-LC (McCune-Reischauer 단순화). 학술도서관·해외 한국학 컬렉션용.

    완전한 ALA-LC는 NL Korea 「로마자 표기 지침」 32p 규칙 전체 적용 필요.
    본 함수는 PoC — 사서 검토 권장.
    """
    rr = hangul_to_rr(text, capitalize_proper=True)
    # 핵심 차이만 변환 (단순화)
    replacements = [
        ("eo", "ŏ"),
        ("eu", "ŭ"),
        ("ch ", "ch' "),
        ("k ", "k' "),
        ("p ", "p' "),
        ("t ", "t' "),
    ]
    out = rr
    for src, dst in replacements:
        out = out.replace(src, dst)
    return out


def add_880_romanized_pair(record_field_value: str, *, scheme: str = "rr") -> str:
    """KORMARC 880 페어용 로마자화. 기존 한자 880과 다른 ▾6 링크.

    scheme: "rr" 또는 "alalc"
    """
    if scheme == "alalc":
        return hangul_to_alalc(record_field_value)
    return hangul_to_rr(record_field_value)


def looks_korean(text: str) -> bool:
    """텍스트에 한글이 포함되어 있는지."""
    return bool(re.search(r"[가-힣]", text or ""))
