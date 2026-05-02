"""데이터 export 다양화 — Part 70 갭 1 정합.

사서 페인 (Part 70):
- KOLAS·KLMS .mrc + CSV 만 = 부족
- 대학 (BIBFRAME)·국제 (MODS)·웹 통합 (JSON·LOD) 진입 X
- 디지털 자원 (Dublin Core·schema.org) 미지원

해결: 4 export 형식 통합 = MARCXML·MODS·JSON-LD·OAI-PMH.
"""

from __future__ import annotations

import json
from typing import Any
from xml.sax.saxutils import escape


def export_marcxml(record_data: dict[str, Any]) -> str:
    """MARCXML export (대학·KORIBLE·OCLC 호환).

    LC MARCXML schema 정합.
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<record xmlns="http://www.loc.gov/MARC21/slim">',
        f"  <leader>{escape(record_data.get('leader', '00000nam a2200000   4500'))}</leader>",
    ]
    for field in record_data.get("control_fields", []):
        tag = field.get("tag", "")
        data = escape(field.get("data", ""))
        lines.append(f'  <controlfield tag="{tag}">{data}</controlfield>')

    for field in record_data.get("data_fields", []):
        tag = field.get("tag", "")
        ind1 = field.get("ind1", " ")
        ind2 = field.get("ind2", " ")
        lines.append(f'  <datafield tag="{tag}" ind1="{ind1}" ind2="{ind2}">')
        for sub in field.get("subfields", []):
            code = sub.get("code", "")
            value = escape(sub.get("value", ""))
            lines.append(f'    <subfield code="{code}">{value}</subfield>')
        lines.append("  </datafield>")

    lines.append("</record>")
    return "\n".join(lines)


def export_mods(record_data: dict[str, Any]) -> str:
    """MODS XML export (NLK 디지털 컬렉션 정합).

    NLK 온라인자료 메타데이터 DB 구축 지침 정합.
    """
    title = escape(record_data.get("title", ""))
    author = escape(record_data.get("author", ""))
    publisher = escape(record_data.get("publisher", ""))
    year = escape(str(record_data.get("year", "")))
    isbn = escape(record_data.get("isbn", ""))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mods xmlns="http://www.loc.gov/mods/v3" version="3.7">
  <titleInfo>
    <title>{title}</title>
  </titleInfo>
  <name type="personal">
    <namePart>{author}</namePart>
    <role><roleTerm type="text">creator</roleTerm></role>
  </name>
  <originInfo>
    <publisher>{publisher}</publisher>
    <dateIssued>{year}</dateIssued>
  </originInfo>
  <identifier type="isbn">{isbn}</identifier>
  <typeOfResource>text</typeOfResource>
  <language><languageTerm type="code" authority="iso639-2b">kor</languageTerm></language>
</mods>"""


def export_jsonld(record_data: dict[str, Any]) -> str:
    """JSON-LD export (schema.org Book 정합·SEO·웹 통합).

    Google·네이버 검색 schema markup 정합.
    """
    data = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": record_data.get("title", ""),
        "author": {
            "@type": "Person",
            "name": record_data.get("author", ""),
        },
        "publisher": {
            "@type": "Organization",
            "name": record_data.get("publisher", ""),
        },
        "datePublished": str(record_data.get("year", "")),
        "isbn": record_data.get("isbn", ""),
        "inLanguage": "ko",
    }
    if kdc := record_data.get("kdc"):
        data["about"] = {"@type": "Thing", "identifier": f"KDC:{kdc}"}
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_oai_pmh(record_data: dict[str, Any], *, identifier: str = "") -> str:
    """OAI-PMH ListRecords response 형식 (KOLISNET·종합목록 수확).

    Dublin Core (oai_dc) 메타데이터 prefix.
    """
    title = escape(record_data.get("title", ""))
    creator = escape(record_data.get("author", ""))
    publisher = escape(record_data.get("publisher", ""))
    date = escape(str(record_data.get("year", "")))
    identifier_v = escape(identifier or record_data.get("isbn", ""))

    return f"""<record>
  <header>
    <identifier>{identifier_v}</identifier>
    <datestamp>{date}</datestamp>
  </header>
  <metadata>
    <oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
               xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:title>{title}</dc:title>
      <dc:creator>{creator}</dc:creator>
      <dc:publisher>{publisher}</dc:publisher>
      <dc:date>{date}</dc:date>
      <dc:identifier>{identifier_v}</dc:identifier>
      <dc:type>text</dc:type>
      <dc:language>ko</dc:language>
    </oai_dc:dc>
  </metadata>
</record>"""


__all__ = ["export_jsonld", "export_marcxml", "export_mods", "export_oai_pmh"]
