"""갈래 B Cycle 32 (V2 §3.2) — N-Vote Consensus.

unsafe 작업 = N개 서브에이전트 병렬 → 결과 비교 → 임계 일치 시 채택·아니면 사람 큐.
적용 영역: 결제·삭제·DB schema·이메일 도메인 변경·가격 변경.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

# V2 §3.2 정합·결제·금융 = 0.8 권장 (4 of 5)
DEFAULT_AGREEMENT_THRESHOLD: float = 0.6


@dataclass(frozen=True)
class Vote:
    """1 서브에이전트의 투표."""

    agent_id: str
    decision: str  # 정규화된 결정 (예: "approve"·"reject"·"refund_50000")
    confidence: float = 1.0  # 0.0~1.0
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "decision": self.decision,
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class ConsensusResult:
    """N-Vote 집계 결과."""

    total_votes: int
    winning_decision: str | None  # 임계 미충족 = None (사람 큐)
    agreement_ratio: float  # winning / total
    threshold_met: bool
    distribution: dict[str, int]  # {"approve": 4, "reject": 1}
    note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_votes": self.total_votes,
            "winning_decision": self.winning_decision,
            "agreement_ratio": self.agreement_ratio,
            "threshold_met": self.threshold_met,
            "distribution": self.distribution,
            "note": self.note,
        }


def aggregate_votes(
    votes: list[Vote], *, threshold: float = DEFAULT_AGREEMENT_THRESHOLD
) -> ConsensusResult:
    """투표 집계 → 임계 통과 시 winning·아니면 None (사람 큐)."""
    if not votes:
        return ConsensusResult(
            total_votes=0,
            winning_decision=None,
            agreement_ratio=0.0,
            threshold_met=False,
            distribution={},
            note="투표 0건·사람 큐로",
        )

    counter: Counter[str] = Counter(v.decision for v in votes)
    winning, count = counter.most_common(1)[0]
    ratio = count / len(votes)

    if ratio >= threshold:
        return ConsensusResult(
            total_votes=len(votes),
            winning_decision=winning,
            agreement_ratio=round(ratio, 4),
            threshold_met=True,
            distribution=dict(counter),
            note=f"✓ 합의·{count}/{len(votes)} = {ratio * 100:.0f}% (임계 {threshold * 100:.0f}%)",
        )
    return ConsensusResult(
        total_votes=len(votes),
        winning_decision=None,
        agreement_ratio=round(ratio, 4),
        threshold_met=False,
        distribution=dict(counter),
        note=(
            f"🔴 합의 미달·최다 {count}/{len(votes)} = {ratio * 100:.0f}% < "
            f"{threshold * 100:.0f}%·사람 큐로"
        ),
    )


def is_consensus_reached(
    votes: list[Vote], *, threshold: float = DEFAULT_AGREEMENT_THRESHOLD
) -> bool:
    """짧은 헬퍼·임계 통과 여부만."""
    return aggregate_votes(votes, threshold=threshold).threshold_met
