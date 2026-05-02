"""049 prefix 자동 발견 모듈 테스트."""

from __future__ import annotations

import pytest

from kormarc_auto.librarian_helpers.prefix_discovery import (
    PrefixDiscoverer,
    PrefixSummary,
)


def test_summary_to_yaml_snippet():
    summary = PrefixSummary(
        total_records=3383,
        prefix_counts={"EQ": 2553, "CQ": 773, "WQ": 57},
        recommended_prefixes=("CQ", "EQ", "WQ"),
        threshold_pct=1.0,
    )
    snippet = summary.to_yaml_snippet()
    assert "registration_prefix" in snippet
    assert '"EQ"' in snippet
    assert '"WQ"' in snippet
    assert '"CQ"' in snippet


def test_threshold_filters_rare_prefixes():
    """threshold 1% 미만 prefix는 권장에서 제외."""
    summary = PrefixSummary(
        total_records=10000,
        prefix_counts={"EQ": 7500, "CQ": 2400, "WQ": 99},  # WQ = 0.99% < 1%
        recommended_prefixes=("CQ", "EQ"),  # WQ 제외
        threshold_pct=1.0,
    )
    assert "WQ" not in summary.recommended_prefixes


def test_invalid_threshold_raises():
    with pytest.raises(ValueError):
        PrefixDiscoverer(threshold_pct=0)
    with pytest.raises(ValueError):
        PrefixDiscoverer(threshold_pct=100)
    with pytest.raises(ValueError):
        PrefixDiscoverer(threshold_pct=-1)


def test_scan_nonexistent_dir_returns_empty():
    from pathlib import Path

    discoverer = PrefixDiscoverer()
    summary = discoverer.scan(Path("/nonexistent/path/that/does/not/exist"))
    assert summary.total_records == 0
    assert summary.recommended_prefixes == ()


def test_extract_049_prefix_normalizes_uppercase():
    class FakeSubfield:
        def __init__(self, code, value):
            self.code = code
            self.value = value

    class FakeField:
        def __init__(self, subfields):
            self.subfields = subfields

    class FakeRecord:
        def __init__(self, field):
            self._field = field

        def get(self, tag):
            return self._field if tag == "049" else None

    record = FakeRecord(FakeField([FakeSubfield("l", "wq12345")]))
    assert PrefixDiscoverer._extract_049_prefix(record) == "WQ"

    record_no = FakeRecord(None)
    assert PrefixDiscoverer._extract_049_prefix(record_no) is None
