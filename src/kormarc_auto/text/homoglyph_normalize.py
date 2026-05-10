"""유사 글자 (homoglyph) 정규화 — OPAC 검색 robust + 사서 결합 사칭 탐지.

Cycle 498·#15 opac_homoglyph_norm·founder fit ★★★·PO 명령 (Cycle 497·AI 고블린 V01).

핵심 영역:
- OPAC 검색 robust = 키릴·그리스 시각 동음이의 글자를 라틴으로 매핑 후 검색
- KORMARC 데이터 무결성 = zero-width 글자 (U+200B 등) 자동 탐지·제거
- NFKC 정규화 = NLK 권장·KS X 6006 정합

NLK 「서지데이터 로마자 표기 지침(2021)」 정합·CLAUDE.md §15 (자가 설치 친화).
헌법 §14 정합 (자관 데이터 X·표준 unicodedata만 사용).
"""

import unicodedata

_HOMOGLYPH_LATIN_MAP = {
    "а": "a", "А": "A", "е": "e", "Е": "E", "о": "o", "О": "O",
    "р": "p", "Р": "P", "с": "c", "С": "C", "у": "y", "У": "Y",
    "х": "x", "Х": "X", "і": "i", "І": "I", "ј": "j", "Ј": "J",
    "ѕ": "s", "Ѕ": "S",
    "α": "a", "Α": "A", "β": "B", "ε": "e", "Ε": "E", "ι": "i",
    "Ι": "I", "ο": "o", "Ο": "O", "ρ": "p", "Ρ": "P", "ν": "v",
    "Ν": "N", "τ": "t", "Τ": "T", "υ": "u", "Υ": "Y", "χ": "X",
    "Χ": "X", "κ": "k", "Κ": "K", "η": "n", "Η": "H",
}

_ZERO_WIDTH_CHARS = (
    "​",
    "‌",
    "‍",
    "⁠",
    "﻿",
    "­",
)


def contains_zero_width(text: str) -> bool:
    """zero-width 글자 존재 여부 (KORMARC 무결성 검증)."""
    if not text:
        return False
    return any(zw in text for zw in _ZERO_WIDTH_CHARS)


def _strip_zero_width(text: str) -> str:
    for zw in _ZERO_WIDTH_CHARS:
        text = text.replace(zw, "")
    return text


def normalize_for_search(text: str) -> str:
    """OPAC 검색용 정규화 — NFKC + zero-width 제거 + homoglyph 라틴 매핑.

    예) 'Кoreа' (키릴 К·라틴 o·라틴 r·라틴 e·키릴 а) → 'Korea'
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = _strip_zero_width(text)
    return "".join(_HOMOGLYPH_LATIN_MAP.get(c, c) for c in text)


def detect_homoglyph_attack(text: str) -> dict:
    """homoglyph 공격 탐지 — 사서 결합·이용자 검색·악성 KORMARC 입력 검증.

    반환 = {
        "has_homoglyph": bool,
        "has_zero_width": bool,
        "suspicious_chars": [(원문 글자, 라틴 매핑), ...],
        "risk_level": "none" | "low" | "high",
    }
    """
    if not text:
        return {
            "has_homoglyph": False,
            "has_zero_width": False,
            "suspicious_chars": [],
            "risk_level": "none",
        }
    suspicious: list[tuple[str, str]] = [
        (c, _HOMOGLYPH_LATIN_MAP[c]) for c in text if c in _HOMOGLYPH_LATIN_MAP
    ]
    has_zw = contains_zero_width(text)
    has_homoglyph = bool(suspicious)
    if not has_homoglyph and not has_zw:
        risk = "none"
    elif has_zw or len(suspicious) >= 3:
        risk = "high"
    else:
        risk = "low"
    return {
        "has_homoglyph": has_homoglyph,
        "has_zero_width": has_zw,
        "suspicious_chars": suspicious,
        "risk_level": risk,
    }


_KORMARC_TEXT_FIELDS = ("245", "100", "110", "111", "246", "440", "490", "700", "710", "711")


def build_homoglyph_sanity_report_kr(record: dict) -> str:
    """KORMARC record 사칭 감사 한국어 리포트 (Cycle 517·sanity-check CLI 통합 시드).

    사서 친화 한국어 출력·CLI·Streamlit·로그 모두 호환.
    """
    if not record:
        return "✅ KORMARC 사칭 감사: 빈 record (검증 항목 X)"
    audit = audit_kormarc_record_homoglyph(record)
    summary = audit["summary"]
    if summary == "all_clean":
        return "✅ KORMARC 사칭 감사: 모든 필드 정상 (homoglyph·zero-width 미감지)"
    high = audit["high_risk_fields"]
    low = audit["low_risk_fields"]
    lines = []
    if summary == "blocked":
        lines.append("🔴 KORMARC 사칭 감사: 차단 권장")
    else:
        lines.append("🟡 KORMARC 사칭 감사: 검토 필요")
    if high:
        lines.append(f"  - 고위험 필드 ({len(high)}건): {', '.join(high)}")
    if low:
        lines.append(f"  - 저위험 필드 ({len(low)}건): {', '.join(low)}")
    lines.append("  - 권장: normalize_kormarc_field() 또는 normalize_for_search() 호출")
    return "\n".join(lines)


def normalize_kormarc_field(field: str, text: str) -> dict:
    """KORMARC 단일 필드 정규화 + audit (Cycle 507·sanity-check CLI 통합 시드).

    반환 = {
        "field": str,
        "original": str,
        "normalized": str,
        "audit": dict (detect_homoglyph_attack 결과),
        "is_text_field": bool,
        "should_warn": bool (high·low 위험 감지 시 True),
    }
    """
    if field not in _KORMARC_TEXT_FIELDS:
        return {
            "field": field,
            "original": text,
            "normalized": text,
            "audit": {"risk_level": "none", "has_homoglyph": False, "has_zero_width": False, "suspicious_chars": []},
            "is_text_field": False,
            "should_warn": False,
        }
    audit = detect_homoglyph_attack(text)
    normalized = normalize_for_search(text)
    return {
        "field": field,
        "original": text,
        "normalized": normalized,
        "audit": audit,
        "is_text_field": True,
        "should_warn": audit["risk_level"] in ("low", "high"),
    }


def audit_kormarc_record_homoglyph(record: dict) -> dict:
    """KORMARC record (필드 → 텍스트 dict)의 homoglyph·zero-width 사칭 감사.

    record 예: {"245": "홍​길동전", "100": "Kорея 작가"}
    반환 = {
        "high_risk_fields": [필드, ...],
        "low_risk_fields": [필드, ...],
        "summary": "all_clean" | "warning" | "blocked",
    }
    헌법 §14 정합 (KORMARC 무결성·자관 데이터 X·표준만 사용).
    """
    if not record:
        return {"high_risk_fields": [], "low_risk_fields": [], "summary": "all_clean"}
    high: list[str] = []
    low: list[str] = []
    for field, text in record.items():
        if field not in _KORMARC_TEXT_FIELDS or not isinstance(text, str):
            continue
        result = detect_homoglyph_attack(text)
        if result["risk_level"] == "high":
            high.append(field)
        elif result["risk_level"] == "low":
            low.append(field)
    if high:
        summary = "blocked"
    elif low:
        summary = "warning"
    else:
        summary = "all_clean"
    return {
        "high_risk_fields": high,
        "low_risk_fields": low,
        "summary": summary,
    }
