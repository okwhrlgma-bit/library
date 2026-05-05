"""갈래 B Cycle 15B (P35) — OG 태그 + robots.txt + 사서 키워드.

네이버 60-70% 점유 = OG 우선·구글 = JSON-LD 우선·이중 운영.
외부 매출 보고서 §5 정합.
"""

from __future__ import annotations


def librarian_top_10_keywords() -> list[dict[str, str | int]]:
    """사서 Top 10 키워드 + 추정 월 검색량 (외부 매출 보고서 §5)."""
    return [
        {
            "keyword": "KORMARC 자동 생성",
            "monthly_search_low": 50,
            "monthly_search_high": 100,
            "competition": "very_low",
            "priority": "★★★ 즉시 공략",
        },
        {
            "keyword": "도서관 마크 만들기",
            "monthly_search_low": 100,
            "monthly_search_high": 300,
            "competition": "low",
            "priority": "★★★",
        },
        {
            "keyword": "마크 작성 프로그램",
            "monthly_search_low": 100,
            "monthly_search_high": 200,
            "competition": "low",
            "priority": "★★★",
        },
        {
            "keyword": "ISBN 마크 변환",
            "monthly_search_low": 50,
            "monthly_search_high": 150,
            "competition": "low",
            "priority": "★★",
        },
        {
            "keyword": "독서로 DLS 마크 반입",
            "monthly_search_low": 30,
            "monthly_search_high": 100,
            "competition": "very_low",
            "priority": "★★★",
        },
        {
            "keyword": "DLS MARC 일괄 등록",
            "monthly_search_low": 20,
            "monthly_search_high": 60,
            "competition": "very_low",
            "priority": "★★",
        },
        {
            "keyword": "KOLAS 마크 자동입력",
            "monthly_search_low": 20,
            "monthly_search_high": 50,
            "competition": "very_low",
            "priority": "★★",
        },
        {
            "keyword": "KOLAS III 종료",
            "monthly_search_low": 50,
            "monthly_search_high": 200,
            "competition": "low",
            "priority": "★★★ 2026 급증 예상",
        },
        {
            "keyword": "KOLAS III 마이그레이션",
            "monthly_search_low": 10,
            "monthly_search_high": 50,
            "competition": "very_low",
            "priority": "★★★ 1위 점령 가능",
        },
        {
            "keyword": "사서 마크 자동화",
            "monthly_search_low": 20,
            "monthly_search_high": 60,
            "competition": "very_low",
            "priority": "★★",
        },
    ]


def naver_search_keywords_density(text: str) -> dict[str, int]:
    """텍스트 내 사서 Top 10 키워드 등장 횟수 (홈페이지 적정 빈도 검증)."""
    counts: dict[str, int] = {}
    for kw_obj in librarian_top_10_keywords():
        kw = str(kw_obj["keyword"])
        counts[kw] = text.count(kw)
    return counts


def build_og_tags(
    *,
    title: str,
    description: str,
    url: str,
    image_url: str = "",
    site_name: str = "kormarc-auto",
) -> str:
    """네이버 우선 OG 태그 (locale=ko_KR 필수)."""
    parts = [
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:url" content="{url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="ko_KR">',
        f'<meta property="og:site_name" content="{site_name}">',
    ]
    if image_url:
        parts.append(f'<meta property="og:image" content="{image_url}">')
    # canonical (외부 보고서 P35 게이트)
    parts.append(f'<link rel="canonical" href="{url}">')
    return "\n".join(parts)


def build_robots_txt(*, allow_ai_bots: bool = True) -> str:
    """robots.txt = Yeti(네이버) + GPTBot/ClaudeBot/PerplexityBot Allow.

    외부 보고서 P35 게이트:
    - AI 봇 차단 시 STOP·LLM GEO 효과 0
    """
    lines = [
        "# robots.txt — kormarc-auto",
        "# 네이버 + AI 봇 모두 허용 (외부 매출 보고서 P35·P40 정합)",
        "",
        "User-agent: *",
        "Allow: /",
        "",
        "# 네이버",
        "User-agent: Yeti",
        "Allow: /",
        "",
    ]
    if allow_ai_bots:
        lines += [
            "# AI 봇 (GEO·LLM 인용)",
            "User-agent: GPTBot",
            "Allow: /",
            "",
            "User-agent: ClaudeBot",
            "Allow: /",
            "",
            "User-agent: PerplexityBot",
            "Allow: /",
            "",
            "User-agent: Google-Extended",
            "Allow: /",
            "",
        ]
    lines.append("Sitemap: https://kormarc-auto.example/sitemap.xml")
    return "\n".join(lines)
