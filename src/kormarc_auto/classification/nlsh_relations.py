"""NLSH 우선어/비우선어 참조관계 — 주제명표목 업무지침(2021) §관계지시기호.

NL Korea 지침 §관계지시기호 (5종):
- USE  (U)  — 비우선어 → 우선어 (See: '한국전쟁' 입력 → '6·25전쟁' 사용)
- UF   (Used For) — 우선어 → 비우선어 (See also from)
- BT   (Broader Term) — 상위어 (계층 위)
- NT   (Narrower Term) — 하위어 (계층 아래)
- RT   (Related Term) — 관련어 (등위·연관)
- 시간: 이전(BT_chrono)/이후(NT_chrono) 관계는 별도 지시기호로 표현 가능

기존 `nlsh_vocabulary.py`는 어휘만, 본 모듈은 관계 그래프.
사서가 650 ▾a에 비우선어를 입력하면 우선어로 자동 치환 (NL 권고).

내장 그래프는 PoC 수준 (실 NLSH 시드 50종+). NL Korea LOD 다운로드 후
`load_from_skos()` 으로 확장 가능.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# 내장 시드 — NL Korea 「주제명표목 업무지침(2021)」 §부록 발췌
# (key) 우선어 -> {USE_FOR: [비우선어], BT: [상위어], NT: [하위어], RT: [관련어]}
NLSH_RELATIONS: dict[str, dict[str, list[str]]] = {
    # 역사·전쟁
    "6·25전쟁": {
        "USE_FOR": ["한국전쟁", "6.25사변", "한국동란", "6.25동란"],
        "BT": ["한국현대사"],
        "RT": ["남북관계", "휴전협정", "미군"],
    },
    "독립운동": {
        "USE_FOR": ["항일운동", "광복운동"],
        "BT": ["한국근대사"],
        "NT": ["3·1운동", "임시정부"],
        "RT": ["일제강점기"],
    },
    "한국현대사": {
        "BT": ["한국사"],
        "NT": ["6·25전쟁", "민주화운동", "산업화"],
    },
    "한국근대사": {
        "BT": ["한국사"],
        "NT": ["독립운동", "개화기", "갑오개혁"],
    },
    "한국사": {
        "NT": ["고대사", "고려사", "조선사", "한국근대사", "한국현대사"],
    },
    "조선사": {
        "USE_FOR": ["이조사", "조선왕조사"],
        "BT": ["한국사"],
    },
    # 문학
    "한국소설": {
        "USE_FOR": ["대한민국소설", "한국현대소설"],
        "BT": ["한국문학"],
        "NT": ["한국단편소설", "한국장편소설"],
        "RT": ["소설"],
    },
    "한국문학": {
        "USE_FOR": ["대한민국문학"],
        "BT": ["문학"],
        "NT": ["한국시", "한국소설", "한국수필", "한국희곡", "한국아동문학"],
    },
    # 도서관·정보
    "도서관학": {
        "USE_FOR": ["문헌정보학", "도서관정보학"],
        "BT": ["사회과학"],
        "NT": ["목록학", "분류학", "장서개발"],
        "RT": ["정보학"],
    },
    "분류학": {
        "USE_FOR": ["도서분류"],
        "BT": ["도서관학"],
        "RT": ["KDC", "DDC"],
    },
    "목록학": {
        "USE_FOR": ["서지학", "도서목록"],
        "BT": ["도서관학"],
        "RT": ["KORMARC", "MARC21"],
    },
    # 사회·경제
    "정보통신": {
        "USE_FOR": ["IT", "정보기술"],
        "BT": ["기술과학"],
        "NT": ["인공지능", "빅데이터", "사물인터넷"],
    },
    "인공지능": {
        "USE_FOR": ["AI", "기계학습", "딥러닝"],
        "BT": ["정보통신", "전산학"],
        "RT": ["로봇공학"],
    },
}


def _build_index() -> tuple[dict[str, str], dict[str, dict[str, list[str]]]]:
    """비우선어 → 우선어 매핑 인덱스 + 정규화 그래프.

    Returns: (use_to_preferred, full_graph)
    """
    use_to_pref: dict[str, str] = {}
    for pref, rels in NLSH_RELATIONS.items():
        use_to_pref[pref] = pref  # 자기 자신
        for nonpref in rels.get("USE_FOR", []):
            use_to_pref[nonpref] = pref
    return use_to_pref, NLSH_RELATIONS


_USE_TO_PREF, _GRAPH = _build_index()


def get_preferred_term(term: str) -> str:
    """비우선어 → 우선어. 모르면 입력 그대로."""
    if not term:
        return term
    return _USE_TO_PREF.get(term.strip(), term.strip())


def get_relations(term: str) -> dict[str, list[str]]:
    """우선어의 모든 관계 반환. 비우선어 입력 시 자동 치환."""
    pref = get_preferred_term(term)
    return dict(_GRAPH.get(pref, {}))


def normalize_subjects(
    terms: Iterable[str],
    *,
    deduplicate: bool = True,
) -> list[str]:
    """650 ▾a 후보 리스트를 우선어로 일괄 치환 + (옵션) 중복 제거."""
    out: list[str] = []
    seen: set[str] = set()
    for t in terms:
        pref = get_preferred_term(t)
        if deduplicate and pref in seen:
            continue
        seen.add(pref)
        out.append(pref)
    return out


def annotate_subject(term: str) -> dict[str, Any]:
    """650 ▾a 입력에 대한 사서 보조 정보.

    Returns:
        {
            "preferred": "6·25전쟁",       # 치환된 우선어 (입력이 비우선어였으면 변경)
            "input_was_nonpreferred": True,
            "BT": [...], "NT": [...], "UF": [...], "RT": [...],
            "suggested_650": "6·25전쟁",   # 그대로 ▾a 사용
            "see_references": ["한국전쟁", ...],  # 도보라참조용
        }
    """
    pref = get_preferred_term(term)
    rels = _GRAPH.get(pref, {})
    return {
        "preferred": pref,
        "input": term,
        "input_was_nonpreferred": term != pref,
        "BT": rels.get("BT", []),
        "NT": rels.get("NT", []),
        "UF": rels.get("USE_FOR", []),  # 도보라참조 후보
        "RT": rels.get("RT", []),
        "suggested_650": pref,
        "see_references": rels.get("USE_FOR", []),
    }


def load_from_skos(skos_jsonld_path: str | Path) -> int:
    """NL Korea LOD SKOS JSON-LD에서 그래프 확장.

    NL이 게시한 NLSH SKOS 파일을 다운로드 후 본 함수로 로드.
    skos:prefLabel → preferred / skos:altLabel → USE_FOR
    skos:broader → BT / skos:narrower → NT / skos:related → RT

    Returns: 로드된 우선어 개수
    """
    path = Path(skos_jsonld_path)
    if not path.exists():
        raise FileNotFoundError(f"SKOS 파일 없음: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    graph = data.get("@graph", []) if isinstance(data, dict) else data
    if not isinstance(graph, list):
        raise ValueError("SKOS JSON-LD @graph 배열 필요")

    count = 0
    for node in graph:
        pref = _extract_label(node.get("prefLabel"))
        if not pref:
            continue
        rels: dict[str, list[str]] = {
            "USE_FOR": [],
            "BT": [],
            "NT": [],
            "RT": [],
        }
        alt = node.get("altLabel")
        if alt:
            rels["USE_FOR"] = (
                [_extract_label(x) for x in alt] if isinstance(alt, list) else [_extract_label(alt)]
            )
        rels["USE_FOR"] = [x for x in rels["USE_FOR"] if x]
        for k_skos, k_int in (("broader", "BT"), ("narrower", "NT"), ("related", "RT")):
            v = node.get(k_skos)
            if v:
                refs = v if isinstance(v, list) else [v]
                rels[k_int] = [
                    str(r.get("@id", r)) if isinstance(r, dict) else str(r) for r in refs
                ]
        NLSH_RELATIONS[pref] = rels
        count += 1
    # 인덱스 재구축
    global _USE_TO_PREF, _GRAPH
    _USE_TO_PREF, _GRAPH = _build_index()
    logger.info("NLSH SKOS 로드: %d 우선어", count)
    return count


def _extract_label(value: Any) -> str:
    """SKOS Label (str / dict @value / 리스트 첫번째) → str."""
    if isinstance(value, dict):
        return str(value.get("@value") or value.get("ko") or "").strip()
    if isinstance(value, list) and value:
        return _extract_label(value[0])
    return str(value or "").strip()


__all__ = [
    "NLSH_RELATIONS",
    "annotate_subject",
    "get_preferred_term",
    "get_relations",
    "load_from_skos",
    "normalize_subjects",
]
