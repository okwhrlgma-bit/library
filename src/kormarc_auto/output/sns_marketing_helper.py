"""도서관 SNS 마케팅 자동 — Part 82+ 페인 #45 정합.

사서 페인:
- 마케팅 전담 X
- 사서 = SNS 운영 부담
- 주 3건 미만 평균 = 활성화 X

해결: 자동 게시물 생성 (신간·큐레이션·행사·통계·인용).
인스타그램·페이스북·블로그·X 호환.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

PostType = Literal[
    "new_book",  # 신간 안내
    "curation",  # 큐레이션
    "event",  # 행사
    "stats",  # 통계·이용자
    "quote",  # 인용·명언
    "tip",  # 사서 팁
    "behind_scenes",  # 비하인드
]


@dataclass(frozen=True)
class SocialPost:
    """SNS 게시물."""

    post_type: PostType
    text: str
    hashtags: list[str]
    cta: str = ""
    image_suggestion: str = ""


# 도서관 표준 해시태그
LIBRARY_HASHTAGS = [
    "#도서관",
    "#book",
    "#독서",
    "#사서추천",
    "#독서스타그램",
    "#책추천",
    "#오늘의책",
]


def generate_new_book_post(book: dict, library_name: str) -> SocialPost:
    """신간 안내 게시물 자동."""
    title = book.get("title", "")
    author = book.get("author", "")
    kdc = book.get("kdc", "")
    description = book.get("description", "")[:150]

    text = (
        f"📚 신간 도착!\n\n"
        f"『{title}』 — {author}\n"
        f"분류: KDC {kdc}\n\n"
        f"{description}\n\n"
        f"{library_name}에서 만나보세요."
    )
    hashtags = [*LIBRARY_HASHTAGS, f"#{title}", f"#{author}", "#신간도서"]
    return SocialPost(
        post_type="new_book",
        text=text,
        hashtags=hashtags,
        cta="대출 신청 하러 가기 ➡",
    )


def generate_curation_post(theme: str, books: list[dict], library_name: str) -> SocialPost:
    """큐레이션 게시물 자동 (book_curation_engine 결과 호환)."""
    book_list = "\n".join(
        f"{i + 1}. {b.get('title', '')} — {b.get('author', '')}" for i, b in enumerate(books[:5])
    )
    text = (
        f"🌟 {theme} 추천 도서 {len(books)}선\n\n"
        f"{book_list}\n\n"
        f"사서가 직접 골랐어요. {library_name}에서 만나요."
    )
    hashtags = [*LIBRARY_HASHTAGS, f"#{theme}", "#큐레이션", "#사서추천"]
    return SocialPost(
        post_type="curation",
        text=text,
        hashtags=hashtags,
        cta="전체 추천 보기 ➡",
    )


def generate_event_post(
    *,
    event_title: str,
    event_date: date,
    location: str,
    library_name: str,
) -> SocialPost:
    """행사 안내 게시물 자동."""
    weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
    date_str = f"{event_date.month}/{event_date.day} ({weekdays_kr[event_date.weekday()]})"
    text = (
        f"📅 행사 안내\n\n"
        f"🎉 {event_title}\n"
        f"📍 {location}\n"
        f"⏰ {date_str}\n\n"
        f"{library_name}에서 함께해요."
    )
    hashtags = [*LIBRARY_HASHTAGS, f"#{event_title}", "#도서관행사", "#무료참여"]
    return SocialPost(
        post_type="event",
        text=text,
        hashtags=hashtags,
        cta="신청 ➡",
        image_suggestion="poster_url",
    )


def generate_weekly_post_plan(
    library_name: str,
    *,
    new_books: list[dict] | None = None,
    curation_theme: str = "",
    upcoming_events: list | None = None,
) -> list[SocialPost]:
    """주간 게시물 계획 자동 (주 3건 + α).

    사서 SNS 마케팅 부담 ↓ = 자동 생성.
    """
    posts = []

    # 월: 신간 1건
    if new_books:
        posts.append(generate_new_book_post(new_books[0], library_name))

    # 수: 큐레이션
    if curation_theme:
        posts.append(generate_curation_post(curation_theme, new_books or [], library_name))

    # 금: 행사 또는 사서 팁
    if upcoming_events:
        evt = upcoming_events[0]
        posts.append(
            generate_event_post(
                event_title=evt.get("title", ""),
                event_date=evt.get("date", date.today()),
                location=evt.get("location", ""),
                library_name=library_name,
            )
        )

    return posts


def to_instagram_format(post: SocialPost, max_length: int = 2200) -> str:
    """인스타그램 형식 (캡션 2,200자 한도·해시태그 30개)."""
    body = post.text
    if post.cta:
        body += f"\n\n{post.cta}"

    hashtag_str = " ".join(post.hashtags[:30])  # 인스타그램 한도 30
    full = f"{body}\n\n{hashtag_str}"
    return full[:max_length]


def to_blog_format(post: SocialPost) -> str:
    """블로그·티스토리·네이버 블로그 형식 (긴 텍스트)."""
    return f"{post.text}\n\n{post.cta}\n\n태그: {', '.join(post.hashtags)}"


__all__ = [
    "LIBRARY_HASHTAGS",
    "PostType",
    "SocialPost",
    "generate_curation_post",
    "generate_event_post",
    "generate_new_book_post",
    "generate_weekly_post_plan",
    "to_blog_format",
    "to_instagram_format",
]
