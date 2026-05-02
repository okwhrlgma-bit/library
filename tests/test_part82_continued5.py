"""Part 82+ 추가 모듈 테스트 (협력·역량)."""
from __future__ import annotations


def test_consortium_helper_basic():
    from kormarc_auto.interlibrary.consortium_helper import (
        recommend_consortium_join,
        get_consortium_info,
        CONSORTIUM_DATABASE,
    )

    # 6 컨소시엄 모두 등록
    assert len(CONSORTIUM_DATABASE) == 6
    assert "chaek_ieum" in CONSORTIUM_DATABASE

    # 공공도서관 = 책이음 + 책두레 + KOLISNET 권장
    recs = recommend_consortium_join(library_type="public", has_kolas=True)
    types = [r.type for r in recs]
    assert "chaek_ieum" in types
    assert "kolisnet" in types

    # 대학 = academic 권장
    recs_acad = recommend_consortium_join(library_type="academic", has_kolas=False)
    assert any(r.type == "academic" for r in recs_acad)

    # 정보 조회
    info = get_consortium_info("chaek_ieum")
    assert info.member_count > 0
    assert "NLK" in info.operator


def test_librarian_competency_tracker_basic():
    from kormarc_auto.ui.librarian_competency_tracker import (
        COMPETENCY_AREAS,
        CompetencyScore,
        calculate_overall_competency,
        kormarc_auto_boost,
        generate_competency_report,
    )

    # 10 영역
    assert len(COMPETENCY_AREAS) == 10

    # 점수 계산
    scores = [
        CompetencyScore(area="cataloging", self_score=4.5, actual_score=4.8, importance=5.0),
        CompetencyScore(area="classification", self_score=4.0, actual_score=4.2, importance=4.0),
        CompetencyScore(area="marketing", self_score=2.0, actual_score=2.5, importance=3.0),
    ]
    summary = calculate_overall_competency(scores)
    assert summary["overall"] > 0
    assert "cataloging" in summary["strengths"]
    assert "marketing" in summary["weaknesses"]

    # boost
    assert kormarc_auto_boost("cataloging") == 2.0
    assert kormarc_auto_boost("administration") == 2.0
    assert kormarc_auto_boost("unknown") == 0.5

    # 보고서
    report = generate_competency_report(scores, "홍길동")
    assert "홍길동" in report
    assert "종합 역량" in report
    assert "강점 영역" in report
    assert "사서 평가 가산점" in report
