"""KORMARC 레코드 검증."""

from __future__ import annotations

from typing import Any

from pymarc import Record

from kormarc_auto.kormarc.application_level import validate_application_level
from kormarc_auto.kormarc.material_type import detect_material_type


def validate_isbn13(isbn: str) -> bool:
    """ISBN-13 체크섬 검증.

    EAN-13 알고리즘: 처음 12자리 가중합 % 10이 0이면 체크 자리는 0,
    아니면 10에서 뺀 값.
    """
    digits = [c for c in isbn if c.isdigit()]
    if len(digits) != 13:
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    check = (10 - total % 10) % 10
    return check == int(digits[12])


def validate_008(value: str) -> tuple[bool, str | None]:
    """008 필드는 정확히 40자리여야 함.

    Returns:
        (유효 여부, 에러 메시지)
    """
    if len(value) != 40:
        return False, f"008 필드 길이 {len(value)} (필요: 40)"
    return True, None


def validate_record(record: Record) -> list[str]:
    """KORMARC 레코드 종합 검증.

    Returns:
        에러 메시지 리스트 (비어있으면 통과).
    """
    errors: list[str] = []

    # 008 필드 길이
    field_008 = record.get_fields("008")
    if not field_008:
        errors.append("008 필드 누락")
    else:
        ok, msg = validate_008(field_008[0].data)
        if not ok and msg:
            errors.append(msg)

    # 245 필드 (표제) 필수
    if not record.get_fields("245"):
        errors.append("245 (표제) 필드 누락")

    # 020 필드 (ISBN) 권장
    isbn_fields = record.get_fields("020")
    for f in isbn_fields:
        for sf_value in f.get_subfields("a"):
            isbn_clean = "".join(c for c in sf_value.split()[0] if c.isdigit())
            if len(isbn_clean) == 13 and not validate_isbn13(isbn_clean):
                errors.append(f"020 ISBN 체크섬 오류: {sf_value}")

    return errors


def validate_record_full(
    record: Record,
    book_data: dict[str, Any] | None = None,
    material_type: str | None = None,
) -> list[str]:
    """KORMARC + 2023.12 M/A/O 적용 수준 종합 검증.

    `validate_record`의 기본 검증 + `application_level.validate_application_level`
    추가. material_type 미지정 시 book_data로 자동 감지.

    Args:
        record: pymarc Record.
        book_data: 외부 API 통합 dict. 없으면 빈 dict.
        material_type: 자료유형 키. 미지정 시 자동 감지.

    Returns:
        에러·위반 메시지 리스트 (비어있으면 정합).
    """
    errors = validate_record(record)
    book_data = book_data or {}
    material_type = material_type or detect_material_type(book_data)

    present_tags = {f.tag for f in record.get_fields()}
    for tag, level, reason in validate_application_level(
        present_tags, book_data, material_type,
    ):
        errors.append(f"[{level}] {tag}: {reason}")

    return errors
