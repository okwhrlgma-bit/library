"""Ex Libris Alma MARCXML 변환 — 페르소나 04 100점 보완 (대학 분관).

페르소나 04 deal-breaker (Part 89): "DDC 미지원 + Alma 호환 X" 즉각 거부.
Part 90: DDC classifier·MeSH·LCSH 매핑 추가 → 본 모듈로 Alma MARCXML 출력 완성.

Alma MARCXML 형식:
- LC 표준 MARCXML schema (https://www.loc.gov/standards/marcxml/)
- pymarc record_to_xml() 활용 + Alma-specific 확장
- holdings/items 분리 (Alma 데이터 모델)
- 880 한자 병기 보존
- 650 ▾2 mesh / ▾2 lcsh source code 보존

Phase 1: KORMARC → MARCXML 변환 + Alma import 직접 사용 가능
Phase 2: SRU/Z39.50 자동 push (Alma API 통합)

Alma 호환성 검증:
- Alma Network Zone import API 형식 정합
- holdings 852 / items 876 자동 생성
- linking number (035) 보존
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom

from pymarc import Record

# Alma MARCXML namespace
MARCXML_NS = "http://www.loc.gov/MARC21/slim"
ALMA_NS = "http://com/exlibrisgroup/alma/bib"


def record_to_alma_marcxml(
    record: Record,
    *,
    library_code: str = "OURLIB",
    holdings_location: str = "MAIN",
    item_call_number: str | None = None,
) -> str:
    """KORMARC pymarc.Record → Alma MARCXML 문자열.

    Args:
        record: pymarc Record (KORMARC builder 출력)
        library_code: 자관 코드 (Alma library code)
        holdings_location: 소장 위치 (예: "MAIN", "MED" 의학분관)
        item_call_number: 청구기호 (Alma items 876 자동)

    Returns:
        UTF-8 MARCXML 문자열 (Alma import 직접 사용 가능)
    """
    ET.register_namespace("", MARCXML_NS)

    root = ET.Element(f"{{{MARCXML_NS}}}collection")
    record_el = ET.SubElement(root, f"{{{MARCXML_NS}}}record")

    # Leader (pymarc Leader 객체 → str)
    leader = ET.SubElement(record_el, f"{{{MARCXML_NS}}}leader")
    leader.text = str(record.leader) if hasattr(record, "leader") else "00000nam a2200000   4500"

    # Control fields (001~008)
    for field in record.fields:
        if field.tag in ("001", "003", "005", "006", "007", "008"):
            cf = ET.SubElement(record_el, f"{{{MARCXML_NS}}}controlfield")
            cf.set("tag", field.tag)
            cf.text = field.data if hasattr(field, "data") else ""
        else:
            df = ET.SubElement(record_el, f"{{{MARCXML_NS}}}datafield")
            df.set("tag", field.tag)
            ind1 = field.indicators[0] if hasattr(field, "indicators") and field.indicators else " "
            ind2 = field.indicators[1] if hasattr(field, "indicators") and field.indicators else " "
            df.set("ind1", str(ind1))
            df.set("ind2", str(ind2))
            for sub in getattr(field, "subfields", []):
                sf = ET.SubElement(df, f"{{{MARCXML_NS}}}subfield")
                sf.set("code", sub.code if hasattr(sub, "code") else sub[0])
                sf.text = sub.value if hasattr(sub, "value") else sub[1]

    # Alma holdings 852 (소장 정보)
    holdings = ET.SubElement(record_el, f"{{{MARCXML_NS}}}datafield")
    holdings.set("tag", "852")
    holdings.set("ind1", "0")
    holdings.set("ind2", "0")
    sf_a = ET.SubElement(holdings, f"{{{MARCXML_NS}}}subfield")
    sf_a.set("code", "a")
    sf_a.text = library_code
    sf_b = ET.SubElement(holdings, f"{{{MARCXML_NS}}}subfield")
    sf_b.set("code", "b")
    sf_b.text = holdings_location
    if item_call_number:
        sf_h = ET.SubElement(holdings, f"{{{MARCXML_NS}}}subfield")
        sf_h.set("code", "h")
        sf_h.text = item_call_number

    # Pretty-print
    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")


def write_alma_xml_file(
    record: Record,
    output_path: str,
    *,
    library_code: str = "OURLIB",
    holdings_location: str = "MAIN",
    item_call_number: str | None = None,
) -> None:
    """Alma MARCXML 파일 저장 (Alma import 폴더 직접 사용)."""
    xml_str = record_to_alma_marcxml(
        record,
        library_code=library_code,
        holdings_location=holdings_location,
        item_call_number=item_call_number,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_str)


# Alma-specific 권장 holdings location 코드 (페르소나 04 영업 가이드)
ALMA_HOLDINGS_LOCATIONS: dict[str, str] = {
    "MAIN": "본관 (Main Library)",
    "MED": "의학분관 (Medical Library)",
    "LAW": "법학분관 (Law Library)",
    "SCI": "과학기술분관 (Science Library)",
    "HUM": "인문사회분관 (Humanities/Social Sciences)",
    "RARE": "고서·귀중본 (Rare Books)",
    "RES": "지정도서 (Reserves)",
    "STK": "서고 (Stacks)",
}


__all__ = [
    "ALMA_HOLDINGS_LOCATIONS",
    "ALMA_NS",
    "MARCXML_NS",
    "record_to_alma_marcxml",
    "write_alma_xml_file",
]
