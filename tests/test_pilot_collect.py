"""scripts/pilot_collect.py 모듈 테스트 (인터랙티브 부분 제외)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# scripts 모듈 import path 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import pilot_collect  # noqa: E402


def test_personas_4_defined():
    """4 페르소나 모두 정의 (macro·acquisition·general·video)."""
    assert set(pilot_collect.PERSONAS.keys()) == {"macro", "acquisition", "general", "video"}
    for data in pilot_collect.PERSONAS.values():
        assert "name" in data
        assert "example" in data
        assert "default_payment_band" in data
        assert "key_painpoints" in data


def test_video_persona_excluded_from_payment():
    """영상 편집 사서는 결제 band 0 (우리 영역 X 명시)."""
    assert pilot_collect.PERSONAS["video"]["default_payment_band"] == "0"


def test_save_creates_file_with_correct_name(tmp_path, monkeypatch):
    """save() → logs/interviews/<date>_<lib>_<librarian>.json."""
    monkeypatch.setattr(pilot_collect, "LOGS_DIR", tmp_path)
    record = {
        "date": "2026-05-12",
        "library_name": "○○도서관",
        "librarian_name": "사서 E",
        "nps": 9,
    }
    path = pilot_collect.save(record)
    assert path.exists()
    assert "2026-05-12" in path.name
    assert "사서" in path.name and "E" in path.name
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["nps"] == 9


def test_save_handles_special_chars_in_library_name(tmp_path, monkeypatch):
    """도서관명에 슬래시·공백 있어도 안전한 파일명."""
    monkeypatch.setattr(pilot_collect, "LOGS_DIR", tmp_path)
    record = {
        "date": "2026-05-12",
        "library_name": "테스트/도서관 분관",
        "librarian_name": "사서 1",
    }
    path = pilot_collect.save(record)
    assert path.exists()
    assert "/" not in path.name
    assert " " not in path.name
