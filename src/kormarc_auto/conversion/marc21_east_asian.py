"""KORMARC → MARC21 동아시아 컬렉션 정밀 변환 (inactive 모듈).

근거: `KORMARC_명세서_§33_미국시장진출.docx` — "동아시아 컬렉션 도서관
(하버드-옌칭, UC버클리)은 한·중·일 MARC21 생성에 큰 어려움. 우리의 한자
880 필드가 고유 우위."

본 모듈은 **§33이 BEP(Break-Even Point) 후 활성화**되는 inactive 코드.
한국 시장 매출이 안정되기 전에는 영업·연구만, 코드는 보유.

활성화 조건 (§33 명세):
- 한국 매출 월 200만원 이상 (3개월 연속)
- 베타 사서 50명 이상
- 동아시아 컬렉션 도서관 1곳 이상 LOI(Letter of Intent)

활성화 시 변경:
- `kormarc/builder.py`에 `marc21_east_asian` 모드 추가
- CLI `kormarc-auto marc21-east-asian` 노출
- 가격: 권당 0.5 USD = 약 700원 (한국 가격의 7배)

핵심 우위:
1. 한자 880 필드 자동 (KORMARC 표준에 내장)
2. ALA-LC 로마자 변환 자동 (`romanization.py` 활용)
3. RDA 264 발행처 자동 분리 (260 → 264 다중)
4. KCR4 → AACR2/RDA 책임표시 매핑
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# 활성화 플래그 — BEP 후 환경변수로만 활성
ACTIVATED = False  # KORMARC_EAST_ASIAN_ACTIVATED 환경변수로 토글


def _check_activated() -> None:
    """비활성 모듈에서 함수 호출 시 명확히 거부 (실수 방지)."""
    if not ACTIVATED:
        raise RuntimeError(
            "marc21_east_asian는 inactive 모듈입니다. "
            "BEP 후 KORMARC_EAST_ASIAN_ACTIVATED=1 환경변수로 활성화하세요. "
            "근거: docs/§33-us-market.md"
        )


def transform_field_245_to_marc21_rda(field_dict: dict[str, Any]) -> dict[str, Any]:
    """245 본표제 → MARC21 RDA 형식 (책임표시 더 풍부).

    KORMARC: 245 ▾a 본표제 ▾b 부표제 ▾c 책임표시
    MARC21 RDA: 245 ▾a 본표제 [▾h GMD 폐지] ▾b 부표제 ▾c 책임표시 (full RDA)

    PoC: ▾a, ▾b, ▾c 그대로 유지하되 GMD 제거.
    """
    out = dict(field_dict)
    if "subfields" in out:
        out["subfields"] = [sf for sf in out["subfields"] if sf.get("code") != "h"]
    return out


def split_260_to_264(field_260: dict[str, Any]) -> list[dict[str, Any]]:
    """KORMARC 260 (단일 발행처) → MARC21 RDA 264 (production·publication·distribution 분리).

    264 지시기호:
    - 0: 제작/생산 (production)
    - 1: 출판/발행 (publication) ← 가장 흔함
    - 2: 배포 (distribution)
    - 3: 제조 (manufacture)
    - 4: 저작권 (copyright)

    PoC: 단일 264 (publication)으로 변환. 발행처·발행지·발행연도 모두 포함.
    """
    subfields = field_260.get("subfields", [])
    return [
        {
            "tag": "264",
            "indicators": [" ", "1"],  # publication
            "subfields": subfields,
        }
    ]


def add_880_pair_with_romanization(
    field_dict: dict[str, Any],
    *,
    romanizer_fn: Any = None,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """한자/한글 → 880 페어 + 880에 ALA-LC 로마자도 함께.

    KORMARC 880: 한자 병기만
    MARC21 880 (LC 한국학 컬렉션 관행): 880 한자 + 880 로마자 동시.

    Returns: (한자/한글 880, 로마자 880) 또는 None (대상 아님)
    """
    if romanizer_fn is None:
        try:
            from kormarc_auto.vernacular.romanization import to_ala_lc

            romanizer_fn = to_ala_lc
        except ImportError:
            return None

    text = next(
        (sf["value"] for sf in field_dict.get("subfields", []) if sf.get("code") == "a"),
        "",
    )
    if not text:
        return None

    cjk_880 = dict(field_dict)
    cjk_880["tag"] = "880"
    cjk_880["linkage"] = "01"  # ▾6 880-01

    romanized_value = romanizer_fn(text) if callable(romanizer_fn) else None
    if not romanized_value:
        return None
    rom_880 = {
        "tag": "880",
        "indicators": field_dict.get("indicators", [" ", " "]),
        "subfields": [{"code": "a", "value": romanized_value}],
        "linkage": "02",  # ▾6 880-02
    }
    return cjk_880, rom_880


def kormarc_to_marc21_east_asian(record_dict: dict[str, Any]) -> dict[str, Any]:
    """KORMARC dict → MARC21 동아시아 컬렉션 정밀 변환.

    inactive 모듈 — _check_activated() 통과 시에만 실행.
    """
    _check_activated()
    fields_in = record_dict.get("fields", [])
    fields_out: list[dict[str, Any]] = []

    for f in fields_in:
        tag = f.get("tag")
        if tag == "260":
            fields_out.extend(split_260_to_264(f))
        elif tag == "245":
            fields_out.append(transform_field_245_to_marc21_rda(f))
        else:
            fields_out.append(f)

        if tag in ("100", "245", "700"):
            pair = add_880_pair_with_romanization(f)
            if pair:
                fields_out.extend(pair)

    return {**record_dict, "fields": fields_out}


__all__ = [
    "ACTIVATED",
    "add_880_pair_with_romanization",
    "kormarc_to_marc21_east_asian",
    "split_260_to_264",
    "transform_field_245_to_marc21_rda",
]
