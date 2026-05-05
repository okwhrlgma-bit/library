"""Cycle 15A P20 — KWCAG 2.2 + KRDS 회귀."""

from __future__ import annotations

from kormarc_auto.a11y import (
    KRDS_COLOR_TOKENS,
    KWCAG_PRINCIPLES,
    PRETENDARD_CDN_URL,
    audit_html,
    audit_kwcag22_text_content,
    color_contrast_ratio,
    color_meaning_matrix,
    is_korean_lang_attr_present,
    pretendard_link_tag,
)


class TestPrinciples:
    def test_4_principles(self):
        assert KWCAG_PRINCIPLES == ("인식", "운용", "이해", "견고")


class TestColorContrast:
    def test_black_on_white_max_contrast(self):
        # 21:1 (최대)
        assert color_contrast_ratio("#000000", "#ffffff") >= 20.0

    def test_white_on_white_min_contrast(self):
        assert color_contrast_ratio("#ffffff", "#ffffff") == 1.0

    def test_aa_normal_text_4_5_ratio(self):
        # KRDS gray_90 vs white = 본문 텍스트 대비 (≥ 4.5:1)
        assert color_contrast_ratio(KRDS_COLOR_TOKENS["gray_90"], "#ffffff") >= 4.5

    def test_korea_blue_on_white(self):
        # primary CTA = 4.5:1 이상
        assert color_contrast_ratio(KRDS_COLOR_TOKENS["korea_blue_60"], "#ffffff") >= 4.5

    def test_invalid_hex_raises(self):
        import pytest

        with pytest.raises(ValueError):
            color_contrast_ratio("#abc", "#ffffff")


class TestKoreanLangDetection:
    def test_html_lang_ko(self):
        assert is_korean_lang_attr_present('<html lang="ko">') is True

    def test_html_lang_ko_uppercase(self):
        assert is_korean_lang_attr_present('<HTML LANG="ko">') is True

    def test_html_lang_en_no(self):
        assert is_korean_lang_attr_present('<html lang="en">') is False

    def test_no_lang_attr_no(self):
        assert is_korean_lang_attr_present("<html>") is False


class TestHtmlAudit:
    def _good_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="ko">
<head><title>좋은 페이지</title></head>
<body>
<h1>제목</h1>
<img src="x.jpg" alt="설명">
<form><label for="email">이메일</label><input id="email" type="email"></form>
<table><caption>표 제목</caption><tr><th scope="col">A</th></tr></table>
</body></html>"""

    def _bad_html(self) -> str:
        return """<!DOCTYPE html>
<html>
<body>
<img src="x.jpg">
<form><input type="email" name="email"></form>
<table><tr><td>A</td></tr></table>
</body></html>"""

    def test_good_html_passing(self):
        report = audit_html(self._good_html())
        assert report.is_passing is True
        assert report.critical_count == 0

    def test_bad_html_critical(self):
        report = audit_html(self._bad_html())
        assert report.is_passing is False
        assert report.critical_count >= 2  # 최소 alt + label

    def test_lang_missing_critical(self):
        report = audit_html("<html><body><h1>x</h1></body></html>")
        codes = [i.code for i in report.issues]
        assert any("3.1.1" in c for c in codes)

    def test_h1_missing_major(self):
        html = '<html lang="ko"><body><p>no heading</p></body></html>'
        report = audit_html(html)
        assert any(i.code.startswith("1.3.1") and "헤딩" in i.code for i in report.issues)

    def test_multiple_h1_minor(self):
        html = '<html lang="ko"><body><h1>A</h1><h1>B</h1></body></html>'
        report = audit_html(html)
        assert any(i.severity == "minor" for i in report.issues)

    def test_api_dict_complete(self):
        report = audit_html(self._good_html())
        d = report.to_api_dict()
        assert "is_passing" in d
        assert "critical_count" in d
        assert "issues" in d


class TestTextContentAudit:
    def test_time_limit_warning(self):
        text = "30초 내 자동 로그아웃됩니다"
        issues = audit_kwcag22_text_content(text)
        assert any("2.2.1" in i.code for i in issues)

    def test_no_issue_for_safe_text(self):
        text = "환영합니다·KORMARC 자동 생성"
        assert audit_kwcag22_text_content(text) == []


class TestKRDS:
    def test_pretendard_cdn_url(self):
        assert PRETENDARD_CDN_URL.startswith("https://")
        assert "pretendard" in PRETENDARD_CDN_URL.lower()

    def test_pretendard_link_tag(self):
        tag = pretendard_link_tag()
        assert "<link" in tag
        assert "stylesheet" in tag
        assert "pretendard" in tag.lower()

    def test_color_tokens_complete(self):
        for key in (
            "korea_blue_60",
            "amber_50",
            "green_50",
            "red_50",
            "gray_90",
            "gray_5",
            "white",
        ):
            assert key in KRDS_COLOR_TOKENS
            assert KRDS_COLOR_TOKENS[key].startswith("#")

    def test_color_meaning_matrix_3_categories(self):
        m = color_meaning_matrix()
        assert set(m.keys()) == {"확실", "검토 필요", "불확실"}
        for cat, info in m.items():
            assert info["color"].startswith("#")
            assert info["icon"]
            assert info["korean"] == cat

    def test_color_meaning_no_color_only_dependency(self):
        # KWCAG 1.4.1 = 색상만으로 정보 전달 X·아이콘 + 텍스트 동시
        for info in color_meaning_matrix().values():
            assert info["icon"] != ""
            assert info["korean"] != ""
