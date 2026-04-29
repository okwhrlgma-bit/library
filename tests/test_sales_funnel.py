"""영업 funnel tracker 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sales_funnel  # noqa: E402


def test_empty_funnel_returns_zeros():
    metrics = sales_funnel.compute_funnel([], [])
    assert metrics.signups == 0
    assert metrics.activated == 0
    assert metrics.activation_rate_pct == 0.0
    assert metrics.end_to_end_pct == 0.0


def test_full_funnel_calculation():
    """5명 가입·4명 활성·2명 한도 도달·1명 결제 → end-to-end 20%."""
    signups = [
        {"api_key": f"key_{i}", "library_name": f"lib_{i}", "is_paid": i == 0}
        for i in range(5)
    ]
    usage = [
        # 4명 활성 (key_0~3 모두 1건 이상 사용)
        {"api_key": "key_0", "records": 60},  # 한도 도달
        {"api_key": "key_1", "records": 55},  # 한도 도달
        {"api_key": "key_2", "records": 30},  # 활성 but 한도 미도달
        {"api_key": "key_3", "records": 10},
        # key_4는 가입만, 사용 X
    ]
    metrics = sales_funnel.compute_funnel(signups, usage, free_quota=50)
    assert metrics.signups == 5
    assert metrics.activated == 4
    assert metrics.free_quota_used == 2
    assert metrics.paid == 1
    assert metrics.activation_rate_pct == 80.0
    assert metrics.quota_exhaust_rate_pct == 50.0
    assert metrics.paid_conversion_rate_pct == 50.0
    assert metrics.end_to_end_pct == 20.0


def test_unsigned_usage_ignored():
    """signup 안 한 키의 usage는 무시."""
    signups = [{"api_key": "key_a"}]
    usage = [
        {"api_key": "key_a", "records": 100},
        {"api_key": "stranger", "records": 200},  # signup 없음 → 무시
    ]
    metrics = sales_funnel.compute_funnel(signups, usage, free_quota=50)
    assert metrics.signups == 1
    assert metrics.activated == 1
    assert metrics.free_quota_used == 1


def test_render_summary_includes_decision():
    """activation_rate < 50% → onboarding 강화 권고 포함."""
    signups = [{"api_key": f"k{i}"} for i in range(10)]
    usage = [{"api_key": "k0", "records": 5}]  # 1/10 = 10%
    metrics = sales_funnel.compute_funnel(signups, usage)
    summary = sales_funnel.render_summary(metrics)
    assert "활성률 < 50%" in summary
    assert "onboarding" in summary


def test_metrics_to_dict_serializable():
    import json
    signups = [{"api_key": "k1", "is_paid": True}]
    usage = [{"api_key": "k1", "records": 60}]
    metrics = sales_funnel.compute_funnel(signups, usage)
    d = metrics.to_dict()
    serialized = json.dumps(d)
    assert "signups" in serialized
    assert "end_to_end_pct" in serialized
