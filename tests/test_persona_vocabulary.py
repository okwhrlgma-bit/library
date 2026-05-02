"""persona_vocabulary 어휘 분기 시스템 테스트 (Part 49·51 어셔션)."""

from __future__ import annotations

from kormarc_auto.ui.persona_vocabulary import (
    PERSONA_TO_MODE,
    VOCABULARY,
    get_persona_mode,
    t,
)


def test_vocabulary_has_70_plus_keys() -> None:
    """PO 명령 정합: 사서 친화 어휘 70+ 키."""
    assert len(VOCABULARY) >= 70, f"어휘 키 수 부족: {len(VOCABULARY)} < 70"


def test_all_keys_have_both_modes() -> None:
    """모든 어휘 키 = librarian + non_expert 양쪽 모드 정의."""
    for key, entry in VOCABULARY.items():
        assert "librarian" in entry, f"librarian 모드 누락: {key}"
        assert "non_expert" in entry, f"non_expert 모드 누락: {key}"


def test_librarian_terms_use_standard_vocabulary() -> None:
    """사서 모드 = 한국 도서관 표준 용어 (PO 필수 명령)."""
    standard_terms = {
        "term.acquisition": "수서",
        "term.shelving": "배가",
        "term.deposit": "납본",
        "term.special_location": "별치기호",
        "term.reserve_collection": "보존서고",
        "term.inventory": "장서점검",
        "term.circulation": "대출·반납",
        "term.interlibrary_loan": "상호대차",
    }
    for key, expected in standard_terms.items():
        assert VOCABULARY[key]["librarian"] == expected, f"표준 용어 불일치: {key}"


def test_non_expert_avoids_jargon() -> None:
    """비전문가 모드 = KORMARC·MARC 등 전문 용어 회피."""
    jargon_terms = {"KORMARC", "MARC", "ISO 2709"}
    for key, entry in VOCABULARY.items():
        non_expert = entry["non_expert"]
        for jargon in jargon_terms:
            if jargon in non_expert and key not in {"system.kolas", "system.dls", "system.alpas"}:
                # 시스템 호환 명시는 예외
                raise AssertionError(f"비전문가 모드에 전문 용어 {jargon} 노출: {key}")


def test_t_function_returns_correct_mode() -> None:
    """t() 함수가 모드별 정확한 어휘 반환."""
    assert t("home.title", mode="librarian") == "KORMARC 자동 생성"
    assert t("home.title", mode="non_expert") == "책 정보 자동 등록"


def test_t_function_returns_placeholder_for_missing() -> None:
    """없는 키는 디버깅용 플레이스홀더 반환."""
    result = t("nonexistent.key", mode="librarian")
    assert "MISSING" in result


def test_persona_to_mode_mapping_complete() -> None:
    """6 페르소나 모두 모드 매핑."""
    expected_personas = {
        "macro_librarian",
        "school_librarian",
        "contract_librarian",
        "university_librarian",
        "volunteer",
        "parent_volunteer",
    }
    assert expected_personas.issubset(PERSONA_TO_MODE.keys())


def test_volunteer_personas_use_non_expert_mode() -> None:
    """자원봉사 계열 페르소나 = 비전문가 모드."""
    assert PERSONA_TO_MODE["volunteer"] == "non_expert"
    assert PERSONA_TO_MODE["parent_volunteer"] == "non_expert"
    assert PERSONA_TO_MODE["student_helper"] == "non_expert"


def test_get_persona_mode_default() -> None:
    """미지정 페르소나 = librarian 기본."""
    assert get_persona_mode("unknown_persona") == "librarian"
    assert get_persona_mode("macro_librarian") == "librarian"
    assert get_persona_mode("parent_volunteer") == "non_expert"
