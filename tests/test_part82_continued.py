"""Part 82+ 추가 모듈 테스트 (OPAC 검색·장서 균형)."""
from __future__ import annotations


def test_opac_search_enhancer_basic():
    from kormarc_auto.classification.opac_search_enhancer import (
        expand_query,
        suggest_alternative_search,
        SYNONYM_MAP,
    )

    # 동의어 확장
    result = expand_query("AI")
    assert "AI" in result.expanded_keywords
    assert "인공지능" in result.expanded_keywords

    # 짧은 검색 = 팁
    result_short = expand_query("a")
    assert any("짧" in t for t in result_short.search_tips)

    # 숫자만 = 팁
    result_num = expand_query("12345")
    assert any("ISBN" in t for t in result_num.search_tips)

    # 대안 검색
    alts = suggest_alternative_search("인공지능")
    assert len(alts) > 0
    assert any("AI" in a or "기계학습" in a for a in alts)


def test_collection_balance_analyzer_basic():
    from kormarc_auto.acquisition.collection_balance_analyzer import (
        analyze_collection,
        generate_balance_summary,
        KDC_MAJOR_CLASSES,
    )

    # 불균형 자관 (문학 80%·총류 5%·나머지 X)
    books = (
        [{"kdc": "813.6"} for _ in range(80)]  # 800 문학
        + [{"kdc": "004.7"} for _ in range(5)]  # 000 총류
        + [{"kdc": "100.5"} for _ in range(15)]  # 100 철학
    )

    report = analyze_collection(books)
    assert report.total_books == 100
    assert report.distribution.get("800", 0) == 80
    assert report.distribution_pct.get("800", 0) == 80.0

    # 800 = 과다 (≥25%)
    assert "800" in report.overrepresented

    # 200·300·400·500·600·700·900 = 5% 미만 = 부족
    for code in ["200", "300", "400", "500", "600", "700", "900"]:
        assert code in report.underrepresented

    # 권장 구매
    assert len(report.recommended_purchases) > 0

    # markdown 보고서
    summary = generate_balance_summary(report)
    assert "총 100권" in summary
    assert "800" in summary
    assert "부족" in summary or "과다" in summary

    # KDC_MAJOR_CLASSES 확인
    assert "000" in KDC_MAJOR_CLASSES
    assert "900" in KDC_MAJOR_CLASSES
