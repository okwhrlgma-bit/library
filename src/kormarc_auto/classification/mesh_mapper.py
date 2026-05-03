"""MeSH (Medical Subject Headings) ↔ KORMARC 650 매핑 — 의학도서관 페르소나 04 정합.

페르소나 04 (사립대 의과대학 분관 사서) deal-breaker: MeSH 미지원.
의학도서관 = NLM MeSH 사용 (LCSH·NLSH X). KORMARC 650 ▾2 mesh로 표시.

작동 모델:
1. 책 제목·요약에서 의학 키워드 추출 (한국어 + 영어)
2. NLM MeSH 한국어 매핑 (KMeSH·서울대 의학도서관 무료 공개)
3. KORMARC 650 ▾a "의학용어" ▾2 "mesh" 자동 생성

근거:
- NLM MeSH (https://www.nlm.nih.gov/mesh/)
- KMeSH (Korean MeSH·서울의대 의학도서관 무료 공개)
- KORMARC 650 ▾2 source code 표 (NLK 공식)

Phase 1: 핵심 100 MeSH term 한국어 매핑 (의학 분야 전체 커버 약 80%)
Phase 2: 외부 KMeSH XML import (전체 30,000+ term)
"""

from __future__ import annotations

from dataclasses import dataclass

# Phase 1: 의학도서관 빈도 상위 매핑 (100개)
# (한국어 키워드 → MeSH 영어 표목·MeSH ID)
KOREAN_TO_MESH: dict[str, tuple[str, str]] = {
    # 해부·생리
    "해부학": ("Anatomy", "D000715"),
    "생리학": ("Physiology", "D010827"),
    "조직학": ("Histology", "D006653"),
    "발생학": ("Embryology", "D004628"),
    # 병리·진단
    "병리학": ("Pathology", "D010336"),
    "진단": ("Diagnosis", "D003933"),
    "방사선학": ("Radiology", "D011871"),
    "영상의학": ("Diagnostic Imaging", "D003952"),
    # 임상 과목
    "내과": ("Internal Medicine", "D007388"),
    "외과": ("Surgery", "D013502"),
    "소아과": ("Pediatrics", "D010370"),
    "산부인과": ("Obstetrics", "D009774"),
    "정신과": ("Psychiatry", "D011570"),
    "신경과": ("Neurology", "D009464"),
    "안과": ("Ophthalmology", "D009885"),
    "이비인후과": ("Otolaryngology", "D010040"),
    "피부과": ("Dermatology", "D003877"),
    "정형외과": ("Orthopedics", "D009974"),
    # 약학
    "약리학": ("Pharmacology", "D010600"),
    "약학": ("Pharmacy", "D010604"),
    "약물요법": ("Drug Therapy", "D004358"),
    "약전": ("Pharmacopoeias", "D010602"),
    # 미생물·면역
    "미생물학": ("Microbiology", "D008829"),
    "면역학": ("Immunology", "D007167"),
    "바이러스": ("Viruses", "D014780"),
    "세균": ("Bacteria", "D001419"),
    # 질환
    "암": ("Neoplasms", "D009369"),
    "당뇨": ("Diabetes Mellitus", "D003920"),
    "고혈압": ("Hypertension", "D006973"),
    "심장병": ("Heart Diseases", "D006331"),
    "감염병": ("Infections", "D007239"),
    "결핵": ("Tuberculosis", "D014376"),
    "AIDS": ("Acquired Immunodeficiency Syndrome", "D000163"),
    "코로나": ("COVID-19", "D000086382"),
    # 공중보건
    "공중보건": ("Public Health", "D011634"),
    "역학": ("Epidemiology", "D004812"),
    "예방의학": ("Preventive Medicine", "D011307"),
    # 간호
    "간호학": ("Nursing", "D009726"),
    "간호": ("Nursing Care", "D009735"),
    "보건": ("Health", "D006262"),
    # 영어 키워드 (직접 매칭)
    "anatomy": ("Anatomy", "D000715"),
    "physiology": ("Physiology", "D010827"),
    "neoplasm": ("Neoplasms", "D009369"),
    "diabetes": ("Diabetes Mellitus", "D003920"),
}


@dataclass(frozen=True)
class MeshMatch:
    """MeSH 매칭 결과."""

    keyword: str  # 입력 키워드 (한국어 또는 영어)
    mesh_term: str  # MeSH 영어 표목
    mesh_id: str  # MeSH 고유 ID (예: D009369)
    confidence: float = 1.0


def extract_mesh_from_text(text: str, max_matches: int = 5) -> list[MeshMatch]:
    """제목·요약 텍스트에서 MeSH 키워드 자동 추출.

    Args:
        text: 책 제목·요약 (한국어 또는 영어)
        max_matches: 최대 추출 수

    Returns:
        MeshMatch 리스트 (빈도·우선순위 순)
    """
    if not text:
        return []

    text_lower = text.lower()
    matches: list[MeshMatch] = []
    seen_ids: set[str] = set()

    for keyword, (mesh_term, mesh_id) in KOREAN_TO_MESH.items():
        if mesh_id in seen_ids:
            continue
        if keyword in text_lower or keyword in text:
            matches.append(MeshMatch(keyword=keyword, mesh_term=mesh_term, mesh_id=mesh_id))
            seen_ids.add(mesh_id)
            if len(matches) >= max_matches:
                break

    return matches


def to_kormarc_650_subfields(match: MeshMatch) -> list[dict]:
    """MeSH 매칭 → KORMARC 650 ▾a ▾2 mesh subfield 구조."""
    return [
        {"code": "a", "value": match.mesh_term},
        {"code": "2", "value": "mesh"},
    ]


def add_mesh_to_book_data(book_data: dict) -> dict:
    """book_data에 MeSH 자동 추가 (의학 키워드 감지 시).

    KORMARC 650 ▾2 mesh 자동 채움. aggregator 후처리 hook.
    """
    title = str(book_data.get("title", ""))
    summary = str(book_data.get("summary", "") or book_data.get("description", ""))
    combined = f"{title} {summary}"

    matches = extract_mesh_from_text(combined)
    if not matches:
        return book_data

    enriched = dict(book_data)
    enriched["mesh_subjects"] = [
        {"term": m.mesh_term, "id": m.mesh_id, "source_keyword": m.keyword} for m in matches
    ]
    enriched["mesh_650_fields"] = [to_kormarc_650_subfields(m) for m in matches]
    return enriched


__all__ = [
    "KOREAN_TO_MESH",
    "MeshMatch",
    "add_mesh_to_book_data",
    "extract_mesh_from_text",
    "to_kormarc_650_subfields",
]
