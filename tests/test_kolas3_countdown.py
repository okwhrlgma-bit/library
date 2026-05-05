"""Cycle 12 P37 — KOLAS III 카운트다운·자가진단·보도자료 회귀."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from kormarc_auto.migration import (
    KOLAS3_END_DATE,
    DiagnosisAnswer,
    days_until_kolas3_end,
    diagnose_migration,
    generate_press_release,
    timeline_actions_for_remaining_days,
)
from kormarc_auto.migration.countdown import KST, lost_data_categories
from kormarc_auto.migration.press_release import channel_specific_format


class TestEndDateInvariant:
    """외부 보고서 P37 게이트: 종료 시점 1초라도 변경 = STOP."""

    def test_end_date_exact(self):
        assert KOLAS3_END_DATE.year == 2026
        assert KOLAS3_END_DATE.month == 12
        assert KOLAS3_END_DATE.day == 31
        assert KOLAS3_END_DATE.hour == 23
        assert KOLAS3_END_DATE.minute == 59
        assert KOLAS3_END_DATE.second == 59

    def test_end_date_kst_timezone(self):
        # KST = UTC+9 = 9시간
        offset = KOLAS3_END_DATE.utcoffset()
        assert offset == timedelta(hours=9)


class TestDaysUntil:
    def test_d_240_at_2026_05_05(self):
        # 2026-05-05 → 2026-12-31 = 240일
        now = datetime(2026, 5, 5, 0, 0, 0, tzinfo=KST)
        days = days_until_kolas3_end(now=now)
        assert days == 240

    def test_d_180_at_2026_07_04(self):
        now = datetime(2026, 7, 4, 0, 0, 0, tzinfo=KST)
        days = days_until_kolas3_end(now=now)
        assert days == 180

    def test_d_0_at_end(self):
        now = KOLAS3_END_DATE
        days = days_until_kolas3_end(now=now)
        assert days == 0

    def test_negative_after_end(self):
        now = datetime(2027, 1, 31, 0, 0, 0, tzinfo=KST)
        days = days_until_kolas3_end(now=now)
        assert days < 0

    def test_naive_datetime_treated_as_kst(self):
        # KST 가정·tzinfo 자동 부착
        now_naive = datetime(2026, 5, 5, 0, 0, 0)
        days = days_until_kolas3_end(now=now_naive)
        assert days == 240


class TestDiagnose:
    def test_high_score_kolas3_no_backup(self):
        ans = DiagnosisAnswer(
            uses_kolas3_standard=True,
            has_recent_backup=False,
            has_alternative_plan=False,
            over_5000_records=True,
            has_dedicated_staff=False,
        )
        d = diagnose_migration(ans, now=datetime(2026, 5, 5, tzinfo=KST))
        # 40 + 20 + 15 + 15 + 10 = 100
        assert d.score == 100
        assert d.urgency == "urgent"

    def test_low_score_no_kolas3_has_backup(self):
        ans = DiagnosisAnswer(
            uses_kolas3_standard=False,
            has_recent_backup=True,
            has_alternative_plan=True,
            over_5000_records=False,
            has_dedicated_staff=True,
        )
        d = diagnose_migration(ans, now=datetime(2026, 5, 5, tzinfo=KST))
        assert d.score == 0
        assert d.urgency == "early"

    def test_urgent_when_d_60(self):
        ans = DiagnosisAnswer(
            uses_kolas3_standard=False,
            has_recent_backup=True,
            has_alternative_plan=True,
            over_5000_records=False,
            has_dedicated_staff=True,
        )
        # D-60 (90일 이내) = urgent (score 0이지만 시간 압박)
        d = diagnose_migration(ans, now=datetime(2026, 11, 1, tzinfo=KST))
        assert d.urgency == "urgent"

    def test_recommendations_korean(self):
        ans = DiagnosisAnswer(True, False, False, True, False)
        d = diagnose_migration(ans, now=datetime(2026, 5, 5, tzinfo=KST))
        assert "🚨" in d.recommendation
        assert len(d.next_actions) >= 3

    def test_diagnosis_immutable(self):
        from dataclasses import FrozenInstanceError

        ans = DiagnosisAnswer(True, True, True, True, True)
        d = diagnose_migration(ans, now=datetime(2026, 5, 5, tzinfo=KST))
        with pytest.raises(FrozenInstanceError):
            d.urgency = "early"  # type: ignore[misc]


class TestTimeline:
    def test_5_milestones(self):
        actions = timeline_actions_for_remaining_days(240)
        assert len(actions) == 5
        keys = list(actions.keys())
        assert any("D-240" in k for k in keys)
        assert any("D-180" in k for k in keys)
        assert any("D-90" in k for k in keys)
        assert any("D-30" in k for k in keys)
        assert any("D-0" in k for k in keys)

    def test_each_milestone_has_actions(self):
        actions = timeline_actions_for_remaining_days(180)
        for milestone, items in actions.items():
            assert len(items) >= 2, f"{milestone} 액션 부족"


class TestLostDataCategories:
    def test_5_categories(self):
        cats = lost_data_categories()
        assert len(cats) == 5

    def test_each_has_action(self):
        for cat in lost_data_categories():
            assert "category" in cat
            assert "why" in cat
            assert "action" in cat
            assert len(cat["action"]) > 10

    def test_includes_chaek_ieum(self):
        cats = lost_data_categories()
        joined = " ".join(c["category"] for c in cats)
        assert "책이음" in joined or "회원 키" in joined


class TestPressRelease:
    def test_includes_headline_d_day(self):
        pr = generate_press_release(now=datetime(2026, 5, 5, tzinfo=KST))
        assert "D-240" in pr
        assert "1,200+" in pr or "1,296" in pr

    def test_includes_official_source_url(self):
        pr = generate_press_release(now=datetime(2026, 5, 5, tzinfo=KST))
        # 외부 보고서 P37 게이트: 인용 수치에 출처 URL
        assert "books.nl.go.kr" in pr
        assert "korea.kr" in pr

    def test_includes_company_name(self):
        pr = generate_press_release(
            company_name="kormarc-auto", now=datetime(2026, 5, 5, tzinfo=KST)
        )
        assert "kormarc-auto" in pr

    def test_no_real_libraries_or_pii(self):
        pr = generate_press_release(now=datetime(2026, 5, 5, tzinfo=KST))
        # leak gate
        for forbidden in ("내를건너서", "내건숲", "은평구공공", "okwhr"):
            assert forbidden not in pr


class TestChannelFormat:
    def test_5_channels_supported(self):
        for ch in ("platum", "venturesquare", "jobpost", "library_journal", "kla"):
            f = channel_specific_format(ch)
            assert "tone" in f
            assert "max_length" in f
            assert "submit_url" in f

    def test_unknown_channel_falls_back(self):
        f = channel_specific_format("unknown")
        # platum default
        assert "스타트업" in f["tone"]
