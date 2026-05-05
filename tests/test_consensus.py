"""Cycle 32~33 — N-Vote + Adversarial 회귀."""

from __future__ import annotations

import pytest

from kormarc_auto.consensus import (
    ADVERSARIAL_DAILY_CAP,
    DEFAULT_AGREEMENT_THRESHOLD,
    AdversarialFinding,
    Vote,
    aggregate_votes,
    classify_finding,
    is_consensus_reached,
)


class TestNVoteThreshold:
    def test_default_threshold_60pct(self):
        assert DEFAULT_AGREEMENT_THRESHOLD == 0.6

    def test_unanimous_passes(self):
        votes = [Vote(agent_id=f"a{i}", decision="approve") for i in range(5)]
        result = aggregate_votes(votes)
        assert result.threshold_met is True
        assert result.winning_decision == "approve"
        assert result.agreement_ratio == 1.0

    def test_4_of_5_passes_default(self):
        votes = [Vote(agent_id=f"a{i}", decision="approve") for i in range(4)]
        votes.append(Vote(agent_id="a5", decision="reject"))
        result = aggregate_votes(votes)
        assert result.threshold_met is True
        assert result.winning_decision == "approve"

    def test_3_of_5_passes_default(self):
        # 60% threshold = 3 of 5 = 정확히 통과
        votes = [Vote(agent_id=f"a{i}", decision="approve") for i in range(3)]
        votes += [Vote(agent_id=f"r{i}", decision="reject") for i in range(2)]
        result = aggregate_votes(votes)
        assert result.threshold_met is True

    def test_2_of_5_fails(self):
        votes = [Vote(agent_id=f"a{i}", decision="approve") for i in range(2)]
        votes += [Vote(agent_id=f"r{i}", decision="reject") for i in range(3)]
        result = aggregate_votes(votes)
        assert result.threshold_met is True  # reject = 3 of 5 = 60%
        assert result.winning_decision == "reject"

    def test_split_3_2_no_consensus_at_higher_threshold(self):
        votes = [Vote(agent_id=f"a{i}", decision="approve") for i in range(3)]
        votes += [Vote(agent_id=f"r{i}", decision="reject") for i in range(2)]
        result = aggregate_votes(votes, threshold=0.8)  # 4 of 5 필요
        assert result.threshold_met is False
        assert result.winning_decision is None
        assert "사람 큐" in result.note


class TestNVoteEmptyAndEdge:
    def test_empty_votes_returns_human_queue(self):
        result = aggregate_votes([])
        assert result.threshold_met is False
        assert result.winning_decision is None
        assert "사람 큐" in result.note

    def test_single_vote_passes(self):
        result = aggregate_votes([Vote(agent_id="a", decision="x")])
        assert result.threshold_met is True
        assert result.agreement_ratio == 1.0


class TestNVoteHelper:
    def test_is_consensus_reached_true(self):
        votes = [Vote(agent_id=f"a{i}", decision="ok") for i in range(5)]
        assert is_consensus_reached(votes) is True

    def test_is_consensus_reached_false_strict(self):
        votes = [Vote(agent_id="a", decision="x"), Vote(agent_id="b", decision="y")]
        assert is_consensus_reached(votes, threshold=0.8) is False


class TestNVoteToDict:
    def test_vote_to_dict(self):
        v = Vote(agent_id="haiku-1", decision="refund_50000", confidence=0.9, rationale="...")
        d = v.to_dict()
        assert d["agent_id"] == "haiku-1"
        assert d["decision"] == "refund_50000"
        assert d["confidence"] == 0.9

    def test_result_to_dict_complete(self):
        votes = [Vote(agent_id=f"a{i}", decision="ok") for i in range(3)]
        d = aggregate_votes(votes).to_dict()
        for k in (
            "total_votes",
            "winning_decision",
            "agreement_ratio",
            "threshold_met",
            "distribution",
            "note",
        ):
            assert k in d


class TestAdversarial:
    def test_daily_cap_50(self):
        assert ADVERSARIAL_DAILY_CAP == 50

    def test_finding_frozen(self):
        from dataclasses import FrozenInstanceError

        f = AdversarialFinding(
            finding_kind="injection",
            severity="critical",
            target_module="src/kormarc_auto/api/aggregator.py",
            repro_steps="...",
        )
        with pytest.raises(FrozenInstanceError):
            f.severity = "low"  # type: ignore[misc]


class TestClassifyFinding:
    def test_sql_injection(self):
        assert classify_finding("SQL injection in search query") == "injection"

    def test_korean_auth_bypass(self):
        assert classify_finding("인증 우회 가능") == "auth_bypass"

    def test_race_condition(self):
        assert classify_finding("race condition in concurrent writes") == "race_condition"

    def test_korean_data_leak(self):
        assert classify_finding("자관 식별자 누설") == "data_leak"

    def test_crypto_weak(self):
        assert classify_finding("MD5 hash used for password") == "crypto_weakness"

    def test_default_logic_flaw(self):
        assert classify_finding("이상한 동작") == "logic_flaw"


class TestPaymentScenario:
    """V2 §3.2 정합·결제 환불 N-Vote 시나리오."""

    def test_refund_4_of_5_approved(self):
        # 4 agent = 환불 50,000원 합의·1 agent = 거부
        votes = [
            Vote(agent_id=f"haiku-{i}", decision="refund_50000", confidence=0.9) for i in range(4)
        ]
        votes.append(Vote(agent_id="haiku-5", decision="reject", confidence=0.7))
        result = aggregate_votes(votes, threshold=0.8)
        # 4/5 = 80% = 임계 충족
        assert result.threshold_met is True
        assert result.winning_decision == "refund_50000"

    def test_refund_split_goes_to_human(self):
        votes = [
            Vote(agent_id="a1", decision="refund_50000"),
            Vote(agent_id="a2", decision="refund_30000"),
            Vote(agent_id="a3", decision="reject"),
        ]
        result = aggregate_votes(votes, threshold=0.6)
        # 1/3 = 33% < 60% = 사람 큐
        assert result.threshold_met is False
        assert "사람 큐" in result.note
