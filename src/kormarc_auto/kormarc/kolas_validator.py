"""KOLAS III 반입 사전 검증 — 일반 validator보다 엄격.

KOLAS III가 .mrc 반입 시 거부할 만한 케이스를 사전 발견해
사서가 헛수고하지 않게 한다.

체크 항목:
- LDR (지도자) 24자
- 008 정확히 40자
- 008 발행연도1(07-10) 4자리 숫자
- 020 ▾a ISBN-13 (필수, 체크섬 통과)
- 040 ▾a 우리 도서관 부호 (필수)
- 245 ▾a 본표제 (필수, 비어있지 않음)
- 008 35-37 언어부호 3자
- 880 페어 일치 (▾6 링크 양방향)
- 한자 포함 필드에 880 페어 누락 경고
- KDC(056) 형식 검증
- 1차 표목(100/110/111) 비어있을 때 245 1지시기호=0 권고
"""

from __future__ import annotations

import logging
import re
from typing import Any

from pymarc import Record

from kormarc_auto.kormarc.validator import validate_record as _basic_validate
from kormarc_auto.vernacular.hanja_converter import has_hanja

logger = logging.getLogger(__name__)


_KDC_PATTERN = re.compile(r"^\d{3}(\.\d+)?$")
_YEAR_PATTERN = re.compile(r"^\d{4}$")


def kolas_strict_validate(record: Record) -> dict[str, Any]:
    """KOLAS III 반입 사전 검증.

    Args:
        record: pymarc.Record

    Returns:
        {
            "ok": bool,                    # 모든 ERROR 통과
            "errors": list[str],           # 반입 거부 가능성 (반드시 수정)
            "warnings": list[str],         # 반입은 되나 품질 저하
            "info": list[str],             # 참고
        }
    """
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    errors.extend(_basic_validate(record))

    # LDR
    leader = str(record.leader)
    if len(leader) != 24:
        errors.append(f"LDR(지도자) 길이 {len(leader)}자 (정확히 24자 필요)")

    # 008
    field_008 = record.get("008")
    if field_008 is None:
        errors.append("008 필드 누락")
    else:
        data = field_008.data or ""
        if len(data) != 40:
            errors.append(f"008 길이 {len(data)}자 (정확히 40자 필요)")
        if len(data) >= 11:
            year1 = data[7:11]
            if year1.strip() and not _YEAR_PATTERN.match(year1):
                errors.append(f"008 발행연도1(07-10) 형식 오류: '{year1}'")
        if len(data) >= 38:
            lang = data[35:38]
            if not lang.strip():
                warnings.append("008 35-37 언어부호 비어있음")

    # 020 ISBN
    field_020 = record.get("020")
    if field_020 is None:
        errors.append("020(ISBN) 필드 누락")
    else:
        isbn_a = next((sf.value for sf in field_020.subfields if sf.code == "a"), None)
        if not isbn_a:
            errors.append("020 ▾a (ISBN) 비어있음")
        elif not _is_valid_isbn13(isbn_a):
            errors.append(f"020 ▾a ISBN 체크섬 실패 또는 형식 오류: '{isbn_a}'")

    # 040
    field_040 = record.get("040")
    if field_040 is None:
        errors.append("040(목록작성기관) 필드 누락")
    else:
        ag = next((sf.value for sf in field_040.subfields if sf.code == "a"), None)
        if not ag or not ag.strip():
            errors.append("040 ▾a (우리 도서관 부호) 비어있음")

    # 245
    field_245 = record.get("245")
    if field_245 is None:
        errors.append("245(표제) 필드 누락")
    else:
        title = next((sf.value for sf in field_245.subfields if sf.code == "a"), None)
        if not title or not title.strip():
            errors.append("245 ▾a (본표제) 비어있음")
        # 1차 표목 없을 때 245 1지시기호=0 권고
        if not (record.get("100") or record.get("110") or record.get("111")):
            ind1 = field_245.indicators[0] if field_245.indicators else " "
            if ind1 != "0":
                warnings.append(
                    f"245 1지시기호={ind1!r} — 1차 표목 없으면 '0' 권장"
                )

    # 056 KDC
    for f56 in record.get_fields("056"):
        kdc = next((sf.value for sf in f56.subfields if sf.code == "a"), None)
        if kdc and not _KDC_PATTERN.match(kdc.strip()):
            warnings.append(f"056 ▾a KDC 형식 비표준: '{kdc}'")

    # 880 페어 검사
    pair_issues = _check_880_pairs(record)
    warnings.extend(pair_issues)

    # 한자 포함 필드인데 880 페어 없음 → 정보
    for tag in ("100", "245", "490", "505", "700"):
        for f in record.get_fields(tag):
            if any(has_hanja(sf.value) for sf in f.subfields) and not any(
                sf.code == "6" for sf in f.subfields
            ):
                info.append(f"{tag} 필드에 한자 포함되나 880 페어 없음 — 자동 생성 권장")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


def _is_valid_isbn13(isbn: str) -> bool:
    """ISBN-13 체크섬 검증."""
    digits = [c for c in isbn if c.isdigit()]
    if len(digits) != 13:
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    check = (10 - (total % 10)) % 10
    return check == int(digits[12])


def _check_880_pairs(record: Record) -> list[str]:
    """880 ▾6 링크 양방향 검사."""
    issues: list[str] = []

    main_links: dict[str, tuple[str, str]] = {}  # link_no → (tag, full_value)
    for f in record.fields:
        if f.tag == "880" or f.is_control_field():
            continue
        for sf in f.subfields:
            if sf.code == "6" and "-" in sf.value:
                tag_part, num_part = sf.value.split("-", 1)
                num = num_part.split("/")[0]
                main_links[f"{f.tag}-{num}"] = (f.tag, sf.value)

    pair_links: dict[str, tuple[str, str]] = {}
    for f in record.get_fields("880"):
        for sf in f.subfields:
            if sf.code == "6" and "-" in sf.value:
                tag_part, num_part = sf.value.split("-", 1)
                num = num_part.split("/")[0]
                pair_links[f"{tag_part}-{num}"] = (tag_part, sf.value)

    for key in main_links:
        if key not in pair_links:
            issues.append(f"880 페어 누락: {key} (원본 필드는 ▾6 880-NN 보유)")
    for key in pair_links:
        if key not in main_links:
            issues.append(f"880 고아 페어: {key} (원본 필드 없음)")

    return issues
