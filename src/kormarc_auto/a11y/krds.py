"""갈래 A Cycle 15A (P20) — KRDS 디자인 토큰 + Pretendard CDN.

행안부 KRDS 정합 색상 + Pretendard 한글 폰트 (사서 PC 친화).
외부 매출 보고서 §5.6 정합.
"""

from __future__ import annotations

# Pretendard CDN (jsdelivr·orioncactus·v1.3.9 안정 버전)
PRETENDARD_CDN_URL = (
    "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"
)

# KRDS 색상 토큰 (Korea blue·amber·green·red·grayscale)
KRDS_COLOR_TOKENS = {
    # Primary
    "korea_blue_60": "#0F4C9F",  # 주 색·CTA 버튼·링크
    "korea_blue_50": "#1B6AC9",  # 호버
    "korea_blue_40": "#3B89E8",  # 보조
    # Semantic
    "amber_50": "#D97706",  # 검토 필요·warning
    "green_50": "#15803D",  # 확실·성공
    "red_50": "#DC2626",  # 불확실·오류
    # Neutral
    "gray_90": "#1F2937",  # 본문 텍스트 (4.5:1 대비 보장 vs gray_5)
    "gray_70": "#4B5563",  # 보조 텍스트
    "gray_50": "#9CA3AF",  # 비활성·ghost text
    "gray_30": "#D1D5DB",  # 구분선
    "gray_10": "#F3F4F6",  # 배경
    "gray_5": "#FAFAFA",  # 배경 더 밝음
    "white": "#FFFFFF",
}


KRDS_TYPOGRAPHY = {
    "font_family": "Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif",
    "size_h1": "2.0rem",
    "size_h2": "1.5rem",
    "size_h3": "1.25rem",
    "size_body": "1.0rem",
    "size_caption": "0.875rem",
    "line_height_body": 1.6,
    "line_height_heading": 1.3,
    "weight_normal": 400,
    "weight_medium": 500,
    "weight_bold": 700,
}


def pretendard_link_tag() -> str:
    """HTML <head>에 삽입할 Pretendard CDN link 태그."""
    return f'<link rel="stylesheet" href="{PRETENDARD_CDN_URL}">'


def color_meaning_matrix() -> dict[str, dict[str, str]]:
    """색상 의미 매트릭스 (KWCAG 1.4.1 색상 의존 회피·아이콘 + 텍스트 동시).

    {"확실": {"color": "...", "icon": "✓", "korean": "확실"}}
    """
    return {
        "확실": {
            "color": KRDS_COLOR_TOKENS["green_50"],
            "icon": "✓",
            "korean": "확실",
            "english": "high",
        },
        "검토 필요": {
            "color": KRDS_COLOR_TOKENS["amber_50"],
            "icon": "ⓘ",
            "korean": "검토 필요",
            "english": "review",
        },
        "불확실": {
            "color": KRDS_COLOR_TOKENS["red_50"],
            "icon": "⚠",
            "korean": "불확실",
            "english": "uncertain",
        },
    }
