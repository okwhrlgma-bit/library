"""인터뷰 누적 분석 단위 테스트."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "aggregate_interviews", ROOT / "scripts" / "aggregate_interviews.py"
)
assert _spec and _spec.loader
ai = importlib.util.module_from_spec(_spec)
sys.modules["aggregate_interviews"] = ai
_spec.loader.exec_module(ai)


def test_nps_promoter_only():
    interviews = [{"nps": 9}, {"nps": 10}, {"nps": 9}]
    s = ai.nps_score(interviews)
    assert s["score"] == 100.0
    assert s["promoters"] == 3


def test_nps_mixed():
    interviews = [{"nps": 10}, {"nps": 7}, {"nps": 5}]
    s = ai.nps_score(interviews)
    assert s["promoters"] == 1
    assert s["passives"] == 1
    assert s["detractors"] == 1
    assert s["score"] == 0.0


def test_nps_empty():
    s = ai.nps_score([])
    assert s["score"] is None
    assert s["n"] == 0


def test_painpoint_top():
    interviews = [
        {"biggest_painpoints": ["KDC 분류", "880 한자"]},
        {"biggest_painpoints": ["KDC 분류"]},
        {"biggest_painpoints": ["등록번호"]},
    ]
    top = ai.painpoint_top(interviews, top=2)
    assert top[0] == ("KDC 분류", 2)
    assert ("880 한자", 1) in top or ("등록번호", 1) in top


def test_willingness_distribution():
    interviews = [
        {"willingness_to_pay_monthly_krw_band": "30000-50000"},
        {"willingness_to_pay_monthly_krw_band": "30000-50000"},
        {"willingness_to_pay_monthly_krw_band": "0"},
    ]
    d = ai.willingness_distribution(interviews)
    assert d["30000-50000"] == 2
    assert d["0"] == 1


def test_by_library_type():
    interviews = [
        {"library_type": "small", "nps": 10},
        {"library_type": "small", "nps": 9},
        {"library_type": "school", "nps": 5},
    ]
    by_t = ai.by_library_type(interviews)
    assert by_t["small"]["count"] == 2
    assert by_t["small"]["nps"]["score"] == 100.0
    assert by_t["school"]["count"] == 1


def test_render_summary_empty():
    assert "인터뷰 0건" in ai.render_summary([])


def test_render_summary_with_data():
    interviews = [
        {
            "nps": 10,
            "biggest_painpoints": ["KDC 분류"],
            "willingness_to_pay_monthly_krw_band": "30000-50000",
            "payment_decision_maker": "self",
            "library_type": "small",
            "feature_requests": ["고서 처리"],
        }
    ]
    text = ai.render_summary(interviews)
    assert "n=1" in text
    assert "100.0" in text
    assert "KDC 분류" in text
    assert "30000-50000" in text
    assert "고서 처리" in text
