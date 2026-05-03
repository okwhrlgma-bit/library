"""페르소나 03·04 FAIL → PASS 전환 회복 테스트 (Part 89·90).

Part 89 검증 결과:
- 페르소나 03 (P15 순회사서) FAIL: mobile/offline_queue·bluetooth_scanner 부재
- 페르소나 04 (대학 분관) FAIL: ddc·mesh 미지원

본 테스트 = 신규 4 모듈 (ddc·mesh·offline_queue·bluetooth_scanner) 핵심 기능 검증.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ============== 페르소나 04 보완 ==============


class TestDdcClassifier:
    def test_kdc_to_ddc_main_class_swap(self):
        from kormarc_auto.classification.ddc_classifier import kdc_to_ddc

        # 윤희윤 매핑: KDC 4(자연) → DDC 5
        result = kdc_to_ddc("4")
        assert result.ddc == "500"
        assert result.source == "kdc_mapping"

        # KDC 5(기술) → DDC 6
        assert kdc_to_ddc("5").ddc == "600"
        # KDC 6(예술) → DDC 7
        assert kdc_to_ddc("6").ddc == "700"
        # KDC 7(언어) → DDC 4
        assert kdc_to_ddc("7").ddc == "400"

    def test_kdc_to_ddc_with_subclass(self):
        from kormarc_auto.classification.ddc_classifier import kdc_to_ddc

        # KDC 813.6 → DDC 813.6 (문학 main class 동일)
        result = kdc_to_ddc("813.6")
        assert result.ddc and result.ddc.startswith("8")

        # KDC 510 (기술과학·의학 분야 추정) → DDC 6xx
        result = kdc_to_ddc("510")
        assert result.ddc and result.ddc.startswith("6")

    def test_kdc_to_ddc_invalid(self):
        from kormarc_auto.classification.ddc_classifier import kdc_to_ddc

        result = kdc_to_ddc("")
        assert result.ddc is None
        assert result.source == "missing"

        result = kdc_to_ddc("abc")
        assert result.ddc is None

    def test_add_ddc_to_book_data_skips_existing(self):
        from kormarc_auto.classification.ddc_classifier import add_ddc_to_book_data

        # 이미 DDC 있으면 그대로
        data = {"kdc": "813", "ddc": "813.6"}
        result = add_ddc_to_book_data(data)
        assert result["ddc"] == "813.6"

    def test_add_ddc_auto_fills_from_kdc(self):
        from kormarc_auto.classification.ddc_classifier import add_ddc_to_book_data

        data = {"kdc": "510"}
        result = add_ddc_to_book_data(data)
        assert "ddc" in result
        assert result["ddc"].startswith("6")  # KDC 5 → DDC 6
        assert result["ddc_source"] == "kdc_mapping"


class TestMeshMapper:
    def test_extract_mesh_korean_keywords(self):
        from kormarc_auto.classification.mesh_mapper import extract_mesh_from_text

        result = extract_mesh_from_text("당뇨병 환자의 영양 관리")
        assert any(m.mesh_id == "D003920" for m in result)  # Diabetes Mellitus
        assert any(m.mesh_term == "Diabetes Mellitus" for m in result)

    def test_extract_mesh_english_keywords(self):
        from kormarc_auto.classification.mesh_mapper import extract_mesh_from_text

        result = extract_mesh_from_text("Anatomy and Physiology Textbook")
        assert any("Anatomy" in m.mesh_term for m in result)
        assert any("Physiology" in m.mesh_term for m in result)

    def test_extract_mesh_dedupe(self):
        """동일 MeSH ID 중복 제거."""
        from kormarc_auto.classification.mesh_mapper import extract_mesh_from_text

        result = extract_mesh_from_text("암 치료 - 신경계 암 종양학 신경과")
        # "암"과 "신경" 모두 있어도 각각 1번만
        ids = [m.mesh_id for m in result]
        assert len(ids) == len(set(ids))

    def test_extract_mesh_empty(self):
        from kormarc_auto.classification.mesh_mapper import extract_mesh_from_text

        assert extract_mesh_from_text("") == []
        assert extract_mesh_from_text("일반 소설") == []

    def test_to_kormarc_650_subfields(self):
        from kormarc_auto.classification.mesh_mapper import (
            MeshMatch,
            to_kormarc_650_subfields,
        )

        match = MeshMatch(keyword="당뇨", mesh_term="Diabetes Mellitus", mesh_id="D003920")
        subfields = to_kormarc_650_subfields(match)
        assert {"code": "a", "value": "Diabetes Mellitus"} in subfields
        assert {"code": "2", "value": "mesh"} in subfields

    def test_add_mesh_to_book_data(self):
        from kormarc_auto.classification.mesh_mapper import add_mesh_to_book_data

        data = {"title": "심장병 진단 핸드북", "summary": "고혈압 관련"}
        result = add_mesh_to_book_data(data)
        assert "mesh_subjects" in result
        assert "mesh_650_fields" in result
        assert len(result["mesh_subjects"]) >= 2  # 심장·고혈압


# ============== 페르소나 03 보완 ==============


class TestOfflineQueue:
    @pytest.fixture
    def db_path(self, tmp_path: Path) -> Path:
        from kormarc_auto.mobile.offline_queue import init_queue_db

        path = tmp_path / "queue.db"
        init_queue_db(path)
        return path

    def test_enqueue_and_list_pending(self, db_path: Path):
        from kormarc_auto.mobile.offline_queue import enqueue, list_pending

        item_id = enqueue(
            db_path,
            tenant_id="LIB001",
            payload_type="isbn",
            payload={"isbn": "9788937437076"},
        )
        assert item_id > 0

        pending = list_pending(db_path, "LIB001")
        assert len(pending) == 1
        assert pending[0].payload["isbn"] == "9788937437076"
        assert pending[0].status == "pending"

    def test_tenant_isolation(self, db_path: Path):
        """다른 자관 큐는 보이지 않음."""
        from kormarc_auto.mobile.offline_queue import enqueue, list_pending

        enqueue(db_path, "LIB001", "isbn", {"isbn": "1111111111111"})
        enqueue(db_path, "LIB002", "isbn", {"isbn": "2222222222222"})

        pending_a = list_pending(db_path, "LIB001")
        pending_b = list_pending(db_path, "LIB002")
        assert len(pending_a) == 1
        assert len(pending_b) == 1
        assert pending_a[0].payload["isbn"] != pending_b[0].payload["isbn"]

    def test_mark_synced_removes_from_pending(self, db_path: Path):
        from kormarc_auto.mobile.offline_queue import (
            enqueue,
            list_pending,
            mark_synced,
        )

        item_id = enqueue(db_path, "LIB001", "isbn", {"isbn": "X"})
        mark_synced(db_path, item_id)

        pending = list_pending(db_path, "LIB001")
        assert len(pending) == 0

    def test_queue_stats(self, db_path: Path):
        from kormarc_auto.mobile.offline_queue import (
            enqueue,
            mark_failed,
            mark_synced,
            queue_stats,
        )

        id1 = enqueue(db_path, "LIB001", "isbn", {"x": 1})
        enqueue(db_path, "LIB001", "isbn", {"x": 2})
        id3 = enqueue(db_path, "LIB001", "isbn", {"x": 3})

        mark_synced(db_path, id1)
        mark_failed(db_path, id3, "Network error")

        stats = queue_stats(db_path, "LIB001")
        assert stats.get("pending") == 1
        assert stats.get("synced") == 1
        assert stats.get("failed") == 1


class TestBluetoothScanner:
    def test_validate_ean13_valid(self):
        from kormarc_auto.mobile.bluetooth_scanner import validate_ean13

        # 어린왕자 ISBN-13
        assert validate_ean13("9788937437076") is True

    def test_validate_ean13_invalid_checksum(self):
        from kormarc_auto.mobile.bluetooth_scanner import validate_ean13

        # 마지막 자리 변조
        assert validate_ean13("9788937437079") is False

    def test_validate_ean13_wrong_length(self):
        from kormarc_auto.mobile.bluetooth_scanner import validate_ean13

        assert validate_ean13("123") is False
        assert validate_ean13("") is False
        assert validate_ean13("12345678901234") is False

    def test_normalize_isbn_strips_hyphens(self):
        from kormarc_auto.mobile.bluetooth_scanner import normalize_isbn

        assert normalize_isbn("978-89-374-3707-6") == "9788937437076"
        assert normalize_isbn("  9788937437076  ") == "9788937437076"

    def test_process_scan_valid(self):
        from kormarc_auto.mobile.bluetooth_scanner import process_scan

        event = process_scan("9788937437076", "honeywell_1602g", "AA:BB:CC")
        assert event.valid is True
        assert event.normalized_isbn == "9788937437076"
        assert event.scanner_type == "honeywell_1602g"
        assert event.device_id == "AA:BB:CC"

    def test_process_scan_invalid(self):
        from kormarc_auto.mobile.bluetooth_scanner import process_scan

        event = process_scan("not-an-isbn")
        assert event.valid is False
        assert event.normalized_isbn is None
        assert event.error and "ISBN" in event.error

    def test_recommended_scanners_complete(self):
        from kormarc_auto.mobile.bluetooth_scanner import RECOMMENDED_SCANNERS

        # 페르소나 03 영업용: 3개 모델 권장
        assert len(RECOMMENDED_SCANNERS) >= 3
        for spec in RECOMMENDED_SCANNERS.values():
            assert "name" in spec
            assert "price_won" in spec
            assert spec["price_won"] > 0
