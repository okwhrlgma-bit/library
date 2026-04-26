"""NLSH 참조관계 단위 테스트."""

from __future__ import annotations

import json

from kormarc_auto.classification.nlsh_relations import (
    annotate_subject,
    get_preferred_term,
    get_relations,
    load_from_skos,
    normalize_subjects,
)


def test_preferred_term_passes_through():
    assert get_preferred_term("6·25전쟁") == "6·25전쟁"


def test_preferred_term_substitutes():
    """비우선어 → 우선어."""
    assert get_preferred_term("한국전쟁") == "6·25전쟁"
    assert get_preferred_term("문헌정보학") == "도서관학"
    assert get_preferred_term("AI") == "인공지능"


def test_preferred_term_unknown():
    """모르는 어는 입력 그대로."""
    assert get_preferred_term("처음듣는단어") == "처음듣는단어"


def test_normalize_subjects_dedup():
    """비우선어 + 우선어 혼재 → 중복 제거 후 우선어만."""
    out = normalize_subjects(["한국전쟁", "6·25전쟁", "독립운동"])
    assert out == ["6·25전쟁", "독립운동"]


def test_normalize_subjects_keep_duplicates():
    out = normalize_subjects(["한국전쟁", "6·25전쟁"], deduplicate=False)
    assert out == ["6·25전쟁", "6·25전쟁"]


def test_get_relations_for_preferred():
    rels = get_relations("도서관학")
    assert "USE_FOR" in rels
    assert "문헌정보학" in rels["USE_FOR"]
    assert "분류학" in rels["NT"]


def test_annotate_subject_nonpreferred_input():
    info = annotate_subject("한국전쟁")
    assert info["preferred"] == "6·25전쟁"
    assert info["input_was_nonpreferred"] is True
    assert "한국전쟁" in info["see_references"]
    assert "한국현대사" in info["BT"]


def test_annotate_subject_unknown():
    info = annotate_subject("처음듣는단어")
    assert info["preferred"] == "처음듣는단어"
    assert info["input_was_nonpreferred"] is False
    assert info["BT"] == []


def test_load_from_skos(tmp_path):
    skos_path = tmp_path / "skos.jsonld"
    skos_path.write_text(
        json.dumps(
            {
                "@graph": [
                    {
                        "prefLabel": "테스트우선어",
                        "altLabel": ["테스트비우선어1", "테스트비우선어2"],
                        "broader": "테스트상위어",
                        "narrower": ["테스트하위1"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    count = load_from_skos(skos_path)
    assert count == 1
    assert get_preferred_term("테스트비우선어1") == "테스트우선어"
    info = annotate_subject("테스트우선어")
    assert "테스트하위1" in info["NT"]
