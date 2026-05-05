"""갈래 A Cycle 15A (P20·v0.7.0 종착) — KWCAG 2.2 + KRDS + Pretendard.

디지털포용법 §21 + 시행령 §20 정합·도서관 RFP 접근성 인증마크 요구 사전 대응.
"""

from kormarc_auto.a11y.krds import (
    KRDS_COLOR_TOKENS,
    KRDS_TYPOGRAPHY,
    PRETENDARD_CDN_URL,
    color_meaning_matrix,
    pretendard_link_tag,
)
from kormarc_auto.a11y.kwcag22 import (
    KWCAG_PRINCIPLES,
    A11yIssue,
    A11yReport,
    audit_html,
    audit_kwcag22_text_content,
    color_contrast_ratio,
    is_korean_lang_attr_present,
)

__all__ = [
    "KRDS_COLOR_TOKENS",
    "KRDS_TYPOGRAPHY",
    "KWCAG_PRINCIPLES",
    "PRETENDARD_CDN_URL",
    "A11yIssue",
    "A11yReport",
    "audit_html",
    "audit_kwcag22_text_content",
    "color_contrast_ratio",
    "color_meaning_matrix",
    "is_korean_lang_attr_present",
    "pretendard_link_tag",
]
