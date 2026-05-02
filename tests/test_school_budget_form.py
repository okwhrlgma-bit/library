"""school_budget_form 학교운영위 결재 양식 테스트 (Part 51, P2 사서교사)."""
from __future__ import annotations

from datetime import date

from kormarc_auto.output.school_budget_form import (
    REGIONAL_NOTES,
    SchoolBudgetFormData,
    generate_school_budget_form_markdown,
    get_regional_template,
)


def test_form_data_default_values() -> None:
    """기본값 = 월 3만원 / 연 36만원 / 표준 안건명."""
    data = SchoolBudgetFormData(
        school_name="테스트초등학교",
        school_address="서울 테스트구 테스트로 1",
        librarian_name="김지수",
    )
    assert data.monthly_cost_krw == 30_000
    assert data.annual_cost_krw == 360_000
    assert "KORMARC" in data.proposal_title


def test_markdown_includes_school_name() -> None:
    """양식에 학교명 포함."""
    data = SchoolBudgetFormData(
        school_name="한빛초등학교",
        school_address="서울 노원구",
        librarian_name="박민수",
    )
    md = generate_school_budget_form_markdown(data)
    assert "한빛초등학교" in md
    assert "박민수" in md


def test_markdown_includes_librarian_honorific() -> None:
    """사서 호칭 '선생님' 포함 (PO 명령 정합)."""
    data = SchoolBudgetFormData(
        school_name="학교",
        school_address="주소",
        librarian_name="이지영",
    )
    md = generate_school_budget_form_markdown(data)
    assert "선생님" in md


def test_markdown_includes_cost_section() -> None:
    """비용 섹션 포함."""
    data = SchoolBudgetFormData(
        school_name="학교",
        school_address="주소",
        librarian_name="사서",
    )
    md = generate_school_budget_form_markdown(data)
    assert "30,000" in md
    assert "360,000" in md


def test_markdown_includes_alpas_comparison() -> None:
    """알파스 비교 (Part 51 영업 자료 정합)."""
    data = SchoolBudgetFormData(
        school_name="학교",
        school_address="주소",
        librarian_name="사서",
    )
    md = generate_school_budget_form_markdown(data)
    assert "알파스" in md
    assert "1,000만원" in md


def test_markdown_includes_government_funding() -> None:
    """AI 바우처 정부 자금 안내 포함."""
    data = SchoolBudgetFormData(
        school_name="학교",
        school_address="주소",
        librarian_name="사서",
    )
    md = generate_school_budget_form_markdown(data)
    assert "AI" in md and ("바우처" in md or "NIPA" in md)


def test_markdown_anonymizes_pilot_library() -> None:
    """자관 익명화 정책 정합 (PILOT 1관 표기, 자관 이름 X)."""
    data = SchoolBudgetFormData(
        school_name="테스트학교",
        school_address="주소",
        librarian_name="사서",
    )
    md = generate_school_budget_form_markdown(data)
    # 자관 식별 키워드 노출 X
    forbidden = ["내를건너서", "내건숲", "은평구공공", "북악산", "윤동주"]
    for keyword in forbidden:
        assert keyword not in md, f"자관 식별 키워드 노출: {keyword}"


def test_regional_template_has_5_regions() -> None:
    """5 지역 표준 (서울·경기·부산·대구·기타)."""
    expected = {"seoul", "gyeonggi", "busan", "daegu", "other"}
    assert expected.issubset(REGIONAL_NOTES.keys())


def test_get_regional_template_seoul() -> None:
    note = get_regional_template("seoul")
    assert "서울" in note


def test_get_regional_template_gyeonggi_mentions_1_school_1_librarian() -> None:
    """경기도 = 1교 1사서 정책 명시."""
    note = get_regional_template("gyeonggi")
    assert "1교 1사서" in note
