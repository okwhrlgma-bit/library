"""Cycle 16B P38 — 자치구·교육청 묶음 견적 회귀."""

from __future__ import annotations

from datetime import date

import pytest

from kormarc_auto.sales.bundle_quote import (
    build_procurement_pack_index,
    generate_bundle_quote,
    render_quote_markdown,
)


class TestSimplifiedTaxBlocked:
    def test_simplified_tax_payer_raises(self):
        # STOP 조건 1 (외부 858 출처): 간이과세자 = 학교·공공 거래 차단
        with pytest.raises(ValueError, match="간이과세자"):
            generate_bundle_quote(
                customer_name="X",
                branch_count=5,
                is_simplified_tax_payer=True,
            )

    def test_general_tax_payer_passes(self):
        q = generate_bundle_quote(
            customer_name="자치구청 5개관",
            branch_count=5,
            is_simplified_tax_payer=False,
        )
        assert q.grand_total_krw > 0


class TestBundleDiscounts:
    def test_5_branch_10pct(self):
        q = generate_bundle_quote(
            customer_name="X", branch_count=5, plan_code="public", cycle="monthly"
        )
        # 150,000 × 5 × (1-0.10) = 675,000
        assert q.subtotal_krw == 675_000
        assert q.vat_krw == 67_500

    def test_10_branch_15pct(self):
        q = generate_bundle_quote(
            customer_name="X", branch_count=10, plan_code="public", cycle="monthly"
        )
        # 150,000 × 10 × (1-0.15) = 1,275,000
        assert q.subtotal_krw == 1_275_000

    def test_25_branch_self_government(self):
        q = generate_bundle_quote(
            customer_name="자치구청 25개관",
            branch_count=25,
            plan_code="public",
            cycle="annual",
            founding_member=False,
        )
        # 150,000 × 25 × (1-0.20) × 12 × (1-0.17) = 29,880,000
        assert q.subtotal_krw == 29_880_000

    def test_100_branch_education_office(self):
        q = generate_bundle_quote(
            customer_name="교육청 100관",
            branch_count=100,
            plan_code="public",
            cycle="annual",
        )
        # 150,000 × 100 × (1-0.25) × 12 × (1-0.17) = 112,050,000
        assert q.subtotal_krw == 112_050_000


class TestLegalBasis:
    def test_clause_includes_cloud_law_for_public(self):
        q = generate_bundle_quote(
            customer_name="X", branch_count=5, plan_code="public", cycle="monthly"
        )
        # public·enterprise = 클라우드컴퓨팅법 §20
        assert "클라우드컴퓨팅법" in q.legal_basis_note

    def test_100_branch_cites_local_law(self):
        q = generate_bundle_quote(
            customer_name="X", branch_count=100, plan_code="public", cycle="monthly"
        )
        assert "지방계약법" in q.legal_basis_note

    def test_5_branch_cites_2000man_threshold(self):
        q = generate_bundle_quote(
            customer_name="X", branch_count=5, plan_code="public", cycle="monthly"
        )
        # 5관 = 수의계약 임계 인용
        assert "지방계약법" in q.legal_basis_note

    def test_general_tax_always_cited(self):
        q = generate_bundle_quote(customer_name="X", branch_count=1, plan_code="small")
        assert "조세특례제한법" in q.legal_basis_note or "일반과세자" in q.legal_basis_note


class TestQuoteValidity:
    def test_default_valid_30_days(self):
        q = generate_bundle_quote(
            customer_name="X",
            branch_count=5,
            issued_on=date(2026, 5, 6),
        )
        assert q.issued_at == "2026-05-06"
        assert q.valid_until == "2026-06-05"

    def test_custom_valid_days(self):
        q = generate_bundle_quote(
            customer_name="X",
            branch_count=5,
            issued_on=date(2026, 5, 6),
            valid_days=15,
        )
        assert q.valid_until == "2026-05-21"


class TestQuoteDict:
    def test_to_quote_dict_includes_vat_note(self):
        q = generate_bundle_quote(customer_name="X", branch_count=5)
        d = q.to_quote_dict()
        assert "VAT" in d["vat_note"]
        assert "일반과세자" in d["vat_note"]
        assert d["currency"] == "KRW"


class TestQuoteMarkdown:
    def test_markdown_includes_supplier_customer(self):
        q = generate_bundle_quote(
            customer_name="○○자치구청 25개관",
            branch_count=25,
            plan_code="public",
            cycle="annual",
        )
        md = render_quote_markdown(q, supplier_name="kormarc-auto")
        assert "kormarc-auto" in md
        assert "○○자치구청 25개관" in md
        assert "공급가" in md and "VAT" in md and "합계" in md

    def test_markdown_includes_payment_method(self):
        q = generate_bundle_quote(customer_name="X", branch_count=5)
        md = render_quote_markdown(q)
        assert "가상계좌" in md
        assert "세금계산서" in md
        assert "직인" in md

    def test_markdown_no_real_libraries(self):
        q = generate_bundle_quote(customer_name="X", branch_count=5)
        md = render_quote_markdown(q)
        for forbidden in ("내를건너서", "내건숲", "은평구공공"):
            assert forbidden not in md


class TestProcurementPack:
    def test_index_includes_required_documents(self):
        idx = build_procurement_pack_index()
        for required in (
            "사업자등록증",
            "통장사본",
            "이용약관",
            "개인정보처리방침",
            "DPA",
            "SLA",
            "환불정책",
            "AI 안내",
        ):
            assert required in idx

    def test_index_describes_each_document(self):
        idx = build_procurement_pack_index()
        for desc in idx.values():
            assert len(desc) > 5
