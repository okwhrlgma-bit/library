"""갈래 B Cycle 16A (P36) — 첫 단락 패러프레이징 강도 측정.

원칙 (외부 보고서 P36 게이트):
- 채널별 첫 단락 30%+ 변형 (네이버 C-Rank 중복 페널티 회피)
- Levenshtein distance ≥ 0.30 = 회귀 통과
- 의미는 보존·표현만 변형 (사실 변경 X)

본 모듈 = 측정만 (실제 변형은 Claude API·외부 LLM 사용).
"""

from __future__ import annotations


def levenshtein_distance(a: str, b: str) -> int:
    """편집 거리 (insertion·deletion·substitution)."""
    if not a:
        return len(b)
    if not b:
        return len(a)

    # space-optimized DP
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def levenshtein_ratio(a: str, b: str) -> float:
    """편집 거리 / max(len(a), len(b))·0.0 = 동일·1.0 = 완전 다름."""
    if not a and not b:
        return 0.0
    max_len = max(len(a), len(b))
    return levenshtein_distance(a, b) / max_len


def measure_paraphrase_strength(original: str, paraphrased: str) -> dict:
    """첫 단락 변형 강도 측정.

    Returns:
        {"distance_ratio": 0.32, "passes_30pct_gate": True, "char_diff": 50, ...}
    """
    ratio = levenshtein_ratio(original, paraphrased)
    return {
        "distance_ratio": round(ratio, 4),
        "passes_30pct_gate": ratio >= 0.30,
        "char_diff": abs(len(paraphrased) - len(original)),
        "original_len": len(original),
        "paraphrased_len": len(paraphrased),
        "channel_recommendation": (
            "OK·네이버 cross-post 안전" if ratio >= 0.30 else "변형 부족·재패러프레이즈 필요"
        ),
    }
