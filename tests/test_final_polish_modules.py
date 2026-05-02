"""최종 보완 모듈 테스트 (DLS·PMF·도서관 위계)."""

from __future__ import annotations


def test_dls_exporter_basic():
    from kormarc_auto.output.dls_exporter import (
        DlsRecord,
        export_to_dls_csv,
        generate_dls_import_guide,
        kormarc_to_dls,
    )

    rec = DlsRecord(
        isbn="9788937437076",
        title="어린왕자",
        author="생텍쥐페리",
        publisher="열린책들",
        year="2007",
        kdc="863.2",
        school_call_number="863/생894ㅇ",
    )
    csv_text = export_to_dls_csv([rec], school_name="○○초등학교")
    assert "어린왕자" in csv_text
    assert "○○초등학교" in csv_text
    assert "학교명" in csv_text  # 헤더

    # KORMARC → DLS
    book_data = {
        "isbn": "9999",
        "title": "테스트",
        "author": "X",
        "publisher": "Y",
        "year": 2026,
        "kdc": "100",
    }
    dls = kormarc_to_dls(book_data)
    assert dls.isbn == "9999"
    assert dls.year == "2026"

    # 가이드
    guide = generate_dls_import_guide("○○초등학교")
    assert "○○초등학교" in guide
    assert "DLS" in guide


def test_pmf_validator_basic():
    from kormarc_auto.intelligence.pmf_validator import (
        evaluate_sean_ellis,
        evaluate_unit_economics,
        evaluate_value_proposition,
        generate_pmf_report,
    )

    # Sean Ellis = 40%+ = PMF 달성
    result = evaluate_sean_ellis(very_count=40, somewhat_count=30, not_count=30)
    assert result.pmf_achieved is True
    assert result.very_disappointed_pct == 40.0
    assert result.sample_size == 100

    # Sean Ellis = 30%·미달
    result_low = evaluate_sean_ellis(very_count=20, somewhat_count=40, not_count=40)
    assert result_low.pmf_achieved is False

    # 단위 경제 = LTV/CAC ≥3
    econ = evaluate_unit_economics(
        cac_won=50_000,
        monthly_arpu=33_000,
        avg_lifetime_months=12,
    )
    # LTV = 396,000 / CAC = 50,000 = 7.92x
    assert econ.healthy is True
    assert econ.ltv_won == 396_000

    # 단위 경제 미달
    econ_bad = evaluate_unit_economics(cac_won=200_000, monthly_arpu=10_000, avg_lifetime_months=6)
    assert econ_bad.healthy is False

    # 10단어 가치
    short = evaluate_value_proposition("권당 8분 → 1분 KORMARC 자동 생성")
    assert short["passes_10_word_test"] is True

    long = evaluate_value_proposition(
        "이 도구는 한국 도서관 사서가 사용하는 KORMARC 메타데이터를 ISBN 입력만으로 자동 생성하는 SaaS 서비스입니다"
    )
    assert long["passes_10_word_test"] is False

    # 종합 PMF
    report = generate_pmf_report(result, econ, "권당 8분 → 1분 KORMARC 자동")
    assert report.overall_pmf is True


def test_library_hierarchy_basic():
    from kormarc_auto.interlibrary.library_hierarchy import (
        HIERARCHY_INFO,
        REGIONAL_INFO,
        LibraryClassification,
        recommend_strategy,
    )

    # 5 위계 모두 등록
    assert len(HIERARCHY_INFO) == 5
    assert "metropolitan_main" in HIERARCHY_INFO

    # 3 지역 유형
    assert len(REGIONAL_INFO) == 3
    assert "rural_fishing" in REGIONAL_INFO

    # 작은도서관 = Personal 9,900
    classification = LibraryClassification(
        hierarchy="small_library",
        regional_type="rural_fishing",
    )
    strategy = recommend_strategy(classification)
    assert "Personal" in strategy["price_tier"]
    assert any("C5b" in p for p in strategy["personas"])
    assert "농어촌" in strategy["funding_recommendation"]

    # 광역대표 = Enterprise
    metro = LibraryClassification(
        hierarchy="metropolitan_main",
        regional_type="urban",
    )
    metro_strategy = recommend_strategy(metro)
    assert metro_strategy["price_tier"] == "Enterprise"
