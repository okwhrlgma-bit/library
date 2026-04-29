"""builder.build_kormarc_record 자동 검증 통합 테스트."""

from __future__ import annotations

import logging

from kormarc_auto.kormarc.builder import build_kormarc_record


def test_build_minimal_book_emits_validation_warning(caplog):
    """최소 book_data → record 빌드 + 자동 검증 → logger.warning."""
    minimal = {"title": "테스트 책", "isbn": "9788912345678"}
    with caplog.at_level(logging.WARNING, logger="kormarc_auto.kormarc.builder"):
        record = build_kormarc_record(minimal)
    assert record is not None
    warnings = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("KORMARC 빌드 검증 위반" in w for w in warnings)


def test_build_with_auto_validate_disabled_no_warning(caplog):
    """auto_validate=False → logger.warning 없음 (테스트·골든 빌드용)."""
    minimal = {"title": "테스트 책", "isbn": "9788912345678"}
    with caplog.at_level(logging.WARNING, logger="kormarc_auto.kormarc.builder"):
        record = build_kormarc_record(minimal, auto_validate=False)
    assert record is not None
    warnings = [r.message for r in caplog.records if "KORMARC 빌드 검증" in r.message]
    assert warnings == []
