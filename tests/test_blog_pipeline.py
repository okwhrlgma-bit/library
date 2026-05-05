"""Cycle 16A P36 — 블로그 파이프라인 회귀."""

from __future__ import annotations

from kormarc_auto.blog_pipeline import (
    BlogPost,
    add_canonical_footer,
    build_canonical_html,
    check_post_facts,
    extract_frontmatter,
    levenshtein_ratio,
    measure_paraphrase_strength,
)


class TestFrontmatter:
    def test_extract_simple(self):
        md = """---
title: Hello
slug: hello
date: 2026-05-06
---

본문 시작.
"""
        fm, body = extract_frontmatter(md)
        assert fm["title"] == "Hello"
        assert fm["slug"] == "hello"
        assert "본문 시작" in body

    def test_no_frontmatter(self):
        md = "# 그냥 본문\n\n내용"
        fm, body = extract_frontmatter(md)
        assert fm == {}
        assert body == md

    def test_tags_list(self):
        md = """---
tags: ["KOLAS3", "마이그레이션"]
---

본문
"""
        fm, _ = extract_frontmatter(md)
        assert fm["tags"] == ["KOLAS3", "마이그레이션"]


class TestCanonical:
    def test_canonical_footer_added(self):
        body = "본문 내용\n\n끝."
        with_footer = add_canonical_footer(body, canonical_url="https://example.com/post")
        assert "원문 출처" in with_footer
        assert "https://example.com/post" in with_footer

    def test_html_includes_canonical_link(self):
        post = BlogPost(
            title="KOLAS III 종료 D-240",
            slug="kolas3-d240",
            body="<p>본문</p>",
            canonical_url="https://example.com/kolas3-d240",
            description="요약",
        )
        html = build_canonical_html(post)
        assert 'rel="canonical"' in html
        assert "https://example.com/kolas3-d240" in html
        assert 'lang="ko"' in html
        assert "ko_KR" in html


class TestParaphrase:
    def test_levenshtein_identical_zero(self):
        assert levenshtein_ratio("hello", "hello") == 0.0

    def test_levenshtein_disjoint_one(self):
        assert levenshtein_ratio("abc", "xyz") == 1.0

    def test_paraphrase_passes_30pct(self):
        original = "KOLAS III 표준형이 2026년 12월 31일에 종료됩니다."
        paraphrased = (
            "공공도서관 자료관리시스템 KOLAS III 표준형 기술 지원이 2026.12.31 자로 마감됩니다."
        )
        result = measure_paraphrase_strength(original, paraphrased)
        assert result["passes_30pct_gate"] is True

    def test_paraphrase_fails_when_too_similar(self):
        original = "KOLAS III 종료 안내"
        paraphrased = "KOLAS III 종료 안내."  # 1 글자 차이
        result = measure_paraphrase_strength(original, paraphrased)
        assert result["passes_30pct_gate"] is False


class TestFactChecker:
    def test_correct_kolas3_date_passes(self):
        text = "KOLAS III 표준형은 2026-12-31 종료됩니다."
        result = check_post_facts(text)
        assert result.is_passing is True

    def test_wrong_date_blocks(self):
        text = "KOLAS III 표준형은 2027-01-01 종료됩니다."
        result = check_post_facts(text)
        assert result.is_passing is False
        assert any("종료일" in i for i in result.issues)

    def test_extension_termination_blocks(self):
        text = "확장형도 종료됩니다."
        result = check_post_facts(text)
        assert result.is_passing is False
        assert any("확장형" in i for i in result.issues)

    def test_correct_extension_separate_track_passes(self):
        text = "표준형만 종료·확장형은 별도 트랙 유지."
        result = check_post_facts(text)
        assert result.is_passing is True

    def test_wrong_successor_count_blocks(self):
        text = "공식 후속 5종이 있습니다."
        result = check_post_facts(text)
        assert result.is_passing is False
        assert any("후속" in i for i in result.issues)

    def test_wrong_library_count_warns(self):
        text = "공공도서관 5,000개"
        result = check_post_facts(text)
        assert result.is_passing is False
        assert any("공공도서관" in i for i in result.issues)
