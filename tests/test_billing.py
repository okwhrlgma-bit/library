"""월간 청구 + 영수증 단위 테스트."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.server import billing  # noqa: E402


def _seed_log(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def test_aggregate_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(tmp_path / "usage.jsonl"))
    s = billing.aggregate_monthly(2026, 4)
    assert s["total_records"] == 0
    assert s["by_key"] == {}


def test_aggregate_filters_by_month(tmp_path, monkeypatch):
    log_path = tmp_path / "usage.jsonl"
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(log_path))

    import datetime as dt

    apr_ts = int(dt.datetime(2026, 4, 15).timestamp())
    may_ts = int(dt.datetime(2026, 5, 1).timestamp())

    _seed_log(
        log_path,
        [
            {"ts": apr_ts, "key_hash": "k1", "kind": "isbn", "ok": True, "cost_estimate_krw": 100},
            {"ts": apr_ts, "key_hash": "k1", "kind": "isbn", "ok": True, "cost_estimate_krw": 100},
            {"ts": apr_ts, "key_hash": "k2", "kind": "photo", "ok": True, "cost_estimate_krw": 100},
            {"ts": apr_ts, "key_hash": "k2", "kind": "photo", "ok": False, "cost_estimate_krw": 0},
            {"ts": may_ts, "key_hash": "k1", "kind": "isbn", "ok": True, "cost_estimate_krw": 100},
        ],
    )

    s = billing.aggregate_monthly(2026, 4)
    assert s["total_records"] == 3  # 4월에 ok=True 3건, 실패 1건은 제외
    assert s["by_key"]["k1"]["records"] == 2
    assert s["by_key"]["k2"]["records"] == 1
    assert s["by_key"]["k1"]["by_kind"] == {"isbn": 2}
    assert s["by_key"]["k2"]["by_kind"] == {"photo": 1}
    assert s["total_revenue_krw"] == 300


def test_recommend_plan_small_use():
    _, price = billing.recommend_plan(50)
    assert price >= 5000


def test_recommend_plan_high_use():
    name, _ = billing.recommend_plan(800)
    assert "월정액" in name


def test_invoice_json_writes(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(tmp_path / "usage.jsonl"))
    out = billing.write_monthly_invoice_json(
        2026, 4, output_path=tmp_path / "inv.json"
    )
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["year"] == 2026
    assert data["month"] == 4


def test_render_invoice_pdf(tmp_path, monkeypatch):
    pytest.importorskip("reportlab")
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(tmp_path / "usage.jsonl"))

    log_path = tmp_path / "usage.jsonl"
    import datetime as dt

    ts = int(dt.datetime(2026, 4, 15).timestamp())
    _seed_log(
        log_path,
        [{"ts": ts, "key_hash": "demo", "kind": "isbn", "ok": True, "cost_estimate_krw": 100}],
    )

    out = billing.render_invoice_pdf(
        2026, 4,
        library_name="테스트도서관",
        api_key_hash="demo",
        output_path=tmp_path / "rcpt.pdf",
    )
    assert out.exists()
    assert out.read_bytes()[:4] == b"%PDF"
