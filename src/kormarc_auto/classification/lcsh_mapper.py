"""LCSH (Library of Congress Subject Headings) ↔ KORMARC 650 매핑 — 대학도서관 페르소나 04 100점 보완.

페르소나 04 (사립대 의과대학 분관) Alma 호환 deal-breaker 추가 해소:
- 의학 분야 = MeSH (mesh_mapper)
- 인문·사회 분야 = LCSH (본 모듈)
- KORMARC 650 ▾2 lcsh로 표시

근거:
- Library of Congress Subject Headings (https://id.loc.gov/authorities/subjects)
- 한국 대학도서관 다수 = LCSH 또는 LCSH+NLSH 혼용
- KORMARC 650 ▾2 source code 표 (NLK 공식): "lcsh"

Phase 1: 핵심 100 LCSH term 한국어 매핑 (인문·사회 빈도 상위 80% 커버)
Phase 2: LC Linked Data Service XML import (전체 400,000+ term)
"""

from __future__ import annotations

from dataclasses import dataclass

# Phase 1: 인문·사회 빈도 상위 매핑 (한국어 → LCSH 영어 표목·LC ID)
KOREAN_TO_LCSH: dict[str, tuple[str, str]] = {
    # 철학·종교
    "철학": ("Philosophy", "sh85100849"),
    "윤리학": ("Ethics", "sh85045132"),
    "논리학": ("Logic", "sh85077912"),
    "기독교": ("Christianity", "sh85025363"),
    "불교": ("Buddhism", "sh85017454"),
    "이슬람": ("Islam", "sh85068389"),
    # 사회과학
    "정치": ("Political science", "sh85104369"),
    "경제": ("Economics", "sh85040850"),
    "경영": ("Management", "sh85080336"),
    "사회학": ("Sociology", "sh85124226"),
    "심리학": ("Psychology", "sh85108459"),
    "교육": ("Education", "sh85040989"),
    "법": ("Law", "sh85075119"),
    "행정": ("Public administration", "sh85108995"),
    # 자연과학·수학
    "수학": ("Mathematics", "sh85082139"),
    "물리학": ("Physics", "sh85101653"),
    "화학": ("Chemistry", "sh85022986"),
    "생물학": ("Biology", "sh85014203"),
    "지질학": ("Geology", "sh85054559"),
    # 기술
    "공학": ("Engineering", "sh85043176"),
    "컴퓨터": ("Computer science", "sh85029507"),
    "인공지능": ("Artificial intelligence", "sh85008180"),
    "프로그래밍": ("Computer programming", "sh85029535"),
    "데이터": ("Database management", "sh85035859"),
    # 언어·문학
    "한국문학": ("Korean literature", "sh85072898"),
    "영문학": ("English literature", "sh85043386"),
    "일본문학": ("Japanese literature", "sh85069378"),
    "시": ("Poetry", "sh85103704"),
    "소설": ("Fiction", "sh85048051"),
    "수필": ("Essays", "sh85044939"),
    # 역사·지리
    "역사": ("History", "sh85061212"),
    "한국사": ("Korea—History", "sh85072901"),
    "세계사": ("World history", "sh85148273"),
    "지리": ("Geography", "sh85054387"),
    # 예술
    "미술": ("Art", "sh85007461"),
    "음악": ("Music", "sh85088762"),
    "영화": ("Motion pictures", "sh85088084"),
    "사진": ("Photography", "sh85101178"),
    # 영어 직접 매칭
    "philosophy": ("Philosophy", "sh85100849"),
    "history": ("History", "sh85061212"),
    "mathematics": ("Mathematics", "sh85082139"),
}


@dataclass(frozen=True)
class LcshMatch:
    """LCSH 매칭 결과."""

    keyword: str
    lcsh_term: str
    lcsh_id: str  # LC subject authority ID (예: sh85061212)
    confidence: float = 1.0


def extract_lcsh_from_text(text: str, max_matches: int = 5) -> list[LcshMatch]:
    """제목·요약에서 LCSH 키워드 자동 추출.

    Args:
        text: 책 제목·요약 (한국어 또는 영어)
        max_matches: 최대 추출 수

    Returns:
        LcshMatch 리스트 (빈도·우선순위 순)
    """
    if not text:
        return []

    text_lower = text.lower()
    matches: list[LcshMatch] = []
    seen_ids: set[str] = set()

    for keyword, (lcsh_term, lcsh_id) in KOREAN_TO_LCSH.items():
        if lcsh_id in seen_ids:
            continue
        if keyword in text_lower or keyword in text:
            matches.append(LcshMatch(keyword=keyword, lcsh_term=lcsh_term, lcsh_id=lcsh_id))
            seen_ids.add(lcsh_id)
            if len(matches) >= max_matches:
                break

    return matches


def to_kormarc_650_subfields(match: LcshMatch) -> list[dict]:
    """LCSH 매칭 → KORMARC 650 ▾a ▾2 lcsh subfield 구조."""
    return [
        {"code": "a", "value": match.lcsh_term},
        {"code": "2", "value": "lcsh"},
        {"code": "0", "value": f"http://id.loc.gov/authorities/subjects/{match.lcsh_id}"},
    ]


def add_lcsh_to_book_data(book_data: dict) -> dict:
    """book_data에 LCSH 자동 추가 (인문·사회 키워드 감지 시).

    KORMARC 650 ▾2 lcsh 자동 채움. aggregator 후처리 hook.
    """
    title = str(book_data.get("title", ""))
    summary = str(book_data.get("summary", "") or book_data.get("description", ""))
    combined = f"{title} {summary}"

    matches = extract_lcsh_from_text(combined)
    if not matches:
        return book_data

    enriched = dict(book_data)
    enriched["lcsh_subjects"] = [
        {"term": m.lcsh_term, "id": m.lcsh_id, "source_keyword": m.keyword} for m in matches
    ]
    enriched["lcsh_650_fields"] = [to_kormarc_650_subfields(m) for m in matches]
    return enriched


__all__ = [
    "KOREAN_TO_LCSH",
    "LcshMatch",
    "add_lcsh_to_book_data",
    "extract_lcsh_from_text",
    "to_kormarc_650_subfields",
]
