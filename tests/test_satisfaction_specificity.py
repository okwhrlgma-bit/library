"""사서 만족도 + 도서관 특이성 모듈 테스트 (PO 명령 2026-05-03 정합)."""

from __future__ import annotations


def test_librarian_satisfaction_basic():
    from kormarc_auto.ui.librarian_satisfaction_tracker import (
        SatisfactionResponse,
        analyze_by_persona,
        calculate_ces,
        calculate_csat,
        calculate_nps,
    )

    # NPS = 60 (Promoter 7·Passive 2·Detractor 1)
    nps_scores = [10, 10, 10, 9, 9, 9, 9, 7, 7, 5]
    nps_result = calculate_nps(nps_scores)
    assert nps_result["nps"] == 60
    assert nps_result["promoters"] == 7
    assert nps_result["passives"] == 2
    assert nps_result["detractors"] == 1
    assert nps_result["achieved_50"] is True

    # CSAT = 4.0+ = 우수
    csat_scores = [5, 5, 4, 4, 4, 5, 4, 5]
    csat_result = calculate_csat(csat_scores)
    assert csat_result["avg"] >= 4.0
    assert csat_result["satisfied_pct"] == 100.0
    assert csat_result["achieved_80"] is True

    # CES ≤2 = 우수
    ces_scores = [1, 2, 1, 2, 1, 2]
    ces_result = calculate_ces(ces_scores)
    assert ces_result["avg"] <= 2.0
    assert ces_result["achieved_low"] is True

    # 페르소나별 분석
    responses = [
        SatisfactionResponse(librarian_id="A", persona="P1", metric="nps", score=10),
        SatisfactionResponse(librarian_id="B", persona="P14", metric="nps", score=9),
        SatisfactionResponse(librarian_id="C", persona="P14", metric="csat", score=5),
    ]
    by_persona = analyze_by_persona(responses)
    assert "P1" in by_persona
    assert "P14" in by_persona
    assert by_persona["P1"]["nps"]["nps"] == 100  # 100% promoter


def test_library_specificity_basic():
    from kormarc_auto.librarian_helpers.library_specificity import (
        REGIONAL_POLICIES,
        LibrarySpecificity,
        auto_apply_specificity,
        detect_library_pattern,
        get_regional_policy,
    )

    # 지역별 정책 (5+)
    assert len(REGIONAL_POLICIES) >= 5
    assert "seoul_eunpyeong" in REGIONAL_POLICIES
    assert "jeonnam" in REGIONAL_POLICIES

    # 은평구 = 책단비
    eunpyeong = get_regional_policy("seoul_eunpyeong")
    assert "책단비" in eunpyeong["membership"]

    # 전남 = 학교 = 3월 시작 + 순회사서
    jeonnam = get_regional_policy("jeonnam")
    assert jeonnam["fiscal_year"] == 3
    assert "순회사서" in jeonnam.get("note", "")

    # 자관 특이성 적용
    library = LibrarySpecificity(
        library_id="LIB001",
        library_name="○○도서관",
        library_type="public",
        hierarchy="branch_main",
        region="seoul_eunpyeong",
        sasagwan_prefix="EQ",
        call_number_format="{KDC}/{이재철}",
        shelf_categories=["시문학", "아동", "향토"],
    )
    book_data = {"title": "윤동주 시집", "isbn": "9999"}
    enriched = auto_apply_specificity(book_data, library)
    assert enriched["registration_no_prefix"] == "EQ"
    assert enriched["cataloging_agency"] == "LIB001"
    # "시문학" = title 매칭 = shelf_category 자동
    assert enriched.get("shelf_category") == "시문학"

    # 패턴 감지 (3건+ 누적)
    history = [
        {"registration_no": "EQ001", "shelf_category": "시문학"},
        {"registration_no": "EQ002", "shelf_category": "시문학"},
        {"registration_no": "EQ003", "shelf_category": "아동"},
    ]
    pattern = detect_library_pattern(history)
    assert pattern["detected_prefix"] == "EQ"
    assert "시문학" in pattern["detected_shelves"]
    assert pattern["confidence"] > 0


def test_builder_with_library_spec():
    """builder.build_kormarc_record가 library_spec 자동 적용."""
    from kormarc_auto.kormarc.builder import build_kormarc_record
    from kormarc_auto.librarian_helpers.library_specificity import LibrarySpecificity

    library = LibrarySpecificity(
        library_id="EQLIB001",
        library_name="은평구립도서관",
        library_type="public",
        hierarchy="branch_main",
        region="seoul_eunpyeong",
        sasagwan_prefix="EQ",
        call_number_format="{KDC}/{이재철}",
        shelf_categories=["시문학", "아동"],
    )

    book_data = {
        "isbn": "9788937437076",
        "title": "윤동주 시집",
        "author": "윤동주",
        "publisher": "민음사",
        "publication_year": "2026",
        "kdc": "811.7",
    }
    record = build_kormarc_record(book_data, library_spec=library, auto_validate=False)

    # 040 ▾a override
    f040 = record.get_fields("040")
    assert f040 and any("EQLIB001" in str(f) for f in f040)

    # 049 ▾l prefix + ▾f 별치 자동
    f049 = record.get_fields("049")
    assert f049, "049 필드가 자동 생성되어야 함"
    f049_str = str(f049[0])
    assert "EQ-AUTO" in f049_str
    assert "시문학" in f049_str
