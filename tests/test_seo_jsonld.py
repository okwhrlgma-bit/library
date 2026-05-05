"""Cycle 15B P35 — SEO + JSON-LD + FAQ + llms.txt 회귀."""

from __future__ import annotations

import json

from kormarc_auto.seo import (
    build_faqpage_jsonld,
    build_llms_txt,
    build_og_tags,
    build_organization_jsonld,
    build_robots_txt,
    build_softwareapplication_jsonld,
    librarian_faq_10,
    librarian_top_10_keywords,
    naver_search_keywords_density,
)


class TestSoftwareApplicationJsonLd:
    def test_5_offers_present(self):
        d = build_softwareapplication_jsonld()
        assert d["@type"] == "SoftwareApplication"
        assert len(d["offers"]) == 5

    def test_krw_currency_in_all_offers(self):
        d = build_softwareapplication_jsonld()
        for o in d["offers"]:
            assert o["priceCurrency"] == "KRW"

    def test_in_language_ko(self):
        d = build_softwareapplication_jsonld()
        assert d["inLanguage"] == "ko"

    def test_application_category_business(self):
        d = build_softwareapplication_jsonld()
        assert d["applicationCategory"] == "BusinessApplication"
        assert "Library" in d["applicationSubCategory"]

    def test_jsonld_serializable(self):
        d = build_softwareapplication_jsonld()
        json.dumps(d, ensure_ascii=False)  # must not raise


class TestFAQPage:
    def test_10_faqs(self):
        assert len(librarian_faq_10()) == 10

    def test_kolas3_in_faq(self):
        faqs = librarian_faq_10()
        joined = " ".join(f["question"] + f["answer"] for f in faqs)
        assert "KOLAS III" in joined
        assert "2026년 12월 31일" in joined or "2026-12-31" in joined

    def test_dls_in_faq(self):
        faqs = librarian_faq_10()
        joined = " ".join(f["question"] + f["answer"] for f in faqs)
        assert "DLS" in joined or "독서로" in joined

    def test_880_hanja_in_faq(self):
        faqs = librarian_faq_10()
        joined = " ".join(f["question"] + f["answer"] for f in faqs)
        assert "880" in joined or "한자" in joined

    def test_faqpage_jsonld_structure(self):
        d = build_faqpage_jsonld()
        assert d["@type"] == "FAQPage"
        assert len(d["mainEntity"]) == 10
        for entry in d["mainEntity"]:
            assert entry["@type"] == "Question"
            assert entry["acceptedAnswer"]["@type"] == "Answer"


class TestOrganization:
    def test_includes_same_as(self):
        d = build_organization_jsonld()
        assert "sameAs" in d
        assert len(d["sameAs"]) >= 1

    def test_inLanguage_ko(self):
        d = build_organization_jsonld()
        assert d["inLanguage"] == "ko"


class TestOgTags:
    def test_og_locale_ko_KR_required(self):
        tags = build_og_tags(title="X", description="Y", url="https://example.com")
        assert "ko_KR" in tags

    def test_canonical_present(self):
        tags = build_og_tags(title="X", description="Y", url="https://example.com")
        assert 'rel="canonical"' in tags

    def test_og_image_optional(self):
        tags_with = build_og_tags(
            title="X",
            description="Y",
            url="https://example.com",
            image_url="https://example.com/i.png",
        )
        tags_without = build_og_tags(title="X", description="Y", url="https://example.com")
        assert "og:image" in tags_with
        assert "og:image" not in tags_without


class TestRobotsTxt:
    def test_yeti_naver_allowed(self):
        rb = build_robots_txt()
        assert "Yeti" in rb
        assert "Allow: /" in rb

    def test_ai_bots_allowed_default(self):
        rb = build_robots_txt()
        # 외부 보고서 P35 게이트 = AI 봇 차단 시 STOP
        assert "GPTBot" in rb
        assert "ClaudeBot" in rb
        assert "PerplexityBot" in rb

    def test_ai_bots_can_be_disabled(self):
        rb = build_robots_txt(allow_ai_bots=False)
        assert "GPTBot" not in rb

    def test_sitemap_present(self):
        assert "Sitemap:" in build_robots_txt()


class TestKeywords:
    def test_10_keywords(self):
        kws = librarian_top_10_keywords()
        assert len(kws) == 10

    def test_kolas3_keywords_present(self):
        joined = " ".join(str(k["keyword"]) for k in librarian_top_10_keywords())
        assert "KOLAS III 종료" in joined or "KOLAS III 마이그레이션" in joined

    def test_density_counts(self):
        text = "KORMARC 자동 생성 도구 = 사서 마크 자동화 핵심"
        counts = naver_search_keywords_density(text)
        assert counts["KORMARC 자동 생성"] == 1
        assert counts["사서 마크 자동화"] == 1


class TestLlmsTxt:
    def test_includes_kolas3_facts(self):
        txt = build_llms_txt()
        assert "2026-12-31" in txt
        assert "KOLAS III" in txt

    def test_includes_4_official_successors(self):
        txt = build_llms_txt()
        for s in ("코라스Ⅲ 확장형", "알파스", "K-LAS 3.0", "KOLAS-WEB"):
            assert s in txt

    def test_includes_pricing(self):
        txt = build_llms_txt()
        assert "30,000" in txt or "₩30,000" in txt
        assert "150,000" in txt or "₩150,000" in txt

    def test_includes_pipa_mention(self):
        txt = build_llms_txt()
        assert "PIPA" in txt or "§28의8" in txt

    def test_no_pii_leak(self):
        txt = build_llms_txt()
        for forbidden in ("내를건너서", "내건숲", "은평구공공", "okwhrlgma"):
            assert forbidden not in txt
