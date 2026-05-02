"""Part 80 최종 모듈 4 신규 테스트."""
from __future__ import annotations

from datetime import date


def test_decision_helper_basic():
    from kormarc_auto.acquisition.decision_helper import (
        recommend_books,
        evaluate_neutrality,
        calculate_decision_score,
    )

    candidates = [
        {
            "isbn": "9788937437076",
            "title": "어린왕자",
            "author": "생텍쥐페리",
            "publisher": "열린책들",
            "price_won": 12000,
            "kdc": "863.2",
            "rating": 4.7,
            "user_requests": 10,
            "publisher_reputation": 0.9,
        },
        {
            "isbn": "9999999999999",
            "title": "보수 정당 음모론",
            "author": "X",
            "publisher": "Y",
            "price_won": 15000,
            "kdc": "340",
            "rating": 3.0,
        },
    ]
    recs = recommend_books(candidates, budget_remaining_won=2_000_000)
    assert len(recs) == 2
    # 어린왕자 = 1위 (높은 평점·중립)
    assert recs[0].title == "어린왕자"
    assert recs[0].decision_score > recs[1].decision_score
    assert recs[0].flag == "neutral"

    # 중립성
    assert evaluate_neutrality({"title": "어린왕자"}) == "neutral"
    assert evaluate_neutrality({"title": "보수 좌파 비판"}) == "political"

    # 점수
    high = calculate_decision_score(rating=4.5, user_requests=10, is_neutral=True)
    low = calculate_decision_score(rating=2.0, user_requests=0, is_neutral=False)
    assert high > low


def test_withdrawn_processor_basic():
    from kormarc_auto.kormarc.withdrawn_processor import (
        add_withdrawal_fields,
        is_withdrawn,
    )

    fields = add_withdrawal_fields(
        record_data={},
        reason="lost",
        withdrawn_date=date(2026, 5, 2),
    )
    assert any(f.tag == "583" for f in fields)

    # is_withdrawn 검증
    record_data = {
        "data_fields": [
            {
                "tag": "583",
                "subfields": [{"code": "a", "value": "withdrawn"}],
            }
        ]
    }
    assert is_withdrawn(record_data) is True
    assert is_withdrawn({"data_fields": []}) is False


def test_event_poster_template_basic():
    from kormarc_auto.output.event_poster_template import (
        render_event_poster,
        THEME_COLORS,
        EventType,
    )

    poster = render_event_poster(
        title="도서관 주간 행사",
        event_type="library_week",
        library_name="○○도서관",
        event_date=date(2026, 4, 12),
        location="1층 강당",
        description="도서관 주간 = 책과 함께하는 일주일",
        contact="02-1234-5678",
    )
    assert "도서관 주간 행사" in poster
    assert "○○도서관" in poster
    assert "1층 강당" in poster
    assert "2026년 4월 12일" in poster
    assert THEME_COLORS["library_week"] in poster

    # 7 EventType 모두 색 정의
    for et in ["library_week", "library_day", "bookstart", "author_talk", "reading_club", "exhibition", "kid_event", "general"]:
        assert et in THEME_COLORS


def test_abuse_response_manual_basic():
    from kormarc_auto.safety.abuse_response_manual import (
        get_response,
        determine_escalation_level,
        RESPONSE_TEMPLATES,
        ResponseLevel,
    )

    # 4 사고 유형 모두 매뉴얼
    for itype in ["verbal_abuse", "sexual_harassment", "complaint", "physical_threat"]:
        assert itype in RESPONSE_TEMPLATES
        for lvl in ["calm", "warning", "escalate", "incident"]:
            resp = get_response(incident_type=itype, level=lvl)
            assert len(resp) > 10

    # Escalation
    assert determine_escalation_level(repeat_count=1, severity=1, abuse_type="verbal_abuse") == "calm"
    assert determine_escalation_level(repeat_count=2, severity=3, abuse_type="verbal_abuse") == "warning"
    assert determine_escalation_level(repeat_count=3, severity=4, abuse_type="verbal_abuse") == "escalate"

    # 성희롱·물리적 = 즉시 incident
    assert determine_escalation_level(abuse_type="sexual_harassment") == "incident"
    assert determine_escalation_level(abuse_type="physical_threat") == "incident"

    # 심각도 5 = incident
    assert determine_escalation_level(severity=5, abuse_type="verbal_abuse") == "incident"
