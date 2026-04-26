"""MARC21 동아시아 변환 단위 테스트 (inactive 모듈)."""

from __future__ import annotations

import pytest

from kormarc_auto.conversion.marc21_east_asian import (
    ACTIVATED,
    kormarc_to_marc21_east_asian,
    split_260_to_264,
    transform_field_245_to_marc21_rda,
)


def test_inactive_by_default():
    """기본 비활성. 호출 시 RuntimeError."""
    assert ACTIVATED is False
    with pytest.raises(RuntimeError, match="inactive"):
        kormarc_to_marc21_east_asian({"fields": []})


def test_split_260_to_264_publication():
    f = {
        "tag": "260",
        "indicators": [" ", " "],
        "subfields": [
            {"code": "a", "value": "서울"},
            {"code": "b", "value": "문학동네"},
            {"code": "c", "value": "2026"},
        ],
    }
    out = split_260_to_264(f)
    assert len(out) == 1
    assert out[0]["tag"] == "264"
    assert out[0]["indicators"] == [" ", "1"]
    assert out[0]["subfields"] == f["subfields"]


def test_transform_245_drops_h():
    f = {
        "tag": "245",
        "indicators": ["1", "0"],
        "subfields": [
            {"code": "a", "value": "작별하지 않는다"},
            {"code": "h", "value": "[활자대장본]"},
            {"code": "c", "value": "한강 지음"},
        ],
    }
    out = transform_field_245_to_marc21_rda(f)
    codes = [sf["code"] for sf in out["subfields"]]
    assert "h" not in codes
    assert "a" in codes
    assert "c" in codes
