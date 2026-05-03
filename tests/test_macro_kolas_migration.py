"""5-1 macro_librarian_mode + 4-1 KOLAS migration 테스트."""

from __future__ import annotations

# ============== 5-1 매크로 사서 모드 ==============


class TestMacroLibrarianMode:
    def test_process_one_book_no_dependencies(self):
        from kormarc_auto.ui.macro_librarian_mode import process_one_book

        result = process_one_book("9788937437076", "○○도서관")
        assert result.isbn == "9788937437076"
        assert result.library_name == "○○도서관"
        # DI 미주입 = None 반환·예외 X
        assert result.mrc_bytes is None
        assert result.chaekdanbi_hwp_path is None

    def test_session_stats_increment(self):
        from kormarc_auto.ui.macro_librarian_mode import (
            MacroSessionStats,
            process_one_book,
        )

        session = MacroSessionStats()
        for i in range(3):
            process_one_book(f"978{i:010d}", "X", session=session)
        assert session.books_processed == 3

    def test_nps_prompt_at_5_books(self):
        from kormarc_auto.ui.macro_librarian_mode import (
            MacroSessionStats,
            process_one_book,
        )

        session = MacroSessionStats()
        results = []
        for i in range(7):
            r = process_one_book(f"978{i:010d}", "X", session=session)
            results.append(r)

        assert results[4].nps_prompt_due is True  # 5번째 = NPS
        assert results[3].nps_prompt_due is False  # 4번째 = X

    def test_aggregate_session_nps(self):
        from kormarc_auto.ui.macro_librarian_mode import (
            MacroSessionStats,
            aggregate_session_nps,
        )

        session = MacroSessionStats(books_processed=10, nps_responses=[10, 9, 9, 8, 7, 6])
        result = aggregate_session_nps(session)
        assert result["count"] == 6
        assert result["promoters"] == 3  # 10·9·9
        assert result["detractors"] == 1  # 6
        # NPS = (3-1)/6 * 100 = 33
        assert result["nps"] == 33

    def test_render_one_screen_html(self):
        from kormarc_auto.ui.macro_librarian_mode import render_one_screen_html

        html = render_one_screen_html("○○도서관")
        assert "○○도서관" in html
        assert "ISBN" in html
        assert "마크 만들기" in html

    def test_render_html_with_last_outputs(self):
        from kormarc_auto.ui.macro_librarian_mode import (
            MacroOutputs,
            render_one_screen_html,
        )

        last = MacroOutputs(
            isbn="9788937437076",
            library_name="○○",
            mrc_bytes=b"data",
            nps_prompt_due=True,
        )
        html = render_one_screen_html("○○", last_outputs=last)
        assert "9788937437076" in html
        assert "NPS" in html


# ============== 4-1 KOLAS Migration ==============


class TestKolasMigration:
    def test_migrate_to_alpas(self):
        from kormarc_auto.interlibrary.kolas_migration import migrate_to_target

        result = migrate_to_target(
            {"isbn": "9788937437076", "title": "X", "registration_no_prefix": "EQ"}, "alpas"
        )
        assert result.target_system == "alpas"
        assert result.output_payload is not None
        assert result.round_trip_match_pct >= 99.0

    def test_migrate_to_koha_warns_on_880(self):
        from kormarc_auto.interlibrary.kolas_migration import migrate_to_target

        result = migrate_to_target(
            {"isbn": "9788937437076", "title": "X", "880": "한자 병기"}, "koha"
        )
        assert any("880" in w for w in result.warnings)

    def test_migrate_to_alma(self):
        from kormarc_auto.interlibrary.kolas_migration import migrate_to_target

        result = migrate_to_target({"isbn": "9788937437076", "title": "X", "kdc": "813"}, "alma")
        assert result.target_system == "alma"
        assert "MARCXML" in str(result.output_payload)

    def test_migrate_to_solars_unsupported(self):
        from kormarc_auto.interlibrary.kolas_migration import migrate_to_target

        result = migrate_to_target({"isbn": "X"}, "solars")
        # SOLARS = vendor 협업 필요
        assert result.output_payload is None
        assert any("SOLARS" in w for w in result.warnings)

    def test_round_trip_validate_alpas_passes_95(self):
        from kormarc_auto.interlibrary.kolas_migration import round_trip_validate

        result = round_trip_validate({"isbn": "X", "title": "Y"}, "alpas")
        assert result["passes_95_target"] is True

    def test_estimate_migration_cost_50k(self):
        from kormarc_auto.interlibrary.kolas_migration import estimate_migration_cost

        result = estimate_migration_cost(50_000)
        assert result["record_count"] == 50_000
        assert result["estimated_hours"] > 0
        assert result["total_cost_won"] > 0

    def test_kolas_eol_countdown(self):
        from kormarc_auto.interlibrary.kolas_migration import kolas_eol_countdown_message

        msg = kolas_eol_countdown_message()
        assert msg["eol_date"] == "2026-12-31"
        assert msg["tam_libraries"] == 1271
        assert msg["urgency"] in ("low", "medium", "high", "critical")
        assert "1,271" in msg["headline"] or "1271" in msg["headline"]
