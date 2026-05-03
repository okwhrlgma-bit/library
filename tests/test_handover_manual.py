"""handover_manual 인계 매뉴얼 테스트 (Part 51, P4 1년 계약직 사서)."""

from __future__ import annotations

from datetime import date

from kormarc_auto.output.handover_manual import (
    HandoverManualData,
    generate_handover_manual_markdown,
    save_handover_manual,
)


def _sample_data() -> HandoverManualData:
    return HandoverManualData(
        library_name="공공도서관 A관",  # 익명화 (자관 익명화 정책 정합)
        librarian_name="김지수",
        contract_start=date(2025, 5, 1),
        contract_end=date(2026, 4, 30),
        next_librarian_start=date(2026, 5, 1),
        self_prefix=["EQ", "CQ"],
        favorite_kdc=["863", "001"],
        favorite_special_locations=["WQ"],
        monthly_records_avg=120,
        total_records=1440,
        notes="자료구입비는 매월 첫 주에 집행합니다.",
        next_renewal_date=date(2026, 7, 1),
        contact_email="kim@example.kr",
    )


def test_markdown_includes_librarian_honorific() -> None:
    """사서 호칭 '선생님' 포함."""
    md = generate_handover_manual_markdown(_sample_data())
    assert "선생님" in md


def test_markdown_includes_self_prefix() -> None:
    """본인 자관 prefix 인계 포함."""
    md = generate_handover_manual_markdown(_sample_data())
    assert "EQ" in md
    assert "CQ" in md


def test_markdown_includes_renewal_date() -> None:
    """결제 갱신 일정 포함 (P4 페인 직접 해결)."""
    md = generate_handover_manual_markdown(_sample_data())
    assert "2026년 7월 1일" in md


def test_markdown_includes_first_week_workflow() -> None:
    """다음 사서 첫 1주 워크플로 안내 포함."""
    md = generate_handover_manual_markdown(_sample_data())
    assert "Day 1" in md or "첫 1주" in md


def test_markdown_anonymizes_when_using_anonymous_name() -> None:
    """익명화된 도서관명 사용 시 자관 식별 키워드 X."""
    md = generate_handover_manual_markdown(_sample_data())
    forbidden = ["내를건너서", "내건숲", "은평구공공", "북악산", "윤동주"]
    for keyword in forbidden:
        assert keyword not in md, f"자관 식별 키워드 노출: {keyword}"


def test_markdown_includes_contact_email() -> None:
    """전임 사서 연락처 + 운영자 이메일 포함."""
    md = generate_handover_manual_markdown(_sample_data())
    assert "kim@example.kr" in md
    assert "contact@kormarc-auto.example" in md


def test_save_handover_manual_creates_file(tmp_path) -> None:
    """파일 저장 성공."""
    output = tmp_path / "handover.md"
    success = save_handover_manual(_sample_data(), str(output))
    assert success
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "인계 매뉴얼" in content


def test_handles_empty_prefix_and_kdc() -> None:
    """빈 prefix·KDC도 graceful 처리."""
    data = HandoverManualData(
        library_name="A관",
        librarian_name="신규",
        contract_start=date(2026, 1, 1),
        contract_end=date(2026, 12, 31),
    )
    md = generate_handover_manual_markdown(data)
    assert "사용 prefix 없음" in md or "(사용 prefix 없음)" in md
