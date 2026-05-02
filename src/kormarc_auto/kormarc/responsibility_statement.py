"""책임표시 자동 분기 — Part 74 정합.

245 ▾c (책임표시) + 700 ▾e 역할 자동.
번역서·공동저자·편집자·감수자·옮긴이 = 자동 분기.

사서 페인 (Part 74·E1):
- 245 ▾c·700 = 번역자·공동저자 분기 수동
- 사서 = 책임표시 매번 결정 = 권당 2분

해결: 역할별 자동 분기 + 245 ▾c 포맷.
"""

from __future__ import annotations

from typing import Any

ROLE_KOREAN = {
    "author": "지음",
    "translator": "옮김",
    "editor": "엮음",
    "compiler": "엮음",
    "supervisor": "감수",
    "illustrator": "그림",
    "photographer": "사진",
    "narrator": "낭독",
    "reviewer": "감수",
    "co_author": "함께 지음",
}


def build_responsibility_statement(book_data: dict[str, Any]) -> str:
    """책임표시 자동 생성 (245 ▾c).

    Args:
        book_data:
            - author·authors: 메인 저자·공동저자
            - translator·editor·illustrator: 역할별
            - 또는 contributors: list[dict(name·role)]

    Returns:
        책임표시 문자열 (예: "홍길동 지음·김철수 옮김·이영희 그림")
    """
    parts = []

    # 메인 저자
    main = book_data.get("author")
    if main:
        co_authors = book_data.get("authors", [])
        if co_authors and len(co_authors) > 1:
            names = [main] + [
                a if isinstance(a, str) else a.get("name", "")
                for a in co_authors
                if (a if isinstance(a, str) else a.get("name", "")) != main
            ]
            parts.append(f"{', '.join(names[:3])} 지음")  # 최대 3명
        else:
            parts.append(f"{main} 지음")

    # 역할별 추가 (KORMARC 표준 순서)
    for role_en in ["translator", "editor", "illustrator", "photographer", "supervisor"]:
        person = book_data.get(role_en)
        if person:
            kr = ROLE_KOREAN.get(role_en, role_en)
            parts.append(f"{person} {kr}")

    # contributors (대안 형식)
    for c in book_data.get("contributors", []):
        if isinstance(c, dict):
            name = c.get("name")
            role = c.get("role")
            if name and role:
                kr = ROLE_KOREAN.get(role, role)
                if name not in [main]:
                    parts.append(f"{name} {kr}")

    return " ; ".join(parts)


def is_translation(book_data: dict[str, Any]) -> bool:
    """번역서 자동 감지."""
    return bool(book_data.get("translator")) or "원저" in str(book_data.get("title", ""))


__all__ = ["ROLE_KOREAN", "build_responsibility_statement", "is_translation"]
