"""ADR 0009 트리거 모니터 단위 테스트."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "aggregate_revenue", ROOT / "scripts" / "aggregate_revenue.py"
)
assert _spec and _spec.loader
ar = importlib.util.module_from_spec(_spec)
sys.modules["aggregate_revenue"] = ar
_spec.loader.exec_module(ar)


def test_beta_librarian_count_dedup(tmp_path, monkeypatch):
    log = tmp_path / "signups.jsonl"
    log.write_text(
        "\n".join(
            [
                json.dumps({"email": "a@x.kr"}),
                json.dumps({"email": "a@x.kr"}),  # 중복
                json.dumps({"email": "b@x.kr"}),
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("KORMARC_SIGNUP_LOG", str(log))
    assert ar.beta_librarian_count() == 2


def test_beta_librarian_count_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_SIGNUP_LOG", str(tmp_path / "missing.jsonl"))
    assert ar.beta_librarian_count() == 0


def test_us_loi_count_active_only(tmp_path, monkeypatch):
    monkeypatch.setattr(ar, "ROOT", tmp_path)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "us_loi.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"library": "Harvard", "status": "active"}),
                json.dumps({"library": "Berkeley", "status": "signed"}),
                json.dumps({"library": "Old", "status": "expired"}),
            ]
        ),
        encoding="utf-8",
    )
    assert ar.us_loi_count() == 2


def test_evaluate_us_trigger_no_data(tmp_path, monkeypatch):
    monkeypatch.setattr(ar, "ROOT", tmp_path)
    monkeypatch.setenv("KORMARC_SIGNUP_LOG", str(tmp_path / "missing.jsonl"))
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(tmp_path / "missing.jsonl"))
    monkeypatch.setenv("KORMARC_USAGE_DB", str(tmp_path / "missing_db.json"))
    r = ar.evaluate_us_trigger()
    assert r["all_triggers_met"] is False
    assert r["beta_librarians"] == 0
    assert r["us_loi"] == 0


def test_sqlite_trigger_below_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(tmp_path / "missing.jsonl"))
    r = ar.evaluate_sqlite_trigger()
    assert r["should_migrate"] is False
    assert r["active_30d"] == 0


def test_sqlite_trigger_above_threshold(tmp_path, monkeypatch):
    log = tmp_path / "usage.jsonl"
    now = int(time.time())
    rows = [
        json.dumps({"ts": now, "key_hash": f"key_{i:03d}", "kind": "isbn", "ok": True})
        for i in range(25)
    ]
    log.write_text("\n".join(rows), encoding="utf-8")
    monkeypatch.setenv("KORMARC_USAGE_LOG", str(log))
    r = ar.evaluate_sqlite_trigger()
    assert r["should_migrate"] is True
    assert r["active_30d"] == 25


def test_render_summary_unmet():
    report = {
        "us_trigger": {
            "evaluated_at": "2026-04-26T00:00:00",
            "kr_consecutive_count": 0,
            "beta_librarians": 5,
            "us_loi": 0,
            "triggers": {
                "kr_revenue_3months": False,
                "beta_librarians_50plus": False,
                "us_loi_1plus": False,
            },
            "all_triggers_met": False,
            "revenues_recent": [],
        },
        "sqlite_trigger": {
            "log_size_mb": 0.5,
            "active_30d": 3,
            "should_migrate": False,
        },
    }
    text = ar.render_summary(report)
    assert "트리거 미충족" in text
    assert "5/50" in text
