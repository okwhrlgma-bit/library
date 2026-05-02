"""MARC·MARCXML·MODS·KOLAS 백업 import — Part 70 갭 2 정합.

사서 페인 (Part 70):
- 알파스 → kormarc-auto 마이그
- KOLAS 백업 → 신규 시스템
- 기존 도서관 시스템 = MARC·MARCXML·MODS 형식

해결: 4 형식 import 자동.
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def import_marc_binary(mrc_bytes: bytes) -> list[dict[str, Any]]:
    """MARC ISO 2709 (.mrc) → list[dict].

    pymarc 사용.
    """
    try:
        import pymarc
    except ImportError:
        return []

    records = []
    reader = pymarc.MARCReader(io.BytesIO(mrc_bytes), to_unicode=True, force_utf8=True)
    for record in reader:
        if record is None:
            continue
        records.append(_record_to_dict(record))
    return records


def import_marcxml(xml_text: str) -> list[dict[str, Any]]:
    """MARCXML → list[dict].

    LC MARCXML schema 정합.
    """
    records = []
    ns = {"marc": "http://www.loc.gov/MARC21/slim"}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    record_elements = root.findall(".//marc:record", ns) or root.findall(".//record")

    for rec_el in record_elements:
        record_data: dict[str, Any] = {"control_fields": [], "data_fields": []}
        for field in rec_el:
            tag_local = field.tag.split("}")[-1]  # namespace 제거
            if tag_local == "leader":
                record_data["leader"] = field.text or ""
            elif tag_local == "controlfield":
                record_data["control_fields"].append(
                    {"tag": field.get("tag", ""), "data": field.text or ""}
                )
            elif tag_local == "datafield":
                subfields = []
                for sub in field:
                    subfields.append({"code": sub.get("code", ""), "value": sub.text or ""})
                record_data["data_fields"].append(
                    {
                        "tag": field.get("tag", ""),
                        "ind1": field.get("ind1", " "),
                        "ind2": field.get("ind2", " "),
                        "subfields": subfields,
                    }
                )
        records.append(record_data)
    return records


def import_mods(xml_text: str) -> list[dict[str, Any]]:
    """MODS XML → list[dict] (NLK 디지털 컬렉션 정합)."""
    records = []
    ns = {"mods": "http://www.loc.gov/mods/v3"}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    # mods:mods 자식 또는 root 자체가 mods
    mods_elements = root.findall(".//mods:mods", ns)
    if not mods_elements:
        if root.tag.endswith("mods"):
            mods_elements = [root]
        else:
            # root가 collection·자식이 mods
            mods_elements = [el for el in root if el.tag.endswith("mods")]

    for mods_el in mods_elements:
        record_data: dict[str, Any] = {}

        title_el = mods_el.find(".//mods:title", ns)
        if title_el is not None:
            record_data["title"] = title_el.text or ""

        name_el = mods_el.find(".//mods:namePart", ns)
        if name_el is not None:
            record_data["author"] = name_el.text or ""

        publisher_el = mods_el.find(".//mods:publisher", ns)
        if publisher_el is not None:
            record_data["publisher"] = publisher_el.text or ""

        date_el = mods_el.find(".//mods:dateIssued", ns)
        if date_el is not None:
            record_data["year"] = date_el.text or ""

        isbn_el = mods_el.find(".//mods:identifier[@type='isbn']", ns)
        if isbn_el is not None:
            record_data["isbn"] = isbn_el.text or ""

        if record_data:
            records.append(record_data)

    return records


def import_kolas_backup(file_path: Path) -> list[dict[str, Any]]:
    """KOLAS 백업 (.mrc) 일괄 import.

    KOLAS III 표준 .mrc 백업 파일 정합.
    """
    return import_marc_binary(file_path.read_bytes())


def _record_to_dict(record: Any) -> dict[str, Any]:
    """pymarc.Record → dict."""
    data: dict[str, Any] = {
        "leader": str(record.leader),
        "control_fields": [],
        "data_fields": [],
    }
    for field in record.fields:
        if field.is_control_field():
            data["control_fields"].append({"tag": field.tag, "data": field.data})
        else:
            ind1, ind2 = (field.indicators[0], field.indicators[1])
            data["data_fields"].append(
                {
                    "tag": field.tag,
                    "ind1": ind1,
                    "ind2": ind2,
                    "subfields": [{"code": s.code, "value": s.value} for s in field.subfields],
                }
            )
    return data


__all__ = [
    "import_kolas_backup",
    "import_marc_binary",
    "import_marcxml",
    "import_mods",
]
