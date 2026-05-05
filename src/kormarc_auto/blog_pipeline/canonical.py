"""갈래 B Cycle 16A (P36) — 블로그 frontmatter + canonical URL.

자체 블로그 = canonical 원본·네이버/브런치/Medium = 변형 + 출처 첨부.
2025 SEO Web Almanac canonical 67% 채택 표준.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BlogPost:
    """단일 진실 소스 (docs/research/*.md frontmatter 파싱)."""

    title: str
    slug: str
    body: str
    canonical_url: str = ""
    tags: list[str] = field(default_factory=list)
    date: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def short_summary(self, max_chars: int = 160) -> str:
        """OG description·150-160자 요약."""
        if self.description:
            return self.description[:max_chars]
        # 본문 첫 단락
        first_para = self.body.split("\n\n", 1)[0] if self.body else ""
        return first_para[:max_chars]


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def extract_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    """YAML frontmatter + 본문 분리.

    Returns:
        (frontmatter dict, 본문 markdown)
    """
    m = _FRONTMATTER_RE.match(markdown)
    if not m:
        return {}, markdown

    fm_text, body = m.group(1), m.group(2)
    fm: dict[str, Any] = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # tags = ["a", "b"] 처리
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            fm[key] = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
        else:
            fm[key] = value
    return fm, body


def add_canonical_footer(body: str, *, canonical_url: str) -> str:
    """채널별 본문 끝에 '원문 출처' 자동 첨부 (네이버/브런치 cross-post)."""
    footer = f"\n\n---\n\n원문 출처: [{canonical_url}]({canonical_url})\n"
    return body.rstrip() + footer


def build_canonical_html(post: BlogPost) -> str:
    """자체 블로그 HTML head + canonical 자동 삽입.

    KOLAS III 종료일 등 인용 수치 = body에서 사실확인 게이트 통과 후 호출.
    """
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{post.title}</title>
<meta name="description" content="{post.short_summary()}">
<link rel="canonical" href="{post.canonical_url}">
<meta property="og:title" content="{post.title}">
<meta property="og:description" content="{post.short_summary()}">
<meta property="og:url" content="{post.canonical_url}">
<meta property="og:locale" content="ko_KR">
<meta property="og:type" content="article">
</head>
<body>
<article>
<h1>{post.title}</h1>
{post.body}
</article>
</body>
</html>
"""
