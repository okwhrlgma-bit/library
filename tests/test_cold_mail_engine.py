"""G1 콜드메일 자동 생성 엔진 테스트."""

from __future__ import annotations


class TestColdMailEngine:
    def test_generate_school_teacher_segment(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            generate_cold_mail,
        )

        req = ColdMailRequest(
            recipient_name="사서 A",
            segment="school_teacher",
            library_name="○○중학교 도서관",
            annual_book_count=500,
        )
        draft = generate_cold_mail(req)
        assert "○○중학교 도서관" in draft.subject
        assert "사서 A" in draft.greeting
        assert "행정실장" in draft.funnel_paragraph
        assert draft.tracking_id.startswith("CM-SCH-")

    def test_generate_small_library_segment(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            generate_cold_mail,
        )

        req = ColdMailRequest(
            recipient_name="관장 B",
            segment="small_library_director",
            library_name="○○작은도서관",
        )
        draft = generate_cold_mail(req)
        assert "본인" in draft.funnel_paragraph or "결재 단계 0" in draft.funnel_paragraph
        assert draft.tracking_id.startswith("CM-SMA-")

    def test_generate_university_branch_segment(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            generate_cold_mail,
        )

        req = ColdMailRequest(
            recipient_name="사서 D",
            segment="university_branch",
            library_name="○○대학 의학분관",
        )
        draft = generate_cold_mail(req)
        assert "본관" in draft.funnel_paragraph or "Alma" in draft.funnel_paragraph

    def test_roi_calculation_in_paragraph(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            generate_cold_mail,
        )

        req = ColdMailRequest(
            recipient_name="사서 X",
            segment="school_teacher",
            library_name="X",
            annual_book_count=1000,
        )
        draft = generate_cold_mail(req)
        # 1000권 = 6,500분 = 약 108시간
        assert "100" in draft.roi_paragraph or "108" in draft.roi_paragraph

    def test_render_full_body(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            generate_cold_mail,
        )

        req = ColdMailRequest(
            recipient_name="사서 Y",
            segment="public_library",
            library_name="X 도서관",
        )
        draft = generate_cold_mail(req)
        body = draft.render()
        assert "사서 Y" in body
        assert "PILOT" in body
        assert draft.tracking_id in body

    def test_batch_generate(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            batch_generate,
        )

        requests = [
            ColdMailRequest(
                recipient_name=f"사서 {i}",
                segment="school_teacher",
                library_name=f"학교 {i}",
            )
            for i in range(10)
        ]
        drafts = batch_generate(requests)
        assert len(drafts) == 10
        # 추적 ID 모두 다름
        ids = {d.tracking_id for d in drafts}
        assert len(ids) == 10

    def test_custom_pain_appended(self):
        from kormarc_auto.sales.cold_mail_engine import (
            ColdMailRequest,
            generate_cold_mail,
        )

        req = ColdMailRequest(
            recipient_name="사서",
            segment="public_library",
            library_name="X",
            custom_pain="우리 자관만의 특이 페인",
        )
        draft = generate_cold_mail(req)
        assert "우리 자관만의 특이 페인" in draft.pain_paragraph

    def test_segment_pain_keywords_complete(self):
        from kormarc_auto.sales.cold_mail_engine import SEGMENT_PAINS

        assert len(SEGMENT_PAINS) == 5  # 5 segment
        for segment, pains in SEGMENT_PAINS.items():
            assert len(pains) >= 3, f"{segment} pain count < 3"
