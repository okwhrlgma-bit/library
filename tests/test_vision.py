"""Phase 2 vision 모듈 테스트.

실 anthropic 호출은 mock으로 대체. 실제 이미지·API 호출은 별도 통합 테스트.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.vision import claude_vision  # noqa: E402
from kormarc_auto.vision.barcode import extract_isbn_from_image  # noqa: E402


def test_barcode_returns_none_for_missing_file():
    """존재하지 않는 파일은 None 반환 (예외 발생 X)."""
    result = extract_isbn_from_image("nonexistent.jpg")
    assert result is None


def test_barcode_module_imports():
    """모듈 import 성공만 확인 (실제 인식은 샘플 이미지 필요)."""
    assert callable(extract_isbn_from_image)


def test_extract_isbn_via_vision_no_paths_returns_none():
    """경로 없으면 None."""
    assert claude_vision.extract_isbn_via_vision([]) is None


@patch("kormarc_auto.vision.claude_vision._build_image_blocks")
@patch("kormarc_auto.vision.claude_vision.cached_messages")
def test_extract_isbn_via_vision_parses_tool_input(mock_call, mock_build):
    """tool_use 응답이 정상 ISBN-13이면 추출."""
    mock_build.return_value = ([{"type": "image", "source": {}}], [b"x"])
    mock_call.return_value = {
        "tool_input": {"isbn13": "9788936434120", "found_in": "barcode"},
        "text": None,
        "cached": False,
    }
    result = claude_vision.extract_isbn_via_vision(["fake.jpg"])
    assert result == "9788936434120"


@patch("kormarc_auto.vision.claude_vision._build_image_blocks")
@patch("kormarc_auto.vision.claude_vision.cached_messages")
def test_extract_isbn_via_vision_rejects_invalid(mock_call, mock_build):
    """13자리 아니거나 978/979 아니면 None."""
    mock_build.return_value = ([{"type": "image", "source": {}}], [b"x"])
    mock_call.return_value = {
        "tool_input": {"isbn13": "12345", "found_in": "none"},
        "text": None,
        "cached": False,
    }
    assert claude_vision.extract_isbn_via_vision(["fake.jpg"]) is None


@patch("kormarc_auto.vision.claude_vision._build_image_blocks")
@patch("kormarc_auto.vision.claude_vision.cached_messages")
def test_extract_metadata_returns_book_data_dict(mock_call, mock_build):
    """tool_use 응답을 BookData 호환 dict로 반환."""
    mock_build.return_value = ([{"type": "image", "source": {}}], [b"x"])
    mock_call.return_value = {
        "tool_input": {
            "isbn": "9788936434120",
            "title": "작별하지 않는다",
            "author": "한강",
            "publisher": "창비",
            "publication_year": "2021",
            "warnings": [],
        },
        "text": None,
        "cached": False,
    }
    result = claude_vision.extract_metadata_from_photos(["fake.jpg"])
    assert result["title"] == "작별하지 않는다"
    assert "claude_vision" in result["sources"]
    assert result["confidence"] > 0
    assert "warnings" in result


def test_extract_metadata_no_paths_returns_empty():
    """경로 없으면 빈 결과."""
    result = claude_vision.extract_metadata_from_photos([])
    assert result["sources"] == []
    assert result["confidence"] == 0.0
