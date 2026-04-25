"""로그 회전·익명화 단위 테스트."""

from __future__ import annotations

import gzip
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# scripts/rotate_logs.py 동적 로드
_spec = importlib.util.spec_from_file_location(
    "rotate_logs", ROOT / "scripts" / "rotate_logs.py"
)
assert _spec and _spec.loader
rotate_logs = importlib.util.module_from_spec(_spec)
sys.modules["rotate_logs"] = rotate_logs
_spec.loader.exec_module(rotate_logs)


def _seed(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def test_rotate_archives_old_usage(tmp_path, monkeypatch):
    monkeypatch.setattr(rotate_logs, "LOG_DIR", tmp_path)
    monkeypatch.setattr(rotate_logs, "ARCHIVE_DIR", tmp_path / "archive")

    now = int(time.time())
    old_ts = now - 100 * 86400  # 100일 전
    new_ts = now - 1 * 86400  # 1일 전

    _seed(
        tmp_path / "usage.jsonl",
        [
            {"ts": old_ts, "key_hash": "x", "kind": "isbn", "ok": True},
            {"ts": new_ts, "key_hash": "y", "kind": "isbn", "ok": True},
        ],
    )

    stats = rotate_logs.rotate(max_age_days=90, anon_age_days=365)
    assert stats["archived"] == 1
    assert stats["kept"] == 1

    # 아카이브 .gz 생성 확인
    archives = list((tmp_path / "archive").glob("usage-*.jsonl.gz"))
    assert len(archives) == 1
    with gzip.open(archives[0], "rt", encoding="utf-8") as f:
        archived = [json.loads(line) for line in f]
    assert len(archived) == 1
    assert archived[0]["key_hash"] == "x"

    # 활성 로그에는 새 것만
    remaining = [
        json.loads(line)
        for line in (tmp_path / "usage.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(remaining) == 1
    assert remaining[0]["key_hash"] == "y"


def test_rotate_anonymizes_old_signups(tmp_path, monkeypatch):
    monkeypatch.setattr(rotate_logs, "LOG_DIR", tmp_path)
    monkeypatch.setattr(rotate_logs, "ARCHIVE_DIR", tmp_path / "archive")

    now = int(time.time())
    very_old = now - 400 * 86400

    _seed(
        tmp_path / "signups.jsonl",
        [
            {
                "ts": very_old,
                "email": "librarian@school.kr",
                "library_name": "테스트도서관",
                "key_hash": "abc",
            },
        ],
    )

    stats = rotate_logs.rotate(max_age_days=90, anon_age_days=365)
    assert stats["anonymized"] == 1

    rows = [
        json.loads(line)
        for line in (tmp_path / "signups.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert "email" not in rows[0]
    assert rows[0]["email_domain"] == "school.kr"
    assert "library_name" not in rows[0]


def test_rotate_anonymizes_old_feedback(tmp_path, monkeypatch):
    monkeypatch.setattr(rotate_logs, "LOG_DIR", tmp_path)
    monkeypatch.setattr(rotate_logs, "ARCHIVE_DIR", tmp_path / "archive")

    now = int(time.time())
    very_old = now - 400 * 86400

    _seed(
        tmp_path / "feedback.jsonl",
        [
            {
                "ts": very_old,
                "key_hash": "user_xyz",
                "rating": 5,
                "category": "feature",
                "comment": "ISBN 자동 좋아요",
            },
        ],
    )

    stats = rotate_logs.rotate(max_age_days=90, anon_age_days=365)
    assert stats["anonymized"] == 1
    rows = [
        json.loads(line)
        for line in (tmp_path / "feedback.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows[0]["key_hash"] == "anon"
    assert rows[0]["comment"] == "ISBN 자동 좋아요"  # 코멘트는 보존


def test_dry_run_no_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(rotate_logs, "LOG_DIR", tmp_path)
    monkeypatch.setattr(rotate_logs, "ARCHIVE_DIR", tmp_path / "archive")

    now = int(time.time())
    _seed(
        tmp_path / "usage.jsonl",
        [{"ts": now - 100 * 86400, "key_hash": "x", "kind": "isbn", "ok": True}],
    )
    rotate_logs.rotate(max_age_days=90, dry_run=True)
    # 활성 로그가 변하지 않아야
    assert (tmp_path / "usage.jsonl").read_text(encoding="utf-8").strip() != ""
    assert not (tmp_path / "archive").exists()
