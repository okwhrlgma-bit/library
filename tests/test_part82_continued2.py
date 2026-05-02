"""Part 82+ 추가 모듈 테스트 (큐레이션·야간 안전·다국어)."""
from __future__ import annotations

from datetime import date


def test_book_curation_engine_basic():
    from kormarc_auto.acquisition.book_curation_engine import (
        CurationCriteria,
        auto_select_theme,
        curate_books,
        generate_curation_markdown,
        CURATION_THEMES,
        AGE_GROUPS,
    )

    # 자동 테마
    assert auto_select_theme(date(2026, 4, 1)) == "spring"
    assert auto_select_theme(date(2026, 7, 1)) == "summer"
    assert auto_select_theme(date(2026, 10, 1)) == "autumn"
    assert auto_select_theme(date(2026, 12, 1)) == "winter"

    # 큐레이션
    candidates = [
        {"isbn": "9788937437076", "title": "어린왕자", "author": "생텍쥐페리", "kdc": "863.2"},
        {"isbn": "9791164060238", "title": "윤동주 시집", "author": "윤동주", "kdc": "811.7"},
        {"isbn": "9999", "title": "어른용", "author": "X", "kdc": "300", "age_target": "adult"},
    ]
    criteria = CurationCriteria(theme="spring", age_group="elementary_high", kdc_focus=["8"], max_books=5)
    result = curate_books(candidates, criteria)
    assert len(result.selected_books) >= 2  # 어린왕자·윤동주 시집
    assert "봄" in result.poster_title or "신학기" in result.poster_title

    # markdown 생성
    md = generate_curation_markdown(result)
    assert "추천" in md
    assert result.poster_title in md

    # CURATION_THEMES·AGE_GROUPS 확인
    assert "spring" in CURATION_THEMES
    assert "elementary_high" in AGE_GROUPS


def test_night_safety_protocol_basic():
    from kormarc_auto.safety.night_safety_protocol import (
        SafetyCheck,
        NIGHT_CHECKLIST,
        get_checklist,
        render_safety_log,
        emergency_contact_info,
    )

    # 4 체크 유형 모두 매뉴얼
    for ct in ["entry", "midnight", "exit", "emergency"]:
        items = get_checklist(ct)
        assert len(items) > 0

    # SafetyCheck 기록
    check = SafetyCheck(
        check_type="entry",
        librarian_name="홍길동",
        completed_items=["출입문 잠금", "보안 시스템"],
    )
    log = render_safety_log([check])
    assert "야간 안전" in log
    assert "홍길동" in log
    assert "✅" in log

    # 비상 연락처
    contacts = emergency_contact_info({"director_phone": "010-1234-5678"})
    assert "112" in contacts
    assert "119" in contacts
    assert "010-1234-5678" in contacts.get("관장", "")


def test_multilingual_helper_basic():
    from kormarc_auto.classification.multilingual_helper import (
        detect_language,
        is_translation,
        build_041_field,
        LANGUAGE_CODES,
    )

    # 한국어
    result_kor = detect_language("어린왕자")
    assert result_kor.primary_language == "kor"

    # 영어
    result_eng = detect_language("Little Prince")
    assert result_eng.primary_language == "eng"

    # 일본어 (가나)
    result_jpn = detect_language("こんにちは")
    assert result_jpn.primary_language == "jpn"

    # 번역서 감지
    assert is_translation({"translator": "김철수"}) is True
    assert is_translation({"author": "홍길동"}) is False
    assert is_translation({"original_language": "fre"}) is True

    # 041 필드 자동 (번역서)
    field = build_041_field({
        "translator": "김철수",
        "language": "kor",
        "original_language": "fre",
    })
    assert field is not None
    assert field["tag"] == "041"
    assert any(s["code"] == "h" and s["value"] == "fre" for s in field["subfields"])

    # 비번역 = None
    assert build_041_field({"author": "홍길동"}) is None

    # LANGUAGE_CODES
    assert "kor" in LANGUAGE_CODES
    assert "eng" in LANGUAGE_CODES
