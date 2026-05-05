"""갈래 B Cycle 32~33 (V2 §3.2·§3.4) — N-Vote Consensus + Adversarial Pair.

V2 §3.2 N-Vote = 결제·삭제·금융 등 unsafe 작업 = N개 병렬 → 다수결 → 임계 미충족 = 사람 큐.
V2 §3.4 Adversarial = Red 공격 + Blue 수비·테스트 커버리지 무한 자성 (일일 50회 캡).

본 모듈 = scaffolding (LLM 호출 자체는 외부 cron·PO Anthropic 키 발급 후).
"""

from kormarc_auto.consensus.adversarial import (
    ADVERSARIAL_DAILY_CAP,
    AdversarialFinding,
    classify_finding,
)
from kormarc_auto.consensus.n_vote import (
    DEFAULT_AGREEMENT_THRESHOLD,
    ConsensusResult,
    Vote,
    aggregate_votes,
    is_consensus_reached,
)

__all__ = [
    "ADVERSARIAL_DAILY_CAP",
    "DEFAULT_AGREEMENT_THRESHOLD",
    "AdversarialFinding",
    "ConsensusResult",
    "Vote",
    "aggregate_votes",
    "classify_finding",
    "is_consensus_reached",
]
