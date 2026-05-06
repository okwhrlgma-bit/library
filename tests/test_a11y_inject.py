"""Cycle 60 UI/UX (헌법 §12) — a11y_inject + librarian_ux 회귀.

KWCAG 2.2 Level AA 정합·KRDS·Pretendard·사서 친화 어휘 검증.
"""

from __future__ import annotations

from kormarc_auto.ui.a11y_inject import (
    A11Y_GLOBAL_CSS,
    render_ai_ghost,
    render_confidence_chip,
)
from kormarc_auto.ui.librarian_ux import (
    LIBRARIAN_DAILY_CYCLE,
    LIBRARIAN_VOCABULARY,
    cite_authority,
    is_mobile_viewport_hint,
    render_librarian_friendly_error,
    render_workflow_position,
    time_saved_estimate,
)


class TestA11yGlobalCSS:
    def test_pretendard_cdn_included(self):
        # 헌법 §12: Pretendard CDN 필수
        assert "pretendard" in A11Y_GLOBAL_CSS.lower()
        assert "jsdelivr" in A11Y_GLOBAL_CSS

    def test_kwcag_skip_link(self):
        # KWCAG 2.4.1 = skip link
        assert "skip-link" in A11Y_GLOBAL_CSS
        assert "본문 바로가기" in A11Y_GLOBAL_CSS

    def test_kwcag_focus_visible(self):
        # KWCAG 2.4.7 = focus visible 항상
        assert "focus-visible" in A11Y_GLOBAL_CSS
        assert "outline" in A11Y_GLOBAL_CSS

    def test_kwcag_touch_target_44px(self):
        # KWCAG 2.5.5 = 44x44px 최소
        assert "44px" in A11Y_GLOBAL_CSS

    def test_reduced_motion_respected(self):
        # KWCAG 2.3.3 = prefers-reduced-motion
        assert "prefers-reduced-motion" in A11Y_GLOBAL_CSS

    def test_lang_ko_specified(self):
        # KWCAG 1.3.1 = lang ko
        assert "lang: ko" in A11Y_GLOBAL_CSS

    def test_korea_blue_color(self):
        # KRDS Korea blue 60 적용 (CTA·링크)
        assert "#0F4C9F" in A11Y_GLOBAL_CSS


class TestConfidenceChip:
    def test_high_chip(self):
        html = render_confidence_chip("high")
        assert "확실" in html
        assert "conf-chip-high" in html

    def test_mid_chip(self):
        html = render_confidence_chip("mid")
        assert "검토 필요" in html
        assert "conf-chip-mid" in html

    def test_low_chip(self):
        html = render_confidence_chip("low")
        assert "불확실" in html
        assert "conf-chip-low" in html

    def test_invalid_falls_back_to_mid(self):
        html = render_confidence_chip("xyz")
        # 헌법 §11·보수적 fallback
        assert "검토 필요" in html

    def test_no_raw_percent_in_chip(self):
        # 헌법 §11 = raw % UI 금지
        for cat in ("high", "mid", "low"):
            html = render_confidence_chip(cat)
            assert "%" not in html
            assert "0." not in html


class TestAIGhost:
    def test_ai_ghost_text(self):
        html = render_ai_ghost("AI가 생성한 KORMARC 245$a")
        assert "ai-ghost" in html
        assert "🤖" in html


class TestLibrarianVocabulary:
    def test_daily_cycle_5_steps(self):
        # Part 49 = 5 단계
        assert len(LIBRARIAN_DAILY_CYCLE) == 5
        steps = [s for s, _ in LIBRARIAN_DAILY_CYCLE]
        assert "수서" in steps
        assert "정리" in steps
        assert "배가" in steps
        assert "납본" in steps

    def test_vocabulary_mapping(self):
        # IT 용어 → 사서 일상 어휘
        assert LIBRARIAN_VOCABULARY["import"] == "반입"
        assert LIBRARIAN_VOCABULARY["validation"] == "검증"
        assert "지시기호" in LIBRARIAN_VOCABULARY["indicator"]


