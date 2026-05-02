"""messages.py 친근 에러 라이브러리 테스트 (Part 47·51)."""
from __future__ import annotations

from kormarc_auto.ui.messages import (
    MESSAGE_CATALOG,
    TONE_RULES,
    show_error,
    show_info,
    validate_message_tone,
)


def test_catalog_has_8_message_types() -> None:
    """8 에러·안내 메시지 타입 정의 (Part 44 §1)."""
    expected_keys = {
        "isbn_invalid", "api_timeout", "api_all_failed", "network_error",
        "kormarc_validation_warning", "permission_denied", "processing", "complete",
    }
    assert expected_keys.issubset(MESSAGE_CATALOG.keys())


def test_show_error_returns_message_with_required_fields() -> None:
    """show_error 결과 = title·body·action·severity·icon 필수."""
    msg = show_error("isbn_invalid")
    assert msg.title
    assert msg.body
    assert msg.action
    assert msg.severity in {"info", "warning", "error"}
    assert msg.icon


def test_show_error_for_missing_key_returns_placeholder() -> None:
    """없는 키 → 디버깅용 플레이스홀더."""
    msg = show_error("nonexistent_key")
    assert "MISSING" in msg.title


def test_show_info_alias() -> None:
    """show_info = show_error 동일 인터페이스."""
    msg_error = show_error("processing", count=10, avg_time=2.5)
    msg_info = show_info("processing", count=10, avg_time=2.5)
    assert msg_error.title == msg_info.title


def test_validate_tone_blocks_blame_words() -> None:
    """비난 어휘 검출 (NN/G 5원칙)."""
    from kormarc_auto.ui.messages import Message

    bad_msg = Message(
        title="잘못된 입력",
        body="invalid ISBN을 입력하셨습니다",
        action="다시 시도",
        severity="error",
        icon="❌",
    )
    violations = validate_message_tone(bad_msg)
    assert len(violations) > 0, "비난 어휘 미검출"


def test_validate_tone_passes_friendly_message() -> None:
    """친근 톤 메시지 통과."""
    from kormarc_auto.ui.messages import Message

    friendly = Message(
        title="ISBN을 다시 확인해주세요",
        body="13자리 숫자가 맞는지 살펴봐주세요. 책 뒷표지에서 찾을 수 있어요.",
        action="다시 입력하기",
        severity="warning",
        icon="📖",
    )
    violations = validate_message_tone(friendly)
    assert violations == []


def test_validate_tone_requires_action() -> None:
    """모든 메시지 = 회복 행동 필수."""
    from kormarc_auto.ui.messages import Message

    no_action = Message(
        title="제목",
        body="본문",
        action="",
        severity="error",
        icon="❌",
    )
    violations = validate_message_tone(no_action)
    assert any("action" in v for v in violations)


def test_processing_message_formats_count() -> None:
    """processing 메시지 = count·avg_time 포맷."""
    msg = show_error("processing", count=100, avg_time=1.5)
    assert "100" in msg.body or "100건" in msg.body or "100권" in msg.body


def test_tone_rules_defined() -> None:
    """TONE_RULES 자가 검증 규칙 정의."""
    assert "blame_user" in TONE_RULES
    assert "actionable_required" in TONE_RULES
    assert TONE_RULES["actionable_required"] is True
