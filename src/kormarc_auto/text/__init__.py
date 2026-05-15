"""kormarc_auto.text — OPAC 검색 정규화·텍스트 처리 (Cycle 498~499·founder fit ★★★)."""

from kormarc_auto.text.homoglyph_normalize import (
    audit_kormarc_record_homoglyph,
    build_homoglyph_sanity_report_kr,
    contains_zero_width,
    detect_homoglyph_attack,
    normalize_for_search,
    normalize_kormarc_field,
)

__all__ = [
    "audit_kormarc_record_homoglyph",
    "build_homoglyph_sanity_report_kr",
    "contains_zero_width",
    "detect_homoglyph_attack",
    "normalize_for_search",
    "normalize_kormarc_field",
]
