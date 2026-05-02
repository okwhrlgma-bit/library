"""Part 82+ 추가 모듈 테스트 (개인화 추천·재난 대응)."""
from __future__ import annotations


def test_personalized_recommender_basic():
    from kormarc_auto.acquisition.personalized_recommender import (
        analyze_user_preference,
        collaborative_filter,
        recommend_for_user,
    )

    # 대출 이력 분석
    history = [
        {"isbn": "1", "kdc": "863.2"},  # 800 문학
        {"isbn": "2", "kdc": "813.6"},  # 800
        {"isbn": "3", "kdc": "004.7"},  # 000
    ]
    pref = analyze_user_preference(history)
    assert "800" in pref["favorite_kdc"]
    assert pref["total_loans"] == 3

    # 추천
    candidates = [
        {"isbn": "10", "title": "신간문학", "kdc": "813.7", "rating": 4.5},
        {"isbn": "11", "title": "AI", "kdc": "004.7", "rating": 4.8},
        {"isbn": "12", "title": "역사", "kdc": "910.1", "rating": 3.5},
    ]
    pref_ext = {
        "favorite_kdc": ["800", "000"],
        "loan_history": history,
        "diversity_score": 0.6,
    }
    recs = recommend_for_user(candidates, pref_ext, max_recommendations=3)
    assert len(recs) == 3
    # 800·000 = 선호 = 점수 ↑
    top_kdcs = [r.book["kdc"][0] + "00" for r in recs[:2]]
    assert any(k in ["800", "000"] for k in top_kdcs)

    # 협업 필터링
    target = ["isbn1", "isbn2"]
    similar = {
        "user_a": ["isbn1", "isbn2", "isbn3", "isbn4"],
        "user_b": ["isbn1", "isbn2", "isbn5"],
        "user_c": ["isbn999"],  # 공통 X
    }
    cf_recs = collaborative_filter(target, similar_users_history=similar, max_recommendations=3)
    assert "isbn3" in cf_recs or "isbn4" in cf_recs or "isbn5" in cf_recs
    assert "isbn999" not in cf_recs  # 공통 X = 추천 X


def test_disaster_response_basic():
    from kormarc_auto.safety.disaster_response import (
        RESPONSE_PROTOCOL,
        DisasterChecklist,
        get_protocol,
        render_response_card,
    )

    # 6 재난 유형 모두 매뉴얼
    for dt in ["earthquake", "flood", "fire", "power_outage", "pandemic", "typhoon"]:
        assert dt in RESPONSE_PROTOCOL
        protocol = get_protocol(dt)
        assert isinstance(protocol, DisasterChecklist)
        assert len(protocol.immediate_actions) > 0
        assert "112" in protocol.emergency_contacts

    # 화재 매뉴얼 = 119 즉시
    fire = get_protocol("fire")
    assert any("119" in a for a in fire.immediate_actions)

    # 침수 = 위층 이동
    flood = get_protocol("flood")
    assert any("위층" in a or "이동" in a for a in flood.immediate_actions)

    # 카드 렌더링
    card = render_response_card("earthquake")
    assert "EARTHQUAKE" in card
    assert "즉시 조치" in card
    assert "사후 조치" in card
    assert "112" in card
