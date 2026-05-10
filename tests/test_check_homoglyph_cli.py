"""Cycle 518 — check_homoglyph.py CLI 테스트 (#15 V01·sanity-check 통합 시드)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import check_homoglyph as cli  # noqa: E402


class TestParseKvArgs:
    def test_basic(self) -> None:
        record = cli.parse_kv_args(["245=홍길동전", "100=허균"])
        assert record == {"245": "홍길동전", "100": "허균"}

    def test_empty(self) -> None:
        assert cli.parse_kv_args([]) == {}

    def test_skips_invalid(self) -> None:
        record = cli.parse_kv_args(["245=홍길동전", "invalid"])
        assert record == {"245": "홍길동전"}

    def test_strip_whitespace(self) -> None:
        record = cli.parse_kv_args([" 245 = 홍길동전 "])
        assert record == {"245": "홍길동전"}


class TestMainKv:
    def test_clean_record_zero_exit(self, capsys) -> None:
        rc = cli.main(["245=홍길동전"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "✅" in captured.out
        assert "정상" in captured.out

    def test_blocked_record(self, capsys) -> None:
        rc = cli.main(["245=Kореа"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "🔴" in captured.out
        assert "고위험" in captured.out


class TestMainJson:
    def test_json_input(self, capsys, tmp_path: Path) -> None:
        f = tmp_path / "record.json"
        f.write_text(json.dumps({"245": "홍길동전"}, ensure_ascii=False), encoding="utf-8")
        rc = cli.main(["--json", str(f)])
        captured = capsys.readouterr()
        assert rc == 0
        assert "✅" in captured.out
