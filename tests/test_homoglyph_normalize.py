"""Cycle 498 — homoglyph 정규화 + 공격 탐지 (#15 opac_homoglyph_norm·founder fit ★★★)."""

from kormarc_auto.text import (
    audit_kormarc_record_homoglyph,
    build_homoglyph_sanity_report_kr,
    contains_zero_width,
    detect_homoglyph_attack,
    normalize_for_search,
    normalize_kormarc_field,
)


class TestNormalizeForSearch:
    def test_empty(self) -> None:
        assert normalize_for_search("") == ""

    def test_pure_korean_unchanged(self) -> None:
        assert normalize_for_search("홍길동") == "홍길동"

    def test_cyrillic_to_latin(self) -> None:
        text = "Kореа"
        result = normalize_for_search(text)
        assert result == "Kopea"

    def test_zero_width_stripped(self) -> None:
        text = "홍길​동"
        assert normalize_for_search(text) == "홍길동"

    def test_nfkc_applied(self) -> None:
        # ① (U+2460) + NFKC = "1" 단순화 안 됨·NFKC = "1"으로 매핑
        text = "①"
        result = normalize_for_search(text)
        assert result == "1"


class TestDetectHomoglyphAttack:
    def test_empty_safe(self) -> None:
        result = detect_homoglyph_attack("")
        assert result["risk_level"] == "none"
        assert result["suspicious_chars"] == []

    def test_clean_korean_no_risk(self) -> None:
        result = detect_homoglyph_attack("홍길동")
        assert result["risk_level"] == "none"
        assert not result["has_homoglyph"]

    def test_low_risk_two_homoglyphs(self) -> None:
        # 키릴 а·о 2개 (3 미만·zero-width 없음 = low)
        result = detect_homoglyph_attack("Kаоre")
        assert result["has_homoglyph"]
        assert result["risk_level"] == "low"
        assert len(result["suspicious_chars"]) == 2

    def test_high_risk_three_plus_homoglyphs(self) -> None:
        # 키릴 а·о·р·е 4개 (3 이상 = high)
        result = detect_homoglyph_attack("Kореа")
        assert result["has_homoglyph"]
        assert result["risk_level"] == "high"

    def test_high_risk_zero_width(self) -> None:
        result = detect_homoglyph_attack("홍​길동")
        assert result["has_zero_width"]
        assert result["risk_level"] == "high"


class TestContainsZeroWidth:
    def test_clean(self) -> None:
        assert not contains_zero_width("정상 텍스트")

    def test_dirty(self) -> None:
        assert contains_zero_width("정상​텍스트")

    def test_empty(self) -> None:
        assert not contains_zero_width("")


class TestAuditKormarcRecordHomoglyph:
    def test_empty_record(self) -> None:
        result = audit_kormarc_record_homoglyph({})
        assert result["summary"] == "all_clean"

    def test_clean_record(self) -> None:
        record = {"245": "홍길동전", "100": "허균"}
        result = audit_kormarc_record_homoglyph(record)
        assert result["summary"] == "all_clean"
        assert result["high_risk_fields"] == []

    def test_warning_low_risk(self) -> None:
        # 키릴 а 1개 (low)
        record = {"245": "Kаrea", "100": "허균"}
        result = audit_kormarc_record_homoglyph(record)
        assert result["summary"] == "warning"
        assert "245" in result["low_risk_fields"]

    def test_blocked_high_risk(self) -> None:
        record = {"245": "홍​길동전"}
        result = audit_kormarc_record_homoglyph(record)
        assert result["summary"] == "blocked"
        assert "245" in result["high_risk_fields"]

    def test_ignores_non_text_fields(self) -> None:
        record = {"008": "abc​def", "245": "홍길동전"}
        result = audit_kormarc_record_homoglyph(record)
        assert result["summary"] == "all_clean"


class TestNormalizeKormarcField:
    def test_clean_text_field(self) -> None:
        result = normalize_kormarc_field("245", "홍길동전")
        assert result["is_text_field"]
        assert not result["should_warn"]
        assert result["normalized"] == "홍길동전"
        assert result["audit"]["risk_level"] == "none"

    def test_homoglyph_text_field_warns(self) -> None:
        result = normalize_kormarc_field("245", "Kореа")
        assert result["is_text_field"]
        assert result["should_warn"]
        assert result["audit"]["risk_level"] == "high"
        assert result["normalized"] == "Kopea"

    def test_non_text_field_passthrough(self) -> None:
        result = normalize_kormarc_field("008", "abc​def")
        assert not result["is_text_field"]
        assert not result["should_warn"]
        assert result["normalized"] == "abc​def"


class TestBuildHomoglyphSanityReportKr:
    def test_empty_record(self) -> None:
        report = build_homoglyph_sanity_report_kr({})
        assert "빈 record" in report

    def test_clean_record(self) -> None:
        report = build_homoglyph_sanity_report_kr({"245": "홍길동전", "100": "허균"})
        assert "✅" in report
        assert "정상" in report

    def test_blocked_record(self) -> None:
        report = build_homoglyph_sanity_report_kr({"245": "홍​길동전"})
        assert "🔴" in report
        assert "고위험" in report

    def test_warning_record(self) -> None:
        report = build_homoglyph_sanity_report_kr({"245": "Kаrea"})
        assert "🟡" in report
        assert "저위험" in report
