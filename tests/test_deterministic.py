"""갈래 A Cycle 8 (P12) — 결정론 검증 테스트.

검증 invariants:
1. compute_input_hash 동일 입력 → 동일 hash (5회)
2. get_pinned_model = ENV override · default fallback
3. DeterministicCallParams = temperature=0·top_p=1
4. assert_deterministic_kwargs = 위반 즉시 ValueError
5. build_record_metadata = 동일 입력 → 동일 hash (timestamp 제외)
6. verify_deterministic_consistency = 동일 모델·입력 → True

설치 미감지 시 자동 skip.
"""

from __future__ import annotations

import pytest

from kormarc_auto.kormarc.record_metadata import (
    build_record_metadata,
    verify_deterministic_consistency,
)
from kormarc_auto.llm.deterministic import (
    DETERMINISTIC_TEMPERATURE,
    DETERMINISTIC_TOP_P,
    assert_deterministic_kwargs,
    compute_input_hash,
    get_pinned_model,
    make_deterministic_call,
)


class TestInputHash:
    def test_same_input_same_hash_5_times(self):
        payload = {"isbn": "9788937437076", "title": "어린 왕자"}
        hashes = [compute_input_hash(payload) for _ in range(5)]
        assert len(set(hashes)) == 1, "동일 입력 → 동일 hash"

    def test_dict_key_order_invariant(self):
        a = {"isbn": "9788937437076", "title": "어린 왕자"}
        b = {"title": "어린 왕자", "isbn": "9788937437076"}
        assert compute_input_hash(a) == compute_input_hash(b)

    def test_different_input_different_hash(self):
        a = compute_input_hash({"isbn": "9788937437076"})
        b = compute_input_hash({"isbn": "9788932473901"})
        assert a != b

    def test_string_input_supported(self):
        assert compute_input_hash("test") == compute_input_hash("test")

    def test_hash_is_sha256_64_hex(self):
        h = compute_input_hash("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestModelPinning:
    def test_default_sonnet(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_MODEL_SONNET", raising=False)
        assert get_pinned_model("sonnet") == "claude-sonnet-4-6"

    def test_default_haiku(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_MODEL_HAIKU", raising=False)
        assert get_pinned_model("haiku") == "claude-haiku-4-5-20251001"

    def test_default_opus(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_MODEL_OPUS", raising=False)
        assert get_pinned_model("opus") == "claude-opus-4-7"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_MODEL_SONNET", "test-pinned-model")
        assert get_pinned_model("sonnet") == "test-pinned-model"

    def test_unknown_tier_falls_back_to_sonnet(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_MODEL_SONNET", raising=False)
        assert get_pinned_model("unknown") == "claude-sonnet-4-6"


class TestCallParams:
    def test_default_temperature_0(self):
        p = make_deterministic_call(tier="sonnet")
        assert p.temperature == DETERMINISTIC_TEMPERATURE == 0.0

    def test_default_top_p_1(self):
        p = make_deterministic_call(tier="sonnet")
        assert p.top_p == DETERMINISTIC_TOP_P == 1.0

    def test_default_timeout_10s(self):
        # 헌법 §3 외부 API timeout 10s
        p = make_deterministic_call(tier="sonnet")
        assert p.timeout_seconds == 10

    def test_to_anthropic_kwargs(self):
        p = make_deterministic_call(tier="sonnet")
        kw = p.to_anthropic_kwargs()
        assert kw["temperature"] == 0.0
        assert kw["top_p"] == 1.0
        assert kw["timeout"] == 10
        assert "model" in kw

    def test_attach_record_metadata_includes_required_keys(self):
        p = make_deterministic_call(tier="sonnet")
        meta = p.attach_record_metadata({"isbn": "9788937437076"})
        for k in ("model_string", "generation_timestamp", "input_hash", "deterministic"):
            assert k in meta


class TestAssertDeterministic:
    def test_pass_on_correct_kwargs(self):
        assert_deterministic_kwargs({"temperature": 0.0, "top_p": 1.0})

    def test_fail_on_temperature_violation(self):
        with pytest.raises(ValueError, match="헌법 §9 위반"):
            assert_deterministic_kwargs({"temperature": 0.7, "top_p": 1.0})

    def test_fail_on_top_p_violation(self):
        with pytest.raises(ValueError, match="헌법 §9 위반"):
            assert_deterministic_kwargs({"temperature": 0.0, "top_p": 0.95})


class TestRecordMetadata:
    def test_same_input_same_hash(self):
        m1 = build_record_metadata(input_payload={"isbn": "9788937437076"})
        m2 = build_record_metadata(input_payload={"isbn": "9788937437076"})
        assert m1["input_hash"] == m2["input_hash"]
        assert m1["model_string"] == m2["model_string"]

    def test_different_input_different_hash(self):
        m1 = build_record_metadata(input_payload={"isbn": "9788937437076"})
        m2 = build_record_metadata(input_payload={"isbn": "9788932473901"})
        assert m1["input_hash"] != m2["input_hash"]

    def test_extra_metadata_merged(self):
        m = build_record_metadata(input_payload={"isbn": "X"}, extra={"operator": "사서 A"})
        assert m["operator"] == "사서 A"

    def test_seed_recorded_when_provided(self):
        m = build_record_metadata(input_payload={"isbn": "X"}, deterministic_seed=42)
        assert m["deterministic_seed"] == 42

    def test_default_deterministic_true(self):
        m = build_record_metadata(input_payload="x")
        assert m["deterministic"] is True


class TestDeterministicConsistency:
    def test_consistent_when_same(self):
        m = build_record_metadata(input_payload={"isbn": "X"})
        m2 = dict(m)
        ok, reason = verify_deterministic_consistency(m, m2)
        assert ok is True
        assert reason is None

    def test_inconsistent_when_different_model(self):
        m1 = build_record_metadata(input_payload={"isbn": "X"})
        m2 = dict(m1)
        m2["model_string"] = "different-model"
        ok, reason = verify_deterministic_consistency(m1, m2)
        assert ok is False
        assert "model_string" in reason

    def test_inconsistent_when_different_hash(self):
        m1 = build_record_metadata(input_payload={"isbn": "X"})
        m2 = build_record_metadata(input_payload={"isbn": "Y"})
        ok, reason = verify_deterministic_consistency(m1, m2)
        assert ok is False
        assert "input_hash" in reason


# Hypothesis property test (skip if not installed)
hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

_PRINTABLE = st.text(
    alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
    min_size=1,
    max_size=40,
)


class TestDeterminismProperty:
    @given(isbn=st.text(alphabet="0123456789", min_size=13, max_size=13))
    def test_isbn_hash_stable_across_calls(self, isbn):
        """동일 ISBN → 5회 호출 동일 hash (결정론 §9)."""
        hashes = [compute_input_hash({"isbn": isbn}) for _ in range(5)]
        assert len(set(hashes)) == 1

    @given(payload=st.dictionaries(keys=_PRINTABLE, values=_PRINTABLE, min_size=1, max_size=5))
    def test_dict_payload_hash_stable(self, payload):
        """임의 dict payload → 5회 호출 동일 hash."""
        hashes = [compute_input_hash(payload) for _ in range(5)]
        assert len(set(hashes)) == 1

    @given(
        seed=st.integers(min_value=0, max_value=2**31),
        payload_str=_PRINTABLE,
    )
    def test_metadata_input_hash_property(self, seed, payload_str):
        """build_record_metadata · 동일 입력·seed → 동일 input_hash."""
        m1 = build_record_metadata(input_payload=payload_str, deterministic_seed=seed)
        m2 = build_record_metadata(input_payload=payload_str, deterministic_seed=seed)
        assert m1["input_hash"] == m2["input_hash"]
        assert m1["deterministic_seed"] == m2["deterministic_seed"] == seed
