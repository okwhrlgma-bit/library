"""장서 점검 (inventory.inspection) 단위 테스트.

OCR/Vision 모듈은 mock — 외부 모델 의존 없이 로직만 검증.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.inventory import inspection  # noqa: E402


def test_call_number_pattern_basic():
    """KDC + 저자기호 패턴 매칭."""
    text = "813.7 한31ㅈ"
    matches = inspection._CALL_NUMBER_PATTERN.findall(text)
    assert matches, "기본 청구기호가 매칭되어야 함"


def test_call_number_pattern_with_volume():
    text = "911.05 김12ㅎ c.2 v.3"
    m = inspection._CALL_NUMBER_PATTERN.search(text)
    assert m is not None
    assert "911.05" in m.group(0)


def test_extract_no_ocr_returns_empty(monkeypatch):
    """OCR 모듈이 없으면 빈 리스트."""
    # vision.ocr import를 강제 실패시킴
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name == "kormarc_auto.vision.ocr":
            raise ImportError("simulated")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = inspection.extract_call_numbers_from_image("dummy.jpg")
    assert result == []


def test_compare_with_inventory_no_db(tmp_path, monkeypatch):
    """자관 DB가 비었을 때 모든 청구기호가 missing_in_db."""
    monkeypatch.setenv("KORMARC_LIBRARY_INDEX", str(tmp_path / "idx.jsonl"))
    result = inspection.compare_with_inventory(["813.7 한31ㅈ", "911 김12ㅇ"])
    assert result["detected_count"] == 2
    assert len(result["missing_in_db"]) == 2
    assert result["matched"] == []
    assert result["summary"]["missing_pct"] == 100.0


def test_compare_missorted(tmp_path, monkeypatch):
    """KDC 범위 밖이면 missorted로 분류 — DB에 등록되어 있을 때."""
    monkeypatch.setenv("KORMARC_LIBRARY_INDEX", str(tmp_path / "idx.jsonl"))
    from kormarc_auto.inventory import library_db

    library_db.add_record(
        {
            "isbn": "9788936434120",
            "title": "테스트",
            "author": "한강",
            "kdc": "813.7",
            "call_number": "813.7 한31ㅈ",
        }
    )
    result = inspection.compare_with_inventory(
        ["813.7 한31ㅈ"],
        expected_kdc_range=("000", "100"),
    )
    # 등록된 항목이지만 범위 밖 → missorted
    assert "813.7 한31ㅈ" in result["missorted"]


def test_normalize_call_number_basic():
    """공백·권차·복본 제거 + 기본 정규화."""
    assert inspection.normalize_call_number("813.7 한31ㅈ") == "813.7한31ㅈ"
    assert inspection.normalize_call_number("813.7 한31ㅈ c.2") == "813.7한31ㅈ"
    assert inspection.normalize_call_number("813.7 한31ㅈ v.3") == "813.7한31ㅈ"


def test_normalize_call_number_ocr_fixes():
    """OCR 흔한 오인식 보정 — 'O'→'0', 'l'→'1' (앞 6자 한정)."""
    # 'O' → '0'
    assert inspection.normalize_call_number("8O3.7") == "803.7"
    # 'l' → '1'
    assert inspection.normalize_call_number("8l3.7") == "813.7"
    # 7자 이후는 한글 영역이라 보정 안 됨
    assert "ㅈ" in inspection.normalize_call_number("813.7 한31ㅈ")


def test_normalize_empty():
    assert inspection.normalize_call_number("") == ""
    assert inspection.normalize_call_number("   ") == ""


def test_write_inspection_csv(tmp_path):
    result = {
        "matched": ["813.7 한31ㅈ"],
        "missorted": ["911 김12ㅎ"],
        "missing_in_db": ["005.13 박22ㅍ"],
        "warnings": ["테스트 경고"],
    }
    out = inspection.write_inspection_csv(result, output_path=tmp_path / "out.csv")
    text = out.read_text(encoding="utf-8-sig")
    assert "category" in text
    assert "813.7 한31ㅈ" in text
    assert "오배가" in text
    assert "테스트 경고" in text


def test_inspection_result_to_csv_bytes():
    result = {"matched": ["A"], "missorted": [], "missing_in_db": ["B"], "warnings": []}
    data = inspection.inspection_result_to_csv_bytes(result)
    text = data.decode("utf-8-sig")
    assert "일치" in text
    assert "미등록" in text


def test_inspect_shelf_images_aggregates(monkeypatch, tmp_path):
    """여러 이미지의 청구기호를 합치고 dedup."""
    monkeypatch.setenv("KORMARC_LIBRARY_INDEX", str(tmp_path / "idx.jsonl"))

    def fake_extract(path):
        return {"a.jpg": ["813.7 한31ㅈ"], "b.jpg": ["813.7 한31ㅈ", "911 김12ㅇ"]}.get(
            Path(path).name, []
        )

    with patch.object(inspection, "extract_call_numbers_from_image", fake_extract):
        result = inspection.inspect_shelf_images(["a.jpg", "b.jpg"])

    assert result["detected_count"] == 2  # dedup
    assert len(result["per_image"]) == 2
