"""Cycle 43 V3 Block 2 — cost_supervisor 회귀.

V3 §3.7 hard cap·per-iter cap·stream-json 파싱·atomic state write.
실제 subprocess 호출 X = unit test (모듈 함수만).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automation"))

from cost_supervisor import (
    PRICING,
    cost_from_usage,
    parse_stream_event,
    price_lookup,
    write_state,
)


class TestPriceLookup:
    def test_haiku(self):
        p = price_lookup("claude-haiku-4-5")
        assert p["in"] == 1.00
        assert p["out"] == 5.00

    def test_sonnet(self):
        p = price_lookup("claude-sonnet-4-6")
        assert p["in"] == 3.00
        assert p["out"] == 15.00

    def test_opus(self):
        p = price_lookup("claude-opus-4-7")
        assert p["in"] == 5.00
        assert p["out"] == 25.00

    def test_unknown_falls_back_to_opus(self):
        # V3 §3.7 conservative fallback
        p = price_lookup("unknown-model-xyz")
        assert p == PRICING["claude-opus-4-7"]

    def test_pricing_invariants(self):
        # 캐시 read = 10% (V3 §3.5)
        for model_p in PRICING.values():
            assert model_p["cache_read"] == pytest.approx(model_p["in"] * 0.10)
            # 캐시 write 5min = 1.25x (V3 §3.5)
            assert model_p["cache_write_5m"] == pytest.approx(model_p["in"] * 1.25)


class TestCostFromUsage:
    def test_input_only_haiku(self):
        # 1M input tokens × $1 = $1.00
        cost = cost_from_usage(
            "claude-haiku-4-5",
            {"input_tokens": 1_000_000, "output_tokens": 0},
        )
        assert cost == pytest.approx(1.00)

    def test_output_only_sonnet(self):
        # 1M output × $15 = $15.00
        cost = cost_from_usage(
            "claude-sonnet-4-6",
            {"input_tokens": 0, "output_tokens": 1_000_000},
        )
        assert cost == pytest.approx(15.00)

    def test_cache_read_discount(self):
        # 1M cache_read × $0.30 (sonnet) = $0.30 (10% of input)
        cost = cost_from_usage(
            "claude-sonnet-4-6",
            {"cache_read_input_tokens": 1_000_000},
        )
        assert cost == pytest.approx(0.30)

    def test_cache_write_premium(self):
        # 1M cache_creation × $3.75 (sonnet) = $3.75 (1.25x input)
        cost = cost_from_usage(
            "claude-sonnet-4-6",
            {"cache_creation_input_tokens": 1_000_000},
        )
        assert cost == pytest.approx(3.75)

    def test_combined_realistic(self):
        # 실제 Sonnet 4.6 사이클 = input 50K + output 5K + cache_read 100K
        cost = cost_from_usage(
            "claude-sonnet-4-6",
            {
                "input_tokens": 50_000,
                "output_tokens": 5_000,
                "cache_read_input_tokens": 100_000,
            },
        )
        # 50K * 3 + 5K * 15 + 100K * 0.3 = 150,000 + 75,000 + 30,000 = 255,000
        # / 1M = $0.255
        assert cost == pytest.approx(0.255)

    def test_empty_usage(self):
        assert cost_from_usage("claude-sonnet-4-6", {}) == 0


class TestParseStreamEvent:
    def test_valid_init_event(self):
        line = '{"type":"system","subtype":"init","model":"claude-sonnet-4-6"}'
        ev = parse_stream_event(line)
        assert ev is not None
        assert ev["type"] == "system"
        assert ev["model"] == "claude-sonnet-4-6"

    def test_assistant_with_usage(self):
        line = '{"type":"assistant","message":{"usage":{"input_tokens":100,"output_tokens":50}}}'
        ev = parse_stream_event(line)
        assert ev["message"]["usage"]["input_tokens"] == 100

    def test_result_with_total_cost(self):
        line = '{"type":"result","total_cost_usd":1.234}'
        ev = parse_stream_event(line)
        assert ev["total_cost_usd"] == 1.234

    def test_invalid_json_returns_none(self):
        assert parse_stream_event("not json") is None

    def test_empty_line_returns_none(self):
        assert parse_stream_event("") is None
        assert parse_stream_event("   \n") is None

    def test_partial_json_returns_none(self):
        assert parse_stream_event('{"type":"system"') is None


class TestWriteState:
    def test_atomic_write(self, tmp_path):
        state_file = tmp_path / "budget.json"
        write_state(state_file, {"cumulative": 1.5, "iteration": 3})
        loaded = json.loads(state_file.read_text())
        assert loaded["cumulative"] == 1.5
        assert loaded["iteration"] == 3

    def test_overwrites_existing(self, tmp_path):
        state_file = tmp_path / "budget.json"
        state_file.write_text('{"old": "data"}')
        write_state(state_file, {"new": "data"})
        loaded = json.loads(state_file.read_text())
        assert "old" not in loaded
        assert loaded["new"] == "data"

    def test_tmp_suffix_cleanup(self, tmp_path):
        # atomic write = .tmp 파일이 .replace로 사라져야
        state_file = tmp_path / "budget.json"
        write_state(state_file, {"x": 1})
        assert not state_file.with_suffix(".tmp").exists()
        assert state_file.exists()


class TestV3InvariantsScenario:
    """V3 §3.7 핵심 invariants 시나리오 검증."""

    def test_hard_cap_signal(self, tmp_path):
        """abort=true·cumulative >= hard = PreToolUse hook이 deny할 state."""
        state_file = tmp_path / "budget.json"
        write_state(
            state_file,
            {"abort": True, "reason": "hard_cap", "cumulative": 20.50},
        )
        loaded = json.loads(state_file.read_text())
        assert loaded["abort"] is True
        assert loaded["reason"] == "hard_cap"

    def test_soft_state_under_threshold(self, tmp_path):
        """abort=false·cumulative < soft = 정상 운영 state."""
        state_file = tmp_path / "budget.json"
        write_state(
            state_file,
            {
                "abort": False,
                "cumulative": 2.30,
                "iteration": 5,
                "last_model": "claude-sonnet-4-6",
            },
        )
        loaded = json.loads(state_file.read_text())
        assert loaded["abort"] is False
        assert loaded["cumulative"] < 5.00  # default soft

    def test_per_iter_cap_state(self, tmp_path):
        """per_iter_cap = single iter 비용 폭주 차단."""
        state_file = tmp_path / "budget.json"
        write_state(
            state_file,
            {"abort": True, "reason": "per_iter_cap"},
        )
        loaded = json.loads(state_file.read_text())
        assert loaded["reason"] == "per_iter_cap"
