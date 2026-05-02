"""Part 82+ 추가 모듈 테스트 (SNS·비대면)."""
from __future__ import annotations

from datetime import date, datetime


def test_sns_marketing_helper_basic():
    from kormarc_auto.output.sns_marketing_helper import (
        generate_new_book_post,
        generate_curation_post,
        generate_event_post,
        generate_weekly_post_plan,
        to_instagram_format,
        to_blog_format,
        LIBRARY_HASHTAGS,
    )

    # 신간
    book = {"title": "어린왕자", "author": "생텍쥐페리", "kdc": "863.2", "description": "고전"}
    post = generate_new_book_post(book, "○○도서관")
    assert "어린왕자" in post.text
    assert "○○도서관" in post.text
    assert any(h in post.hashtags for h in LIBRARY_HASHTAGS)

    # 큐레이션
    cur = generate_curation_post("봄", [book], "○○도서관")
    assert "봄" in cur.text
    assert "어린왕자" in cur.text

    # 행사
    evt = generate_event_post(
        event_title="저자 강연",
        event_date=date(2026, 5, 15),
        location="1층 강당",
        library_name="○○도서관",
    )
    assert "저자 강연" in evt.text
    assert "5/15" in evt.text

    # 주간 계획
    plan = generate_weekly_post_plan(
        "○○도서관",
        new_books=[book],
        curation_theme="봄",
        upcoming_events=[
            {"title": "강연", "date": date(2026, 5, 20), "location": "강당"}
        ],
    )
    assert len(plan) == 3  # 신간·큐레이션·행사

    # Instagram·Blog 포맷
    insta = to_instagram_format(post)
    assert len(insta) <= 2200

    blog = to_blog_format(post)
    assert "태그" in blog


def test_nontact_service_helper_basic():
    from kormarc_auto.output.nontact_service_helper import (
        NontactRequest,
        SERVICE_DESCRIPTIONS,
        estimate_service_time,
        generate_user_notification,
    )

    # 6 서비스 모두 매뉴얼
    for st in ["drive_through", "postal", "online_event", "ebook_loan", "qr_pickup", "vr_ar"]:
        assert st in SERVICE_DESCRIPTIONS

    # 신청
    req = NontactRequest(
        service_type="drive_through",
        user_id="user001",
        book_ids=["9788937437076", "9791164060238"],
    )
    estimate = estimate_service_time(req)
    assert estimate["service_name"] == "북 드라이브스루"
    assert estimate["lead_time_days"] == 1

    notif = generate_user_notification(req, "○○도서관")
    assert "○○도서관" in notif
    assert "북 드라이브스루" in notif
