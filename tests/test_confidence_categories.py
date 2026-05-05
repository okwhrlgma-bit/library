"""Cycle 13A P15 — 카테고리형 신뢰 + raw % 폐지 회귀."""

from __future__ import annotations

from kormarc_auto.llm.confidence import (
    calculate_confidence,
    is_raw_percentage_in_text,
)


class TestThreeCategories:
    def test_only_3_categories(self):
        c1 = calculate_confidence(
            {"isbn_grounded": True, "external_api_match": True, "model_self_confidence_high": True}
        )
        c2 = calculate_confidence({"isbn_grounded": True})
        c3 = calculate_confidence({"llm_inferred_only": True})
        assert c1.category in ("확실", "검토 필요", "불확실")
        assert c2.category in ("확실", "검토 필요", "불확실")
        assert c3.category in ("확실", "검토 필요", "불확실")

    def test_high_signals_yields_확실(self):
        c = calculate_confidence(
            {
                "isbn_grounded": True,
                "external_api_match": True,
                "model_self_confidence_high": True,
                "field_rule_based": True,
            }
        )
        assert c.category == "확실"

    def test_partial_signals_yields_검토(self):
        c = calculate_confidence({"isbn_grounded": True, "model_self_confidence_mid": True})
        assert c.category == "검토 필요"

    def test_no_evidence_yields_불확실(self):
        c = calculate_confidence({"llm_inferred_only": True, "ground_truth_unavailable": True})
        assert c.category == "불확실"


class TestTopSignals:
    def test_top_2_returned(self):
        c = calculate_confidence(
            {
                "isbn_grounded": True,
                "external_api_match": True,
                "model_self_confidence_high": True,
                "kdc_authority_match": True,
            }
        )
        assert len(c.top_signals) == 2

    def test_signals_sorted_by_abs_weight(self):
        c = calculate_confidence({"isbn_grounded": True, "vision_ocr_supported": True})
        # isbn_grounded(30) > vision_ocr_supported(10)
        assert c.top_signals[0].code == "isbn_grounded"

    def test_negative_signals_can_appear(self):
        c = calculate_confidence({"llm_inferred_only": True, "vision_ocr_supported": True})
        # llm_inferred_only(-20) abs = 20 > vision(10) abs = 10
        assert c.top_signals[0].code == "llm_inferred_only"

    def test_signals_have_korean_description(self):
        c = calculate_confidence({"isbn_grounded": True})
        assert c.top_signals[0].description == "ISBN 검증 통과"


class TestChipDict:
    def test_no_raw_percentage_in_chip(self):
        c = calculate_confidence({"isbn_grounded": True, "external_api_match": True})
        chip = c.to_chip_dict()
        # 헌법 §2 강화·raw % 노출 금지
        assert "score" not in chip
        assert "probability" not in chip
        assert "%" not in chip["category"]
        # weight는 detail panel용 (UI에 raw % 안 노출)
        assert "category" in chip and "color" in chip and "icon" in chip

    def test_chip_color_mapping(self):
        c = calculate_confidence(
            {
                "isbn_grounded": True,
                "external_api_match": True,
                "model_self_confidence_high": True,
                "field_rule_based": True,
            }
        )
        assert c.to_chip_dict()["color"] == "green"

        c2 = calculate_confidence({"isbn_grounded": True, "model_self_confidence_mid": True})
        assert c2.to_chip_dict()["color"] == "amber"

        c3 = calculate_confidence({"llm_inferred_only": True})
        assert c3.to_chip_dict()["color"] == "red"


class TestRawPercentageDetector:
    def test_detects_92_3_pct(self):
        assert is_raw_percentage_in_text("정합도 92.3% 달성") is True

    def test_detects_87_pct(self):
        assert is_raw_percentage_in_text("정확도 87%") is True

    def test_detects_신뢰도_dot_value(self):
        assert is_raw_percentage_in_text("신뢰도 0.87") is True

    def test_detects_확률(self):
        assert is_raw_percentage_in_text("확률 0.5") is True

    def test_detects_score(self):
        assert is_raw_percentage_in_text("score 0.85") is True

    def test_does_not_flag_year_2026(self):
        # 2026 같은 연도 = % 없으면 무관
        assert is_raw_percentage_in_text("2026년 5월") is False

    def test_does_not_flag_korean_category(self):
        # 헌법 §2 정합 = 카테고리 한국어는 OK
        assert is_raw_percentage_in_text("확실·검토 필요·불확실") is False

    def test_does_not_flag_isbn(self):
        assert is_raw_percentage_in_text("ISBN 9788937437076") is False
