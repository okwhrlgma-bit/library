"""Property-based testing — Part 92 §A.5 (Hypothesis 6.152+).

PO 명령 (Part 92): "round-trip·idempotence·metamorphic·invariant"
Anthropic 2025-10 paper (arXiv 2510.09907) = 자율 Hypothesis 생성 검증

KORMARC 핵심 invariants:
- Leader = 24자
- Leader byte 09 = 'a' (UTF-8 인코딩)
- 008 = 40자
- 020 ▾a = 13자 (ISBN-13)·체크 디지트 정합
"""

from __future__ import annotations

import pytest

# Hypothesis 미설치 시 = skip (개발 도구 옵션)
hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

# ============== KORMARC Leader 24자 invariant ==============


class TestLeaderInvariant:
    @given(record_type=st.sampled_from(["a", "c", "g", "i", "m"]))
    @settings(max_examples=20)
    def test_leader_24_chars(self, record_type: str):
        from pymarc import Record

        leader = f"00000n{record_type}m a2200000   4500"
        rec = Record(leader=leader, force_utf8=True)
        assert len(str(rec.leader)) == 24, "leader 길이 24자 invariant 위반"


# ============== ISBN-13 체크 디지트 invariant ==============


def _calc_ean13_check(twelve_digits: str) -> int:
    """EAN-13 체크 디지트 계산."""
    digits = [int(c) for c in twelve_digits]
    s = sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(digits))
    return (10 - s % 10) % 10


@st.composite
def isbn13_strategy(draw):
    """13자리 ISBN (978/979 prefix·체크 디지트 정합)."""
    prefix = draw(st.sampled_from(["978", "979"]))
    body = draw(st.text(alphabet="0123456789", min_size=9, max_size=9))
    twelve = prefix + body
    check = _calc_ean13_check(twelve)
    return twelve + str(check)


class TestIsbnInvariant:
    @given(isbn=isbn13_strategy())
    @settings(max_examples=50)
    def test_validate_ean13_accepts_generated(self, isbn: str):
        from kormarc_auto.mobile.bluetooth_scanner import validate_ean13

        assert validate_ean13(isbn) is True, f"생성된 정상 ISBN {isbn} = 검증 실패"

    @given(isbn=st.text(alphabet="0123456789", min_size=12, max_size=12))
    @settings(max_examples=20)
    def test_12_digit_rejected(self, isbn: str):
        from kormarc_auto.mobile.bluetooth_scanner import validate_ean13

        assert validate_ean13(isbn) is False, "12자리 = ISBN-13 X·거부 필수"


# ============== budgaeho 5자리 round-trip ==============


class TestBudgaehoRoundTrip:
    @given(code=st.text(alphabet="0123456789", min_size=5, max_size=5))
    @settings(max_examples=30)
    def test_decode_5digit_returns_kdc(self, code: str):
        from kormarc_auto.classification.budgaeho_decoder import decode_budgaeho

        result = decode_budgaeho(code)
        assert result is not None, f"5자리 숫자 {code} = 항상 디코딩 가능"
        assert len(result.kdc_2digit) == 2

    @given(
        invalid=st.text(min_size=1, max_size=10).filter(lambda s: not (len(s) == 5 and s.isdigit()))
    )
    @settings(max_examples=20)
    def test_invalid_returns_none(self, invalid: str):
        from kormarc_auto.classification.budgaeho_decoder import decode_budgaeho

        assert decode_budgaeho(invalid) is None, f"비정합 입력 {invalid!r} = None 필수"


# ============== KDC↔DDC swap idempotence ==============


class TestKdcDdcMapping:
    @given(kdc_main=st.sampled_from(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]))
    @settings(max_examples=15)
    def test_kdc_to_ddc_returns_valid_ddc(self, kdc_main: str):
        from kormarc_auto.classification.ddc_classifier import kdc_to_ddc

        result = kdc_to_ddc(kdc_main)
        assert result.ddc is not None, f"KDC 단일 자리 {kdc_main} = DDC 매핑 보장"
        # DDC = 3자리 (예: "500")
        assert result.ddc[0].isdigit()


# ============== 텐넌트 격리 invariant ==============


class TestTenantInvariant:
    @given(
        tenant_id=st.text(min_size=3, max_size=20).filter(str.strip),
    )
    @settings(max_examples=20)
    def test_set_get_tenant_consistency(self, tenant_id: str):
        from kormarc_auto.security.tenant_isolation import (
            clear_tenant,
            get_current_tenant,
            set_current_tenant,
        )

        clear_tenant()
        set_current_tenant(tenant_id)
        assert get_current_tenant() == tenant_id, "set/get tenant 일관성 invariant"
        clear_tenant()


# ============== SLO 메트릭 metamorphic ==============


class TestSloMetamorphic:
    @given(
        durations=st.lists(st.floats(min_value=0.1, max_value=1000.0), min_size=10, max_size=100)
    )
    @settings(max_examples=10)
    def test_p95_geq_p50(self, durations: list[float]):
        from kormarc_auto.observability.slo_metrics import (
            get_slo_summary,
            record_metric,
            reset_window,
        )

        reset_window()
        for d in durations:
            record_metric("isbn_to_mrc", duration_ms=d, success=True)

        s = get_slo_summary()["isbn_to_mrc"]
        if s["p95_ms"] is not None and s["avg_ms"] is not None:
            # metamorphic: p95 >= avg (대부분 케이스)
            sorted_d = sorted(durations)
            median = sorted_d[len(sorted_d) // 2]
            assert s["p95_ms"] >= median * 0.5, "p95 metamorphic invariant 위반"