class TestTimeSavedEstimate:
    def test_basic(self):
        result = time_saved_estimate(100)
        # 100권 × 6분 = 600분 = 10시간
        assert result["minutes_saved"] == "600분"
        assert "10.0시간" in result["hours_saved"]
        # 10시간 × ₩20,000 = ₩200,000
        assert "200,000" in result["krw_saved"]

    def test_zero_records(self):
        result = time_saved_estimate(0)
        assert result["minutes_saved"] == "0분"
        assert "₩0" in result["krw_saved"]

    def test_constitution_reference(self):
        result = time_saved_estimate(1)
        # 헌법 §0 = 권당 8분 → 2분 = 6분 절감 명시
        assert "8분" in result["context"]
        assert "2분" in result["context"]


class TestLibrarianFriendlyErrors:
    def test_isbn_invalid_message(self):
        title, body = render_librarian_friendly_error("isbn_invalid")
        assert "ISBN" in title
        assert "13자리" in body

    def test_kdc_ambiguous_respects_constitution(self):
        _title, body = render_librarian_friendly_error("kdc_ambiguous")
        # 헌법 §3 = KDC 사서 책임·자동 결정 X
        assert "사서" in body
        assert "자동" in body

    def test_pii_warning_pipa_compliant(self):
        _title, body = render_librarian_friendly_error("pii_warning")
        # 헌법 §3 + PIPA §28의8
        assert "PIPA" in body or "본문" in body

    def test_unknown_falls_back_safely(self):
        title, body = render_librarian_friendly_error("unknown_kind")
        assert title  # 빈 string X
        assert body


class TestWorkflowPosition:
    def test_current_step_bolded(self):
        result = render_workflow_position("정리")
        assert "**정리**" in result
        # 다른 단계는 굵지 않게
        assert "**수서**" not in result

    def test_all_5_steps_present(self):
        result = render_workflow_position("이용")
        assert "수서" in result
        assert "정리" in result
        assert "배가" in result
        assert "이용" in result
        assert "납본" in result

    def test_arrow_separator(self):
        result = render_workflow_position("수서")
        assert "→" in result


class TestCiteAuthority:
    def test_nlk(self):
        html = cite_authority("nlk")
        assert "국립중앙도서관" in html
        assert "📖" in html

    def test_kait(self):
        html = cite_authority("kait")
        assert "KAIT" in html or "정보통신산업진흥원" in html

    def test_unknown_authority(self):
        # graceful fallback
        html = cite_authority("custom_org")
        assert "📌" in html


class TestMobileViewport:
    def test_mobile_under_768(self):
        assert is_mobile_viewport_hint(375) is True
        assert is_mobile_viewport_hint(640) is True

    def test_desktop_above_768(self):
        assert is_mobile_viewport_hint(1024) is False
        assert is_mobile_viewport_hint(1920) is False

    def test_no_hint_defaults_desktop(self):
        # 보수적 기본값 = desktop (KWCAG 44px 항상 적용·모바일 분기는 옵션)
        assert is_mobile_viewport_hint(None) is False


class TestConstitutionInvariants:
    """헌법 §3·§10·§11·§12 정합 검증."""

    def test_no_raw_probability_in_chips(self):
        # 헌법 §11
        for cat in ("high", "mid", "low"):
            html = render_confidence_chip(cat)
            import re

            # raw % 패턴 = "0.95"·"95%"·"확률 0.87" 등 모두 금지
            assert not re.search(r"\d+\.\d+", html)
            assert "%" not in html

    def test_ai_ghost_has_ai_signal(self):
        # 헌법 §10 = AI 생성 사실 표시 의무
        html = render_ai_ghost("test")
        assert "🤖" in html or "AI" in html or "ai-" in html

    def test_pretendard_in_global_css(self):
        # 헌법 §12 = Pretendard CDN 필수
        assert "Pretendard" in A11Y_GLOBAL_CSS or "pretendard" in A11Y_GLOBAL_CSS
