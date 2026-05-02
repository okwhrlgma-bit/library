"""aggregate_interviews.by_persona — 4 페르소나 분석 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import aggregate_interviews  # noqa: E402


def _make(
    persona: str,
    nps: int,
    time_saved: float = 75.0,
    q1: str = "HIGH",
    quote: bool = True,
    label: str = "?",
) -> dict:
    return {
        "persona": persona,
        "persona_label": label,
        "nps": nps,
        "time_saved_pct": time_saved,
        "q1_payment_band": q1,
        "consent_kla_quote": quote,
        "library_type": "public",
    }


def test_by_persona_groups_correctly():
    interviews = [
        _make("macro", 9, label="매크로"),
        _make("macro", 8, label="매크로"),
        _make("acquisition", 7, label="수서"),
        _make("general", 5, label="종합"),
    ]
    result = aggregate_interviews.by_persona(interviews)
    assert result["macro"]["count"] == 2
    assert result["acquisition"]["count"] == 1
    assert result["general"]["count"] == 1


def test_by_persona_nps_average():
    interviews = [
        _make("macro", 10),
        _make("macro", 0),
    ]
    result = aggregate_interviews.by_persona(interviews)
    # 1 promoter (10) + 1 detractor (0) → NPS 0
    assert result["macro"]["nps"]["score"] == 0


def test_by_persona_time_saved_average():
    interviews = [
        _make("macro", 9, time_saved=70.0),
        _make("macro", 9, time_saved=80.0),
    ]
    result = aggregate_interviews.by_persona(interviews)
    assert result["macro"]["avg_time_saved_pct"] == 75.0


def test_by_persona_kla_quotable_filtered():
    """consent_kla_quote=False는 KLA 인용 가능 카운트 제외."""
    interviews = [
        _make("macro", 9, quote=True),
        _make("macro", 8, quote=False),
        _make("macro", 7, quote=True),
    ]
    result = aggregate_interviews.by_persona(interviews)
    assert result["macro"]["kla_quotable_count"] == 2


def test_by_persona_q1_distribution():
    interviews = [
        _make("acquisition", 9, q1="HIGH"),
        _make("acquisition", 8, q1="HIGH"),
        _make("acquisition", 6, q1="MID"),
    ]
    result = aggregate_interviews.by_persona(interviews)
    q1 = result["acquisition"]["q1_distribution"]
    assert q1["HIGH"] == 2
    assert q1["MID"] == 1


def test_by_persona_empty_returns_empty():
    assert aggregate_interviews.by_persona([]) == {}
