"""KORMARC ↔ MARC21 양방향 변환.

용도:
- 해외 도서관(LC, BL 등)에서 받은 MARC21 → KORMARC로 변환해 자관 반입
- 자관 KORMARC → MARC21로 변환해 글로벌 카탈로그 노출 (해외 한국학 도서관 등)

핵심 차이:
- 한국 특수 필드: 049 청구기호, 880 한자병기, 950 가격, 056 KDC
- MARC21 특수 필드: 020 ▾q (binding type), 050 LCC, 082 DDC, 650 LCSH
- 008 발행국부호: KORMARC와 MARC21 일부 코드 다름
- 245 1지시기호: 의미 동일하지만 적용 관행 차이
"""

from __future__ import annotations

import logging

from pymarc import Field, Indicators, Record

logger = logging.getLogger(__name__)


# 한국 특수 필드 → MARC21에서 보존되지만 표준 외 (LC가 임의 무시 가능)
KOREA_SPECIFIC_TAGS = {"049", "950", "956"}

# MARC21 특수 필드 → KORMARC에서 보존되지만 한국 도서관 시스템이 무시
MARC21_SPECIFIC_TAGS = {"050", "090"}


def kormarc_to_marc21(record: Record, *, drop_korea_specific: bool = False) -> Record:
    """KORMARC 레코드를 MARC21 호환 형식으로 변환.

    Args:
        record: 원본 KORMARC 레코드 (in-place 수정 X — 새 레코드 반환)
        drop_korea_specific: True면 049·950 등 한국 특수 필드 제거

    Returns:
        MARC21 호환 pymarc.Record
    """
    new_record = Record(force_utf8=True, leader=str(record.leader))

    for field in record.fields:
        if drop_korea_specific and field.tag in KOREA_SPECIFIC_TAGS:
            continue

        if field.is_control_field():
            new_record.add_field(Field(tag=field.tag, data=field.data))
            continue

        # 056 KDC → 082 DDC가 있으면 그대로, 없으면 KDC만 보존 (LC가 무시)
        # 880 한자병기는 보존 (MARC21도 880 표준)
        # 264 RDA는 표준 호환

        new_subfields = list(field.subfields)
        new_record.add_field(
            Field(
                tag=field.tag,
                indicators=Indicators(field.indicators[0], field.indicators[1]),
                subfields=new_subfields,
            )
        )

    logger.info("KORMARC → MARC21 변환: %d 필드 → %d 필드", len(record.fields), len(new_record.fields))
    return new_record


def marc21_to_kormarc(record: Record, *, drop_lc_specific: bool = False) -> Record:
    """MARC21 레코드를 KORMARC 호환 형식으로 변환.

    Args:
        record: 원본 MARC21 레코드
        drop_lc_specific: True면 050(LCC) 등 LC 특수 필드 제거

    Returns:
        KORMARC 호환 pymarc.Record
    """
    new_record = Record(force_utf8=True, leader=str(record.leader))

    for field in record.fields:
        if drop_lc_specific and field.tag in MARC21_SPECIFIC_TAGS:
            continue

        if field.is_control_field():
            new_record.add_field(Field(tag=field.tag, data=field.data))
            continue

        # 082 DDC → 056 KDC 변환은 정확한 매핑이 불가능 (분류 체계 다름)
        #   → 사서가 별도로 056 KDC 추가하도록 빈 placeholder만 안내
        new_subfields = list(field.subfields)
        new_record.add_field(
            Field(
                tag=field.tag,
                indicators=Indicators(field.indicators[0], field.indicators[1]),
                subfields=new_subfields,
            )
        )

    logger.info("MARC21 → KORMARC 변환: %d 필드 → %d 필드", len(record.fields), len(new_record.fields))
    return new_record


def get_conversion_warnings(record: Record, target: str) -> list[str]:
    """변환 시 사서가 알아야 할 경고 (정확도 영향).

    Args:
        record: 원본 레코드
        target: "marc21" 또는 "kormarc"

    Returns:
        경고 메시지 리스트
    """
    warnings: list[str] = []

    if target == "marc21":
        if record.get_fields("049"):
            warnings.append("049 청구기호는 한국 특수 — LC·BL은 무시할 수 있음 (852로 대체 권장)")
        if record.get_fields("950"):
            warnings.append("950 가격은 한국 특수 — MARC21에선 020 ▾c 또는 037 ▾c 권장")
        if record.get_fields("056") and not record.get_fields("082"):
            warnings.append("056 KDC만 있고 082 DDC 없음 — MARC21 도서관은 DDC 선호")
    elif target == "kormarc":
        if record.get_fields("050"):
            warnings.append("050 LCC는 미국 표준 — 한국 도서관에선 056 KDC 별도 추가 필요")
        if record.get_fields("082") and not record.get_fields("056"):
            warnings.append("082 DDC만 있음 — 056 KDC를 사서가 직접 부여 필요")
        if record.get_fields("650") and any(
            sf.code == "2" and sf.value == "0"
            for f in record.get_fields("650")
            for sf in f.subfields
        ):
            warnings.append("650 LCSH 주제명 — NLSH 또는 도정나 키워드 보강 권장")

    return warnings
