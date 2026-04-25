"""Phase 1 단위 테스트 — 외부 API 호출 없이 검증 가능한 부분만.

실제 API 호출 테스트는 tests/test_integration.py에서 (인증키 필요).
"""

from __future__ import annotations

import sys
from pathlib import Path

# src 경로 추가
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kormarc_auto.kormarc.builder import build_kormarc_record  # noqa: E402
from kormarc_auto.kormarc.mapping import (  # noqa: E402
    build_008,
    normalize_isbn,
    parse_publication_place,
)
from kormarc_auto.kormarc.validator import validate_isbn13, validate_record  # noqa: E402
from kormarc_auto.vernacular.field_880 import add_880_pairs  # noqa: E402
from kormarc_auto.vernacular.hanja_converter import has_hanja  # noqa: E402


class TestISBNValidation:
    def test_valid_isbn13(self):
        assert validate_isbn13("9788936434120") is True

    def test_invalid_checksum(self):
        assert validate_isbn13("9788936434121") is False

    def test_too_short(self):
        assert validate_isbn13("123456789") is False

    def test_with_hyphens(self):
        assert validate_isbn13("978-89-364-3412-0") is True


class TestISBNNormalization:
    def test_already_13(self):
        assert normalize_isbn("9788936434120") == "9788936434120"

    def test_with_hyphens(self):
        assert normalize_isbn("978-89-364-3412-0") == "9788936434120"

    def test_isbn10_to_13(self):
        # ISBN-10: 8936434128 → ISBN-13: 9788936434120
        result = normalize_isbn("8936434128")
        assert result == "9788936434120"

    def test_invalid(self):
        assert normalize_isbn("abc") is None
        assert normalize_isbn("") is None
        assert normalize_isbn(None) is None


class TestField008:
    def test_length_is_40(self):
        result = build_008(publication_year="2014", publication_place="파주")
        assert len(result) == 40

    def test_publication_year_in_position(self):
        result = build_008(publication_year="2014")
        assert result[7:11] == "2014"

    def test_korean_language_default(self):
        result = build_008(publication_year="2024")
        assert result[35:38] == "kor"

    def test_unknown_place(self):
        result = build_008(publication_year="2024", publication_place="알수없음")
        assert result[15:18] == "xx "


class TestPublicationPlace:
    def test_paju(self):
        assert parse_publication_place("파주: 창비") == "파주"

    def test_seoul_publisher(self):
        assert parse_publication_place("창비") is None  # 도시명 없으면 None


class TestHanjaDetection:
    def test_has_hanja(self):
        assert has_hanja("韓國") is True
        assert has_hanja("한국") is False
        assert has_hanja("한국(韓國)") is True
        assert has_hanja(None) is False
        assert has_hanja("") is False


class TestKormarcBuilder:
    def test_minimal_record(self):
        book_data = {
            "isbn": "9788936434120",
            "title": "작별하지 않는다",
            "author": "한강",
            "publisher": "창비",
            "publication_year": "2014",
            "sources": ["nl_korea"],
            "confidence": 0.95,
        }
        record = build_kormarc_record(book_data)
        # 필수 필드 존재
        assert record.get_fields("008")
        assert record.get_fields("020")
        assert record.get_fields("245")
        assert record.get_fields("100")

        # 008 길이 40
        assert len(record.get_fields("008")[0].data) == 40

        # 245 ▾a에 표제
        title_field = record.get_fields("245")[0]
        assert "작별하지 않는다" in title_field.value()

    def test_record_validation(self):
        book_data = {
            "isbn": "9788936434120",
            "title": "테스트 도서",
            "author": "테스트저자",
            "publication_year": "2024",
            "publisher": "파주: 테스트출판사",
        }
        record = build_kormarc_record(book_data)
        errors = validate_record(record)
        assert errors == [], f"검증 오류: {errors}"

    def test_880_pair_generation(self):
        book_data = {
            "isbn": "9788936434120",
            "title": "韓國의 歷史",  # 한자 포함
            "author": "金九",  # 한자 인명
            "publisher": "창비",
            "publication_year": "2024",
        }
        record = build_kormarc_record(book_data)
        pair_count = add_880_pairs(record)

        assert pair_count >= 1, "한자 포함인데 880 페어 미생성"
        assert record.get_fields("880"), "880 필드 미존재"

    def test_no_880_when_no_hanja(self):
        book_data = {
            "isbn": "9788936434120",
            "title": "한글만 있는 표제",
            "author": "홍길동",
            "publisher": "창비",
            "publication_year": "2024",
        }
        record = build_kormarc_record(book_data)
        pair_count = add_880_pairs(record)

        assert pair_count == 0, "한자 없는데 880 페어 생성됨"
