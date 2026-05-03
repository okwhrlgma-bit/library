"""B안 Cycle 2 — KORMARC_DEMO_MODE offline demo 회귀 테스트.

검증:
- aggregator offline 분기 (외부 호출 0건)
- 5건 SAMPLE_BOOKS 모두 처리 가능
- round-trip 100% baseline 유지
- 30초 회귀 게이트 (실측 < 1초)
"""

from __future__ import annotations

import os
import time
from io import BytesIO

import pytest


@pytest.fixture
def demo_mode():
    """KORMARC_DEMO_MODE=1 컨텍스트."""
    prev = os.environ.get("KORMARC_DEMO_MODE")
    os.environ["KORMARC_DEMO_MODE"] = "1"
    yield
    if prev is None:
        os.environ.pop("KORMARC_DEMO_MODE", None)
    else:
        os.environ["KORMARC_DEMO_MODE"] = prev


def test_aggregator_offline_no_external_call(demo_mode):
    """KORMARC_DEMO_MODE=1 = SAMPLE_BOOKS만 사용·외부 호출 0건."""
    from kormarc_auto.api.aggregator import aggregate_by_isbn

    r = aggregate_by_isbn("9788937437076")
    assert r["sources"] == ["offline_mock"]
    assert r["title"] == "어린 왕자"
    assert r["confidence"] == 0.95


def test_aggregator_offline_unknown_isbn_no_call(demo_mode):
    """미등록 ISBN도 외부 호출 X·offline_no_match True."""
    from kormarc_auto.api.aggregator import aggregate_by_isbn

    r = aggregate_by_isbn("9999999999999")
    assert r["sources"] == []
    assert r["offline_no_match"] is True


def test_demo_5_records_30sec_gate(demo_mode):
    """B안 Cycle 2 게이트 — 5건 30초 이내·round-trip 100%."""
    from pymarc import MARCReader

    from kormarc_auto.api.aggregator import aggregate_by_isbn
    from kormarc_auto.demo.offline_mock_server import list_demo_isbns
    from kormarc_auto.kormarc.builder import build_kormarc_record

    isbns = list_demo_isbns()[:5]
    t0 = time.time()
    ok = 0
    rt_pass = 0
    for isbn in isbns:
        data = aggregate_by_isbn(isbn)
        if not data.get("sources"):
            continue
        record = build_kormarc_record(data, cataloging_agency="DEMO")
        ok += 1
        # round-trip 회귀 (Cycle 1 baseline 정합)
        raw1 = record.as_marc()
        r2 = next(MARCReader(BytesIO(raw1), to_unicode=True, force_utf8=False), None)
        if r2 is not None and r2.as_marc() == raw1:
            rt_pass += 1

    elapsed = time.time() - t0
    assert ok == 5, f"5/5 처리 실패 ({ok}/5)"
    assert rt_pass == 5, f"round-trip 회귀 ({rt_pass}/5)"
    assert elapsed < 30, f"30초 게이트 위반 ({elapsed:.2f}s)"


def test_offline_no_anthropic_calls(demo_mode):
    """KORMARC_DEMO_MODE=1 = anthropic SDK 호출 0건 (mock 우선)."""
    from kormarc_auto.demo.offline_mock_server import (
        is_demo_mode,
        mock_anthropic_kdc_recommendation,
    )

    assert is_demo_mode() is True
    resp = mock_anthropic_kdc_recommendation("어린 왕자")
    assert resp.status_code == 200


def test_demo_isbn_count_at_least_5():
    """SAMPLE_BOOKS ≥ 5건 (B안 Cycle 2 5-record 게이트 충족)."""
    from kormarc_auto.demo.offline_mock_server import SAMPLE_BOOKS, list_demo_isbns

    assert len(SAMPLE_BOOKS) >= 5
    assert len(list_demo_isbns()) >= 5
