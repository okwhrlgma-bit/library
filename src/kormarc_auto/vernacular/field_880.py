"""KORMARC 880 필드 자동 페어 생성.

식별기호 6 형식:
    원본 필드(예 245)의 식별기호: ▾6 880-NN
    880 필드의 식별기호:         ▾6 245-NN/$1   ($1 = CJK 한자)

NN은 발생 번호 (01부터 순차 증가, 같은 페어끼리 일치).
"""

from __future__ import annotations

import logging

from pymarc import Field, Indicators, Record, Subfield

from kormarc_auto.vernacular.hanja_converter import hanja_to_hangul, has_hanja

logger = logging.getLogger(__name__)

# 880 페어를 자동 생성할 대상 필드
PAIRABLE_TAGS = {"100", "245", "490", "505", "700"}


def add_880_pairs(record: Record) -> int:
    """레코드를 스캔하여 한자 포함 필드에 880 페어 자동 추가.

    Args:
        record: pymarc.Record (in-place 수정)

    Returns:
        추가된 880 페어 개수
    """
    pair_count = 0

    for tag in PAIRABLE_TAGS:
        for field in record.get_fields(tag):
            # 모든 서브필드를 검사하여 한자 포함 여부 확인
            has_any_hanja = any(has_hanja(sf.value) for sf in field.subfields)
            if not has_any_hanja:
                continue

            pair_count += 1
            link_no = f"{pair_count:02d}"

            # 원본 필드에 ▾6 880-NN 추가
            field.add_subfield(code="6", value=f"880-{link_no}", pos=0)

            # 880 필드 생성 (한자→한글 변환된 값)
            converted_subfields = [Subfield(code="6", value=f"{tag}-{link_no}/$1")]
            for sf in field.subfields:
                if sf.code == "6":
                    continue
                converted_value = hanja_to_hangul(sf.value) if has_hanja(sf.value) else sf.value
                converted_subfields.append(Subfield(code=sf.code, value=converted_value))

            record.add_field(
                Field(
                    tag="880",
                    indicators=Indicators(field.indicators[0], field.indicators[1]),
                    subfields=converted_subfields,
                )
            )

            logger.info("880 페어 생성: %s-%s (한자 → 한글)", tag, link_no)

    return pair_count
