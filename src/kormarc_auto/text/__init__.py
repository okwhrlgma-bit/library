"""kormarc_auto.text — OPAC 검색 정규화·텍스트 처리 (Cycle 498~499·founder fit ★★★)."""

from kormarc_auto.text.homoglyph_normalize import (
    normalize_for_search,
    detect_homoglyph_attack,
    contains_zero_width,
    audit_kormarc_record_homoglyph,
    normalize_kormarc_field,
    build_homoglyph_sanity_report_kr,
)

__all__ = [
    "normalize_for_search",
    "detect_homoglyph_attack",
    "contains_zero_width",
    "audit_kormarc_record_homoglyph",
    "normalize_kormarc_field",
    "build_homoglyph_sanity_report_kr",
]
