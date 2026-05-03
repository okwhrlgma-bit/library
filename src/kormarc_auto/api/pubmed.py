"""PubMed/MEDLINE 검색 클라이언트 — 페르소나 04 100점 (의학 도서관).

PubMed E-utilities (NCBI):
- esearch.fcgi: 키워드 → PMID 리스트
- efetch.fcgi: PMID → MEDLINE 메타데이터
- 무료·API 키 옵션 (rate limit 3 req/s → 10 req/s)

용도:
- 의학 학술 도서·저널 메타데이터 보강
- 의학 사서가 PubMed에서 직접 검색·KORMARC 자동 생성

KORMARC 매핑:
- PMID → 035 ▾a (PMID:12345)
- DOI → 024 ▾a (DOI 표준)
- MeSH → 650 ▾2 mesh (mesh_mapper.py 통합)
- Authors → 100/700
- Journal → 773 (모기관 정보)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

CONFIDENCE_PUBMED = 0.92  # 의학 도메인 표준


@dataclass(frozen=True)
class PubMedRecord:
    """PubMed 검색 결과 1건."""

    pmid: str
    title: str
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    year: str = ""
    doi: str = ""
    mesh_terms: list[str] = field(default_factory=list)
    abstract: str = ""
    confidence: float = CONFIDENCE_PUBMED


def search_pubmed(
    query: str,
    *,
    max_results: int = 10,
    api_key: str | None = None,
    timeout: int = 10,
) -> list[str]:
    """PubMed esearch → PMID 리스트.

    Args:
        query: 검색 키워드 (예: "diabetes mellitus 2026")
        max_results: 최대 PMID
        api_key: PUBMED_API_KEY (옵션·rate limit 10/s)
        timeout: 초 (기본 10)

    Returns:
        PMID 문자열 리스트
    """
    try:
        import requests
    except ImportError:
        logger.warning("requests 미설치")
        return []

    params: dict[str, Any] = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    }
    if api_key:
        params["api_key"] = api_key

    try:
        resp = requests.get(PUBMED_ESEARCH_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        logger.warning("PubMed search 실패: %s", e)
        return []


def fetch_pubmed_record(
    pmid: str,
    *,
    api_key: str | None = None,
    timeout: int = 10,
) -> PubMedRecord | None:
    """PubMed efetch → PubMedRecord (MEDLINE 형식 파싱).

    Returns:
        PubMedRecord 또는 None (실패 시)
    """
    try:
        import requests
    except ImportError:
        return None

    params: dict[str, Any] = {
        "db": "pubmed",
        "id": pmid,
        "rettype": "medline",
        "retmode": "text",
    }
    if api_key:
        params["api_key"] = api_key

    try:
        resp = requests.get(PUBMED_EFETCH_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        return _parse_medline(pmid, resp.text)
    except Exception as e:
        logger.warning("PubMed fetch 실패 (PMID=%s): %s", pmid, e)
        return None


def _parse_medline(pmid: str, text: str) -> PubMedRecord:
    """MEDLINE 형식 → PubMedRecord (간단 파서·핵심 필드만)."""
    title = ""
    authors: list[str] = []
    journal = ""
    year = ""
    doi = ""
    mesh: list[str] = []
    abstract = ""

    for line in text.splitlines():
        if line.startswith("TI  - "):
            title = line[6:].strip()
        elif line.startswith("AU  - "):
            authors.append(line[6:].strip())
        elif line.startswith("TA  - "):
            journal = line[6:].strip()
        elif line.startswith("DP  - "):
            dp = line[6:].strip()
            year = dp[:4] if dp[:4].isdigit() else ""
        elif line.startswith("AID - ") and "[doi]" in line:
            doi = line[6:].split(" ")[0]
        elif line.startswith("MH  - "):
            mesh.append(line[6:].strip())
        elif line.startswith("AB  - "):
            abstract = line[6:].strip()

    return PubMedRecord(
        pmid=pmid,
        title=title,
        authors=authors,
        journal=journal,
        year=year,
        doi=doi,
        mesh_terms=mesh,
        abstract=abstract,
    )


def to_kormarc_book_data(record: PubMedRecord) -> dict[str, Any]:
    """PubMedRecord → KORMARC builder book_data dict.

    Returns:
        builder.build_kormarc_record() 입력 형식
    """
    return {
        "title": record.title,
        "author": "; ".join(record.authors) if record.authors else "",
        "publisher": record.journal,
        "publication_year": record.year,
        "pmid": record.pmid,
        "doi": record.doi,
        "mesh_subjects": [{"term": m, "id": "", "source_keyword": m} for m in record.mesh_terms],
        "summary": record.abstract,
        "confidence": record.confidence,
        "attribution": "PubMed/MEDLINE (NCBI)",
        "035_pmid": f"PMID:{record.pmid}",  # KORMARC 035 ▾a
        "024_doi": record.doi,  # KORMARC 024 ▾a
    }


__all__ = [
    "CONFIDENCE_PUBMED",
    "PUBMED_EFETCH_URL",
    "PUBMED_ESEARCH_URL",
    "PubMedRecord",
    "fetch_pubmed_record",
    "search_pubmed",
    "to_kormarc_book_data",
]
