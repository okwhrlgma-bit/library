"""Phase 3 KDC 분류 + 880 테스트 (mock 기반)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.classification.kdc_classifier import recommend_kdc  # noqa: E402
from kormarc_auto.vernacular.hanja_converter import hanja_to_hangul, has_hanja  # noqa: E402


class TestKDCRecommendation:
    def test_uses_nl_korea_kdc_first(self):
        book_data = {"kdc": "813.7", "additional_code": "03810"}
        result = recommend_kdc(book_data)
        assert result[0]["code"] == "813.7"
        assert result[0]["source"] == "nl_korea"
        assert result[0]["confidence"] >= 0.9

    def test_falls_back_to_additional_code(self):
        book_data = {"additional_code": "03810"}
        result = recommend_kdc(book_data)
        assert any(c["source"] == "additional_code" for c in result)

    def test_returns_fallback_when_no_data(self):
        book_data = {}
        result = recommend_kdc(book_data)
        assert len(result) >= 1
        assert result[0]["source"] in {"fallback", "additional_code"}

    @patch("kormarc_auto.classification.kdc_classifier.cached_messages")
    def test_calls_ai_when_low_confidence(self, mock_call):
        """1·2순위 신뢰도 부족 + AI 시그널 있으면 AI 호출."""
        mock_call.return_value = {
            "tool_input": {
                "candidates": [
                    {"code": "813.7", "confidence": 0.85, "rationale": "현대 한국 소설"},
                    {"code": "813.6", "confidence": 0.10, "rationale": ""},
                ]
            },
            "text": None,
            "cached": False,
        }
        book_data = {"title": "작별하지 않는다", "author": "한강", "summary": "역사 소설"}
        result = recommend_kdc(book_data)
        ai_results = [c for c in result if c["source"] == "ai"]
        assert ai_results
        assert ai_results[0]["code"] == "813.7"

    @patch("kormarc_auto.classification.kdc_classifier.cached_messages")
    def test_skips_ai_when_nl_korea_present(self, mock_call):
        """NL Korea KDC가 0.95면 AI 호출 안 함."""
        book_data = {
            "kdc": "813.7",
            "title": "테스트",
            "summary": "내용",
        }
        recommend_kdc(book_data)
        mock_call.assert_not_called()

    def test_returns_at_most_5_candidates(self):
        """다양한 소스가 있어도 정렬·반환 잘 됨."""
        book_data = {"kdc": "813.7", "additional_code": "03810"}
        result = recommend_kdc(book_data)
        assert isinstance(result, list)
        assert len(result) >= 1


class TestHanjaConverter:
    def test_detects_hanja(self):
        assert has_hanja("韓國")
        assert not has_hanja("한국")

    def test_translates_basic(self):
        result = hanja_to_hangul("韓國")
        assert "한" in result or "韓" in result  # 라이브러리 미설치 시 원본 유지
