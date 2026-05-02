"""Part 82 확장 모듈 테스트 (기증·청구기호 검수)."""

from __future__ import annotations

from datetime import date


def test_donation_processor_basic():
    from kormarc_auto.acquisition.donation_processor import (
        DonationItem,
        evaluate_donation,
        generate_donation_certificate,
    )

    item = DonationItem(
        isbn="9788937437076",
        title="어린왕자",
        donor_name="홍길동",
        donor_contact="010-0000-0000",
        donation_date=date(2026, 5, 2),
        condition="양호",
    )

    # 양호 = accept
    result = evaluate_donation(item)
    assert result["decision"] == "accepted"

    # 폐기 검토 = reject
    bad_item = DonationItem(isbn="X", title="X", donor_name="X", condition="폐기 검토")
    bad_result = evaluate_donation(bad_item)
    assert bad_result["decision"] == "rejected"

    # 복본 + 보통 상태 = reject
    dup = DonationItem(isbn="X", title="X", donor_name="X", condition="낮음")
    dup_result = evaluate_donation(dup, library_has_copy=True)
    assert dup_result["decision"] == "rejected"

    # 기증증서
    cert = generate_donation_certificate(item, "○○도서관")
    assert "홍길동" in cert
    assert "○○도서관" in cert
    assert "어린왕자" in cert


def test_call_number_validator_basic():
    from kormarc_auto.librarian_helpers.call_number_validator import (
        suggest_call_number,
        validate_call_number,
    )

    # 정상 = 적은 issue
    issues = validate_call_number("863.2/ㅇ123ㅁ")
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 0

    # KDC 누락
    issues_no_kdc = validate_call_number("/ㅇ123ㅁ")
    assert any(i.component == "분류" and i.level == "error" for i in issues_no_kdc)

    # '/' 누락
    issues_no_slash = validate_call_number("863.2 ㅇ123ㅁ")
    assert any(i.component == "도서" and i.level == "warning" for i in issues_no_slash)

    # 자관 prefix 추가
    issues_prefix = validate_call_number("863.2/ㅇ123ㅁ", sasagwan_prefix="시문학")
    assert any(i.component == "별치" for i in issues_prefix)

    # suggest_call_number
    cn = suggest_call_number(kdc="863.2", author_korean="홍길동", volume=3)
    assert "863.2" in cn
    assert "v.3" in cn

    cn2 = suggest_call_number(kdc="811.7", author_korean="윤동주", sasagwan_prefix="시문학", copy=2)
    assert cn2.startswith("시문학")
    assert "c.2" in cn2
