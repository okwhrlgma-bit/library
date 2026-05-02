"""Part 81 신규 모듈 테스트 (245 검수·사서교사 대시보드)."""
from __future__ import annotations


def test_title_245_validator_basic():
    from kormarc_auto.kormarc.title_245_validator import (
        validate_245,
        auto_fix_suggestions,
    )

    # 정상 245
    record_data = {
        "data_fields": [
            {
                "tag": "245",
                "ind1": "1",
                "ind2": "0",
                "subfields": [
                    {"code": "a", "value": "어린왕자"},
                    {"code": "c", "value": "생텍쥐페리 지음"},
                ],
            }
        ]
    }
    issues = validate_245(record_data)
    # 정상 입력 = 적은 issue (warning·info만)
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 0

    # 245 누락 = error
    issues_missing = validate_245({"data_fields": []})
    assert any(i.level == "error" for i in issues_missing)

    # 4인 이상 합저 = warning
    record_4plus = {
        "data_fields": [
            {
                "tag": "245",
                "ind1": "1",
                "ind2": "0",
                "subfields": [
                    {"code": "a", "value": "공동 저서"},
                    {"code": "c", "value": "홍길동, 김철수, 이영희, 박지수 지음"},
                ],
            }
        ]
    }
    issues_4plus = validate_245(record_4plus)
    assert any("4인 이상" in i.message for i in issues_4plus)

    # ▾h 자료유형 = '[ ]' 없음 = error
    record_h = {
        "data_fields": [
            {
                "tag": "245",
                "ind1": "1",
                "ind2": "0",
                "subfields": [
                    {"code": "a", "value": "오디오북"},
                    {"code": "h", "value": "녹음자료"},
                ],
            }
        ]
    }
    issues_h = validate_245(record_h)
    assert any(i.subfield == "h" and i.level == "error" for i in issues_h)


def test_school_librarian_dashboard_basic():
    from kormarc_auto.ui.school_librarian_dashboard import (
        STANDARD_TASKS,
        calculate_weekly_savings,
        categorize_tasks,
    )

    # 표준 업무 10건
    assert len(STANDARD_TASKS) >= 10

    # 절감 계산
    savings = calculate_weekly_savings()
    assert savings["total_minutes_per_week"] > 0
    assert savings["saved_minutes"] > 0
    assert 0 <= savings["automation_ratio"] <= 1

    # 카테고리 분류
    by_cat = categorize_tasks()
    assert "cataloging" in by_cat
    assert "collaboration" in by_cat
    assert "admin" in by_cat
