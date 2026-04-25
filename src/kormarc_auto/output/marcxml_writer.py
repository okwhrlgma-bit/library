"""MARCXML 출력 (Alma·Koha·BIBFRAME 호환)."""

from __future__ import annotations

from pathlib import Path

from pymarc import Record, marcxml


def write_marcxml(record: Record, isbn: str, output_dir: str | Path = "./output") -> Path:
    """MARCXML 형식으로 저장."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{isbn}.xml"

    xml_bytes = marcxml.record_to_xml(record, namespace=True)
    out_path.write_bytes(xml_bytes)
    return out_path
