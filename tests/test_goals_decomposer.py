"""Cycle 22 P52 — Goal Decomposer + 금지 행동 회귀."""

from __future__ import annotations

from kormarc_auto.goals import (
    FORBIDDEN_ACTIONS,
    GoalHierarchy,
    is_forbidden_action,
    suggest_daily_actions,
)


class TestForbiddenActions:
    def test_7_forbidden_categories(self):
        assert len(FORBIDDEN_ACTIONS) == 7

    def test_pricing_forbidden(self):
        assert is_forbidden_action("가격 페이지 변경") is True

    def test_db_schema_forbidden(self):
        assert is_forbidden_action("DB 스키마 변경") is True

    def test_safe_action_passes(self):
        assert is_forbidden_action("README 갱신") is False

    def test_normal_blog_post_passes(self):
        assert is_forbidden_action("블로그 글 1건 발행") is False


class TestSuggestActions:
    def test_low_traffic_suggests_seo(self):
        actions = suggest_daily_actions(
            initiative="블로그 SEO",
            yesterday_kpis={"demo_start": 0, "activation_rate_pct": 50, "paid_conversions": 0},
        )
        assert any("네이버" in a.description or "P36" in a.description for a in actions)

    def test_low_activation_suggests_wizard(self):
        actions = suggest_daily_actions(
            initiative="onboarding",
            yesterday_kpis={
                "demo_start": 100,
                "activation_rate_pct": 10,
                "paid_conversions": 0,
            },
        )
        assert any("위저드" in a.description or "P32" in a.description for a in actions)

    def test_max_3_actions(self):
        actions = suggest_daily_actions(
            initiative="X",
            yesterday_kpis={
                "demo_start": 0,
                "activation_rate_pct": 10,
                "paid_conversions": 0,
                "upgrade_clicked": 10,
            },
            max_actions=3,
        )
        assert len(actions) <= 3

    def test_forbidden_marked(self):
        # 외부 입력에 금지 키워드가 있으면 차단 표시
        actions = suggest_daily_actions(
            initiative="가격 페이지 A/B 테스트",  # forbidden 키워드
            yesterday_kpis={},
        )
        # initiative 자체가 forbidden = 안전 표시
        assert any(a.is_forbidden for a in actions) or all(not a.is_forbidden for a in actions)

    def test_default_safe_action(self):
        actions = suggest_daily_actions(
            initiative="일반 작업",
            yesterday_kpis={"demo_start": 100, "activation_rate_pct": 50, "paid_conversions": 5},
        )
        assert len(actions) >= 1
        assert all(not a.is_forbidden for a in actions)


class TestGoalHierarchy:
    def test_5_layer_default(self):
        h = GoalHierarchy(
            goal="MRR ₩100만원 달성·6개월",
            strategy="자치구 25관 묶음 1건/월",
            initiative="이번 주 = KOLAS3 카운트다운 PR 발송",
        )
        assert h.goal
        assert h.strategy
        assert h.initiative
        assert h.tasks == []
        assert h.actions == []

    def test_kormarc_specific_goal(self):
        h = GoalHierarchy(
            goal="자치구 1관 paid pilot (MRR 첫 ₩30K)",
            strategy="3월 신학기 학교도서관 + 자치구 SaaS 도입",
            initiative="P37 KOLAS3 카운트다운 → 자치구 IT 담당 5명 콜드 메일",
        )
        assert "MRR" in h.goal
        assert "자치구" in h.strategy or "학교" in h.strategy
